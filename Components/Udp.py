# UDP datagrams

import socket
import random

import Sender

# no of packet lost per 10 packets

PACKETS_TO_BE_LOST = 2  # from QT
DROP_PROBABILITY = 10 - PACKETS_TO_BE_LOST


# Sending with UPD; simulating that some packets may be lost
# with DROP_PROBABILITY rate
def send(packet, socket, address):
    if random.randint(0, DROP_PROBABILITY) > 0:
        socket.sendto(packet, address)
        # logger -> ok
    else:
        pass
        # logger -> miss
    return


# Receiving a packet with UDP
def receive(socket):
    packet, address = socket.recvfrom(Sender.PACKET_SIZE + 4)
    return packet, address

