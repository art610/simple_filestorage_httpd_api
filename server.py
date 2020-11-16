"""
Модуль http-сервера с основной реализацией API
"""
import socket
import sys
from typing import Union, Tuple, List, Dict
from loguru import logger

logger.add("./debug.log", format="{time} {level} {message}", level="DEBUG", rotation="10KB")
logger = logger.opt(colors=True)


@logger.catch
def run_server(server_addr, server_port, client_queue, buffer):
    server_socket = get_server_socket(server_addr, server_port, client_queue)
    accept_connections(server_socket, buffer)


@logger.catch
def get_server_socket(host_addr: str = 'localhost', port: int = 9000,
                      clients_queue_size: int = 5) -> socket.socket:
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
def accept_connections(server_socket: socket.socket, buffer_size: int = 4096):
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
            first_req_line_list, req_headers_dict, req_body = get_request_elements(client_request)

            logger.debug("<cyan>Request first line:</>{}", first_req_line_list)
            logger.debug("<cyan>Request headers:</>\n{}", req_headers_dict)
            logger.debug("<cyan>Request body:</>\n{}", req_body)

            client_socket.send("HTTP/1.1 200 OK\n\n".encode())

            client_socket.close()

        logger.debug('All is good')


def get_request_elements(request: bytes) -> Union[Tuple[List[str], Dict, bytes]]:
    """
    Функция позволяет распарсить запрос клиента (аргумент request) и получить:
    req_start_line_list - основную строку запроса в виде кортежа из метода, URI и версии HTTP
    req_headers_dict - словарь с заголовками запроса
    req_body_part - тело запроса в виде байтовой строки
    """

    headers_end = request.find(b'\r\n\r\n')
    headers = request[:headers_end].decode().split('\r\n')
    req_start_line_list: List[str] = headers[0].split(' ')
    del headers[0]

    req_headers_dict: Dict = {}
    for i in headers:
        key = i.split(': ')[0]
        val = i.split(': ')[1]
        req_headers_dict[key] = val

    req_body_part: bytes = request[headers_end + len('\r\n\r\n'):]

    return req_start_line_list, req_headers_dict, req_body_part


if __name__ == '__main__':
    server_addr: str = 'localhost'
    server_port: int = 9000
    buffer: int = 4096
    client_queue: int = 5
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
