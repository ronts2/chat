"""This module contains the message type classes which are sent to the server."""

# message types
FILE_DATA_START = 'file:start'
FILE_DATA_CHUNK = 'file:data'
FILE_DATA_FIN = 'file:fin'
REGULAR_MSG = 'regular'


class Message(object):
    def __init__(self, type, data):
        """
        The class constructor.
        :param type: the type of message.
        :param data: the data of the message.
        """
        self.type = type
        self.data = data
