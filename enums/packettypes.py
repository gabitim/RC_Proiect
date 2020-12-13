from enum import Enum


class PacketTypes(Enum):
    DATA = 1
    ACK = 2
    REQUEST = 3
    HANDSHAKE = 4
    FINISH = 5
