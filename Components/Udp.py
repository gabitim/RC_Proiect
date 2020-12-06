# UDP datagrams

import socket
import random

import Sender
from Components import Logger, PacketHandler
from enums.logtypes import LogTypes

SENDER_PORT = 24450


class Udp:
    def __init__(self, socket, source_port, destination_port, LOG_SIGNAL=None):
        self.socket = socket
        self.packet_handler = PacketHandler.PacketHandler(source_port, destination_port)

        self.loss_chance = 0
        self.buffer_size = 0
        self.update_buffer_size(self.packet_handler.HEADER_SIZE + self.packet_handler.HANDSHAKE_SIZE)

        self.logger = Logger.Logger(LOG_SIGNAL)

    def send(self, type, seq_num=0, data=''):
        if random.randint(0, 100) <= self.LOSS_CHANCE:
            self.logger.log(LogTypes.WRN, 'Packet was lost')
            return
        self.packet_handler.make(type, seq_num, data)
        self.socket.sendall(self.packet_handler.get_bytes())

    def send_handshake(self, type, data_max_size, loss_chance, corruption_chance, filename):
        if random.randint(0, 100) <= self.LOSS_CHANCE:
            self.logger.log(LogTypes.WRN, 'Packet was lost')
            return
        self.packet_handler.make_handshake(type, data_max_size, loss_chance, corruption_chance, filename)
        self.socket.sendall(self.packet_handler.get_bytes())

    def set_loss_chance(self, loss_chance):
        self.loss_chance = loss_chance

    def update_buffer_size(self, buffer_size):
        self.buffer_size = buffer_size + 4

    # Receiving a packet with UDP
    def receive(self):
        bytes = socket.recv(self.buffer_size)
        temp = self.packet_handler.unmake(bytes)
        if temp is None:
            return None
        elif temp[0] != self.packet_handler.Types.HANDSHAKE:
            return temp
        else:
            self.update_buffer_size(temp[2])
            self.set_loss_chance(temp[3])

            return temp[0], temp[1], temp[4]
