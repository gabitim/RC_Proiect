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

# packet/acknowledgement number used as error code when sending packets
ERROR_NUMBER = -1000

SEP = os.path.sep
SLEEP_INTERVAL = 0.05


# TO DO DELETE THESE FUCKING GLOBAL VARIABLES
# global variables
last_ack_received = -1
mutex = _thread.allocate_lock()  # used  for synchronizing threads
timer_object = Timer.Timer()  # instance of Timer class


class SenderAcknowledgementHandler:
    ACK_BUFFER_SIZE = 4

    def __init__(self, sender_thread, udp, number_of_frames, LOG_SIGNAL=None):
        self.udp = udp
        self.number_of_frames = number_of_frames
        self.logger = Logger.Logger(LOG_SIGNAL)
        self.sender_thread = sender_thread

    def wait_for_ack(self):
        global last_ack_received
        global mutex
        global timer_object

        # we wait for the sender to send ack for the current LAR
        while True:
            try:
                packet = self.udp.receive()
            except:
                break

            if packet is None:
                mutex.acquire()
                # Arbitrary value to signal receiver error
                last_ack_received = self.number_of_frames * 2
                timer_object.stop()
                mutex.release()
                return

            _, seq_num, _ = packet
            self.logger.log(LogTypes.RCV, f'Acknowledgement {seq_num} received.')

            if seq_num > last_ack_received:
                mutex.acquire()
                last_ack_received = seq_num
                self.logger.log(LogTypes.OTH, f'Shifting window to {last_ack_received}.')
                timer_object.stop()
                mutex.release()


class Sender(threading.Thread):

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

    def handshake(self):
        self.logger.log(LogTypes.INF, 'Handshake started')

        '''  PROBLEM WITH SEP FROM WINDOWS!!  '''
        last_sep = self.FILENAME.rfind(f'{SEP}')
        last_sep = max(last_sep, self.FILENAME.rfind('/'))

        self.udp.send_handshake(PacketHandler.PacketHandler.Types.HANDSHAKE,
                                self.PACKET_SIZE,
                                self.LOSS_CHANCE,
                                self.CORRUPTION_CHANCE,
                                self.FILENAME[last_sep + 1:])

        data = udp.receive()

        self.logger.log(LogTypes.INF, 'Handshake successful')

    def read_data(self):
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

        number_of_frames = len(packets)
        self.logger.log(LogTypes.INF, f'{number_of_frames} were created')
        return frames

    def wait_for_conn(self):
        default_address = ('0.0.0.0', Udp.SENDER_PORT)

        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as socket:
            socket.bind(default_address)
            socket.listen(1)
            client_socket, receiver_addr = socket.accept()

        return client_socket, receiver_addr

    def error(self, message):
        self.logger.log(LogTypes.ERR, message)
        self.socket.close()
        if not self.console_mode:
            dispatcher.send(self.FINISH_SIGNAL, type=FinishTypes.ERROR)
        self.running = False

    def run(self):
        global mutex
        global last_ack_received
        global timer_object

        self.logger.log(LogTypes.SET, 'Sender has started')

        self.socket, reciever_addr = self.wait_for_conn()
        try:
            self.udp = Udp.Udp(self.socket, reciever_addr, self.logger)
            self.handshake()
            frames = self.read_data()
            number_of_frames = len(frames)

            window_size = min(self.WINDOW_SIZE, number_of_frames)
            last_frame_sent = -1
            ack_handler = SenderAcknowledgementHandler(
                self,
                self.udp, number_of_frames,
                self.LOG_SIGNAL
            )
            _thread.start_new_thread(ack_handler.wait_for_ack, ())

            # we run until all the packets are delivered
            while self.running and last_ack_received < number_of_frames - 1:
                mutex.acquire()

                # starting the timer
                if not timer_object.timer_is_running():
                    # print(f"starting the timer") # TODO REMOVE?
                    timer_object.start()

                # send the packets from window
                while last_frame_sent < last_ack_received + window_size:
                    last_frame_sent += 1
                    self.udp.send(PacketHandler.Types.DATA, last_frame_sent, frames[last_frame_sent])
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
                    window_size = min(self.WINDOW_SIZE, number_of_frames - last_ack_received - 1)
                mutex.release()

            if last_ack_received > number_of_frames:
                self.logger.log(LogTypes.ERR, 'Receiver Error')
                self.socket.close()
                if not self.console_mode:
                    dispatcher.send(self.FINISH_SIGNAL, type=FinishTypes.ERROR)
                return

            if self.running:  # normal sender execution end
                # send an empty packet for breaking the loop and closing the file
                self.logger.log(LogTypes.SET, 'All packets sent. Shutting down.')
                self.udp.send(PacketHandler.Types.FINISH)
                temp = self.udp.receive()
                if not self.console_mode:
                    dispatcher.send(self.FINISH_SIGNAL, type=FinishTypes.NORMAL)
            self.socket.close()
        except:
            self.socket.close()


    def terminate(self):
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
