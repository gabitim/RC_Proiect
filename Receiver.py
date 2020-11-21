# this script can send a file using Go back n, sliding window protocol

import socket
import sys
import os
import threading
from pydispatch import dispatcher
from enums.finishtypes import FinishTypes
from enums.logtypes import LogTypes

SEP = os.path.sep

from Components import Logger, \
    ReceiverPacketHandler, \
    SenderPacketHandler, \
    Udp

# parameter from QT ; default value below
RECEIVER_ADDRESS = ('localhost', 9998)


class ReceiverAcknowledgementHandler:
    def __init__(self, socket, LOG_SIGNAL=None):
        self.socket = socket
        self.LOG_SIGNAL = LOG_SIGNAL
        self.logger = Logger.Logger(self.LOG_SIGNAL)

    def send_ack(self, address, packet_number, last_frame_received):
        # if we have the right package send the ack to move the window
        if packet_number == last_frame_received + 1:
            last_frame_received += 1
            self.logger.log(LogTypes.OTH, 'Got expected packet')
            self.logger.log(LogTypes.SNT, f'Acknowledgement {last_frame_received} sent.')
            ack_packet = SenderPacketHandler.make_packet(last_frame_received)
            Udp.send(ack_packet, self.socket, address)

            return last_frame_received, True
        # if we have wrong packet send ack to reset the window
        else:
            self.logger.log(LogTypes.OTH, 'Got wrong packet')
            self.logger.log(LogTypes.SNT, f'Acknowledgement {last_frame_received} sent.')
            ack_packet = SenderPacketHandler.make_packet(last_frame_received)
            Udp.send(ack_packet, self.socket, address)

            return last_frame_received, False


# receive packets and writes them into filename
class Receiver:
    def __init__(self, foldername, SIGNALS=None):
        self.running = False

        file = "SAVEDFILE.jpg"
        self.filename = foldername + SEP + file

        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.socket.bind(RECEIVER_ADDRESS)

        if SIGNALS is None:
            self.console_mode = True
            self.LOG_SIGNAL = None
        else:
            self.console_mode = False

            # [LOG_SIGNAL, FINISH_SIGNAL, STOP_SIGNAL]
            self.SIGNALS = SIGNALS
            self.LOG_SIGNAL = self.SIGNALS[0]
            self.FINISH_SIGNAL = self.SIGNALS[1]
            self.STOP_SIGNAL = self.SIGNALS[2]

            dispatcher.connect(self.STOP_SIGNAL, self.stop, weak=False)

        self.logger = Logger.Logger(self.LOG_SIGNAL)

    def start(self):
        self._thread = threading.Thread(target=self.run)
        self._thread.start()
        self.running = True

    def run(self):
        self.logger.log(LogTypes.SET, 'Sender has started')

        #TODO handshake

        self.logger.log(LogTypes.INF, 'Handshake successful')

        # try open, or create the file for writing
        try:
            file = open(self.filename, 'wb')
        except IOError:
            self.logger.log(LogTypes.ERR, f'Unable to open {self.filename}')
            #TODO return
            return

        ack_handler = ReceiverAcknowledgementHandler(self.socket, self.LOG_SIGNAL)

        last_frame_received = -1

        while self.running:  # get the next packet from sender
            packet, address = Udp.receive(self.socket)
            if not packet:
                break

            packet_number, data = ReceiverPacketHandler.extract_information(packet)
            self.logger.log(LogTypes.RCV, f'Packet {packet_number} received.')

            last_frame_received, can_write = ack_handler.send_ack(address, packet_number, last_frame_received)

            if can_write:
                file.write(data)

        if self.running: # normal receiver execution end
            # finnish writing --> closing the file
            self.logger.log(LogTypes.SET, 'All packets received. Shutting down.')
            file.close()
            self.socket.close()
            self.running = False
            dispatcher.send(self.FINISH_SIGNAL, type=FinishTypes.NORMAL) #TODO return

    def stop(self):
        self.running = False


def start_receiver(foldername):
    receiver = Receiver(foldername) #TODO console
    receiver.start()


if __name__ == '__main__':
    # command line params:
    # 1. filename

    # filename = f"tests{SEP}SAVED3.pdf"
    foldername = f"test"
    start_receiver(foldername)
