"""
Module for file hashing algorithms
"""
import hashlib


def get_hash_md5(filename: str) -> str:
    """
    Simple hash MD5 algorithm using hashlib
    """
    # OPTIMIZE: use more fast hash algorithm
    with open(filename, 'rb') as reading_file:
        hash_obj = hashlib.md5()
        while True:
            data = reading_file.read(8192)
            if not data:
                break
            hash_obj.update(data)
        return hash_obj.hexdigest()
