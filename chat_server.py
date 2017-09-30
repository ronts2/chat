"""
This module contains the server (main script for the server host)
The server follows the communication protocol: send size of data - then the data itself
"""
import select

from essentials import file_handler, protocols, chatsocket
from server_utils import commands, user

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
        self.server = chatsocket.ChatSocket()
        self.users_by_nick = dict()
        self.users_by_client = dict()
        self.downloads = dict()
        self._init_messages()
        self.protocols = protocols.Protocol(self.handle_regular_msg, self.disconnect_user, None, self.file_not_found,
                                            self.process_file_chunk, self.save_file)

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
        self.upload_start_msg = 'Attempting to upload file: {}'
        self.already_uploading_msg = 'You can only upload one file at a time.'
        self.upload_finished_msg = '{} has finished uploading!'
        self.file_not_found_msg = 'file: {} was not found.'

    # Server utilities
    def start_server(self):
        """
        Starts the server -> polls the network for incoming connections/messages
        Proceeds to process them
        """
        print 'IP:', self.server.server_ip, 'Port:', self.server.port
        self.server.initialize_server_socket()
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

    def accept_new_user(self, sock):
        """
        Accepts the chatsocket socket connection and creates a User object
        :param sock: connection listener
        """
        client, address = sock.accept()
        nick = client.receive()
        if nick in self.users_by_nick:
            client.send_regular_msg(self.invalid_nick_message.format(nick))
            return
        self.process_new_user(user.User(nick, client, address[0]))

    def process_new_user(self, user):
        """
        Finalizes the connecting process
        :param user: a User object
        """
        self.add_user(user)
        # The host is the owner (Admin) of the server
        if user.address == self.server.server_ip:
            commands.promote(commands.CommandArgs(self, user, ''))
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

    # Server logic
    def handle_client(self, user):
        """
        Handles the chatsocket's needs
        :param user: the user to handle
        """
        msg = user.client.receive_obj()
        if msg:
            self.handle_message(msg, user)
        elif user.connected:
            self.disconnect_user(user)
            self.broadcast(self.disconnect_message.format(user.display_name))

    def handle_command(self, msg, user):
        command = commands.Command.parse_msg(msg)
        if command:
            if self.check_permission(user, command):
                command(commands.CommandArgs(self, user, msg))
            else:
                user.client.send_regular_msg(self.no_permission_message)

    def check_permission(self, user, command):
        """
        Checks if the user is allowed to execute the command
        :param user: the user who wishes to execute the command
        :param command: the command which is wished to be executed
        :return: True if user is allowed to execute said command, False otherwise
        """
        return not command.admin_only or user.is_admin

    def handle_regular_msg(self, msg, user):
        """
        Handles a regular message.
        :param msg: the message.
        :param user: the user who sent the message.
        """
        self.broadcast(user.display_name + ': ' + msg.data)
        self.handle_command(msg.data, user)

    def handle_message(self, msg, user):
        """
        Handles the user's message - broadcasts the message and attempts to execute the command
        unless the user's muted, in which case it will do nothing but send the user
        a reminder that he is muted
        :param msg: the user's message
        :param user: the user who sent the message
        """
        if user.muted:
            user.client.send_regular_msg(self.muted_message)
        else:
            self.protocols.initiate_protocol(msg.header, msg=msg, user=user)

    def file_not_found(self, name, user, msg):
        """
        Handles a file not found message.
        :param name: the file's name
        :param user: the user who who sent the message.
        :param msg: the 'file not found' message.
        """
        self.broadcast(self.file_not_found_msg.format(name))

    def process_file_chunk(self, user,  msg):
        """
        Adds the file chunk data to the downloaded file data.
        :param user: the user who sent the file chunk.
        :param msg: the 'file chunk' message.
        """
        self.downloads[user.nickname].append(msg.data)

    def save_file(self, name, user, msg):
        """
        Saves a downloaded file.
        :param name: the file's name.
        :param user: the user who sent the file.
        :param msg: the 'file finished' message.
        """
        file_handler.create_file('dl/' + name, ''.join(self.downloads[user.nickname]))
        self.downloads[user.nickname] = list()
        self.broadcast(self.upload_finished_msg.format(name))
        self.broadcast_file(name, user.nickname)

    def change_display_name(self, user, new_nick):
        """
        changes the nickname of a user
        :param user: the user whose nickname will change
        :param new_nick: The new nickname
        """
        self.users_by_nick[user.nickname].display_name = new_nick
        self.users_by_client[user.client].display_name = new_nick

    def broadcast_file(self, path, name):
        """
        Sends a file to all users.
        :param path: the file's path.
        :param name: the name of the user who uploaded the file.
        """
        for client in self.users_by_client:
            try:
                client.send_file(path, name)
            except:
                pass

    def broadcast(self, content):
        """
        Broadcasts content to everyone
        :param content: the content to send
        """
        for client in self.users_by_client:
            try:
                client.send_regular_msg(content)
            except:
                pass

    def disconnect_user(self, user):
        """
        Disconnects the user from the server
        :param user: the user to disconnect
        """
        try:
            user.client.send_msg(protocols.build_header(protocols.END_CONNECTION), '')
        except:
            pass
        user.connected = False
        user.client.close_sock()
        self.remove_user(user)


def main():
    s = Server()
    s.start_server()
    s.server.close_sock()


if __name__ == '__main__':
    main()
