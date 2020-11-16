"""
Модуль http-сервера с основной реализацией API
"""

import socket


def get_server_socket(host_addr, port, clients_queue_size):
    """
    Создаем объект socket c IPv4 и TCP с указанными в аргументах адресом и портом сервера
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


def accept_connections(server_socket, buffer_size):
    while True:
        try:
            client_socket, client_addr = server_socket.accept()
        except KeyboardInterrupt as e:
            server_socket.close()
            print("Connection was close:", e)
            break
        else:
            print("New connection from:", client_addr)

            client_request = client_socket.recv(buffer_size)

            print(client_request)

            client_socket.close()

        print('All is good')
