#!/usr/bin/python3.8
# -*- coding: UTF-8 -*-
"""
Данный модуль будет основной точкой входа
"""
import os
import sys
import argparse
from loguru import logger
from daemon import Daemon
import server

version = "0.1.0"


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


def create_parser():
    # Создаем парсер с данными о программе
    parser = argparse.ArgumentParser(
        prog='http-upload-server',
        description="""Реализация демона (daemon), который предоставляет 
        HTTP API для загрузки (upload), скачивания (download) и 
        удаления (delete) файлов.""",
        epilog="""(c) Artem Zhelonkin (tyo3436@gmail.com) 2020.
        Автор программы, как всегда, 
        не несет никакой ответственности ни за что.
        """,
        add_help=False
    )

    # Группа параметров для родительского парсера
    parent_group = parser.add_argument_group(title='Параметры')

    parent_group.add_argument('--help', '-h', action='help',
                              help='Вывести справку')

    parent_group.add_argument('--version', '-V',
                              action='version',
                              help='Вывести номер версии',
                              version='%(prog)s v{}'.format(version))

    # Группа подпарсеров аргументов с namespace = control
    subparsers = parser.add_subparsers(dest='control',
                                       title='Команды для управления сервером',
                                       description="""Команды, позволяющие 
                                       запустить, остановить, перезапустить 
                                       сервер и вывести идентификатор 
                                       процесса""")

    # Создаем парсер для команды start
    start_parser = subparsers.add_parser('start',
                                         add_help=False,
                                         help="""Start server daemon""",
                                         description="""Команда для запуска 
                                         серверного демона. Будет создан 
                                         соответствующий PID-файл и процесс, 
                                         идентификатор которого можно получить 
                                         при помощи параметра get_pid.""")

    # Группа аргументов для команды start
    start_group = start_parser.add_argument_group(title='Параметры')

    # Добавляем параметры

    start_group.add_argument('--help', '-h', action="help",
                             help='Вывести справку')

    start_group.add_argument('--host', default='0.0.0.0',
                             help="""Add server addr (IPv4),
                             default - 'localhost'""",
                             metavar='HOSTNAME')

    start_group.add_argument('--port', default=9000,
                             help="""Add server port, 
                             default - '9000'""",
                             metavar='PORT')

    start_group.add_argument('--log', default='DEBUG',
                             help="""Add log level, 
                             default 'DEBUG'""",
                             metavar='LEVEL')

    start_group.add_argument('--listen', default=5,
                             help="""Add listen clients numb, 
                             default - 5""",
                             metavar='LEVEL')

    start_group.add_argument('--buffer', default=4096,
                             help="""Add server buffer size, 
                             default - 4096""",
                             metavar='BUFFER')

    # Создаем подпарсер для команды stop
    stop_parser = subparsers.add_parser('stop',
                                        add_help=False,
                                        help="""Stop server daemon""",
                                        description="""Stop server daemon""")

    stop_parser.add_argument('--help', '-h', action="help",
                             help='Вывести справку')

    # Создаем подпарсер для команды restart
    restart_parser = subparsers.add_parser('restart',
                                           add_help=False,
                                           help="""Reload server daemon""",
                                           description="""Reload server 
                                           daemon""")

    restart_parser.add_argument('--help', '-h', action="help",
                                help='Вывести справку')

    # Создаем подпарсер для команды get_pid
    get_pid_parser = subparsers.add_parser('get_pid',
                                           add_help=False,
                                           help="""Get server daemon 
                                           process ID""",
                                           description="""Get server daemon 
                                           process ID""")

    get_pid_parser.add_argument('--help', '-h', action="help",
                                help='Вывести справку')

    return parser


if __name__ == '__main__':

    parser = create_parser()
    namespace = parser.parse_args(sys.argv[1:])

    PID_FILE = './daemon_pid.pid'
    STD_IN = os.devnull
    STD_OUT = './log/output.log'
    STD_ERR = './log/error.log'
    HOME_DIR = '.'

    daemon_main = App(PID_FILE, STD_IN, STD_OUT, STD_ERR, HOME_DIR)

    if namespace.control == "start":

        SERVER_ADDR: str = namespace.host
        SERVER_PORT: int = int(namespace.port)
        LOG_LEVEL: str = namespace.log
        LISTEN_CLIENTS_NUMB: int = int(namespace.listen)
        MAX_SERVER_BUFFER_SIZE: int = int(namespace.buffer)

        logger.add("./log/daemon/debug.log", format="{time} {level} {message}",
                   level=LOG_LEVEL,
                   rotation="10MB")
        logger = logger.opt(colors=True)

        daemon_main.start()

    elif namespace.control == "stop":
        daemon_main.stop()

    elif namespace.control == "restart":
        daemon_main.restart()

    elif namespace.control == "get_pid":
        print(daemon_main.get_pid())

    else:
        parser.print_help()
