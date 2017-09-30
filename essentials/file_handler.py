import os


def get_name_from_path(path):
    """
    Extracts the file's name from a path.
    :param path: path to a file.
    :return: the file's name.
    """
    return os.path.basename(path)


def load_file(path):
    """
    Loads a file.
    :param path: a path of a file.
    :return: the file's data.
    """
    with open(path, 'rb') as file:
        return file.read()


def generate_chunks(path, size):
    """
    Generates chunks of given data in a file.
    :param path: the path of the file.
    :param size: the max size of each chunk of data.
    :return: list of data chunks.
    """
    data = load_file(path)
    return [data[i:i+size] for i in xrange(0, len(data), size)]


def create_file(path, data):
    """
    Creates a file in the given path with the given data.
    :param path: the file path.
    :param data: the file's data
    """
    dir_path = os.path.dirname(path)
    if not os.path.exists(dir_path):
        os.mkdir(dir_path)
    with open(path, 'wb') as file:
        file.write(data)
