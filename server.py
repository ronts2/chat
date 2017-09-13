"""
This module contains the server (main script for the server host)
The server follows the communication protocol: send size of data - then the data itself
"""
import select
import socket

import jsonpickle as pickle

from essentials import messages, file_handler
from server_utils import commands

ADDRESS = socket.gethostbyname(socket.gethostname())
PORT = 9900
MSG_LEN_SIZE = 6
MAX_CONNECTIONS = 5


class Server(object):
    """
    This class is a chat server
    It is used to set up the server
    """
    def __init__(self):
        """
        The class constructor
        """
        self.server = self.create_socket()
        self.users_by_nick = dict()
        self.users_by_client = dict()
        self.downloads = dict()
        self._init_messages()
        # flags
        self.request_flag = 'req'
        self.connection_flag = 'con'
        # request flags
        self.file_flag = 'file'
        # connection flags
        self.close_flag = 'close'

    def _init_messages(self):
        self.connect_message = '{} connected'
        self.disconnect_message = '{} disconnected.'
        self.invalid_nick_message = 'Nickname: {} is taken.'
        self.no_permission_message = 'You have no permission to use this command!'
        self.whisper_message = '{} whispered: {}'
        self.kick_message_whisper = 'You were kicked from the server.'
        self.kick_message_all = 'User {} was kicked from the server.'
        self.mute_message = "You've been muted. you can no longer send messages, but you can still view the chat."
        self.muted_message = 'You cannot send messages or run commands while you are muted.'
        self.unmute_message = 'You are no longer muted.'
        self.commands_message = 'Allowed commands: {}'
        self.admins_message = 'Admins: {}'
        self.promote_message = 'You are now an admin.'
        self.demote_message = 'You are now a regular.'
        self.user_not_found = 'User {} not found.'

    def build_protocol(self, *args, **kwargs):
        """
        Build a request string.
        :return: request string.
        """
        return ':'.join(('.'.join(kwargs['flags']),  kwargs['path']))

    # Socket
    def create_socket(self):
        """
        Generates a server socket
        :return: server socket
        """
        server = socket.socket()
        server.bind((ADDRESS, PORT))
        server.listen(MAX_CONNECTIONS)
        return server

    # Server utilities
    def start_server(self):
        """
        Starts the server -> polls the network for incoming connections/messages
        Proceeds to process them
        """
        while True:
            inputs = self.get_client_list() + [self.server]
            readable, writable, exceptional = select.select(inputs, [], [])
            self.handle_inputs(readable)

    def get_client_list(self):
        return self.users_by_client.keys()

    def handle_inputs(self, readable):
        """
        Processes the incoming inputs
        :param readable: list of inputs
        """
        for sock in readable:
            if sock is self.server:
                if len(self.users_by_nick) < MAX_CONNECTIONS:
                    self.accept_new_user(sock)
            else:
                self.handle_client(self.users_by_client[sock])

    def _receive_all(self, size, client):
        """
        Gathers data sent from the client until all data is received
        :param size: the size of the data
        :param client: the client
        :return: received data
        """
        data = client.recv(size)
        while len(data) < size:
            data += client.recv(size-len(data))
        return data

    def receive(self, client):
        """
        Receives messages from the client
        :param client: the client socket
        :return: message object
        """
        try:
            msg = self._receive_all(MSG_LEN_SIZE, client)
            size = int(msg)
            tmp = pickle.loads(self._receive_all(size, client))
            return tmp
        except:
            return ''

    def accept_new_user(self, sock):
        """
        Accepts the client socket connection and creates a User object
        :param sock: connection listener
        """
        client, address = sock.accept()
        user = pickle.loads(self.receive(client).data)
        user.client, user.address = client, address[0]
        if user.nickname in self.users_by_nick:
            self.direct_message(client, self.invalid_nick_message.format(user.nickname))
            return
        self.process_new_user(user)

    def process_new_user(self, user):
        """
        Finalizes the connecting process
        :param user: a User object
        """
        self.add_user(user)
        # The host is the owner (Admin) of the server
        if user.address == ADDRESS:
            commands.promote_user(commands.CommandArgs(self, user, ''))
        self.broadcast(self.connect_message.format(user.display_name))

    def add_user(self, user):
        """
        Updates user dictionaries to accommodate the new user
        :param user: a USer object
        """
        user.connected = True
        self.users_by_nick[user.nickname] = user
        self.users_by_client[user.client] = user
        self.downloads[user.nickname] = list()

    def remove_user(self, user):
        """
        Updates user dictionaries to accommodate the new user
        :param user: a USer object
        """
        del self.users_by_nick[user.nickname]
        del self.users_by_client[user.client]
        del self.downloads[user.nickname]

    def close_client(self, client):
        """
        Closes the client socket
        """
        client.shutdown(socket.SHUT_RDWR)  # Stop receiving/sending
        client.close()

    # Server logic
    def handle_client(self, user):
        """
        Handles the client's needs
        :param user: the user to handle
        """
        msg = self.receive(user.client)
        if msg:
            self.handle_message(msg, user)
        elif user.connected:
            self.disconnect_user(user)
            self.broadcast(self.disconnect_message.format(user.display_name))

    def handle_command(self, user, message):
        command = commands.Command.parse_msg(message)
        if command:
            if self.check_permission(user, command):
                command(commands.CommandArgs(self, user, message))
            else:
                self.direct_message(user, self.no_permission_message)

    def check_permission(self, user, command):
        """
        Checks if the user is allowed to execute the command
        :param user: the user who wishes to execute the command
        :param command: the command which is wished to be executed
        :return: True if user is allowed to execute said command, False otherwise
        """
        return not command.admin_only or user.is_admin

    def handle_message(self, msg, user):
        """
        Handles the user's message - broadcasts the message and attempts to execute the command
        unless the user's muted, in which case it will do nothing but send the user
        a reminder that he is muted
        :param msg: the user's message
        :param user: the user who sent the message
        """
        if user.muted:
            self.direct_message(user, self.muted_message)
        elif msg.type == messages.REGULAR_MSG:
            self.broadcast(user.display_name + ': ' + msg.data)
            self.handle_command(user, msg.data)
        else:
            self.handle_protocol(msg, user)

    def handle_protocol(self, msg, user):
        """
        Handles protocol messages.
        :param msg: the user's message
        :param user: the user who sent the message
        """
        if msg.type == messages.FILE_DATA_CHUNK:
            self.downloads[user.nickname].append(msg.data)
        elif msg.type == messages.FILE_DATA_FIN:
            file_handler.create_file('dl/' + msg.data, ''.join(self.downloads[user.nickname]))
            self.downloads[user.nickname] = list()

    def change_display_name(self, user, new_nick):
        """
        changes the nickname of a user
        :param user: the user whose nickname will change
        :param new_nick: The new nickname
        """
        self.users_by_nick[user.nickname].display_name = new_nick
        self.users_by_client[user.client].display_name = new_nick

    def broadcast(self, content):
        """
        Broadcasts content to everyone
        :param content: the content to send
        """
        for nick, user in self.users_by_nick.iteritems():
            try:
                self.direct_message(user, content)
            except:
                pass

    def disconnect_user(self, user):
        """
        Disconnects the user from the server
        :param user: the user to disconnect
        """
        try:
            self.direct_message(user, '')  # send an empty message - signaling the client socket is closing
        except:
            pass
        user.connected = False
        self.close_client(user.client)
        self.remove_user(user)

    def direct_message(self, user, content):
        """
        Send a message to a user
        :param user: the user to direct_message to
        :param content: the content to be whispered
        """
        user.client.sendall(str(len(content)).zfill(MSG_LEN_SIZE))
        user.client.sendall(content)


def main():
    s = Server()
    s.start_server()
    s.server.close()

if __name__ == '__main__':
    main()
