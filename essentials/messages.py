"""This module contains the message type classes which are sent to the server."""


class Message(object):
    """
    This class is used to Encapsulate sent strings.
    """
    def __init__(self, header, data):
        """
        The class constructor.
        :param header: the header of message.
        :param data: the data of the message.
        """
        self.header = header
        self.data = data
