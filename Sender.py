# this script can send a file using Go back n, sliding window protocol

import socket
import os
import sys
import _thread
import threading
import time
from pydispatch import dispatcher
from enums.finishtypes import FinishTypes
from enums.logtypes import LogTypes

# import the modules scripts
from Components import Logger, \
    ReceiverPacketHandler, \
    SenderPacketHandler, \
    Timer, \
    Udp


SEP = os.path.sep
SENDER_ADDRESS = ('localhost', 6663)
SLEEP_INTERVAL = 0.05

# parameters from UI QT; below are default values
FILENAME = f"tests{SEP}test"
PACKET_SIZE = 8096
RECEIVER_ADDRESS = ('localhost', 9998)
TIMEOUT_INTERVAL = 0.5
WINDOW_SIZE = 4

# global variables
LAR = 0  # by LAR we will understand last ack received
mutex = _thread.allocate_lock()  # used  for synchronizing threads
timer_object = Timer.Timer(TIMEOUT_INTERVAL)  # instance of Timer class


class SenderAcknowledgementHandler:
    def __init__(self, socket, LOG_SIGNAL=None):
        self.socket = socket
        self.LOG_SIGNAL = LOG_SIGNAL
        self.logger = Logger.Logger(self.LOG_SIGNAL)

    def wait_for_ack(self):
        global LAR
        global mutex
        global timer_object

        # we wait for the sender to send ack for the current LAR
        while True:
            try:
                packet, _ = Udp.receive(self.socket) #TODO PACK
            except:
                break

            ack, _ = ReceiverPacketHandler.extract_information(packet) #TODO pack

            # if we have ACK for the LAR
            self.logger.log(LogTypes.RCV, f'Acknowledgement {LAR} received.')
            if ack >= LAR:
                mutex.acquire()
                LAR = ack + 1
                self.logger.log(LogTypes.WSH, f'Shifting window to {LAR}.')
                timer_object.stop()
                mutex.release()


class Sender:
    def __init__(self, filename, SIGNALS=None):
        self.running = False

        self.filename = filename

        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.socket.bind(SENDER_ADDRESS)
        self.filename = filename

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
        global mutex
        global LAR
        global timer_object

        self.logger.log(LogTypes.SET, 'Sender has started')

        #TODO handshake

        self.logger.log(LogTypes.INF, 'Handshake successful')

        # we try open the file
        try:
            file = open(self.filename, 'rb')
        except IOError:
            self.logger.log(LogTypes.ERR, f'Unable to open {self.filename}')
            #TODO return
            return

        # create packets and add to buffer
        packets = []
        packet_number = 0

        while True:
            data = file.read(PACKET_SIZE)
            if not data:
                break
            packets.append(SenderPacketHandler.make_packet(packet_number, data)) #TODO pack
            packet_number += 1

        file.close()

        number_of_packets = len(packets)
        self.logger.log(LogTypes.INF, f'{number_of_packets} were created')
        window_size = min(WINDOW_SIZE, number_of_packets) #TODO logic

        # by LFS we will understand last frame sent
        LFS = 0

        ack_handler = SenderAcknowledgementHandler(self.socket, self.LOG_SIGNAL)
        _thread.start_new_thread(ack_handler.wait_for_ack, ())

        # we run until all the packets are sent
        while self.running and LAR < number_of_packets:
            mutex.acquire()

            # starting the timer
            if not timer_object.timer_is_running():
                # print(f"starting the timer") # TODO REMOVE?
                timer_object.start()

            # send the packets from window
            while LFS < LAR + window_size:
                self.logger.log(LogTypes.SNT, f'Packet {LFS} sent.')
                Udp.send(packets[LFS], self.socket, RECEIVER_ADDRESS) #TODO pack
                LFS += 1

            # we put this thread to sleep until we have a timeout or we have ack
            while timer_object.timer_is_running() and not timer_object.timeout():
                mutex.release()
                # print('Sender is sleeping; waiting for ack or timeout') # TODO REMOVE?
                time.sleep(SLEEP_INTERVAL)
                mutex.acquire()

            if timer_object.timeout():
                # print('we timeout out') # TODO REMOVE?
                self.logger.log(LogTypes.INF, f'Timeout. Resending window.')
                timer_object.stop()
                # we send all the packets from window again
                LFS = LAR
            else:
                # if we didnt timeout that means we got a correct ack
                window_size = min(WINDOW_SIZE, number_of_packets - LAR) #TODO check
            mutex.release()

        if self.running: # normal sender execution end
            # send an empty packet for breaking the loop and closing the file
            self.logger.log(LogTypes.SET, 'All packets sent. Shutting down.')
            Udp.send(SenderPacketHandler.make_empty_packet(), self.socket, RECEIVER_ADDRESS) #TODO pack
            self.socket.close()
            self.running = False
            dispatcher.send(self.FINISH_SIGNAL, type=FinishTypes.NORMAL) #TODO return

    def stop(self):
        self.running = False


def start_sender(filename):
    sender = Sender(filename) #TODO console
    sender.start()


if __name__ == '__main__':
    # command line params:
    # 1. path to the file to be sent
    # 2. Receiver address; default (localhost, 8080)
    # 3. Packet size; default 1024 bytes
    # 4. Window size; default 4
    # 5. Timeout interval; default 0.5 sec

    filename = f"test{SEP}send{SEP}test.jpg"

    start_sender(filename)
