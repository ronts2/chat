"""
This module contains the chat client (main script for users)
"""
import re
import time
from threading import Thread

from client_utils import gui, user, clientsocket
from essentials import file_handler, protocols

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
        self.client = clientsocket.ClientSocket()
        self.gui = gui.GUI(self)
        self.protocols = protocols.Protocol(file=self.client.send_file, close=self.client.close_sock)
        self.downloads = dict()

    def exit(self):
        self.client.send_regular(QUIT_MSG)

    def wait_for_gui(self):
        while not self.gui.running:
            time.sleep(GUI_WAIT_TIME)

    def download_file(self, name, data=None):
        if data:
            self.downloads[name].append(data)
        else:
            self.downloads[name] = list()

    def create_file(self, name):
        file_handler.create_file(name, ''.join(self.downloads[name]))

    def process_message(self, msg):
        """
        Processes messages sent by the server.
        :param msg: a message sent from the server.
        """
        if self.protocols.check_protocol(msg):
            self.protocols.initiate_protocol(msg)
            return
        message = ' '.join((time.strftime('%H:%M'), msg))
        if self.gui.running:
            self.gui.display_message(message)

    def receive_messages(self):
        while self.gui.running:
            message = self.client.receive()
            if not message:
                break
            self.process_message(message)

    def initiate_conversation(self, nickname):
        self.wait_for_gui()
        try:
            self.client.connect()
        except:
            self.gui.display_connection_status(False)
            quit()
        self.gui.display_connection_status(True)
        self.client.send_obj(user.User(nickname))
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
