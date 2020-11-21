# UDP datagrams

import socket
import random

import Sender
from Components import Logger
from enums.logtypes import LogTypes

# Sending with UPD; simulating that some packets may be lost
# with DROP_PROBABILITY rate
class UdpSender:
    def __init__(self, LOSS_CHANCE, LOG_SIGNAL=None):
        self.LOSS_CHANCE = LOSS_CHANCE
        self.logger = Logger.Logger(LOG_SIGNAL)

    def send(self, packet, socket, address):
        if random.randint(0, 100) > self.LOSS_CHANCE:
            socket.sendto(packet, address)
        else:
            self.logger.log(LogTypes.WRN, 'Packet was lost')


# Receiving a packet with UDP
def receive(socket, buffer_size):
    packet, address = socket.recvfrom(buffer_size + 4)
    return packet, address
