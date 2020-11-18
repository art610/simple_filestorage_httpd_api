"""
Implementation of file deletion on DELETE method
"""
import os


def delete_file(file_hash, file_abs_path):
    """

    :param file_hash:
    :param file_abs_path:
    :return:
    """
    try:
        os.remove(file_abs_path)
    except FileNotFoundError:
        return False
    else:
        file_dir_len = len(file_abs_path) - len(file_hash)
        os.rmdir(file_abs_path[:file_dir_len])

    return True
