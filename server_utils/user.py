"""
This module contains the user class
"""


class User(object):
    """
    This class is used by the server
    It is used to determine the nickname of the user (displayed in chat), their client socket,
    their server status (administrator/regular) and whether the user is muted or not
    """
    def __init__(self, nickname, client, address):
        """
        The class constructor
        :param nickname: the user's nickname
        :param client: the user's client socket
        :param address: the user's address
        """
        self.nickname = nickname
        # if the server changes needs to change the nickname
        # it will use the display name instead
        self.display_name = nickname
        self.is_admin = False
        self.muted = False
        self.connected = False
        self.client = client
        self.address = address
