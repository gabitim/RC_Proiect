from enum import Enum


class Logtypes(Enum):
    SET = 1  # END OF TRANSMISSION
    SNT = 2 # SENT
    RCV = 3 # RECEIVED
    ERR = 4 # ERROR
    WRN = 5 # WARNING
    INF = 6 # INFORMATIVE
