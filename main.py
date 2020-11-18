"""
Данный модуль будет основной точкой входа
"""
import os
import sys
import server
from daemon import Daemon
from loguru import logger

logger.add("./log/daemon/debug.log", format="{time} {level} {message}",
           level="DEBUG",
           rotation="10MB")
logger = logger.opt(colors=True)

SERVER_ADDR: str = 'localhost'
SERVER_PORT: int = 9000

LISTEN_CLIENTS_NUMB: int = 12
MAX_SERVER_BUFFER_SIZE: int = 4096


class App(Daemon):
    def run(self):
        server.run_server(SERVER_ADDR, SERVER_PORT, LISTEN_CLIENTS_NUMB,
                          MAX_SERVER_BUFFER_SIZE)


pid_file = './daemon_pid.pid'
stdin = os.devnull
stdout = './log/output.log'
stderr = './log/error.log'
home_dir = '.'

daemon_main = App(pid_file, stdin, stdout, stderr, home_dir)

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

if __name__ == '__main__':
    pass
