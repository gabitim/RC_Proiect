# this script can send a file using Go back n, sliding window protocol

import socket
import os
import sys
import _thread
import time

# import the modules scripts
from Components import Logger, \
    ReceiverPacketHandler, \
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
            packet, _ = Udp.receive(self.socket)
            ack, _ = ReceiverPacketHandler.extract_information(packet)

            # if we have ACK for the LAR
            print(f'Got ACK for {LAR}')
            if ack >= LAR:
                mutex.acquire()
                LAR = ack + 1
                print(f"LAR updated; new LAR --> {LAR}")
                timer_object.stop()
                mutex.release()


class Sender:
    def __init__(self, socket, filename):
        self.socket = socket
        self.filename = filename

    def send(self):
        global mutex
        global LAR
        global timer_object

        # SenderAcknowledgementHandler object
        ack_handler = SenderAcknowledgementHandler(self.socket)

        # we try open the file
        try:
            file = open(self.filename, 'rb')
        except IOError:
            print('Unable to open', self.filename)  # logg
            return

        # create packets and add to buffer
        packets = []
        packet_number = 0

        while True:
            data = file.read(PACKET_SIZE)
            if not data:
                break
            packets.append(SenderPacketHandler.make_packet(packet_number, data))
            packet_number += 1

        number_of_packets = len(packets)
        print(f"{number_of_packets} packets made")
        window_size = min(WINDOW_SIZE, number_of_packets)

        # by LFS we will understand last frame sent
        LFS = 0

        _thread.start_new_thread(ack_handler.wait_for_ack, ())

        # we run until all the packets are sent
        while LAR < number_of_packets:
            mutex.acquire()

            # starting the timer
            if not timer_object.timer_is_running():
                print(f"starting the timer")
                timer_object.start()

            # send the packets from window
            while LFS < LAR + window_size:
                print(f"Sending packet: {LFS}")
                Udp.send(packets[LFS], self.socket, RECEIVER_ADDRESS)
                LFS += 1

            # we put this thread to sleep until we have a timeout or we have ack
            while timer_object.timer_is_running() and not timer_object.timeout():
                mutex.release()
                print('Sender is sleeping; waiting for ack or timeout')
                time.sleep(SLEEP_INTERVAL)
                mutex.acquire()

            if timer_object.timeout():
                print('we timeout out')
                timer_object.stop()
                # we send all the packets from window again
                LFS = LAR
            else:
                # if we didnt timeout that means we got a correct ack
                print(f"we got correct ack; shifting window: now LAR is -->  {LAR}")
                window_size = min(WINDOW_SIZE, number_of_packets - LAR)
            mutex.release()

        # send an empty packet for breaking the loop and closing the file
        print("we sent all the packets; Time to end ")
        Udp.send(SenderPacketHandler.make_empty_packet(), self.socket, RECEIVER_ADDRESS)
        file.close()


if __name__ == '__main__':
    # TO BE LINKED WITH UI

    # command line params:
    # 1. path to the file to be sent
    # 2. Receiver address; default (localhost, 8080)
    # 3. Packet size; default 1024 bytes
    # 4. Window size; default 4
    # 5. Timeout interval; default 0.5 sec

    filename = f"tests{SEP}ipv.pdf"

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind(SENDER_ADDRESS)

    sender = Sender(sock, filename)
    sender.send()

    sock.close()
