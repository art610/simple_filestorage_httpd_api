"""
Implementation of file Uploads on POST method
"""

import os
import socket
import hashlib
from pathlib import Path
from typing import Tuple, Dict
from loguru import logger


# Можно добавлять хэши файлов в отдельное хранилище ключ-значение
# STORE = {}
# Потребуется реализовать проверку файлов на дубликаты в хранилище


@logger.catch
def check_post_request(req_headers: Dict, req_body: bytes) -> bool:
    """
    Проверка POST-запроса перед обработкой

    Функция для проверки структуры содержимого POST-запроса, который должен
    содержать заголовок Content-Type с указанием boundary для границ данных
    в виде байт для файла, Content-Length для размера файла и проверки
    его правильной загрузки на сервер, а также что-либо в Request Body,

    :param req_headers:
    :param req_body:
    :return: True - если запрос правильный, в противном случае False
    """
    try:
        content_type = req_headers["Content-Type"]
        content_length = req_headers["Content-Length"]
        boundary = content_type.split('; ')[1].split('=')[1]
    except KeyError as key_error:
        logger.error("{}", key_error)
        return False
    except IndexError as index_error:
        logger.error("{}", index_error)
        return False

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
def serve_post_request(is_file_received, storage_dir, temp_file) -> Tuple:
    """
    Основной обработчик для POST запросов

    :param is_file_received: клиентский сокет
    :param storage_dir: размер буфера обмена для сервера
    :param temp_file: словарь из заголовков запроса клиента
    :return: Кортеж из хэша записанного файла и статус код, определяющий
    успешность работы функции, если возникли проблемы, то возвращается
    пустая строка и статус код, определяющий тип проблемы
    """

    # Если is_file_received = False, возвращаем 500 Internal Server Error
    if not is_file_received:
        return '', 500

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
        status = 409
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
                             req_headers: Dict, req_body: bytes,
                             filename: str) -> bool:
    """
    Функция позволяет получить файл от клиента и записать его в filename

    :param client_sock: объект socket для клиента, сделавшего запрос
    :param server_buffer: максимальный размер серверного буфера
    :param req_headers: словарь с заголовками запроса клиента
    :param req_body: тело запроса клиента с данными для записи
    :param filename: имя файла для записи данных
    :return: True - если файл был записан без ошибок
    """

    content_len = req_headers["Content-Length"]
    boundary = \
        req_headers["Content-Type"].split('; ')[1].split(
            '=')[1]

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
def get_hash_md5(filename: str) -> str:
    """
    Simple hash MD5 algorithm using hashlib
    """
    # OPTIMIZE: use more fast hash algorithm
    with open(filename, 'rb') as reading_file:
        hash_obj = hashlib.md5()
        while True:
            data = reading_file.read(8192)
            if not data:
                break
            hash_obj.update(data)
        return hash_obj.hexdigest()
