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
    ReceiverPacketHandler, \
    SenderPacketHandler, \
    Timer, \
    Udp

# packet/acknowledgement number used as error code when sending packets
ERROR_NUMBER = -1000

SEP = os.path.sep
SENDER_ADDRESS = ('localhost', 6663)
SLEEP_INTERVAL = 0.05

# parameters from UI QT; below are default values
RECEIVER_ADDRESS = ('localhost', 9998)

# global variables
last_ack_received = -1
mutex = _thread.allocate_lock()  # used  for synchronizing threads
timer_object = Timer.Timer()  # instance of Timer class


class SenderAcknowledgementHandler:
    ACK_BUFFER_SIZE = 4

    def __init__(self, socket, CORRUPTION_CHANCE, number_of_packets, LOG_SIGNAL=None):
        self.socket = socket
        self.CORRUPTION_CHANCE = CORRUPTION_CHANCE
        self.number_of_packets = number_of_packets
        self.logger = Logger.Logger(LOG_SIGNAL)

    def wait_for_ack(self):
        global last_ack_received
        global mutex
        global timer_object

        # we wait for the sender to send ack for the current LAR
        while True:
            try:
                packet, _ = Udp.receive(self.socket, SenderAcknowledgementHandler.ACK_BUFFER_SIZE)
            except:
                break

            ack, _ = ReceiverPacketHandler.extract_information(packet)

            if ack == ERROR_NUMBER:
                mutex.acquire()
                # Arbitrary value to signal receiver error
                last_ack_received = self.number_of_packets * 2
                timer_object.stop()
                mutex.release()
                return

            if random.randint(0, 100) <= self.CORRUPTION_CHANCE:
                self.logger.log(LogTypes.WRN, 'Acknowledgement is corrupted')
            else:
                # if we have ACK for the LAR
                self.logger.log(LogTypes.RCV, f'Acknowledgement {ack} received.')
                if ack > last_ack_received:
                    mutex.acquire()
                    last_ack_received = ack
                    self.logger.log(LogTypes.OTH, f'Shifting window to {last_ack_received}.')
                    timer_object.stop()
                    mutex.release()


class Sender(threading.Thread):
    HANDSHAKE_SIZE = 16 + 8 + 8 + 256

    # parameters order: PACKET_SIZE, WINDOW_SIZE, LOSS_CHANCE, CORRUPTION_CHANCE, TIMEOUT
    def __init__(self, filename, parameters, SIGNALS=None):
        super().__init__()
        self.running = True

        self.filename = filename

        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.socket.bind(SENDER_ADDRESS)
        self.filename = filename

        self.PACKET_SIZE = parameters[0]
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

    def run(self):
        global mutex
        global last_ack_received
        global timer_object

        self.logger.log(LogTypes.SET, 'Sender has started')

        udp_sender = Udp.UdpSender(self.LOSS_CHANCE, self.LOG_SIGNAL)

        packet_size_bytes = self.PACKET_SIZE.to_bytes(16, byteorder='little', signed=True)
        loss_chance_bytes = self.LOSS_CHANCE.to_bytes(8, byteorder='little', signed=True)
        corruption_chance_bytes = self.CORRUPTION_CHANCE.to_bytes(8, byteorder='little', signed=True)
        last_sep = self.filename.rfind(f'{SEP}')
        # windows is wierd
        last_sep = max(last_sep, self.filename.rfind('/'))

        filename_bytes = self.filename[last_sep + 1:].encode('utf-8')
        packet = packet_size_bytes + loss_chance_bytes + corruption_chance_bytes + filename_bytes

        udp_sender.send(packet, self.socket, RECEIVER_ADDRESS)
        data = self.socket.recv(Sender.HANDSHAKE_SIZE)
        if packet_size_bytes != data[0:16] or loss_chance_bytes != data[16:24] or\
            corruption_chance_bytes != data[24:32] or filename_bytes != data[32:]:
            self.logger.log(LogTypes.ERR, f'Handshake failed')
            self.socket.close()
            if not self.console_mode:
                dispatcher.send(self.FINISH_SIGNAL, type=FinishTypes.ERROR)
            return

        self.logger.log(LogTypes.INF, 'Handshake successful')

        # we try open the file
        try:
            file = open(self.filename, 'rb')
        except IOError:
            self.logger.log(LogTypes.ERR, f'Unable to open {self.filename}')
            udp_sender.send(SenderPacketHandler.make_packet(-1000, 'Sender Error'), self.socket, RECEIVER_ADDRESS)
            self.socket.close()
            if not self.console_mode:
                dispatcher.send(self.FINISH_SIGNAL, type=FinishTypes.ERROR)
            return

        # create packets and add to buffer
        packets = []
        packet_number = 0

        while True:
            data = file.read(self.PACKET_SIZE)
            if not data:
                break
            packets.append(SenderPacketHandler.make_packet(packet_number, data))
            packet_number += 1

        file.close()

        number_of_packets = len(packets)
        self.logger.log(LogTypes.INF, f'{number_of_packets} were created')
        window_size = min(self.WINDOW_SIZE, number_of_packets)

        last_frame_sent = -1

        ack_handler = SenderAcknowledgementHandler(self.socket, self.CORRUPTION_CHANCE, number_of_packets, self.LOG_SIGNAL)
        _thread.start_new_thread(ack_handler.wait_for_ack, ())

        # we run until all the packets are delivered
        while self.running and last_ack_received < number_of_packets - 1:
            mutex.acquire()

            # starting the timer
            if not timer_object.timer_is_running():
                # print(f"starting the timer") # TODO REMOVE?
                timer_object.start()

            # send the packets from window
            while last_frame_sent < last_ack_received + window_size:
                last_frame_sent += 1
                udp_sender.send(packets[last_frame_sent], self.socket, RECEIVER_ADDRESS)
                self.logger.log(LogTypes.SNT, f'Packet {last_frame_sent} sent.')

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
                last_frame_sent = last_ack_received
            else:
                # if we didnt timeout that means we got a correct ack
                window_size = min(self.WINDOW_SIZE, number_of_packets - last_ack_received - 1)
            mutex.release()

        if last_ack_received > number_of_packets:
            self.logger.log(LogTypes.ERR, 'Receiver Error')
            self.socket.close()
            if not self.console_mode:
                dispatcher.send(self.FINISH_SIGNAL, type=FinishTypes.ERROR)
            return

        if self.running: # normal sender execution end
            # send an empty packet for breaking the loop and closing the file
            self.logger.log(LogTypes.SET, 'All packets sent. Shutting down.')
            udp_sender.send(SenderPacketHandler.make_empty_packet(), self.socket, RECEIVER_ADDRESS)
            self.socket.close()
            if not self.console_mode:
                dispatcher.send(self.FINISH_SIGNAL, type=FinishTypes.NORMAL)
        else:
            udp_sender.send(SenderPacketHandler.make_packet(ERROR_NUMBER), self.socket, RECEIVER_ADDRESS)
            self.socket.close()


    def terminate(self):
        self.running = False


def run_sender(filename, parameters):
    sender = Sender(filename, parameters) #TODO console
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
