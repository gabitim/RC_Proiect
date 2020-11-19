# this script can send a file using Go back n, sliding window protocol

import socket
import sys
import os
import PyQt5.QtCore
import threading
from PyQt5.QtCore import pyqtSlot

SEP = os.path.sep

from Components import Logger, \
    ReceiverPacketHandler, \
    SenderPacketHandler, \
    Udp

# parameter from QT ; default value below
RECEIVER_ADDRESS = ('localhost', 9998)


class ReceiverAcknowledgementHandler:
    def __init__(self, socket, file):
        self.socket = socket
        self.file = file

    def send_ack(self, address, packet_number, LFR):
        # if we have the right package send the ack to move the window
        if packet_number == LFR:
            print('Got expected packet')
            print(f"Send ACK {LFR}")
            ack_packet = SenderPacketHandler.make_packet(LFR)
            Udp.send(ack_packet, self.socket, address)

            LFR += 1
            return LFR, True
        # if we have wrong packet send ack to reset the window
        else:
            print('Got Wrong Packet')
            print(f"Sending ack for resetting the window {LFR - 1}")
            ack_packet = SenderPacketHandler.make_packet(LFR - 1)
            Udp.send(ack_packet, self.socket, address)

            return LFR, False


# receive packets and writes them into filename
class Receiver(PyQt5.QtCore.QObject):
    log_signal = PyQt5.QtCore.pyqtSignal(str, str)

    def __init__(self, folder_name):
        super().__init__()

        filename = "SAVEDFILE.jpg"
        filepath = folder_name + SEP + filename
        self.filename = filepath

        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.socket.bind(RECEIVER_ADDRESS)

    def start(self):
        self._thread = threading.Thread(target=self.run)
        self._thread.start()

    def run(self):
        # try open, or create the file for writing
        try:
            file = open(self.filename, 'wb')
        except IOError:
            print(f"Unable to open or create {self.filename}")
            return

        ack_handler = ReceiverAcknowledgementHandler(self.socket, file)

        # by LFR we will understand last accepted frame received
        LFR = 0

        while True:  # get the next packet from sender
            packet, address = Udp.receive(self.socket)
            if not packet:
                print("we received all the packets; time to end")
                break

            packet_number, data = ReceiverPacketHandler.extract_information(packet)
            print(f"Got packet {packet_number}")
            LFR, can_write = ack_handler.send_ack(address, packet_number, LFR)

            if can_write:
                print(f"writing data from packet {LFR - 1} in the new file")
                self.log_signal.emit('RCV', f'Packet {LFR - 1} received.')
                self.log_signal.emit('SNT', f'Acknowledgement {LFR - 1} sent.')
                file.write(data)

        # finnish writing --> closing the file
        file.close()
        self.socket.close()


def start_receiver(folderName): #from QT
    receiver = Receiver(folderName)
    receiver.start()


if __name__ == '__main__':
    # command line params:
    # 1. filename

    # filename = f"tests{SEP}SAVED3.pdf"
    folderName = f"test"
    start_receiver(folderName)
