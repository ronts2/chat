"""
This module is used to work with files.
"""
import os


PATH_EXISTS = os.path.exists
GET_FILE_NAME = os.path.basename


def get_location(*args):
    """
    Generates the absolute path for a directory.
    :param args: directory components.
    :return: absolute path string.
    """
    return os.path.abspath(os.path.join(*args))


def generate_chunks(path, size):
    """
    Generates chunks of given data in a file.
    :param path: the path of the file.
    :param size: the max size of each chunk of data.
    :return: data chunks.
    """
    with open(path, 'rb') as file:
        data = file.read(size)
        while data:
            yield data
            data = file.read(size)


def open_file(path):
    """
    Opens a file.
    :param path: the file's path.
    :return: open file.
    """
    return open(path, 'wb')


def create_file(path):
    """
    Creates a file in the given path.
    :param path: the file path.
    """
    dir_path = os.path.dirname(path)
    if not PATH_EXISTS(dir_path):
        os.mkdir(dir_path)
    with open(path, 'wb') as file:
        pass
