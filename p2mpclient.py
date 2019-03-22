import socket
import bitstring
import signal
import sys
#import utils
# The P2MP must be invoked as the following:
# p2mpclient srever-1 server-2 server-3 server-port# file-name MSS

# obtains data from the file on a byte basis
def rdt_send():
    data_read = f.read(MSS)
    if data_read:
        return data_read
    return None


# Timeout handler for ACKs
def timeout_handler(signum, frame):
    for i in range(0, len(server_acks)):
        if server_acks[i] == False:
            print("Timeout, sequence number = ", str(segment_num))
            sock.sendto(file_data, servers[i])
            signal.alarm(5)



# signal handler for processing ACK timeouts
signal.signal(signal.SIGALRM, timeout_handler())

UDP_IP = '127.0.0.1'

UDP_PORT = 8888

# retrieve the port number from the system arguments
port_num = sys.argv[-3:-2]

# retrieve the filename from command line arguments
filename = sys.argv[-2:-1]

# retrieve the MSS from command line arguments
MSS = sys.argv[-1:]

# retrieve the server addresses from command line arguments
server_addrs = sys.argv[:-3]

# number of servers
num_servers = len(server_addrs)

# intialize the servers tuples
servers = []

# set each servers to its corresponding address and port number tuple
for i in num_servers:
    servers.append( (server_addrs[i], port_num))


# intialize the segment number to zero
segment_num = 0

# create a socket for udp connections
sock = socket.socket( socket.AF_INET, socket.SOCK_DGRAM)

# bind the socket to the ip address and port for this client
sock.bind((UDP_IP, UDP_PORT))

# open the file for reading
f = open(filename, "rb")

# intialize server ACKS
server_acks = [False]*num_servers

# intialize file data
file_data = None

# while they are still bytes to be read from the file
# continue to send segments to the servers
while True:

    # calls rdt_send to obtain bytes from the file until reaching MSS
    file_data = rdt_send()
    segment = utils.buildDataPacket( file_data, segment_num)

    # call function  to retrieve segment and pass in segment_number
    if file_data == None:
        break
    for server in servers:
        signal.alarm(5)

        sock.sendto( segment,  server )

    waiting_for_acks = True
    server_acks = [False]*num_servers

    # while the ACKs for each server are acknowledged
    while waiting_for_acks:
        # retrieve ACK message and address
        segment_ack, addr = sock.recvfrom(1024)

        # need method to process ACK packet

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

# has processed the entire file and sent all segments

# now send the FIN segment to all servers






