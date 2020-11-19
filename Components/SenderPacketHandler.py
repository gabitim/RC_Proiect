# this script handles the creation of packets

# create an empty packet
def make_empty_packet():
    return b''


# creates a packet with 2 parts:
# header: first 4 bytes --> the packet number
# packet_data --> effective data to be sent
def make_packet(packet_number, packet_data=b''):
    header = packet_number.to_bytes(4, byteorder='little', signed=True)
    # logger
    complete_packet = header + packet_data
    return complete_packet
