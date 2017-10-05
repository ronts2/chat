"""This module contains the protocols used for communication.
between the client and server independent of user interaction.
"""

# mutual
REGULAR = 'reg'
END_CONNECTION = 'end_con'

REQUEST_FILE = 'req_file'
FILE_NOT_FOUND = 'file_not_found'
FILE_START = 'file_start'
FILE_CHUNK = 'file_chunk'
FILE_END = 'file_end'

# clients
FILE_DL = 'file_dl'


def build_header(protocol, resource=None):
    """
    Builds a header string.
    :param protocol: the protocol string.
    :param resource: protocol-related resource
    :return: header string.
    """
    return ':'.join((protocol, resource or ''))


class Protocol(object):
    """This class is used to allow client-server communication behind the scenes."""
    def __init__(self, regular, end_connection, request_file, file_not_found, file_start, file_chunk, file_end,
                 file_dl):
        """The class constructor."""
        self.protocols = {REGULAR: regular, END_CONNECTION: end_connection, REQUEST_FILE: request_file,
                          FILE_NOT_FOUND: file_not_found, FILE_START: file_start, FILE_CHUNK: file_chunk,
                          FILE_END: file_end, FILE_DL: file_dl}

    def check_protocol(self, text):
        """Checks whether a string is a protocol message.
        :param text: a string
        :returns: True if the text is a protocol message, False otherwise.
        """
        return text in self.protocols

    def initiate_protocol(self, header, **kwargs):
        """
        Parses a protocol msg.
        :param header: the received message's header.
        :param kwargs: additional arguments to pass.
        """
        components = header.split(':')
        protocol, data = components[0], ':'.join(filter(None, components[1:]))
        func = self.protocols[protocol]
        if not func:
            print protocol
        if not data:
            func(**kwargs)
        else:
            func(data, **kwargs)
