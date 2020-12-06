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
    ReceiverPacketHandler, \
    SenderPacketHandler, \
    Udp

SEP = os.path.sep

# TODO parameter from QT ; default value below
SENDER_ADDRESS = ('localhost', Udp.SENDER_PORT)

class ReceiverAcknowledgementHandler:
    def __init__(self, socket, LOG_SIGNAL=None):
        self.socket = socket
        self.LOG_SIGNAL = LOG_SIGNAL
        self.logger = Logger.Logger(self.LOG_SIGNAL)

    def send_ack(self, udp_sender, address, packet_number, last_frame_received):
        # if we have the right package send the ack to move the window
        if packet_number == last_frame_received + 1:
            last_frame_received += 1
            self.logger.log(LogTypes.OTH, 'Got expected packet')
            self.logger.log(LogTypes.SNT, f'Acknowledgement {last_frame_received} sent.')
            ack_packet = SenderPacketHandler.make_packet(last_frame_received)
            udp_sender.send(ack_packet, self.socket, address)

            return last_frame_received, True
        # if we have wrong packet send ack to reset the window
        else:
            self.logger.log(LogTypes.OTH, 'Got wrong packet')
            self.logger.log(LogTypes.SNT, f'Acknowledgement {last_frame_received} sent.')
            ack_packet = SenderPacketHandler.make_packet(last_frame_received)
            udp_sender.send(ack_packet, self.socket, address)

            return last_frame_received, False


# receive packets and writes them into filename
class Receiver(threading.Thread):
    def __init__(self, foldername, SIGNALS=None):
        super().__init__()
        self.running = True
        self.sender_address = SENDER_ADDRESS

        self.filename = foldername + SEP
        self.socket = None

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
            self.connectToSocket()


            data, address = Udp.receive(self.socket, Receiver.HANDSHAKE_SIZE)

            self.PACKET_SIZE = int.from_bytes(data[0:16], byteorder='little', signed=True)
            self.LOSS_CHANCE = int.from_bytes(data[16:24], byteorder='little', signed=True)
            self.CORRUPTION_CHANCE = int.from_bytes(data[24:32], byteorder='little', signed=True)
            self.filename += data[32:].decode("utf-8")

            self.socket.sendto(data, self.sender_address)

            udp_sender = Udp.UdpSender(self.LOSS_CHANCE, self.LOG_SIGNAL)

            self.logger.log(LogTypes.INF, 'Handshake successful')

            # try open, or create the file for writing
            try:
                file = open(self.filename, 'wb')
            except IOError:
                self.logger.log(LogTypes.ERR, f'Unable to open {self.filename}')
                udp_sender.send(SenderPacketHandler.make_packet(-1000, 'Sender Error'), self.socket, RECEIVER_ADDRESS)
                self.socket.close()
                if not self.console_mode:
                    dispatcher.send(self.FINISH_SIGNAL, type=FinishTypes.ERROR)
                return

            ack_handler = ReceiverAcknowledgementHandler(self.socket, self.LOG_SIGNAL)

            last_frame_received = -1

            while self.running:  # get the next packet from sender
                packet, address = Udp.receive(self.socket, self.PACKET_SIZE)
                if not packet:
                    break

                packet_number, data = ReceiverPacketHandler.extract_information(packet)

                if packet_number == ERROR_NUMBER:
                    self.logger.log(LogTypes.ERR, 'Sender Error')
                    self.socket.close()
                    if not self.console_mode:
                        dispatcher.send(self.FINISH_SIGNAL, type=FinishTypes.ERROR)
                    return

                if random.randint(0, 100) <= self.CORRUPTION_CHANCE:
                    self.logger.log(LogTypes.WRN, 'Packet is corrupted')
                else:
                    self.logger.log(LogTypes.RCV, f'Packet {packet_number} received.')
                    last_frame_received, can_write = ack_handler.send_ack(udp_sender, address, packet_number, last_frame_received)
                    if can_write:
                        file.write(data)

            if self.running: # normal receiver execution end
                # finnish writing --> closing the file
                self.logger.log(LogTypes.SET, 'All packets received. Shutting down.')
                file.close()
                self.socket.close()
                if not self.console_mode:
                    dispatcher.send(self.FINISH_SIGNAL, type=FinishTypes.NORMAL)
            else:
                if self.sender_address is not None:
                    udp_sender.send(SenderPacketHandler.make_packet(ERROR_NUMBER), self.socket, self.sender_address)
                self.socket.close()

    def terminate(self):
        self.running = False

    def error(self, message):
        self.socket.close()
        self.logger.log(LogTypes.ERR, message)
        if not self.console_mode:
            dispatcher.send(self.FINISH_SIGNAL, type=FinishTypes.ERROR)
        self.terminate()

    def connectToSocket(self):
        while self.running:
            counter = 0
            try: # try every second during 60 seconds to connect, else terminate
                self.socket.connect(SENDER_ADDRESS)
            except:
                counter = counter + 1
                if counter > 60:
                    self.error('Could not connect to a Sender')
                time.sleep(1)



def run_receiver(foldername):
    receiver = Receiver(foldername)
    receiver.run()


if __name__ == '__main__':
    # this is to be used for testing purpose only
    # examples of default parameters
    foldername = f"test"

    run_receiver(foldername)
