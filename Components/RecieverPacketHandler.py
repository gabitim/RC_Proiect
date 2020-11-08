# this script handles the extraction of information from packet

# first 4 bytes are the header and they represent the packet number
# from the sequence of packets
# from byte 5 onward is data from packet
def extract_information(packet):
    packet_number = int.from_bytes(packet[0:4], byteorder='little', signed=True)
    packet_data = packet[4:]

    return packet_number, packet_data