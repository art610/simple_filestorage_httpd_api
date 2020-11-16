"""
Simple client for test connection
"""
import socket
import sys
from loguru import logger

logger.add("./debug.log", format="{time} {level} {message}", level="DEBUG", rotation="10KB")
logger = logger.opt(colors=True)


@logger.catch
def send_test_request(host_addr: str = 'localhost', port: int = 9000,
                      chunk_size: int = 1024) -> str:
    """
    Функция позволяет "поздороваться" с сервером и получить от него ответ
    """
    server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_sock.connect((host_addr, port))

    server_sock.send("Hello".encode())
    server_response = server_sock.recv(chunk_size)

    server_sock.close()

    return server_response.decode()


if __name__ == '__main__':
    server_addr: str = 'localhost'
    server_port: int = 9000
    chunk: int = 1024
    try:
        server_addr = sys.argv[1]
        server_port = int(sys.argv[2])
        chunk = int(sys.argv[3])
    except IndexError:
        logger.info('<red>Server addr: {}</>', server_addr)
        logger.info('<red>Server port: {}</>', server_port)
        logger.info('Chunk: {}', chunk)

    logger.info('Server response: {}', send_test_request(server_addr, server_port, chunk))
