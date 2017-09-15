"""
This module contains the ChatClient class, used for client-server communication.
The ChatClient follows the communication protocol: send size of data - then the data itself.
"""
import socket
import jsonpickle as pickle
from threading import Thread
from time import sleep

import file_handler
import messages

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
                 data_chunk_size=DEF_DATA_CHUNK_SIZE, _sock=None):
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
        if _sock:
            super(ChatSocket, self).__init__(_sock=_sock)
        else:
            super(ChatSocket, self).__init__()

    def fileno(self):
        return super(ChatSocket, self).fileno()

    def receive(self):
        """
        Gathers data sent from the server
        :return: message from the server or None if the server closed
        """
        size = self._receive_all(MSG_LEN_SIZE)
        if not size:
            return None
        data = self._receive_all(int(size))
        return data

    def _receive_all(self, size):
        """
        Receives data sent from the server until all data is received
        :param size: the size of the data
        :return: received data
        """
        try:
            data = super(ChatSocket, self).recv(size)
            while len(data) < size:
                data += super(ChatSocket, self).recv(size - len(data))
            return data
        except:
            return ''

    def receive_obj(self):
        return pickle.loads(self.receive())

    def send_file(self, path):
        """
        Sends a file to the server.
        :param path: a path to a file.
        """
        data_chunks = file_handler.generate_chunks(path, DEF_DATA_CHUNK_SIZE)
        sender = Thread(target=self._send_chunks, args=[data_chunks, path])
        sender.start()

    def _send_chunks(self, chunks, path):
        for chunk in chunks:
            self.send_str(pickle.dumps(messages.Message(messages.FILE_DATA_CHUNK, chunk)))
            sleep(0.1)
        self.send_str(pickle.dumps(messages.Message(messages.FILE_DATA_FIN, path)))

    def send_obj(self, obj):
        self.send_regular(pickle.dumps(obj))

    def send_regular(self, data):
        self.send_str(pickle.dumps(messages.Message(messages.REGULAR_MSG, data)))

    def send_str(self, msg):
        """
        Sends a pickled message to the server
        :param msg: the message object
        """
        super(ChatSocket, self).sendall(str(len(msg)).zfill(MSG_LEN_SIZE))
        super(ChatSocket, self).sendall(msg)

    def close_sock(self):
        """
        Closes the socket
        """
        try:
            self.shutdown(socket.SHUT_RDWR)  # Stop receiving/sending
        except:
            pass
        self.close()
