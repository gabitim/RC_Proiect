# UDP datagrams

import socket
import random

from Components import Logger, PacketHandler
from enums.logtypes import LogTypes

SENDER_PORT = 24450


class Udp:
    def __init__(self, socket, source_port, destination_address=None, LOG_SIGNAL=None):
        self.socket = socket
        self.destination_address = destination_address
        destination_port = destination_address[1] if destination_address is not None else None
        self.packet_handler = PacketHandler.PacketHandler(source_port, destination_port)

        self.loss_chance = 0
        self.buffer_size = 0
        self.update_buffer_size(self.packet_handler.HEADER_SIZE + self.packet_handler.HANDSHAKE_SIZE)

        self.logger = Logger.Logger(LOG_SIGNAL)

    def send(self, type, seq_num=0, data=b''):
        if random.randint(0, 100) <= self.loss_chance:
            self.logger.log(LogTypes.WRN, 'Packet was lost')
            return
        self.packet_handler.make(type, seq_num, data)
        self.socket.sendto(self.packet_handler.get_bytes(), self.destination_address)

    def send_handshake(self, data_max_size, loss_chance, corruption_chance, filename):
        if random.randint(0, 100) <= self.loss_chance:
            self.logger.log(LogTypes.WRN, 'Packet was lost')
            return
        self.packet_handler.make_handshake(PacketHandler.Types.HANDSHAKE, data_max_size, loss_chance, corruption_chance, filename)
        self.socket.sendto(self.packet_handler.get_bytes(), self.destination_address)

    def set_loss_chance(self, loss_chance):
        self.loss_chance = loss_chance

    def update_buffer_size(self, buffer_size):
        self.buffer_size = buffer_size + 4

    def accept_request(self):
        bytes, address = self.socket.recvfrom(self.buffer_size)
        if bytes is None:
            return False
        temp = self.packet_handler.unmake(bytes)
        if temp is None or temp[0] != PacketHandler.Types.REQUEST:
            return False

        self.destination_address = address
        self.packet_handler.set_destination_port(address[1])
        return True

    # Receiving a packet with UDP
    def receive(self):
        bytes, address = self.socket.recvfrom(self.buffer_size)
        # source and destination are reversed in incomming packets
        if address != self.destination_address or bytes is None:
            return None
        temp = self.packet_handler.unmake(bytes)
        if temp is None:
            return None
        elif temp[0] != PacketHandler.Types.HANDSHAKE:
            return temp
        else:
            self.update_buffer_size(temp[2] + self.packet_handler.HEADER_SIZE)
            self.set_loss_chance(temp[3])

            return temp

    def update_source_port(self):
        source_port = self.socket.getsockname()[1]
        self.packet_handler.set_source_port(source_port)
