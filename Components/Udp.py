# UDP datagrams

import socket
import random

import Sender

# no of packet lost per 10 packets

DROP_PROBABILITY = 5

# Sending with UPD; simulating that some packets may be lost
# with DROP_PROBABILITY rate
def send(packet, socket, address):
    if random.randint(0, 100) > DROP_PROBABILITY:
        socket.sendto(packet, address)
        # logger -> ok
    else:
        pass
        # logger -> miss
    return


# Receiving a packet with UDP
def receive(socket):
    packet, address = socket.recvfrom(Sender.PACKET_SIZE + 4)
    print(f'socket is {socket}')
    return packet, address
