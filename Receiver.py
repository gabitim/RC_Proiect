# this script can send a file using Go back n, sliding window protocol

import time
import socket
import sys
import os
import threading
import random
from pydispatch import dispatcher
from enums.finishtypes import FinishTypes
from enums.logtypes import LogTypes

from Components import Logger, \
    PacketHandler, \
    Udp

SEP = os.path.sep

# receive packets and writes them into filename
class Receiver(threading.Thread):
    def __init__(self, foldername, sender_ip='127.0.0.1', SIGNALS=None): # TODO add sender_ip
        super().__init__()
        self.running = True
        self.sender_address = (sender_ip, Udp.SENDER_PORT)

        self.filename = foldername + SEP
        self.socket = None
        self.udp = None

        if SIGNALS is None:
            self.console_mode = True
            self.LOG_SIGNAL = None
        else:
            self.console_mode = False
            # [LOG_SIGNAL, FINISH_SIGNAL]
            self.SIGNALS = SIGNALS
            self.LOG_SIGNAL = self.SIGNALS[0]
            self.FINISH_SIGNAL = self.SIGNALS[1]

        self.logger = Logger.Logger(self.LOG_SIGNAL)

    def run(self):
        self.logger.log(LogTypes.SET, 'Receiver has started')

        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as self.socket:
            # socket does not have an address yet, so init with port 0
            self.udp = Udp.Udp(self.socket, 0, self.sender_address, self.LOG_SIGNAL)
            self.handshake()

            # try open, or create the file for writing
            with open(self.filename, 'wb') as file:
                self.receive_packets(file)

            if self.running: # normal receiver execution end
                # TODO keep sending until recv thread joins
                self.udp.send(PacketHandler.Types.FINISH)
                temp = self.udp.receive()
                self.logger.log(LogTypes.SET, 'All packets received. Shutting down.')
                if not self.console_mode:
                    dispatcher.send(self.FINISH_SIGNAL, type=FinishTypes.NORMAL)

    def terminate(self):
        self.running = False

    def error(self, message):
        self.logger.log(LogTypes.ERR, message)
        if not self.console_mode:
            dispatcher.send(self.FINISH_SIGNAL, type=FinishTypes.ERROR)
        self.terminate()

    def handshake(self):
        self.udp.send(PacketHandler.Types.REQUEST)
        self.udp.update_source_port()
        temp = self.udp.receive()
        if temp is None:
            pass # TODO

        type, _, DATA_MAX_SIZE, LOSS_CHANCE, CORRUPTION_CHANCE, self.filename = temp
        if type != PacketHandler.Types.HANDSHAKE:
            pass # TODO
        # TODO what should be sent?
        self.udp.send_handshake(DATA_MAX_SIZE, LOSS_CHANCE, CORRUPTION_CHANCE, self.filename)
        self.logger.log(LogTypes.INF, 'Handshake successful')

    def receive_packets(self, file):
        last_frame_received = -1

        while self.running:  # get the next packet from sender
            temp = self.udp.receive()
            if not temp:
                self.error('Sender error')
                break

            type, seq_num, data = temp
            if type == PacketHandler.Types.FINISH:
                break
            else:
                self.logger.log(LogTypes.RCV, f'Packet {seq_num} received.')
                last_frame_received, can_write = self.send_ack(seq_num, last_frame_received)
                if can_write:
                    file.write(data)

    def send_ack(self, packet_number, last_frame_received):
        # if we have the right package send the ack to move the window
        if packet_number == last_frame_received + 1:
            last_frame_received += 1
            self.logger.log(LogTypes.OTH, 'Got expected packet')
            self.logger.log(LogTypes.SNT, f'Acknowledgement {last_frame_received} sent.')
            self.udp.send(PacketHandler.Types.ACK, last_frame_received)

            return last_frame_received, True
        # if we have wrong packet send ack to reset the window
        else:
            self.logger.log(LogTypes.OTH, 'Got wrong packet')
            self.logger.log(LogTypes.SNT, f'Acknowledgement {last_frame_received} sent.')
            self.udp.send(PacketHandler.Types.ACK, last_frame_received)

            return last_frame_received, False

def run_receiver(foldername):
    receiver = Receiver(foldername)
    receiver.run()


if __name__ == '__main__':
    # this is to be used for testing purpose only
    # examples of default parameters
    foldername = f"test"

    run_receiver(foldername)

''' TODO example
while self.running:
    counter = 0
    try: # try every second during 60 seconds to connect, else terminate
        self.socket.connec(SENDER_ADDRESS)
    except:
        counter = counter + 1
        if counter > 60:
            self.error('Could not connect to a Sender')
        time.sleep(1)
'''
