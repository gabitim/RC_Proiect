from enum import Enum
"""
packet = Packet(date, dimeni)

packet.make_handshake(data)

udp.send(packet)
"""

'''
--- source port [0-15]
--- destination port[16-31]
--- length [32-47]
--- checksum [48-63]
--- type[64-66]
--- seq_num[67-95]
--- data[96..]
'''


class PacketHandler:
    HEADER_SIZE = 96
    HANDSHAKE_SIZE = 64

    class Types(Enum):
        DATA = 1
        ACK = 2
        HANDSHAKE = 3
        ERROR = 4
        FINISH = 5

    def __init__(self, source_port, destination_port):
        self.source_port = source_port
        self.destination_port = destination_port
        self.length = 0
        self.checksum = 0
        self.type = 0
        self.seq_num = 0
        self.data = ''
        self.handshake_bytes = b''

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
        self.data = data_max_size.to_bytes(16, byteorder='little', signed=False)
        self.data += loss_chance.to_bytes(8, byteorder='little', signed=False)
        self.data += corruption_chance.to_bytes(8, byteorder='little', signed=False)
        self.data += filename.to_bytes(32, byteorder='little', signed=False)

        self.compute_length()
        self.compute_checksum()

    def compute_length(self):
        self.length = len(self.data) + self.HEADER_SIZE

    def compute_checksum(self):
        pass

    def get_type(self):
        return self.type

    def get_bytes(self):
        bytes = self.source_port.to_bytes(16, byteorder='little', signed=False)
        bytes += self.destination_port.to_bytes(16, byteorder='little', signed=False)
        bytes += self.length.to_bytes(16, byteorder='little', signed=False)
        bytes += self.checksum.to_bytes(16, byteorder='little', signed=False)
        bytes += self.type.to_bytes(3, byteorder='little', signed=False)
        bytes += self.seq_num.to_bytes(29, byteorder='little', signed=False)
        bytes += self.data

        return bytes

    def decode(self, bytes):
        source_port = int.from_bytes(bytes[0:16], byteorder='little', signed=False)
        destination_port = int.from_bytes(bytes[16:32], byteorder='little', signed=False)
        length = int.from_bytes(bytes[32:48], byteorder='little', signed=False)
        checksum = int.from_bytes(bytes[48:64], byteorder='little', signed=False)
        type = int.from_bytes(bytes[64:67], byteorder='little', signed=False)
        seq_num = int.from_bytes(bytes[67:96], byteorder='little', signed=False)
        data = bytes[96:]

        if len(bytes) != length:
            return None

        # TODO hex(zlib.crc32(b'hello-world'))
        # compute checksum !!
        # if checksum != compute_checksum(bytes):
        #         return None

        # source and destination are reversed in incomming packets
        if source_port != self.destination_port:
            return None
        # source and destination are reversed in incomming packets
        if destination_port != self.source_port:
            return None

        return type, seq_num, data

    def unmake(self, bytes):
        temp = self.decode(bytes)
        if temp is None:
            return None

        if temp[0] == Types.HANDSHAKE:
            return temp[0], temp[1], self.unmake_handshake(temp[2])
        else:
            return temp

    def unmake_handshake(self, data):
        data_max_size = int.from_bytes(data[0:16], byteorder='little', signed=False)
        loss_chance = int.from_bytes(data[16:24], byteorder='little', signed=False)
        corruption_chance = int.from_bytes(data[24:32], byteorder='little', signed=False)
        filename = str.from_bytes(data[32:], byteorder='little', signed=False)

        # TODO set corruption_chance
        return data_max_size, loss_chance, filename
