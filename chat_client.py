"""
This module contains the chat client (main script for users).
"""
import re
import time
from threading import Thread

from client_utils import gui
from essentials import file_handler, protocols, chatsocket

SERVER_ADDRESS = 'ronsite.ddns.net'
CLIENT_THREAD_TIMEOUT = 3
GUI_WAIT_TIME = 0.2  # seconds to wait while the gui is initializing
NICKNAME_REG = re.compile('^[a-zA-Z]([a-zA-Z0-9])*$')
QUIT_MSG = '?quit'
DL_DIR = 'client_dl'
FILE_FIN_MSG = 'file: {} has finished downloading.'
FILE_UP_START = 'Uploading file. please wait.'
MAX_GUI_WAIT = 2


def get_nick():
    """
    Asks the user for a nickname.
    :return: nickname string.
    """
    while True:
        nick = raw_input('Enter nickname: ')
        if NICKNAME_REG.match(nick):
            return nick
        print "Invalid nickname! Nickname may only contain letters and numbers."


class ChatClient(object):
    """
    This class is the main chatsocket script.
    It is used to run the application (with a GUI).
    """
    def __init__(self):
        """
        The class constructor.
        """
        self.client = chatsocket.ChatSocket(server_ip=SERVER_ADDRESS)
        self.protocols = protocols.Protocol(self.handle_regular_msg, self.close, self.send_file, None, None, None,
                                            self.file_end, None)

    def exit(self):
        """
        Exists the server.
        """
        self.client.send_regular_msg(QUIT_MSG)

    def close(self, **kwargs):
        """
        Closes the connection to the server.
        """
        self.client.close_sock()

    def wait_for_gui(self):
        """
        Waits for the gui to initialize.
        :return: True if GUI successfully initialized, False otherwise.
        """
        waited = 0
        while not self.gui.running:
            if waited >= MAX_GUI_WAIT:
                return False
            time.sleep(GUI_WAIT_TIME)
            waited += GUI_WAIT_TIME
        return True

    def request_file(self, name, **kwargs):
        """
        Requests a file from the server.
        :param name: the file's name
        """
        self.client.send_msg(protocols.build_header(protocols.REQUEST_FILE, name), '')

    def file_end(self, name, **kwargs):
        """
        Handles an upload-finished message.
        :param name: the file's name.
        """
        #self.gui.enable_input()

    def send_file(self, path, **kwargs):
        """
        Handles file requests.
        :param path: the requested file's path.
        """
        if not file_handler.PATH_EXISTS(path):
            self.client.send_msg(protocols.build_header(protocols.FILE_NOT_FOUND, path), '')
        else:
            #self.gui.disable_input()
            self.gui.display_message(FILE_UP_START)
            self.client.send_file(path)

    def process_file_chunk(self, name, msg):
        """
        Processes a file chunk.
        :param name: the file's name.
        :param msg: the message.
        """
        if msg.data:
            file_handler.create_file(file_handler.get_location(DL_DIR, name))

    def handle_regular_msg(self, msg):
        """
        Handles regular-type messages.
        :param msg: a message.
        """
        message = ' '.join((time.strftime('%H:%M'), msg.data))
        if self.gui.running:
            self.gui.display_message(message)

    def receive_messages(self):
        """
        Start receiving messages.
        """
        while self.client.open:
            message = self.client.receive_obj()
            if not message:
                return
            self.protocols.initiate_protocol(message.header, msg=message)

    def initiate_conversation(self, nickname):
        """
        Initiates conversation with the server.
        :param nickname: the user's nickname.
        """
        if not self.wait_for_gui():
            print 'GUI failed to initialize.'
            return
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
        self.gui = gui.GUI(self)
        client_thread = Thread(target=self.initiate_conversation, args=[nickname])
        client_thread.start()
        self.gui.start_gui('Chat - ' + nickname)
        client_thread.join(CLIENT_THREAD_TIMEOUT)


def main():
    chat_client = ChatClient()
    chat_client.start_client()


if __name__ == '__main__':
    main()
