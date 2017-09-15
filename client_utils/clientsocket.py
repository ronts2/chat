"""
This module contains the ClientSocket class, used for client-server communication
"""
from essentials import chatsocket

DEF_LISTEN = 1


class ClientSocket(chatsocket.ChatSocket):
    """
    The client socket contains the client socket and the server's info
    """
    def __init__(self, server_ip=chatsocket.DEF_SERVER_IP, port=chatsocket.DEF_SERVER_PORT):
        """
        The class constructor.
        :param server_ip: IP of the server.
        :param port: port of the server.
        """
        super(ClientSocket, self).__init__(server_ip=server_ip, port=port)

    def connect(self):
        """
        Connects to the server
        """
        super(ClientSocket, self).connect((self.server_ip, self.port))
