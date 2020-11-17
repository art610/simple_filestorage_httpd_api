"""
Simple client for test connection
"""
import socket
import sys
import requests
import uuid
from pathlib import Path
from loguru import logger

logger.add("./log/client/debug.log", format="{time} {level} {message}", level="DEBUG",
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
    try:
        data = content_boundary.encode()
        yield data
        while chunks:
            data = file_stream.read(chunk_size)
            if not data:
                break
            yield data
            chunks -= 1
    except FileNotFoundError:
        return 'File Not Found Error'


def send_post_request(server_host, file_sample):

    boundary = '--' + str(uuid.uuid4()) + '--'

    custom_header = {"Connection": "close",
                     "Content-Type": "multipart/form-data; boundary={}".format(
                         boundary),
                     "Content-Length": str(Path(file_sample).stat().st_size)}

    print(custom_header)

    file_stream = open(file_sample, 'rb')

    with requests.Session() as s:
        r = requests.post(server_host, data=file_read_by_chunks(file_stream,
                                                                boundary),
                          headers=custom_header)
        logger.debug(r)
        file_hash = r.content.decode()
        r.close()

    file_stream.close()

    print(file_hash)
    # r = requests.get(server_host, params=r.content)


if __name__ == '__main__':
    server_addr: str = 'localhost'
    server_port: int = 9000
    SERVER_HTTP_ADDR = 'http://' + server_addr + ':' + str(server_port)
    chunk: int = 1024
    current_dir = str(Path().parent.absolute()) + '/'
    FILE_SAMPLE = current_dir + 'sample_file.txt'

    try:
        server_addr = sys.argv[1]
        server_port = int(sys.argv[2])
        chunk = int(sys.argv[3])
    except IndexError:
        logger.info('<red>Server addr: {}</>', server_addr)
        logger.info('<red>Server port: {}</>', server_port)
        logger.info('Chunk: {}', chunk)

    # logger.info('Non HTTP request: {}',
    #             send_non_http_request(server_addr, server_port, chunk))

    # request_header = requests.get(SERVER_HTTP_ADDR)
    # request_body = request_header.content
    # logger.info('GET empty request: {}\n {}', request_header, request_body)
    # request_header.close()

    send_post_request(SERVER_HTTP_ADDR, FILE_SAMPLE)


    # request_header = requests.post(SERVER_HTTP_ADDR)
    # request_body = request_header.content
    # logger.info('POST empty request: {}\n {}', request_header, request_body)
    # request_header.close()

    # request_header = requests.delete(SERVER_HTTP_ADDR)
    # request_body = request_header.content
    # logger.info('DELETE empty request: {}\n {}', request_header, request_body)
    # request_header.close()
