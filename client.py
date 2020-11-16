"""
Simple client for test connection
"""
import socket
import sys
import requests
from loguru import logger

logger.add("./debug.log", format="{time} {level} {message}", level="DEBUG", rotation="10KB")
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


if __name__ == '__main__':
    server_addr: str = 'localhost'
    server_port: int = 9000
    server_http_addr = 'http://' + server_addr + ':' + str(server_port)
    chunk: int = 1024
    try:
        server_addr = sys.argv[1]
        server_port = int(sys.argv[2])
        chunk = int(sys.argv[3])
    except IndexError:
        logger.info('<red>Server addr: {}</>', server_addr)
        logger.info('<red>Server port: {}</>', server_port)
        logger.info('Chunk: {}', chunk)

    logger.info('Non HTTP request: {}', send_non_http_request(server_addr, server_port, chunk))

    request_header = requests.get(server_http_addr)
    request_body = request_header.content
    logger.info('GET empty request: {}\n {}', request_header, request_body)
    request_header.close()

    request_header = requests.post(server_http_addr)
    request_body = request_header.content
    logger.info('POST empty request: {}\n {}', request_header, request_body)
    request_header.close()

    request_header = requests.delete(server_http_addr)
    request_body = request_header.content
    logger.info('DELETE empty request: {}\n {}', request_header, request_body)
    request_header.close()
