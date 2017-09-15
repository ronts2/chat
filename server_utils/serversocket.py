"""
This module contains the ServerClient class, used for server communication
"""
from essentials import chatsocket

DEF_LISTEN = 1


class ServerSocket(chatsocket.ChatSocket):
    """
    The server socket contains the server socket and the server's info
    """
    def __init__(self, listen=DEF_LISTEN):
        """
        The class constructor.
        :param listen: the socket
        """
        self.listen = listen
        super(ServerSocket, self).__init__()

    def initialize_server_socket(self):
        """
        Initializes the server socket.
        """
        self.bind((self.server_ip, self.port))
        super(ServerSocket, self).listen(self.listen)

    def accept(self):
        """
        Accepts a client connection.
        :return: client socket and address as returned by the socket.accept method.
        """
        return super(ServerSocket, self).accept()
