"""
Implementation of file Download on GET method
"""


def send_file_to_client(client_socket, file_abs_path):
    """

    :param client_socket:
    :param file_hash:
    :param file_abs_path:
    :return:
    """
    try:
        file_stream = open(file_abs_path, 'rb')
    except FileNotFoundError:
        print('File not found')
        return False
    else:
        file_chunk = file_stream.read(1024)
        while file_chunk:
            client_socket.send(file_chunk)
            print('Sent', repr(file_chunk))
            file_chunk = file_stream.read(1024)
        file_stream.close()
        print('Done sending')
        return True
