import socket
import threading
import sys
import utils
import time

""""
Obtains the file data from the file on a byte basis.
Returns the next MSS amount of bytes from the file.
If the there is no data left to read in, returns None.
"""
def rdt_send():
    data_read = f.read(MSS)
    if data_read:
        return data_read
    return None


"""
Handles the timeouts for any acknowledged segments for a server.
Displays the sequence number of the timeout to the console.
Resends the segment to the server that timed out and restarts this timer.
"""
def timeout_handler(server, segment, index):
    if(index >= len(timer_threads)):
        return
    print("Timeout, sequence number = ", str(segment_num))

    time_thread = threading.Timer(TIMEOUT, timeout_handler, [server, segment, index])
    timer_threads[index] = time_thread
    sock.sendto(segment, server)
    time_thread.start()
# UDP IP address for this Client
#UDP_IP = '127.0.0.1'
UDP_IP = utils.getIPAddress()

# UDP Port for this Client
UDP_PORT = 8888

# The timeout amount for each ACK
TIMEOUT = 0.1

lock1 = threading.Lock()

lock2 = threading.Lock()

# Ensures that the correct command line arguments are entered by the user.
# Displays an usage message and exits if incorrect.
if len(sys.argv) < 5:
    print("Usage: python p2mpclient.py <server1> <server2> <..serverX..> <port num> <filename> <MSS>")
    print("( Must contain at least one server to run but there is no limit on the number of servers )")
    exit(1)

# The port number for the servers
port_num = int(sys.argv[-3:-2][0])

# The filename to be sent to the servers
filename = str(sys.argv[-2:-1][0])

# The MSS for the file's bytes to be sent on each segment
MSS = int(sys.argv[-1:][0])

# The IP addresses for all of the servers
server_addrs = sys.argv[1:-3]

# The number of servers to send this file to
num_servers = len(server_addrs)

# The list of server addresses
servers = []

# The list of timer threads
timer_threads = []

# Sets each server to its corresponding IP address and port number
for i in range(0, num_servers):
    servers.append( (server_addrs[i], port_num))


# Initializes the starting segment number to 0
segment_num = 0

# Opens a socket for the UDP connections
sock = socket.socket( socket.AF_INET, socket.SOCK_DGRAM)

# Binds this socket to Client's IP address and port number
sock.bind((UDP_IP, UDP_PORT))

# Opens the file to be sent for reading
f = open(filename, "rb")

finished = False

#lock = threading.Lock()
# While they are still bytes to be read in from the file
# continue to send the sequential segment  to all the servers.
# Follows the Stop-and-Wait ARQ scheme.
start = time.time()
try:
    while True:

        # Obtains the MSS of read in bytes from the file
        file_data = rdt_send()

        # If there is no more data to be read from the file, the Client is done sending, send FIN packet
        if file_data is None:
            segment = utils.buildFINPacket()
        # Builds the segment to send
        else:
            segment = utils.buildDataPacket(file_data, segment_num)


        # Reinitializes the timer threads
        timer_threads.clear()

        # Sends the segment to each server
        for i in range(0, num_servers):
            sock.sendto( segment,  servers[i] )

            # Creates and starts a timer for each segment sent
            timer = threading.Timer(TIMEOUT, timeout_handler, [servers[i], segment, i])
            timer_threads.append(timer)
            timer.start()

        # Initializes to True
        waiting_for_acks = True

        # Initializes the list of acknowledged ACK packets to False
        server_acks = [False]*num_servers

        # Initalizes number of ACKs to 0
        num_acks = 0

        # Waits until obtains an ACK from each server for the
        # specific segment sequence number that was sent
        while waiting_for_acks:
            # Retrieves the ACK message and address from the server
            data, addr = sock.recvfrom(1024)

            # need method to process ACK packet
            # check that this segment is ACK packet and contains correct sequence num
            # otherwise ignore this segment
            #seqnum = None
            if data[6:8] == b'\xff\xff':
                finished = True
                seg_num = segment_num
            else:
                seg_num = int.from_bytes( data[:4], byteorder='big')

            if seg_num == segment_num:
                # Sets the retrieved ACK packets for the corresponding servers to True
                for i in range(0, num_servers):
                    if not server_acks[i] and servers[i][0] == addr[0]:
                        server_acks[i] = True
                        num_acks = num_acks + 1
                        timer_threads[i].cancel()

            # If all of the ACKs have been acknowledged for this segment,
            # proceeds to send the next segment to the servers
            if num_acks == num_servers:
                break
        if finished:
            break
        # Increments the sequence number of the segments by 1
        segment_num = segment_num + 1

except Exception as e:
    print("Exception occured!")
    print( e )
    f.close()
    sock.close()
    for thread in timer_threads:
        thread.cancel()
        thread.join()
    exit(1)

# has processed the entire file and sent all segments

# now send the FIN segment to all servers
end = time.time()
print(end - start)
f.close()
sock.close()
for thread in timer_threads:
    thread.cancel()
    thread.join()
print("Exiting normally")




