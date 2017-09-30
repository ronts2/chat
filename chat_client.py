"""
This module contains the chat client (main script for users)
"""
import re
import time
from threading import Thread

from client_utils import gui
from essentials import file_handler, protocols, chatsocket

CLIENT_THREAD_TIMEOUT = 3
GUI_WAIT_TIME = 0.2  # seconds to wait while the gui is initializing
NICKNAME_REG = re.compile('^[a-zA-Z]([a-zA-Z0-9])*$')
QUIT_MSG = '?quit'


def get_nick():
    while True:
        nick = raw_input('Enter nickname: ')
        if NICKNAME_REG.match(nick):
            return nick
        print "Invalid nickname! Nickname must not start with '@' and have no white space."


class ChatClient(object):
    """
    This class is the main chatsocket script
    It is used to run the application (with a GUI)
    """
    def __init__(self):
        """
        The class constructor
        """
        self.client = chatsocket.ChatSocket()
        self.gui = gui.GUI(self)
        self.protocols = protocols.Protocol(self.handle_regular_msg, self.close, self.send_file,
                                            self.download_file, self.create_file, self.request_file)
        self.downloads = dict()

    def exit(self):
        self.client.send_regular_msg(QUIT_MSG)

    def close(self, **kwargs):
        self.client.close_sock()

    def wait_for_gui(self):
        while not self.gui.running:
            time.sleep(GUI_WAIT_TIME)

    def request_file(self, name, **kwargs):
        """
        Requests a file from the server.
        :param name: the file's name
        """
        self.client.send_msg(protocols.build_header(protocols.REQUEST_FILE, name), '')

    def send_file(self, path, **kwargs):
        if not file_handler.path_exists(path):
            self.client.send_msg(protocols.build_header(protocols.FILE_NOT_FOUND, path), '')
        else:
            self.client.send_file(path)

    def download_file(self, user, msg):
        exists = self.downloads.get(user)
        if not exists:
            self.downloads[user] = list()
        if msg.data:
            self.downloads[user].append(msg.data)
        else:
            del self.downloads[user]

    def create_file(self, name, **kwargs):
        file_handler.create_file('client_dl/' + name, ''.join(self.downloads))

    def handle_regular_msg(self, msg):
        """
        Handles regular-type messages.
        :param msg: a message.
        """
        message = ' '.join((time.strftime('%H:%M'), msg.data))
        if self.gui.running:
            self.gui.display_message(message)

    def receive_messages(self):
        while self.client.open:
            message = self.client.receive_obj()
            if not message:
                return
            self.protocols.initiate_protocol(message.header, msg=message)

    def initiate_conversation(self, nickname):
        self.wait_for_gui()
        try:
            self.client.connect()
        except:
            self.gui.display_connection_status(False)
            quit()
        self.gui.display_connection_status(True)
        self.client.send_str(nickname)
        self.receive_messages()
        if self.gui.running:
            self.gui.display_connection_status(False)

    def start_client(self):
        """
        Runs the application
        Starts the gui, displays the connection status and receives message from the server
        """
        nickname = get_nick()
        client_thread = Thread(target=self.initiate_conversation, args=[nickname])
        client_thread.start()
        self.gui.start_gui('Chat - ' + nickname)
        client_thread.join(CLIENT_THREAD_TIMEOUT)


def main():
    chat_client = ChatClient()
    chat_client.start_client()


if __name__ == '__main__':
    main()
