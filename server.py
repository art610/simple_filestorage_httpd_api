#!/usr/bin/python3.8
# -*- coding: UTF-8 -*-
"""
Модуль http-сервера с основной реализацией API
"""
import os
import sys
import socket
from pathlib import Path
from typing import Union, Tuple, List, Dict
from loguru import logger
import post_handler as post
import get_handler as get
import delete_handler

METHODS: Tuple[str, ...] = ('GET', 'POST', 'DELETE')
HTTP_VERSIONS: Tuple[str, ...] = ('HTTP/1.1',)
STORAGE_DIR = str(Path().parent.absolute()) + '/store/'


@logger.catch
def run_server(hostname_ipv4: str = '0.0.0.0', host_port: int = 9000,
               waiting_clients: int = 5,
               max_buffer_size: int = 4096) -> socket.socket:
    """
    Функция для запуска сервера, которая возвращает серверный сокет
    """
    server_socket = get_server_socket(hostname_ipv4, host_port,
                                      waiting_clients)
    accept_connections(server_socket, METHODS, HTTP_VERSIONS, max_buffer_size)
    return server_socket


@logger.catch
def get_server_socket(host_addr: str = '0.0.0.0', port: int = 9000,
                      clients_queue_size: int = 5) -> socket.socket:
    """
    Создаем объект socket c IPv4 и TCP с указанными в аргументах адресом и
    портом сервера.
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
def accept_connections(server_socket: socket.socket, methods: Tuple = METHODS,
                       http_versions: Tuple = HTTP_VERSIONS,
                       buffer_size: int = 4096):
    """
    Принимаем запросы от клиентов в бесконечном цикле
    """
    while True:
        try:
            client_socket, client_addr = server_socket.accept()
        except KeyboardInterrupt as interruption_error:
            server_socket.close()
            logger.debug("Connection was close by peer: {}",
                         interruption_error)
            break
        else:
            logger.debug("New connection from: {}", client_addr)

            client_request = client_socket.recv(buffer_size)
            first_req_line, req_headers_dict, req_body = get_request_elements(
                client_request)

            logger.debug("<cyan>Request first line:</>{}", first_req_line)
            logger.debug("<cyan>Request headers:</>\n{}", req_headers_dict)
            logger.debug("<cyan>Request body:</>\n{}", req_body)

            first_status = check_request_by_first_line(first_req_line,
                                                       methods,
                                                       http_versions)
            if first_status == 200:  # 200 OK

                method = first_req_line[0]
                url_string = first_req_line[1]

                if method == 'GET':
                    # TODO: Implement - file downloading, issue #5
                    logger.debug('GET method')

                    file_hash, file_abs_path = find_file_hash_in_req(
                        url_string)

                    if file_hash == '400':
                        client_socket.send(
                            "HTTP/1.1 400 Bad Request\n\n".encode())
                    elif file_hash == '404':
                        client_socket.send(
                            "HTTP/1.1 404 Not Found\n\n".encode())
                    else:
                        client_socket.send("HTTP/1.1 200 OK\n\n".encode())

                        is_ok = get.send_file_to_client(client_socket,
                                                        file_abs_path)

                        if not is_ok:
                            client_socket.send("HTTP/1.1 500 \
Internal Server Error\n\n".encode())

                elif method == 'POST':
                    file_hash, status = post.post_request_handler(
                        client_socket, buffer_size,
                        req_headers_dict,
                        req_body)

                    if status == 200:
                        client_socket.send(
                            "HTTP/1.1 200 OK\n\n{}".format(file_hash).encode())

                    elif status == 409:
                        client_socket.send(
                            "HTTP/1.1 409 Conflict\n\n{}".format(
                                file_hash).encode())

                    elif status == 400:
                        client_socket.send(
                            "HTTP/1.1 400 Bad Request\n\n".encode())

                    else:
                        client_socket.send(
                            "HTTP/1.1 500 Internal Server Error\n\n".encode())

                else:  # method == DELETE
                    # TODO: Implement - file deletion, issue #6
                    logger.debug('DELETE method')

                    file_hash, abs_path = find_file_hash_in_req(
                        url_string)

                    if file_hash == '400':
                        client_socket.send(
                            "HTTP/1.1 400 Bad Request\n\n".encode())
                    elif file_hash == '404':
                        client_socket.send(
                            "HTTP/1.1 404 Not Found\n\n".encode())
                    else:
                        is_ok = delete_handler.delete_file(file_hash, abs_path)

                        if is_ok:
                            client_socket.send(
                                "HTTP/1.1 200 OK\n\n DELETE method".encode())
                        else:
                            client_socket.send("HTTP/1.1 500 Internal Server \
Error\n\n".encode())

            else:
                if first_status == 405:
                    logger.debug('405 Method Not Allowed: {}',
                                 first_req_line[0])
                    client_socket.send(
                        "HTTP/1.1 405 Method Not Allowed\n\n".encode())

                elif first_status == 505:
                    logger.debug('505 HTTP Version Not Supported: {}',
                                 first_req_line[2])
                    client_socket.send(
                        "HTTP/1.1 505 HTTP Version Not Supported\n\n".encode())

                else:  # resp_status_code == 400
                    logger.debug('400 Bad Request\n{}', client_request)
                    client_socket.send("HTTP/1.1 400 Bad Request\n\n".encode())

            client_socket.close()


def find_file_hash_in_req(uri: str) -> Tuple[str, str]:
    """

    :param uri:
    :return:
    """
    try:
        params = {}
        for param in uri.split('?')[1].split('&'):
            param_key, param_value = param.split('=')
            params[param_key] = param_value
        print("All parameters in request", params)

        file_hash = params['file_hash']

        if file_hash:
            file_store_dir = file_hash[:2]
            file_abs_path = STORAGE_DIR + file_store_dir + "/" + file_hash

            if os.path.exists(file_abs_path):
                return file_hash, file_abs_path

            return '404', ''  # File Not Found

        return '400', ''  # Bad Request

    except IndexError:
        return '400', ''  # Bad Request
    except KeyError:
        return '400', ''  # Bad Request


@logger.catch
def check_request_by_first_line(request_first_line: List, methods: Tuple,
                                http_versions: Tuple) -> int:
    """
    Проверяем запрос на корректность, содержание одного из
    возможных методов, и версию протокола HTTP.
    Принимаем в качестве аргументов:
    request_first_line - первую строку запроса в формате списка из содержимых
    элементов methods - кортеж допустимых для запроса методов
    http_versions - кортеж допустимых версий протокола HTTP
    Возвращаем статус код в виде целого числа int
    """
    try:
        method = request_first_line[0]
        # uri = request_first_line[1]
        http_version = request_first_line[2]
    except IndexError:
        logger.warning("IndexError [request_first_line]: 400 Bad Request")
        return 400
    else:
        if method not in methods:
            logger.warning("405 Method Not Allowed")
            return 405
        if http_version not in http_versions:
            logger.warning("505 HTTP Version Not Supported")
            return 505

        return 200  # OK


@logger.catch
def get_request_elements(request: bytes) -> Union[Tuple[List, Dict, bytes]]:
    """
    Функция позволяет распарсить запрос клиента (аргумент request) и получить:
    req_start_line_list - основную строку запроса в виде кортежа из метода, URI
    и версии HTTP;
    req_headers_dict - словарь с заголовками запроса;
    req_body_part - тело запроса в виде байтовой строки.
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

    LOG_LEVEL = "DEBUG"  # argv3 -> prod / dev

    SERVER_ADDR: str = 'localhost'  # argv1
    SERVER_PORT: int = 9000  # argv2
    MAX_SERVER_BUFFER_SIZE: int = 4096
    LISTEN_CLIENTS_NUMB: int = 5

    try:
        SERVER_ADDR = sys.argv[1]
        SERVER_PORT = int(sys.argv[2])
        MAX_SERVER_BUFFER_SIZE = int(sys.argv[3])
        LISTEN_CLIENTS_NUMB = int(sys.argv[4])
    except IndexError:
        logger.info('<red>Host: {}</>', SERVER_ADDR)
        logger.info('<red>Port: {}</>', SERVER_PORT)
        logger.info('Buffer: {}', MAX_SERVER_BUFFER_SIZE)
        logger.info('Listen: {}', LISTEN_CLIENTS_NUMB)

    logger.add("./log/debug.log", format="{time} {level} {message}",
               level="DEBUG",
               rotation="10KB")
    logger = logger.opt(colors=True)

    run_server(SERVER_ADDR, SERVER_PORT, LISTEN_CLIENTS_NUMB,
               MAX_SERVER_BUFFER_SIZE)
