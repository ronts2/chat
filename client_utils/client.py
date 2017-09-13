"""
This module contains the client class, used for client-server communication
The client follows the communication protocol: send size of data - then the data itself
The client sends pickled Message 
"""
import socket
import jsonpickle as pickle
from threading import Thread
from time import sleep

from essentials import file_handler, messages

MSG_LEN_SIZE = 6  # The size of the length of a message
# the default server ip address - the current computer
DEF_SERVER_IP = socket.gethostbyname(socket.gethostname())
# the default server port - the programmer's choice
DEF_SERVER_PORT = 9900
DATA_CHUNK_SIZE = 1024


class Client(object):
    """
    The client follows the communication protocol: send size of data - then the data itself
    The client contains the client socket and the server's info
    """
    def __init__(self, server_ip=DEF_SERVER_IP, port=DEF_SERVER_PORT):
        """
        The class constructor
        :param server_ip: the server's ip address
        :param port: the server's port
        """
        self.port = port
        self.server_ip = server_ip
        self.client = socket.socket()

    def establish_connection(self):
        """
        Connects to the server
        """
        self.client.connect((self.server_ip, self.port))

    def receive(self):
        """
        Gathers data sent from the server
        :return: message from the server or None if the server closed
        """
        size = self.receive_all(MSG_LEN_SIZE)
        if not size:
            return None
        data = self.receive_all(int(size))
        return data

    def receive_all(self, size):
        """
        Receives data sent from the server until all data is received
        :param size: the size of the data
        :return: received data
        """
        try:
            data = self.client.recv(size)
            while len(data) < size:
                data += self.client.recv(size-len(data))
            return data
        except:
            return ''

    def send_file(self, path):
        """
        Sends a file to the server.
        :param path: a path to a file.
        """
        data_chunks = file_handler.generate_chunks(path, DATA_CHUNK_SIZE)
        sender = Thread(target=self.send_chunks, args=[data_chunks, path])
        sender.start()

    def send_chunks(self, chunks, path):
        for chunk in chunks:
            self.send(pickle.dumps(messages.Message(messages.FILE_DATA_CHUNK, chunk)))
            sleep(0.1)
        self.send(pickle.dumps(messages.Message(messages.FILE_DATA_FIN, path)))

    def send_obj(self, obj):
        self.send_regular(pickle.dumps(obj))

    def send_regular(self, data):
        self.send(pickle.dumps(messages.Message(messages.REGULAR_MSG, data)))

    def send(self, msg):
        """
        Sends a pickled message to the server
        :param msg: the message object
        """
        self.client.sendall(str(len(msg)).zfill(MSG_LEN_SIZE))
        self.client.sendall(msg)

    def close(self):
        """
        Closes the socket
        """
        self.client.shutdown(socket.SHUT_RDWR)  # Stop receiving/sending
        self.client.close()
