from socket import socket
import bitstring

# The P2MP must be invoked as the following:
# p2mpclient srever-1 server-2 server-3 server-port# file-name MSS

# obtains data from the file on a byte basis
def rdt_send():
    data_read = file.read(MSS)
    if data_read:
        return data_read
    return None


# sends the segment to all of the hosts
# must receive all ACKs from servers for this segment until it can move to process the next segment
# need a way to handle the timeout of unacknowledged ACKs from the servers (signal?)
def send_segment(datagram):
    segment = None
    add_segment_header(segment)
    # send segments to all servers


    # receive ACKS from all servers
    # resend to the specific server not yet ACKed from if there is a timeout

    # once has received all ACKs, return

# add the segment header to the datagram
def add_segment_header(segment):
    # BitVector class to restrict bit number?
    # Need to calculate the checksum
    return None

UDP_IP = '127.0.0.1'

UDP_PORT = 7735

MSS = 100

sock = socket( socket.AF_INET, socket.SOCK_DGRAM)
sock.bind((UDP_IP, UDP_PORT))

file = open("myfile", "rb")

# open file for reading

buffer = bitstring.BitStream()
current_index = 0
segment_finished = False

while True:
    # calls rdt_send to obtain bytes from the file until reaching MSS
    file_data = rdt_send()
    # File is done reading data
    if file_data == None:
        break
    data = bitstring.BitStream()
    data.insert(file_data, 0)
    if( (data.bytes + buffer.bytes) == MSS ):
        segment_finished = True
        send_segment(buffer)
        segment_finished = False
        buffer = bitstring.BitStream()
    elif ( ( data.bytes + buffer.bytes ) > MSS):
        segment_finished = True
        temp = bitstring.BitStream()
        #slice the data array from beginning until number that equals MSS
        # grab this amount and append on to the buffer

        #set the buffer to the remaining data in temp


        send_segment(buffer)

        segment_finished = False

    else:
        buffer.append(temp)







