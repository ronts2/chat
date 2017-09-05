"""
This module contains the chat client (main script for users)
"""
import time
from threading import Thread
import re

from client_utils import client, gui

CLIENT_THREAD_TIMEOUT = 3
GUI_WAIT_TIME = 0.5  # seconds to wait while the gui is initializing
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

    def wait_for_gui(self):
        while not self.gui.running:
            time.sleep(GUI_WAIT_TIME)

    def receive_messages(self):
        message = self.client.receive_data()
        while message:
            message = ' '.join((time.strftime('%H:%M'), message))
            self.gui.display_message(message)
            message = self.client.receive_data()

    def initiate_conversation(self, nickname):
        self.wait_for_gui()
        try:
            self.client.establish_connection()
        except:
            self.gui.display_connection_status(False)
            quit()
        self.gui.display_connection_status(True)
        self.client.send(nickname)
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
