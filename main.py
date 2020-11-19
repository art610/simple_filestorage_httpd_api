#!/usr/bin/python3.8
# -*- coding: UTF-8 -*-
"""
Данный модуль будет основной точкой входа
"""
import os
import sys
from loguru import logger
from daemon import Daemon
import server

logger.add("./log/daemon/debug.log", format="{time} {level} {message}",
           level="DEBUG",
           rotation="10MB")
logger = logger.opt(colors=True)

SERVER_ADDR: str = 'localhost'
SERVER_PORT: int = 9000

LISTEN_CLIENTS_NUMB: int = 12
MAX_SERVER_BUFFER_SIZE: int = 4096

PID_FILE = './daemon_pid.pid'
STD_IN = os.devnull
STD_OUT = './log/output.log'
STD_ERR = './log/error.log'
HOME_DIR = '.'


class App(Daemon):
    """
    Class App extends Daemon for HTTP-server
    """

    def run(self):
        """
        HTTPD
        """
        server.run_server(SERVER_ADDR, SERVER_PORT, LISTEN_CLIENTS_NUMB,
                          MAX_SERVER_BUFFER_SIZE)


if __name__ == '__main__':
    daemon_main = App(PID_FILE, STD_IN, STD_OUT, STD_ERR, HOME_DIR)

    control = sys.argv[1]

    if control == 'start':
        daemon_main.start()
    elif control == 'stop':
        daemon_main.stop()
    elif control == 'restart':
        daemon_main.restart()
    elif control == 'run':
        daemon_main.run()
    elif control == 'get_pid':
        logger.info("Daemon PID: {}", daemon_main.get_pid())
    else:
        daemon_main.is_running()
