# this script can send a file using Go back n, sliding window protocol

import time
import socket
import os
import threading
from pydispatch import dispatcher
from enums.finishtypes import FinishTypes
from enums.logtypes import LogTypes
from enums.packettypes import PacketTypes

from Components import Logger, \
    Udp, \
    Timer

SEP = os.path.sep


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

            self.SIGNALS = SIGNALS
            # order: [LOG_SIGNAL, FINISH_SIGNAL]
            self.LOG_SIGNAL = self.SIGNALS[0]
            self.FINISH_SIGNAL = self.SIGNALS[1]

        self.logger = Logger.Logger(self.LOG_SIGNAL)

    def run(self):
        self.logger.log(LogTypes.SET, 'Receiver has started')

        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as self.socket:
            self.socket.setblocking(False)
            # socket does not have an address yet, so init with port 0
            self.udp = Udp.Udp(self.socket, 0, self.sender_address, LOG_SIGNAL=self.LOG_SIGNAL)
            try:
                # with handshake set a connection and receive vital parameters (3 steps)
                parameters_packet = self.handshake()

                # receive data
                if self.running:
                    file_data = self.receive_packets(parameters_packet)

                # write data
                if self.running:
                    self.logger.log(LogTypes.INF, 'Writing to file')
                    with open(self.filename, 'wb') as file:
                        file.write(file_data)

                # close
                if self.running:
                    self.finish()

            except ConnectionResetError:
                self.error('Sender-side error')

    def handshake(self):
        """3 steps:"""

        """1. SEND HANDSHAKE REQUEST"""
        if self.running:
            self.logger.log(LogTypes.INF, 'Handshake started')
        self.udp.send(PacketTypes.REQUEST)
        self.udp.update_source_port()

        """2. WAIT FOR HANDSHAKE RESPONSE"""
        counter = 0
        HANDSHAKE_TRIES = 60
        HANDSHAKE_SLEEP_TIME = 1
        while self.running:
            time.sleep(HANDSHAKE_SLEEP_TIME)
            try:
                temp = self.udp.receive()
                if temp is not None and temp[0] == PacketTypes.HANDSHAKE:
                    break
            except (BlockingIOError, ConnectionResetError):
                pass
            counter = counter + 1
            if counter > HANDSHAKE_TRIES:
                self.error('Did not receive Handshake Response')

            self.udp.send(PacketTypes.REQUEST)

        if self.running:
            type, _, filename = temp
            self.filename = self.filename + filename

        """3. SEND HANDSHAKE ACK"""
        counter = 0
        HANDSHAKE_ACK_TRIES = 20
        HANDSHAKE_ACK_SLEEP_TIME = 0.1
        first_packet = None
        while self.running:
            self.udp.send(PacketTypes.ACK, -1)
            time.sleep(HANDSHAKE_ACK_SLEEP_TIME)
            try:
                data = self.udp.receive()
                if data is not None and data[0] == PacketTypes.DATA:
                    first_packet = data
                    break
            except BlockingIOError:
                pass
            counter = counter + 1
            if counter > HANDSHAKE_ACK_TRIES:
                self.error('Could not send handshake')

        if self.running:
            self.logger.log(LogTypes.INF, 'Handshake successful')
        return first_packet

    def receive_packets(self, parameters_packet):
        last_frame_received = -1
        file_data = b''

        type, seq_num, data = parameters_packet
        self.logger.log(LogTypes.RCV, f'Packet {seq_num} received.')

        last_frame_received, can_write = self.send_ack(seq_num, last_frame_received)

        if can_write:
            file_data += data

        RECEIVE_TIMEOUT = 10
        timer = Timer.Timer(RECEIVE_TIMEOUT)

        """GO BACK N LOGIC --> wait for packets, send ack, and move the window"""
        timer.start()
        while self.running and not timer.timeout():  # get the next packet from sender
            try:
                temp = self.udp.receive()
            except BlockingIOError:
                continue

            if temp is None:
                continue

            timer.restart()

            type, seq_num, data = temp
            # receive finish frame (step 6 from sender) its time to stop
            if type == PacketTypes.FINISH:
                break
            else:
                self.logger.log(LogTypes.RCV, f'Packet {seq_num} received.')
                last_frame_received, can_write = self.send_ack(seq_num, last_frame_received)
                if can_write:
                    file_data += data

        if timer.timeout():
            self.error('Timeout reached')
        return file_data

    def send_ack(self, packet_number, last_frame_received):
        """GO BACK N LOGIC --> if we have the right frame send the ack to move the window """
        if packet_number == last_frame_received + 1:
            last_frame_received += 1
            self.logger.log(LogTypes.OTH, 'Got expected packet')
            self.logger.log(LogTypes.SNT, f'Acknowledgement {last_frame_received} sent.')
            self.udp.send(PacketTypes.ACK, last_frame_received)

            return last_frame_received, True
        # if we have wrong packet send ack to reset the window
        else:
            self.logger.log(LogTypes.OTH, 'Got wrong packet')
            self.logger.log(LogTypes.SNT, f'Acknowledgement {last_frame_received} sent.')
            self.udp.send(PacketTypes.ACK, last_frame_received)

            return last_frame_received, False

    def finish(self):
        self.logger.log(LogTypes.SET, 'All packets received. Shutting down.')

        counter = 0
        FINISH_TRIES = 20
        FINISH_SLEEP_TIME = 0.1
        while self.running:
            # send finish ack (step 7 from sender)
            self.udp.send(PacketTypes.FINISH)
            time.sleep(FINISH_SLEEP_TIME)
            counter += 1
            if counter > FINISH_TRIES:
                break

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

    run_receiver(foldername)
