"""This module contains the protocols used for communication
between the client and server independent of user interaction.
"""
# flags
REQUEST_FLAG = 'req'
CONNECTION_FLAG = 'con'

# request flags
FILE_REQ = 'file'

# connection flags
CLOSE_CON = 'close'


class Protocol(object):
    """This class is used to allow client-server communication behind the scenes."""
    def __init__(self, *args, **kwargs):
        """The class constructor."""
        self.protocols = {REQUEST_FLAG: {FILE_REQ: kwargs.get(FILE_REQ)},
                          CONNECTION_FLAG: {CLOSE_CON: kwargs.get(CLOSE_CON)}}

    def check_protocol(self, text):
        """Checks whether a string is a protocol message.
        :param text: a string
        :returns: True if the text is a protocol message, False otherwise.
        """
        components = text.split('.')
        return components[0] in self.protocols

    def _parse_protocol(self, components, protocols):
        """
        Initiates protocols.
        :param components: flag components of a protocol.
        :return: the function corresponding to the protocol.
        """
        if len(components) == 1:
            return protocols[components[0]]
        return self._parse_protocol(components[1:], protocols[components[0]])

    def initiate_protocol(self, msg):
        """
        Parses a protocol string.
        :param msg: a protocol flags string.
        """
        protocol, data = msg.split(':')
        func = self._parse_protocol(protocol.split('.'), self.protocols)
        if not data:
            func()
        else:
            func(data)

    def build_protocol(self, flags, resource=None):
        """
        Build a request string.
        :return: request string.
        """
        return ':'.join(('.'.join(flags), resource or ''))

