from enum import Enum


class PacketTypes(Enum):
    DATA = 1
    ACK = 2
    REQ = 3 # REQUEST
    PRMT = 4 # PARAMETERS
    FIN = 5 # FINISH
