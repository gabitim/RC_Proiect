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
TRY_NUMBER = 60


# receive packets and writes them into filename
class Receiver(threading.Thread):
    def __init__(self, foldername, sender_ip, SIGNALS=None):
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
            self.socket.setblocking(False)
            # socket does not have an address yet, so init with port 0
            self.udp = Udp.Udp(self.socket, 0, self.sender_address, self.LOG_SIGNAL)
            try:
                first_packet = self.handshake()

                if self.running:
                    with open(self.filename, 'wb') as file:
                        self.receive_packets(file, first_packet)

                if self.running:
                    self.finish()

            except ConnectionResetError:
                self.error('Sender-side error')

    def handshake(self):
        if self.running:
            self.logger.log(LogTypes.INF, 'Handshake started')
        self.udp.send(PacketHandler.Types.REQUEST)
        self.udp.update_source_port()
        counter = 0
        while self.running:
            time.sleep(1)
            try:
                temp = self.udp.receive()
                if temp[0] == PacketHandler.Types.HANDSHAKE:
                    break
            except (BlockingIOError, ConnectionResetError):
                counter = counter + 1
                if counter > TRY_NUMBER:
                    self.error('Did not receive Handshake')

            self.udp.send(PacketHandler.Types.REQUEST)

        if self.running:
            type, _, filename = temp
            self.filename = self.filename + filename

        counter = 0
        first_packet = None
        while self.running:
            self.udp.send(PacketHandler.Types.HANDSHAKE)
            time.sleep(0.1)
            try:
                data = self.udp.receive()
                if data[0] == PacketHandler.Types.DATA:
                    first_packet = data
                    break
            except BlockingIOError:
                counter = counter + 1
                if counter > TRY_NUMBER:
                    self.error('Could not send handshake')

        if self.running:
            self.logger.log(LogTypes.INF, 'Handshake successful')
        return first_packet

    def receive_packets(self, file, first_packet):
        last_frame_received = -1

        type, seq_num, data = first_packet
        self.logger.log(LogTypes.RCV, f'Packet {seq_num} received.')
        last_frame_received, can_write = self.send_ack(seq_num, last_frame_received)
        if can_write:
            file.write(data)

        while self.running:  # get the next packet from sender
            try:
                temp = self.udp.receive()
            except BlockingIOError:
                continue
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

    def finish(self):
        self.logger.log(LogTypes.SET, 'All packets received. Shutting down.')

        counter = 0
        while self.running:
            self.udp.send(PacketHandler.Types.FINISH)
            time.sleep(0.1)
            try:
                self.udp.receive()
            except ConnectionResetError:
                # we finish normally
                break
            except BlockingIOError:
                # we finish with error
                counter = counter + 1
                if counter > TRY_NUMBER:
                    self.error('Could not send finish')

        if self.running and not self.console_mode:
            dispatcher.send(self.FINISH_SIGNAL, type=FinishTypes.NORMAL)

    def terminate(self):
        self.running = False

    def error(self, message):
        self.logger.log(LogTypes.ERR, message)
        if not self.console_mode:
            dispatcher.send(self.FINISH_SIGNAL, type=FinishTypes.ERROR)
        self.terminate()


def run_receiver(foldername):
    receiver = Receiver(foldername)
    receiver.run()


if __name__ == '__main__':
    # this is to be used for testing purpose only
    # examples of default parameters
    foldername = f"test"
    sender_ip = '127.0.0.1'

    run_receiver(foldername, sender_ip)
