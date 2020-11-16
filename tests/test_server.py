"""
Unit tests for server module [pytest]

Short description. Can help with autogenerate docs.
"""
import threading
import socket
import sys
import requests
import pytest
from pathlib import Path
from server import run_server

SERVER_ADDR: str = 'localhost'
SERVER_PORT: int = 9000
SERVER_URL = 'http://' + SERVER_ADDR + ':' + str(SERVER_PORT)

LISTEN_CLIENTS_NUMB: int = 12
MAX_SERVER_BUFFER_SIZE: int = 4096


@pytest.fixture(autouse=True)
def start_server():
    thread = threading.Thread(target=run_server,
                              args=(SERVER_ADDR, SERVER_PORT, LISTEN_CLIENTS_NUMB,
                                    MAX_SERVER_BUFFER_SIZE))
    thread.daemon = True
    thread.start()
    yield


def test_response_for_incorrect_request_method():
    """
    Simple test for incorrect request method to HTTP-server
    """
    with requests.Session() as s:
        request = requests.put(SERVER_URL)
        s.close()

    assert request.status_code == 405


def test_response_for_incorrect_request_http_protocol_version():
    """
    Simple test for request with incorrect http protocol
    """
    server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_sock.connect((SERVER_ADDR, SERVER_PORT))

    server_sock.send("Hello world".encode())
    server_response = server_sock.recv(1024)

    server_sock.close()

    assert server_response == b"HTTP/1.1 400 Bad Request\n\n"


def test_response_for_get_request():
    """
    Simple test for GET request to HTTP-server
    """

    with requests.Session() as s:
        request = requests.get(SERVER_URL)
        s.close()

    assert request.status_code == 200


def test_response_for_post_request():
    """
    Simple test for POST request to HTTP-server
    """

    with requests.Session() as s:
        request = requests.post(SERVER_URL)
        s.close()

    assert request.status_code == 200


def test_response_for_delete_request():
    """
    Simple test for DELETE request to HTTP-server
    """

    with requests.Session() as s:
        request = requests.delete(SERVER_URL)
        s.close()

    assert request.status_code == 200


# Input point if we directly run this script
if __name__ == "__main__":
    # test_response_for_get_request()
    python_executable_full_path = sys.executable
    server_script = str((Path().parent.absolute()).parent) + '/server.py'
