"""
This module contains the chat client (main script for users)
"""
import re
import time
from threading import Thread

from client_utils import client, gui, user
from essentials import file_handler, protocols

CLIENT_THREAD_TIMEOUT = 3
GUI_WAIT_TIME = 0.2  # seconds to wait while the gui is initializing
NICKNAME_REG = re.compile('^[a-zA-Z]([a-zA-Z0-9])*$')


def get_nick():
    while True:
        nick = raw_input('Enter nickname: ')
        if NICKNAME_REG.match(nick):
            return nick
        print "Invalid nickname! Nickname must not start with '@' and have no white space."


class ChatClient(object):
    """
    This class is the main client script
    It is used to run the application (with a GUI)
    """
    def __init__(self):
        """
        The class constructor
        """
        self.client = client.Client()
        self.gui = gui.GUI(self)
        self.protocols = protocols.Protocol(file=self.client.send_file, close=self.client.close)
        self.downloads = dict()

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
        self.gui.display_message(message)

    def receive_messages(self):
        while True:
            message = self.client.receive()
            if not message:
                break
            self.process_message(message)

    def initiate_conversation(self, nickname):
        self.wait_for_gui()
        try:
            self.client.establish_connection()
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
        self.client.close()


def main():
    chat_client = ChatClient()
    chat_client.start_client()


if __name__ == '__main__':
    main()
