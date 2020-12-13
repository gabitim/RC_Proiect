from enum import Enum


class PacketTypes(Enum):
    DATA = 1
    ACK = 2
    REQUEST = 3
    HANDSHAKE = 4
    FINISH = 5

    def to_bytes(self, length, byteorder, signed=False):
        return self.value.to_bytes(length, byteorder=byteorder, signed=signed)
