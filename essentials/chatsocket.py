"""
This module contains the ChatClient class, used for client-server communication.
The ChatClient follows the communication protocol: send size of data - then the data itself.
"""
import socket
import jsonpickle as pickle
from threading import Thread

import file_handler
import messages
import protocols

MSG_LEN_SIZE = 6  # The size of the length of a message
# the default server ip address - the current computer
DEF_SERVER_IP = socket.gethostbyname(socket.gethostname())
# the default server port - the host's choice
DEF_SERVER_PORT = 9900
DEF_DATA_CHUNK_SIZE = 4096
DEF_LISTEN = 1


class ChatSocket(socket.socket):
    """
    The chat socket follows the communication protocol: send size of data - then the data itself
    The chat socket contains the chat socket socket and the server's info
    """
    def __init__(self, server_ip=DEF_SERVER_IP, port=DEF_SERVER_PORT, msg_len_size=MSG_LEN_SIZE,
                 data_chunk_size=DEF_DATA_CHUNK_SIZE, listen=DEF_LISTEN, _sock=None):
        """
        The class constructor.
        :param server_ip: IP of the server.
        :param port: port of the server.
        :param msg_len_size: the maximum number of digits representing data size.
        :param data_chunk_size: the size of a data chunk (used to split sent file data)
        """
        self.port = port
        self.server_ip = server_ip
        self.msg_len_size = msg_len_size
        self.data_chunk_size = data_chunk_size
        self.listen = listen
        if _sock:
            super(ChatSocket, self).__init__(_sock=_sock)
        else:
            super(ChatSocket, self).__init__()
        self.open = False

    def connect(self):
        super(ChatSocket, self).connect((self.server_ip, self.port))
        self.open = True

    def initialize_server_socket(self):
        """
        Initializes the server socket.
        """
        self.bind((self.server_ip, self.port))
        super(ChatSocket, self).listen(self.listen)

    def accept(self):
        """
        Accepts a client connection.
        :return: client socket and address as returned by the socket.accept method.
        """
        sock, address = super(ChatSocket, self).accept()
        return ChatSocket(_sock=sock), address

    def receive(self):
        """
        Gathers data sent from the server
        :return: message from the server or None if the server closed
        """
        size = self._receive_all(MSG_LEN_SIZE)
        if not size:
            return ''
        data = self._receive_all(int(size))
        return data

    def _receive_all(self, size):
        """
        Receives data sent from the server until all data is received
        :param size: the size of the data
        :return: received data
        """
        try:
            data = self.recv(size)
            while len(data) < size:
                data += self.recv(size - len(data))
            return data
        except:
            return ''

    def receive_obj(self):
        """
        Receives an object from the server.
        :return: sent object.
        """
        try:
            return pickle.loads(self.receive())
        except:
            return ''

    def send_str(self, msg):
        """
        Sends a string to the server
        :param msg: the message object
        """
        self.sendall(str(len(msg)).zfill(MSG_LEN_SIZE))
        self.sendall(msg)

    def send_obj(self, obj):
        """
        Sends and object to the server.
        :param obj: an object.
        """
        self.send_str(pickle.dumps(obj))

    def send_msg(self, header, data):
        """
        Sends a message to the server.
        :param header: the message's protocol header.
        :param data: the message's data.
        """
        self.send_obj(messages.Message(header, data))

    def send_regular_msg(self, data):
        """
        Sends a regular-type message to the server.
        :param data: the message's data
        """
        self.send_msg(protocols.build_header(protocols.REGULAR), data)

    def _send_chunks(self, chunks, path):
        for chunk in chunks:
            self.send_msg(protocols.build_header(protocols.FILE_CHUNK), chunk)
        self.send_msg(protocols.build_header(protocols.FILE_END, path), '')

    def send_file(self, path):
        """
        Sends a file to the server.
        :param path: a path to a file.
        """
        path_chunks = file_handler.generate_chunks(path, DEF_DATA_CHUNK_SIZE)
        sender = Thread(target=self._send_chunks, args=[path_chunks, path])
        sender.start()

    def close_sock(self):
        """
        Closes the socket
        """
        try:
            self.shutdown(socket.SHUT_RDWR)  # Stop receiving/sending
        except:
            pass
        self.close()
        self.open = False
