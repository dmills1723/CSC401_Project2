import socket
import bitstring
import signal

# The P2MP must be invoked as the following:
# p2mpclient srever-1 server-2 server-3 server-port# file-name MSS

# obtains data from the file on a byte basis
def rdt_send():
    data_read = f.read(MSS)
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

def timeout_handler(signum, frame):
    for i in range(0, len(server_acks)):
        if server_acks[i] == False:
            sock.sendto(file_data, servers[i])
            signal.alarm(5)



# signal handler for processing ACK timeouts
signal.signal(signal.SIGALRM, timeout_handler())

UDP_IP = '127.0.0.1'

UDP_PORT = 8888

MSS = 100

 # intialize to zero
segment_num = 0

# retrieve the filename from command line arguments
filename = 'RFCServer.py'

# process servers based on command line arguments
num_servers = 1

servers = []

servers.append( ('127.0.0.1', 7735) )

# create a socket for udp connections
sock = socket.socket( socket.AF_INET, socket.SOCK_DGRAM)

# bind the socket to the ip address and port for this client
sock.bind((UDP_IP, UDP_PORT))

# open the file for reading
f = open(filename, "rb")

# open file for reading

buffer = bitstring.BitArray()

server_acks = [False]*num_servers

file_data = None

while True:

    # calls rdt_send to obtain bytes from the file until reaching MSS
    file_data = rdt_send()

    # call function  to retrieve segment and pass in segment_number
    if file_data == None:
        break
    for server in servers:
        signal.alarm(5)
        sock.sendto( file_data,  server )

    waiting_for_acks = True
    server_acks = [False]*num_servers

    while waiting_for_acks:
        # retrieve ACK message and address
        segment_ack, addr = sock.recvfrom(1024)
        print(str(segment_ack.decode('ascii')))

        for i in num_servers:
            if num_servers[i][0] == addr:
                server_acks[i] = True
                break
        num_acks = 0
        for ack in server_acks:
            if ack:
                num_acks = num_acks + 1

        if num_acks == num_servers:
            break

    signal.alarm(0)
    segment_num = segment_num + 1





