"""
Unit tests for server module [pytest]

Short description. Can help with autogenerate docs.
"""
import socket
import sys
import requests
from server import run_server

SERVER_ADDR: str = 'localhost'
SERVER_PORT: int = 9000
SERVER_URL = 'http://' + SERVER_ADDR + ':' + str(SERVER_PORT)

LISTEN_CLIENTS_NUMB: int = 5
MAX_SERVER_BUFFER_SIZE: int = 4096


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
    test_response_for_get_request()
