import os


def path_exists(path):
    """
    Checks whether the path exists.
    :param path: the path.
    :return: True if path exists, otherwise False.
    """
    return os.path.exists(path)


def get_name_from_path(path):
    """
    Extracts the file's name from a path.
    :param path: path to a file.
    :return: the file's name.
    """
    return os.path.basename(path)


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


def create_file(path, data):
    """
    Creates a file in the given path with the given data.
    :param path: the file path.
    :param data: the file's data
    """
    dir_path = os.path.dirname(path)
    if not path_exists(dir_path):
        os.mkdir(dir_path)
    with open(path, 'wb') as file:
        file.write(data)
