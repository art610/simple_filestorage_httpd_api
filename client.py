"""
Simple client for test connection
"""
import socket
import sys
import uuid
from pathlib import Path
import requests
from loguru import logger
from file_hashing import get_hash_md5

logger.add("./log/client/debug.log", format="{time} {level} {message}",
           level="DEBUG",
           rotation="10KB")
logger = logger.opt(colors=True)


def send_non_http_request(host_addr: str = 'localhost', port: int = 9000,
                          chunk_size: int = 1024) -> str:
    """
    Функция позволяет "поздороваться" с сервером и получить от него ответ
    """
    server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_sock.connect((host_addr, port))

    server_sock.send("Hello world".encode())
    server_response = server_sock.recv(chunk_size)

    server_sock.close()

    return server_response.decode()


def file_read_by_chunks(file_stream, content_boundary, chunk_size=1024,
                        chunks=-1):
    """Lazy function (generator) to read a file piece by piece.
    Default chunk size: 1k
    If file not exists can return: [StopIteration: File Not Found Error]
    """
    data = content_boundary.encode()
    yield data
    while chunks:
        data = file_stream.read(chunk_size)
        if not data:
            break
        yield data
        chunks -= 1


def send_post_request(server_host, file_sample):
    """
    Function for sending post request with file
    :param server_host:
    :param file_sample:
    :return: resp - ответ сервера, file_hash - хэш в теле ответа
    """
    boundary = '--' + str(uuid.uuid4()) + '--'

    custom_header = {"Connection": "close",
                     "Content-Type": "multipart/form-data; boundary={}".format(
                         boundary),
                     "Content-Length": str(Path(file_sample).stat().st_size)}

    print(custom_header)

    file_stream = open(file_sample, 'rb')

    with requests.Session() as session:
        server_response = requests.post(server_host,
                                        data=file_read_by_chunks(file_stream,
                                                                 boundary),
                                        headers=custom_header)
        logger.debug(server_response)
        response_file_hash = server_response.content.decode()
        session.close()

    file_stream.close()

    return server_response, response_file_hash


def download_file(host_addr, params):
    """

    :param host_addr:
    :param params:
    :return:
    """
    current_dir = str(Path().parent.absolute()) + '/'
    if 'file_hash' in params:
        filename = params['file_hash']
    else:
        filename = 'none'
    full_received_file_name = current_dir + filename
    response_for_get = requests.get(host_addr, params=params, stream=True)
    print(response_for_get)
    if response_for_get.status_code == 200:
        print(response_for_get)
        file = open(full_received_file_name, "wb")
        for chunk_size in response_for_get.iter_content(chunk_size=1024):
            file.write(chunk_size)
        file.close()
    else:
        print(response_for_get)


def delete_file(host_addr, params):
    """

    :param host_addr:
    :param params:
    :return:
    """
    response_for_delete = requests.delete(url=host_addr, params=params)
    logger.debug(response_for_delete)


if __name__ == '__main__':
    server_addr: str = 'localhost'
    server_port: int = 9000
    SERVER_HTTP_ADDR = 'http://' + server_addr + ':' + str(server_port)
    chunk: int = 1024
    CURRENT_DIR = str(Path().parent.absolute()) + '/'
    FILE_SAMPLE = CURRENT_DIR + 'sample_file.txt'

    try:
        server_addr = sys.argv[1]
        server_port = int(sys.argv[2])
        chunk = int(sys.argv[3])
    except IndexError:
        logger.info('<red>Server addr: {}</>', server_addr)
        logger.info('<red>Server port: {}</>', server_port)
        logger.info('Chunk: {}', chunk)

    logger.info('Non HTTP request: {}',
                send_non_http_request(server_addr, server_port, chunk))

    request_header = requests.get(SERVER_HTTP_ADDR)
    request_body = request_header.content
    logger.info('GET empty request: {}\n {}', request_header, request_body)
    request_header.close()

    resp, file_hash = send_post_request(SERVER_HTTP_ADDR, FILE_SAMPLE)
    logger.info('POST request: {}\n{}', resp, file_hash)

    STORAGE = CURRENT_DIR + 'store/'
    uploaded_file_dir = STORAGE + file_hash[:2] + "/"
    uploaded_file = uploaded_file_dir + file_hash

    logger.debug(uploaded_file_dir)
    logger.debug(uploaded_file)

    request_header = requests.post(SERVER_HTTP_ADDR)
    request_body = request_header.content
    logger.info('POST empty request: {}\n {}', request_header, request_body)
    request_header.close()

    FILE_HASH = get_hash_md5(FILE_SAMPLE)
    download_file(SERVER_HTTP_ADDR, {'file_hash': FILE_HASH})
    delete_file(SERVER_HTTP_ADDR, {'file_hash': FILE_HASH})
