from enum import Enum
import random
import zlib

from Components import Logger
from enums.logtypes import LogTypes

'''
    OUR PACKET STRUCTURE
--- source port [0-15]
--- destination port[16-31]
--- length [32-47]
--- checksum [48-63]
--- type[64-66]
--- seq_num[67-95]
--- data[96..]
'''


class Types(Enum):
    DATA = 1
    ACK = 2
    REQUEST = 3
    HANDSHAKE = 4
    FINISH = 5

    def to_bytes(self, length, byteorder, signed=False):
        return self.value.to_bytes(length, byteorder=byteorder, signed=signed)


class PacketHandler:
    HEADER_SIZE = 96
    HANDSHAKE_SIZE = 64

    def __init__(self, source_port, destination_port, CORRUPTION_CHANCE, LOG_SIGNAL=None):
        self.source_port = source_port
        self.destination_port = destination_port
        self.length = 0
        self.checksum = 0
        self.type = 0
        self.seq_num = 0
        self.data = b''
        self.corruption_chance = CORRUPTION_CHANCE

        self.logger = Logger.Logger(LOG_SIGNAL)

    def make(self, type, seq_num=0, data=b''):
        self.type = type
        self.seq_num = seq_num
        self.data = data

        self.compute_length()
        self.compute_checksum()

    # for handshake
    def make_handshake(self, type, data_max_size, loss_chance, corruption_chance, filename):
        self.type = type
        self.seq_num = 0
        self.data = data_max_size.to_bytes(16, 'little')
        self.data += loss_chance.to_bytes(8, 'little')
        self.data += corruption_chance.to_bytes(8, 'little')
        self.data += filename.encode().ljust(32, b'\0')

        self.compute_length()
        self.compute_checksum()

    def compute_length(self):
        self.length = len(self.data) + self.HEADER_SIZE

    def compute_checksum(self):
        packet_bytes = self.get_bytes()
        self.checksum = zlib.crc32(packet_bytes[:48] + packet_bytes[64:])

    def get_type(self):
        return self.type

    def get_bytes(self):
        packet_bytes = self.source_port.to_bytes(16, 'little')
        packet_bytes += self.destination_port.to_bytes(16, 'little')
        packet_bytes += self.length.to_bytes(16, 'little')
        packet_bytes += self.checksum.to_bytes(16, 'little')
        packet_bytes += self.type.to_bytes(3, 'little')
        packet_bytes += self.seq_num.to_bytes(29, 'little', signed=True)
        packet_bytes += self.data

        ''' simulate wrong checksum!! '''
        if random.randint(0, 1000) <= self.corruption_chance:
            corrupted_byte = random.randint(0, len(packet_bytes))
            bytes_list = list(packet_bytes)
            bytes_list[corrupted_byte] += 1
            packet_bytes = bytes(bytes_list)

        return packet_bytes

    def decode(self, packet_bytes):
        source_port = int.from_bytes(packet_bytes[0:16], 'little')
        destination_port = int.from_bytes(packet_bytes[16:32], 'little')
        length = int.from_bytes(packet_bytes[32:48], 'little')
        checksum = int.from_bytes(packet_bytes[48:64], 'little')
        type = Types(int.from_bytes(packet_bytes[64:67], 'little'))
        seq_num = int.from_bytes(packet_bytes[67:96], 'little', signed=True)
        data = packet_bytes[96:]

        ''' Check Packet Integrity '''
        # source and destination are reversed in incomming packets
        if source_port != self.destination_port and self.destination_port is not None:
            self.logger.log(LogTypes.WRN, 'Packet has wrong source port')
            return None
        # source and destination are reversed in incomming packets
        if destination_port != self.source_port:
            self.logger.log(LogTypes.WRN, 'Packet has wrong destination port')
            return None

        if len(packet_bytes) != length:
            self.logger.log(LogTypes.WRN, 'Packet has wrong length')
            return None

        if checksum != zlib.crc32(packet_bytes[:48] + packet_bytes[64:]):
            self.logger.log(LogTypes.WRN, 'Packet was corrupted')
            return None

        return type, seq_num, data

    def unmake(self, packet_bytes):
        temp = self.decode(packet_bytes)
        if temp is None:
            return None

        if temp[0] == Types.HANDSHAKE:
            return temp[0], temp[1], *self.unmake_handshake(temp[2])
        else:
            return temp

    def unmake_handshake(self, data):
        data_max_size = int.from_bytes(data[0:16], 'little')
        loss_chance = int.from_bytes(data[16:24], 'little')
        corruption_chance = int.from_bytes(data[24:32], 'little')
        filename = data[32:].rstrip(b'\0').decode()

        self.set_corruption_chance(corruption_chance)
        return data_max_size, loss_chance, filename

    def set_destination_port(self, destination_port):
        self.destination_port = destination_port

    def set_source_port(self, source_port):
        self.source_port = source_port

    def set_corruption_chance(self, corruption_chance):
        self.corruption_chance = corruption_chance
