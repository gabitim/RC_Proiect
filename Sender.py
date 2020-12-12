# this script can send a file using Go back n, sliding window protocol

import socket
import os
import sys
import _thread
import threading
import time
import random
from pydispatch import dispatcher
from enums.finishtypes import FinishTypes
from enums.logtypes import LogTypes

# import the modules scripts
from Components import Logger, \
    PacketHandler, \
    Timer, \
    Udp

SEP = os.path.sep


class Sender(threading.Thread):
    BIND_ADDRESS = ('0.0.0.0', Udp.SENDER_PORT)

    # parameters order: PACKET_SIZE, WINDOW_SIZE, LOSS_CHANCE, CORRUPTION_CHANCE, TIMEOUT
    def __init__(self, filename, parameters, SIGNALS=None):
        super().__init__()
        self.running = True

        self.socket = None
        self.udp = None

        self.FILENAME = filename
        self.DATA_MAX_SIZE = parameters[0]
        self.WINDOW_SIZE = parameters[1]
        self.LOSS_CHANCE = parameters[2]
        self.CORRUPTION_CHANCE = parameters[3]
        self.TIMEOUT = parameters[4]

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

        self.timer = None
        self.last_ack_received = -1

    def run(self):

        self.logger.log(LogTypes.SET, 'Sender has started')
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as self.socket:
            self.socket.setblocking(False)
            self.socket.bind(Sender.BIND_ADDRESS)
            self.udp = Udp.Udp(self.socket, Udp.SENDER_PORT, LOG_SIGNAL=self.LOG_SIGNAL)
            try:
                self.wait_for_request()
                self.handshake()
                frames = self.read_data()
                number_of_frames = len(frames)

                # we run until all the packets are delivered
                self.last_ack_received = -1
                last_frame_sent = -1
                SEND_TIMEOUT = 0.2
                self.timer = Timer.Timer(SEND_TIMEOUT)
                timeout_counter = 0
                MAX_TIMEOUTS = 50
                window_size = min(self.WINDOW_SIZE, number_of_frames)
                while self.running and self.last_ack_received < number_of_frames - 1:

                    self.timer.start()
                    # send the packets from window
                    while last_frame_sent < self.last_ack_received + window_size:
                        last_frame_sent += 1
                        while self.running: # try sending until buffer has space
                            try:
                                self.udp.send(PacketHandler.Types.DATA, last_frame_sent, frames[last_frame_sent])
                                break
                            except BlockingIOError:
                                pass

                        self.logger.log(LogTypes.SNT, f'Packet {last_frame_sent} sent.')

                    # we put this thread to sleep until we have a timeout or we have ack
                    while not self.timer.timeout() and self.timer.running():
                        self.check_response()

                    if self.timer.timeout():
                        self.logger.log(LogTypes.INF, f'Timeout. Resending window.')
                        self.timer.stop()
                        # we send all the packets from window again
                        last_frame_sent = self.last_ack_received
                        
                        timeout_counter += 1
                        if timeout_counter > MAX_TIMEOUTS:
                            self.error('Max timeouts for the same window reached')
                    else:
                        # if we didnt timeout that means we got a correct ack
                        timeout_counter = 0
                        window_size = min(self.WINDOW_SIZE, number_of_frames - self.last_ack_received - 1)

                if self.running:  # normal sender execution end
                    self.finish()

            except ConnectionResetError:
                self.error('Receiver-side error')

    def wait_for_request(self):
        counter = 0
        REQUEST_TRIES = 60
        REQUEST_SLEEP_TIME = 1
        while self.running:
            try:  # try every second during 60 seconds to connect, else terminate
                if self.udp.accept_request():
                    break
            except BlockingIOError:
                counter = counter + 1
                if counter > REQUEST_TRIES:
                    self.error('No Receiver requests')
                time.sleep(REQUEST_SLEEP_TIME)

    def handshake(self):
        if self.running:
            self.logger.log(LogTypes.INF, 'Handshake started')

        last_sep = self.FILENAME.rfind(f'{SEP}')
        '''  SOLVES PROBLEM WITH SEP FROM WINDOWS!!  '''
        last_sep = max(last_sep, self.FILENAME.rfind('/'))

        counter = 0
        HANDSHAKE_TRIES = 60
        HANDSHAKE_SLEEP_TIME = 0.1
        while self.running:

            self.udp.send_handshake(self.DATA_MAX_SIZE,
                                    self.LOSS_CHANCE,
                                    self.CORRUPTION_CHANCE,
                                    self.FILENAME[last_sep + 1:])
            time.sleep(HANDSHAKE_SLEEP_TIME)
            try:
                data = self.udp.receive()
                if data[0] == PacketHandler.Types.HANDSHAKE:
                    break
            except BlockingIOError:
                counter = counter + 1

                if counter > HANDSHAKE_TRIES:
                    self.error('Could not send handshake')

        if self.running:
            self.logger.log(LogTypes.INF, 'Handshake successful')

    def read_data(self):
        if self.running is False:
            return []

        try:
            file = open(self.FILENAME, 'rb')

            # create packets and add to buffer
            frames = []

            while True:
                data = file.read(self.DATA_MAX_SIZE)
                if not data:
                    break
                frames.append(data)

        except IOError:
            self.error(f'Unable to open {self.FILENAME}')
        except:
            self.error(f'Unexpected file error')
        finally:
            file.close()

        self.logger.log(LogTypes.INF, f'{len(frames)} were created')
        return frames

    def check_response(self):
        try:
            packet = self.udp.receive()
        except BlockingIOError:
            return

        if packet is None:
            self.error("Receiver error")
            return

        if packet[0] == PacketHandler.Types.ACK:
            _, seq_num, _ = packet
            self.logger.log(LogTypes.RCV, f'Acknowledgement {seq_num} received.')

            if seq_num > self.last_ack_received:
                self.last_ack_received = seq_num
                self.logger.log(LogTypes.OTH, f'Shifting window to {self.last_ack_received}.')
                self.timer.stop()

    def finish(self):
        self.logger.log(LogTypes.SET, 'All packets sent. Shutting down.')

        counter = 0
        FINISH_TRIES = 40
        FINISH_SLEEP_TIME = 0.1
        while self.running:

            self.udp.send(PacketHandler.Types.FINISH)
            time.sleep(FINISH_SLEEP_TIME)
            try:
                temp = self.udp.receive()
                if temp[0] == PacketHandler.Types.FINISH:
                    break
            except BlockingIOError:
                counter = counter + 1

                if counter > FINISH_TRIES:
                    self.error('Could not send finish')

        if self.running and not self.console_mode:
            dispatcher.send(self.FINISH_SIGNAL, type=FinishTypes.NORMAL)

    def terminate(self):
        self.running = False

    def error(self, message):
        self.logger.log(LogTypes.ERR, message)
        if not self.console_mode:
            dispatcher.send(self.FINISH_SIGNAL, type=FinishTypes.ERROR)
        self.running = False


def run_sender(filename, parameters):
    sender = Sender(filename, parameters)  # TODO console
    sender.run()


if __name__ == '__main__':
    # this is to be used for testing purpose only
    # examples of default parameters
    filename = f"test{SEP}send{SEP}test.jpg"
    PACKET_SIZE = 4096
    WINDOW_SIZE = 32
    LOSS_CHANCE = 5
    CORRUPTION_CHANCE = 1
    TIMEOUT = 0.5
    parameters = [PACKET_SIZE, WINDOW_SIZE, LOSS_CHANCE, CORRUPTION_CHANCE, TIMEOUT]

    run_sender(filename, parameters)
