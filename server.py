"""
Модуль http-сервера с основной реализацией API
"""
import socket
import sys
from typing import Union, Tuple, List, Dict
from loguru import logger

logger.add("./debug.log", format="{time} {level} {message}", level="DEBUG", rotation="10KB")
logger = logger.opt(colors=True)

METHODS: Tuple[str, ...] = ('GET', 'POST', 'DELETE')
HTTP_VERSIONS: Tuple[str, ...] = ('HTTP/1.1',)


@logger.catch
def run_server(hostname_ipv4, host_port, waiting_clients, max_buffer_size):
    server_socket = get_server_socket(hostname_ipv4, host_port, waiting_clients)
    accept_connections(server_socket, METHODS, HTTP_VERSIONS, max_buffer_size)
    return server_socket


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
def accept_connections(server_socket: socket.socket, methods, http_versions,
                       buffer_size: int = 4096):
    """
    Принимаем запросы от клиентов в бесконечном цикле
    """
    while True:
        try:
            client_socket, client_addr = server_socket.accept()
        except KeyboardInterrupt as e:
            server_socket.close()
            logger.debug("Connection was close by peer: {}", e)
            break
        else:
            logger.debug("New connection from: {}", client_addr)

            client_request = client_socket.recv(buffer_size)
            first_req_line_list, req_headers_dict, req_body = get_request_elements(client_request)

            logger.debug("<cyan>Request first line:</>{}", first_req_line_list)
            logger.debug("<cyan>Request headers:</>\n{}", req_headers_dict)
            logger.debug("<cyan>Request body:</>\n{}", req_body)

            resp_status_code = check_request_by_first_line(first_req_line_list, methods,
                                                           http_versions)
            if resp_status_code == 200:  # 200 OK

                method = first_req_line_list[0]

                if method == 'GET':
                    # TODO: Implement the required functionality - file downloading, issue #5
                    logger.debug('GET method')
                    client_socket.send("HTTP/1.1 200 OK\n\nGET method".encode())

                elif method == 'POST':
                    # TODO: Implement the required functionality - file uploading, issue #4
                    logger.debug('POST method')
                    client_socket.send("HTTP/1.1 200 OK\n\nPOST method".encode())

                else:  # method == DELETE
                    # TODO: Implement the required functionality - file deletion, issue #6
                    logger.debug('DELETE method')
                    client_socket.send("HTTP/1.1 200 OK\n\n DELETE method".encode())

                client_socket.close()

            else:
                if resp_status_code == 405:
                    logger.debug('405 Method Not Allowed: {}', first_req_line_list[0])
                    client_socket.send("HTTP/1.1 405 Method Not Allowed\n\n".encode())
                    client_socket.close()
                elif resp_status_code == 505:
                    logger.debug('505 HTTP Version Not Supported: {}', first_req_line_list[2])
                    client_socket.send("HTTP/1.1 505 HTTP Version Not Supported\n\n".encode())
                    client_socket.close()
                else:  # resp_status_code == 400
                    logger.debug('400 Bad Request\n{}', client_request)
                    client_socket.send("HTTP/1.1 400 Bad Request\n\n".encode())
                    client_socket.close()


@logger.catch
def check_request_by_first_line(request_first_line: List, methods: Tuple,
                                http_versions: Tuple) -> int:
    """
    Проверяем запрос на корректность, содержание одного из
    возможных методов, и версию протокола HTTP.
    Принимаем в качестве аргументов:
    request_first_line - первую строку запроса в формате списка из содержимых элементов
    methods - кортеж допустимых для запроса методов
    http_versions - кортеж допустимых версий протокола HTTP
    Возвращаем статус код в виде целого числа int
    """
    try:
        method = request_first_line[0]
        # uri = request_first_line[1]
        http_version = request_first_line[2]
    except IndexError:
        return 400  # 400 Bad Request
    else:
        if method not in methods:
            return 405  # 405 Method Not Allowed
        if http_version not in http_versions:
            return 505  # HTTP Version Not Supported

        return 200  # OK


@logger.catch
def get_request_elements(request: bytes) -> Union[Tuple[List[str], Dict, bytes]]:
    """
    Функция позволяет распарсить запрос клиента (аргумент request) и получить:
    req_start_line_list - основную строку запроса в виде кортежа из метода, URI и версии HTTP
    req_headers_dict - словарь с заголовками запроса
    req_body_part - тело запроса в виде байтовой строки
    """

    headers_end = request.find(b'\r\n\r\n')
    headers = request[:headers_end].decode().split('\r\n')
    req_start_line_list: List[str, ...] = headers[0].split(' ')
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
    accept_connections(server_sock, METHODS, HTTP_VERSIONS, buffer)
