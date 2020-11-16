"""
Модуль http-сервера с основной реализацией API
"""
import socket
import sys
from loguru import logger

logger.add("./debug.log", format="{time} {level} {message}", level="DEBUG", rotation="10KB")
logger = logger.opt(colors=True)


@logger.catch
def run_server(server_addr, server_port, client_queue, buffer):
    server_socket = get_server_socket(server_addr, server_port, client_queue)
    accept_connections(server_socket, buffer)


@logger.catch
def get_server_socket(host_addr='localhost', port=9000, clients_queue_size=5):
    """
    Создаем объект socket c IPv4 и TCP с указанными в аргументах адресом и портом сервера
    Принимаем указанное в clients_queue_size количество подключений от клиентов
    Пока что будем их обрабатывать по очереди синхронно - одно за другим
    Аргументы:
    host_addr - адрес сервера IPv4 в виде строки str
    port - порт, на котором будет осуществляться доступ к серверу, int
    client_queue_size - параметр метода listen, int
    Функция возвращаяет объект server_socket
    """
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind((host_addr, port))
    server_socket.listen(clients_queue_size)

    return server_socket


@logger.catch
def accept_connections(server_socket, buffer_size=4096):
    """
    Принимаем запросы от клиентов в бесконечном цикле
    """
    while True:
        try:
            client_socket, client_addr = server_socket.accept()
        except KeyboardInterrupt as e:
            server_socket.close()
            logger.debug("Connection was close by peer")
            break
        else:
            logger.debug("New connection from: {}", client_addr)

            client_request = client_socket.recv(buffer_size)

            logger.debug(client_request)
            client_socket.send("HTTP/1.1 200 OK\n\n".encode())
            client_socket.close()

        logger.debug('All is good')


if __name__ == '__main__':
    server_addr = 'localhost'
    server_port = 9000
    buffer = 4096
    client_queue = 5
    try:
        server_addr = sys.argv[1]
        server_port = int(sys.argv[2])
        buffer = int(sys.argv[3])
        client_queue = int(sys.argv[4])
    except IndexError:
        logger.info('<red>Host: {}</>', server_addr)
        logger.info('<red>Port: {}</>', server_port)
        logger.info('Buffer: {}', buffer)
        logger.info('Listen: {}', client_queue)

    server_sock = get_server_socket(server_addr, server_port, client_queue)
    accept_connections(server_sock, buffer)
