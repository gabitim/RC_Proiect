# this script can send a file using Go back n, sliding window protocol

import socket
import os
import sys
import _thread
import time

# import the modules scripts
from Components import Logger, \
    RecieverPacketHandler, \
    SenderPacketHandler, \
    Timer, \
    Udp

SEP = os.path.sep
SENDER_ADDRESS = ('localhost', 0)
SLEEP_INTERVAL = 0.05

# parameters from UI QT; below are default values
FILENAME = f"tests{SEP}test"
PACKET_SIZE = 1024
RECEIVER_ADDRESS = ('localhost', 8080)
TIMEOUT_INTERVAL = 0.5
WINDOW_SIZE = 4

# global variables
LAR = 0  # by LAR we will understand last ack received
mutex = _thread.allocate_lock()  # used  for synchronizing threads
timer_object = Timer.Timer(TIMEOUT_INTERVAL)  # instance of Timer class


class SenderAcknowledgementHandler:
    def __init__(self, socket):
        self.socket = socket

    def wait_for_ack(self):
        global LAR
        global mutex
        global timer_object

        # we wait for the sender to send ack for the current LAR
        while True:
            packet = Udp.receive(socket)
            ack = RecieverPacketHandler.extract_information(packet)

            # if we have ACK for the LAR
            print(f'Got ACK for {LAR}')
            if ack >= LAR:
                mutex.acquire()
                LAR = ack + 1
                print(f"LAR updated; new LAR --> {LAR}")
                timer_object.stop()
                mutex.release()


def send(socket, filename):
    global mutex
    global LAR
    global timer_object

    # SenderAcknowledgementHandler object
    ack_handler = SenderAcknowledgementHandler(socket)

    # we try open the file


if __name__ == '__main__':
    # TO BE LINKED WITH UI

    # command line params:
    # 1. path to the file to be sent
    # 2. Receiver address; default (localhost, 8080)
    # 3. Packet size; default 1024 bytes
    # 4. Window size; default 4
    # 5. Timeout interval; default 0.5 sec

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind(SENDER_ADDRESS)

    send(sock, FILENAME)
    sock.close()
