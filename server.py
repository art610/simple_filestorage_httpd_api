"""
Модуль http-сервера с основной реализацией API
"""
import os
import sys
import socket
import hashlib
from pathlib import Path
from typing import Union, Tuple, List, Dict
from loguru import logger

logger.add("./debug.log", format="{time} {level} {message}", level="DEBUG",
           rotation="10KB")
logger = logger.opt(colors=True)

METHODS: Tuple[str, ...] = ('GET', 'POST', 'DELETE')
HTTP_VERSIONS: Tuple[str, ...] = ('HTTP/1.1',)


@logger.catch
def run_server(hostname_ipv4, host_port, waiting_clients, max_buffer_size):
    """
    Функция для запуска сервера, которая возвращает серверный сокет
    """
    server_socket = get_server_socket(hostname_ipv4, host_port,
                                      waiting_clients)
    accept_connections(server_socket, METHODS, HTTP_VERSIONS, max_buffer_size)
    return server_socket


@logger.catch
def get_server_socket(host_addr: str = 'localhost', port: int = 9000,
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
def accept_connections(server_socket: socket.socket, methods, http_versions,
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

            resp_status_code = check_request_by_first_line(first_req_line,
                                                           methods,
                                                           http_versions)
            if resp_status_code == 200:  # 200 OK

                method = first_req_line[0]

                if method == 'GET':
                    # TODO: Implement - file downloading, issue #5
                    logger.debug('GET method')
                    client_socket.send(
                        "HTTP/1.1 200 OK\n\nGET method".encode())

                elif method == 'POST':
                    # TODO: Implement - file uploading, issue #4

                    # возвращаем True, если проверка прошла успешно
                    if check_post_request(req_headers_dict, req_body):

                        try:
                            # пробуем обслужить запрос и получить хэш
                            file_hash, status = serve_post_request(
                                client_socket,
                                buffer_size,
                                req_headers_dict,
                                req_body)

                        except RuntimeError as runtime_error:
                            # при возникновении проблем, возвращаем ошибку
                            client_socket.send(
                                "HTTP/1.1 500 InternalServerError\n\n".encode())
                            client_socket.close()

                        else:
                            # если всё прошло успешно - возвращаем ответ 200
                            # вместе с хэшом сохраненного файла
                            if status == 200:
                                client_socket.send(
                                    "HTTP/1.1 200 OK\n\n{}".format(
                                        file_hash).encode())
                            elif status == 409:
                                client_socket.send(
                                    "HTTP/1.1 409 Conflict\n\nFile exists: {}".format(
                                        file_hash).encode())
                            else:
                                client_socket.send(
                                    "HTTP/1.1 500 Internal Server Error\n\n".encode())

                    else:
                        # можно указать в ответе - что требуется для 200 OK
                        client_socket.send(
                            "HTTP/1.1 400 Bad Request\n\n".encode())

                else:  # method == DELETE
                    # TODO: Implement - file deletion, issue #6
                    logger.debug('DELETE method')
                    client_socket.send(
                        "HTTP/1.1 200 OK\n\n DELETE method".encode())

            else:
                if resp_status_code == 405:
                    logger.debug('405 Method Not Allowed: {}',
                                 first_req_line[0])
                    client_socket.send(
                        "HTTP/1.1 405 Method Not Allowed\n\n".encode())

                elif resp_status_code == 505:
                    logger.debug('505 HTTP Version Not Supported: {}',
                                 first_req_line[2])
                    client_socket.send(
                        "HTTP/1.1 505 HTTP Version Not Supported\n\n".encode())

                else:  # resp_status_code == 400
                    logger.debug('400 Bad Request\n{}', client_request)
                    client_socket.send("HTTP/1.1 400 Bad Request\n\n".encode())

            client_socket.close()


# =====START=============== POST METHOD IMPLEMENTATION ========================

# Можно добавлять хэши файлов в отдельное хранилище ключ-значение
# STORE = {}
# Потребуется реализовать проверку файлов на дубликаты в хранилище


@logger.catch
def check_post_request(req_headers_dict, req_body):
    """
    Проверка POST-запроса перед обработкой

    Функция для проверки структуры содержимого POST-запроса, который должен
    содержать заголовок Content-Type с указанием boundary для границ данных
    в виде байт для файла, Content-Length для размера файла и проверки
    его правильной загрузки на сервер, а также что-либо в Request Body,

    :param req_headers_dict:
    :param req_body:
    :return: True - если запрос правильный, в противном случае False
    """

    content_type = req_headers_dict["Content-Type"]
    content_length = req_headers_dict["Content-Length"]
    boundary = content_type.split('; ')[1].split('=')[1]

    # проверим, что каждый элемент что-либо содержит
    if not (content_type and content_length and boundary and req_body):
        return False

    # Возможность привести содержимое Content-Length к целочисленному типу int
    try:
        int(content_length)
    except ValueError:
        return False

    return True  # 200 OK


@logger.catch
def serve_post_request(client_sock: socket.socket, server_buffer: int,
                       req_headers: Dict, req_body: bytes):
    """

    :param client_sock:
    :param server_buffer:
    :param req_headers:
    :param req_body:
    :return:
    """
    storage_dir = str(Path().parent.absolute()) + '/store/'
    temp_file = storage_dir + 'temp'

    content_length = req_headers["Content-Length"]
    boundary = req_headers["Content-Type"].split('; ')[1].split('=')[1]

    is_file_received = receive_file_from_client(client_sock, server_buffer,
                                                content_length, boundary,
                                                req_body,
                                                temp_file)

    # Если is_file_received = False, возвращаем 500 Internal Server Error
    if not is_file_received:
        return 500

    # Если файл был успешно загружен, то получаем его хэш
    file_hash = get_hash_md5(temp_file)
    # Пара первых символов хэша становится названием каталога для файла
    hash_first_symbols = file_hash[:2]
    # Полное имя файла
    new_dir = storage_dir + hash_first_symbols

    # Проверяем правильность создания директории
    check_dir = Path(new_dir)
    if not check_dir.is_dir():
        try:
            os.mkdir(new_dir)
        except OSError:
            logger.error("Creation of the directory {} failed", new_dir)
        else:
            logger.success("Successfully created the directory {} ", new_dir)

    new_file_name = new_dir + '/' + file_hash

    check_file = Path(new_file_name)
    if check_file.is_file():
        os.remove(temp_file)
        status = 409  # 409 Conflict: File Exists
        logger.error("409 Conflict: File Exists")
        return file_hash, status

    # Добавлен новый файл
    os.rename(temp_file, new_file_name)
    status = 200

    # Add new entity to key:value STORE
    # STORE[file_hash] = new_file_name
    # print(STORE)

    return file_hash, status


@logger.catch
def receive_file_from_client(client_sock: socket.socket, server_buffer: int,
                             content_len, boundary, req_body: bytes,
                             filename: str):
    """
    Функция позволяет получить файл от клиента и записать его в filename

    :param client_sock: объект socket для клиента, сделавшего запрос
    :param server_buffer: максимальный размер серверного буфера
    :param content_len: размер данных для записи
    :param boundary: граница, которая позволяет определить часть для записи
    :param req_body: тело запроса клиента с данными для записи
    :param filename: имя файла для записи данных
    :return: True - если файл был записан без ошибок
    """

    chunk_start = req_body.find(boundary.encode()) + len(boundary)
    chunk = req_body[chunk_start:]

    write_file = open(filename, 'wb')
    write_file.write(chunk)

    start_count_len = len(chunk)
    while start_count_len < int(content_len):
        chunk = client_sock.recv(server_buffer)
        if chunk == '':
            write_file.close()
            logger.error("500 Internal Server Error: Socket connection broken")
            return False
        write_file.write(chunk)
        start_count_len += len(chunk)
    write_file.close()
    if int(content_len) != int(
            Path(filename).stat().st_size):
        logger.error("500 Internal Server Error: Socket connection broken")
        return False

    return True


@logger.catch
def get_hash_md5(filename):
    """
    Simple hash MD5 algorithm using hashlib
    """
    # OPTIMIZE: use more fast hash algorithm
    with open(filename, 'rb') as f:
        m = hashlib.md5()
        while True:
            data = f.read(8192)
            if not data:
                break
            m.update(data)
        return m.hexdigest()


# ======================= POST METHOD IMPLEMENTATION ==================END=====

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
