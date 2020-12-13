import random
import zlib

from Components import Logger
from enums.logtypes import LogTypes
from enums.packettypes import PacketTypes


'''
    OUR PACKET STRUCTURE (BITS)
--- source port [0-15]
--- destination port [16-31]
--- length [32-47]
--- checksum [48-79]
--- reserved [80-92]
--- type [93-95]
--- seq_num [96-127]
--- data[128..]
'''

# THE REST OF THIS CLASS USES BYTES ONLY!!!
class PacketHandler:
    HEADER_SIZE = 16
    HANDSHAKE_SIZE = 10

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
        self.data = data_max_size.to_bytes(2, 'little')
        self.data += loss_chance.to_bytes(2, 'little')
        self.data += corruption_chance.to_bytes(2, 'little')
        self.data += filename.encode().ljust(4, b'\0')

        self.compute_length()
        self.compute_checksum()

    def compute_length(self):
        self.length = len(self.data) + self.HEADER_SIZE

    def compute_checksum(self):
        packet_bytes = self.get_bytes()
        self.checksum = zlib.crc32(packet_bytes[:6] + packet_bytes[10:])

    def get_type(self):
        return self.type

    def get_bytes(self):
        packet_bytes = self.source_port.to_bytes(2, 'little')
        packet_bytes += self.destination_port.to_bytes(2, 'little')
        packet_bytes += self.length.to_bytes(2, 'little')
        packet_bytes += self.checksum.to_bytes(4, 'little')

        # reserved is not currently planned for use
        reserved = 0
        reserved_and_type = (reserved << 3) | self.type.value
        packet_bytes += reserved_and_type.to_bytes(2, 'little')
        packet_bytes += self.seq_num.to_bytes(4, 'little', signed=True)
        packet_bytes += self.data

        ''' simulate wrong checksum!! '''
        if random.randint(0, 1000) <= self.corruption_chance:
            bytes_list = list(packet_bytes)
            corrupted_byte = random.randint(0, len(bytes_list) - 1)
            bytes_list[corrupted_byte] = (bytes_list[corrupted_byte] + 1) % 256
            packet_bytes = bytes(bytes_list)

        return packet_bytes

    def decode(self, packet_bytes):
        # decode up to checksum
        source_port = int.from_bytes(packet_bytes[0:2], 'little')
        destination_port = int.from_bytes(packet_bytes[2:4], 'little')
        length = int.from_bytes(packet_bytes[4:6], 'little')
        checksum = int.from_bytes(packet_bytes[6:10], 'little')

        # Check Packet Integrity
        if checksum != zlib.crc32(packet_bytes[:6] + packet_bytes[10:]):
            self.logger.log(LogTypes.WRN, 'Packet was corrupted')
            return None

        # source and destination are reversed in incomming packets
        if self.destination_port is not None and source_port != self.destination_port:
            self.logger.log(LogTypes.WRN, 'Packet has wrong source port')
            return None

        # source and destination are reversed in incomming packets
        if destination_port != self.source_port:
            self.logger.log(LogTypes.WRN, 'Packet has wrong destination port')
            return None

        if len(packet_bytes) != length:
            self.logger.log(LogTypes.WRN, 'Packet has wrong length')
            return None

        # decode after checksum
        reserved_and_type = int.from_bytes(packet_bytes[10:12], 'little')
        reserved = reserved_and_type >> 3
        type = PacketTypes(reserved_and_type & 7) # first 3 bits
        seq_num = int.from_bytes(packet_bytes[12:16], 'little', signed=True)
        data = packet_bytes[16:]

        return type, seq_num, data

    def unmake(self, packet_bytes):
        temp = self.decode(packet_bytes)
        if temp is None:
            return None

        if temp[0] == PacketTypes.HANDSHAKE:
            return temp[0], temp[1], *self.unmake_handshake(temp[2])
        else:
            return temp

    def unmake_handshake(self, data):
        data_max_size = int.from_bytes(data[0:2], 'little')
        loss_chance = int.from_bytes(data[2:4], 'little')
        corruption_chance = int.from_bytes(data[4:6], 'little')
        filename = data[6:].rstrip(b'\0').decode()

        self.set_corruption_chance(corruption_chance)
        return data_max_size, loss_chance, filename

    def set_destination_port(self, destination_port):
        self.destination_port = destination_port

    def set_source_port(self, source_port):
        self.source_port = source_port

    def set_corruption_chance(self, corruption_chance):
        self.corruption_chance = corruption_chance
