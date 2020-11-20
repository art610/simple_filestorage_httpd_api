#!/usr/bin/python3.8
# -*- coding: UTF-8 -*-

"""
***
Modified generic daemon class
***
Author:         http://www.jejik.com/articles/2007/02/
                        a_simple_unix_linux_daemon_in_python/www.boxedice.com
License:        http://creativecommons.org/licenses/by-sa/3.0/

Modified by (1):    23rd Jan 2009 (David Mytton <david@boxedice.com>)
Changes (1):
                - Replaced hard coded '/dev/null in __init__ with os.devnull
                - Added OS check to conditionally remove code that doesn't
                  work on OS X
                - Added output to console on completion
                - Tidied up formatting
                11th Mar 2009 (David Mytton <david@boxedice.com>)
                - Fixed problem with daemon exiting on Python 2.4
                  (before SystemExit was part of the Exception base)
                13th Aug 2010 (David Mytton <david@boxedice.com>
                - Fixed unhandled exception if PID file is empty

Modified by (2):    Artem Zhelonkin (tyo3436@gmail.com)
Changes (1):
                - Class 'Daemon' earlie inherits from object, that was safely
                removed from bases in python3 (useless-object-inheritance)
                - Remove eventlet import and Daemon __init__ argument
                - Remove gevent import and Daemon __init__ argument
                - Add signal.SIGHUP with sigtermhandler func
                - Add logger with Loguru
                - Add changes with PEP8
"""

from __future__ import print_function
import atexit
import errno
import os
import sys
import time
import signal
from loguru import logger

logger.add("./log/daemon/debug.log", format="{time} {level} {message}",
           level="DEBUG",
           rotation="10MB")
logger = logger.opt(colors=True)


class Daemon:
    """
    A generic daemon class.
    Usage: subclass the Daemon class and override the run() method
    """

    def __init__(self, pidfile, stdin=os.devnull,
                 stdout=os.devnull, stderr=os.devnull,
                 home_dir='.', umask=0o22, verbose=1):
        self.stdin = stdin
        self.stdout = stdout
        self.stderr = stderr
        self.pidfile = pidfile
        self.home_dir = home_dir
        self.verbose = verbose
        self.umask = umask
        self.daemon_alive = True

    def log(self, *args):
        """

        :param args:
        :return:
        """
        if self.verbose >= 1:
            logger.info(*args)

    def daemonize(self):
        """
        Do the UNIX double-fork magic, see Stevens' "Advanced
        Programming in the UNIX Environment" for details (ISBN 0201563177)
        http://www.erlenstar.demon.co.uk/unix/faq_2.html#SEC16
        """
        try:
            pid = os.fork()
            if pid > 0:
                # Exit first parent
                sys.exit(0)
        except OSError as os_error:
            sys.stderr.write(
                "fork #1 failed: %d (%s)\n" % (
                    os_error.errno, os_error.strerror))
            sys.exit(1)

        # Decouple from parent environment
        os.chdir(self.home_dir)
        os.setsid()
        os.umask(self.umask)

        # Do second fork
        try:
            pid = os.fork()
            if pid > 0:
                # Exit from second parent
                sys.exit(0)
        except OSError as os_error:
            sys.stderr.write(
                "fork #2 failed: %d (%s)\n" % (
                    os_error.errno, os_error.strerror))
            sys.exit(1)

        if sys.platform != 'darwin':  # This block breaks on OS X
            # Redirect standard file descriptors
            sys.stdout.flush()
            sys.stderr.flush()
            std_in = open(self.stdin, 'r')
            std_out = open(self.stdout, 'a+')
            if self.stderr:
                try:
                    std_err = open(self.stderr, 'a+', 0)
                except ValueError:
                    # Python 3 can't have unbuffered text I/O
                    std_err = open(self.stderr, 'a+', 1)
            else:
                std_err = std_out
            os.dup2(std_in.fileno(), sys.stdin.fileno())
            os.dup2(std_out.fileno(), sys.stdout.fileno())
            os.dup2(std_err.fileno(), sys.stderr.fileno())

        def sigterm_handler(signum, frame):
            logger.debug(
                "System reboot - daemon was stopped:\n sig: {} \n frame: {}",
                signum,
                frame)
            self.daemon_alive = False
            sys.exit()

        signal.signal(signal.SIGTERM, sigterm_handler)
        signal.signal(signal.SIGINT, sigterm_handler)
        signal.signal(signal.SIGHUP, sigterm_handler)

        self.log("Started")

        # Write pidfile
        atexit.register(
            self.delpid)  # Make sure pid file is removed if we quit
        pid = str(os.getpid())
        open(self.pidfile, 'w+').write("%s\n" % pid)

    def delpid(self):
        """
        Delete daemon PID file
        :return: None
        """
        try:
            # the process may fork itself again
            pid = int(open(self.pidfile, 'r').read().strip())
            if pid == os.getpid():
                os.remove(self.pidfile)
        except OSError as os_error:
            if os_error.errno == errno.ENOENT:
                pass
            else:
                raise

    def start(self, *args, **kwargs):
        """
        Start the daemon
        """

        self.log("Starting...")

        # Check for a pidfile to see if the daemon already runs
        try:
            pid_file_stream = open(self.pidfile, 'r')
            pid = int(pid_file_stream.read().strip())
            pid_file_stream.close()
        except IOError:
            pid = None
        except SystemExit:
            pid = None

        if pid:
            message = "pidfile %s already exists. Is it already running?\n"
            sys.stderr.write(message % self.pidfile)
            sys.exit(1)

        # Start the daemon
        self.daemonize()
        self.run(*args, **kwargs)

    def stop(self):
        """
        Stop the daemon
        """

        if self.verbose >= 1:
            self.log("Stopping...")

        # Get the pid from the pidfile
        pid = self.get_pid()

        if not pid:
            message = "pidfile %s does not exist. Not running?\n"
            sys.stderr.write(message % self.pidfile)

            # Just to be sure. A ValueError might occur if the PID file is
            # empty but does actually exist
            if os.path.exists(self.pidfile):
                os.remove(self.pidfile)

            return  # Not an error in a restart

        # Try killing the daemon process
        try:
            i = 0
            while 1:
                os.kill(pid, signal.SIGTERM)
                time.sleep(0.1)
                i = i + 1
                if i % 10 == 0:
                    os.kill(pid, signal.SIGHUP)
        except OSError as err:
            if err.errno == errno.ESRCH:
                if os.path.exists(self.pidfile):
                    os.remove(self.pidfile)
            else:
                print(str(err))
                sys.exit(1)

        self.log("Stopped")

    def restart(self):
        """
        Restart the daemon
        """
        self.stop()
        self.start()

    def get_pid(self):
        """
        Get daemon Process ID
        :return: pid or None
        """
        try:
            pid_file_stream = open(self.pidfile, 'r')
            pid = int(pid_file_stream.read().strip())
            pid_file_stream.close()
        except IOError:
            pid = None
        except SystemExit:
            pid = None
        return pid

    def is_running(self):
        """
        Get info about daemon process status
        """
        pid = self.get_pid()

        if pid is None:
            self.log('Process is stopped')
            return False
        if os.path.exists('/proc/%d' % pid):
            self.log('Process (pid %d) is running...' % pid)
            return True

        self.log('Process (pid %d) is killed' % pid)
        return False

    def run(self):
        """
        You should override this method when you subclass Daemon.
        It will be called after the process has been
        daemonized by start() or restart().
        """
        raise NotImplementedError
