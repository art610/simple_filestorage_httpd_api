"""
Unit tests for server module [pytest]

Short description. Can help with autogenerate docs.
"""
import os
import threading
import socket
import time
import requests
import pytest
from pathlib import Path
from server import run_server
from client import send_post_request

SERVER_ADDR: str = 'localhost'
SERVER_PORT: int = 11200
SERVER_URL = 'http://' + SERVER_ADDR + ':' + str(SERVER_PORT)

LISTEN_CLIENTS_NUMB: int = 12
MAX_SERVER_BUFFER_SIZE: int = 4096


@pytest.fixture(autouse=True)
def start_server():
    thread = threading.Thread(target=run_server,
                              args=(
                                  SERVER_ADDR, SERVER_PORT,
                                  LISTEN_CLIENTS_NUMB,
                                  MAX_SERVER_BUFFER_SIZE
                              ))
    thread.daemon = True
    thread.start()
    yield


def test_response_for_incorrect_request_method():
    """
    Simple test for incorrect request method to HTTP-server
    """
    time.sleep(3)
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


def test_response_for_empty_get_request():
    """
    Simple test for GET request to HTTP-server
    """
    with requests.Session() as s:
        request = requests.get(SERVER_URL)
        s.close()

    assert request.status_code == 400


def test_response_for_incorrect_post_request():
    """
    Simple test for POST request to HTTP-server
    """
    with requests.Session() as s:
        request = requests.post(SERVER_URL)
        s.close()

    assert request.status_code == 400


def test_response_for_post_request():
    """
    Simple test for POST request to HTTP-server
    """
    base_dir = str(Path().parent.absolute())
    current_dir = base_dir + '/tests/assets/'
    file_sample = current_dir + 'sample_image.jpg'
    resp, file_hash = send_post_request(SERVER_URL, file_sample)

    assert resp.status_code == 200


def test_response_for_post_request_if_file_exists():
    """
    Simple test for POST request to HTTP-server
    """
    base_dir = str(Path().parent.absolute())
    current_dir = base_dir + '/tests/assets/'
    file_sample = current_dir + 'sample_image.jpg'
    resp, file_hash = send_post_request(SERVER_URL, file_sample)

    assert resp.status_code == 409


def test_response_for_get_request_if_file_exists_in_store():
    """
    Simple test for GET request to HTTP-server
    """
    base_dir = str(Path().parent.absolute())
    file_hash = '59c19f7df4ceba37936035844bb2ab5c'
    file_dir = base_dir + '/store/59/'
    filename = file_dir + file_hash

    params = {'file_hash': file_hash}

    response_for_get = requests.get(SERVER_URL, params=params, stream=True)

    write_temp = 'write_temp.data'
    if response_for_get.status_code == 200:
        file = open(write_temp, "wb")
        for chunk_size in response_for_get.iter_content(chunk_size=1024):
            file.write(chunk_size)
        file.close()
    write_temp_len = Path(write_temp).stat().st_size
    filename_len = Path(filename).stat().st_size

    is_ok = write_temp_len == filename_len
    os.remove(write_temp)
    os.remove(filename)
    os.rmdir(file_dir)

    assert is_ok


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
    pass
