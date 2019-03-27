import socket
import threading
import sys
import utils
import time

""""
Obtains the data from the file on a byte basis.
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
    # Timeout occurs out of sequence, ignore it
    if(index >= len(timer_threads)):
        return
    print("Timeout, sequence number = ", str(segment_num))

    time_thread = threading.Timer(TIMEOUT, timeout_handler, [server, segment, index])
    timer_threads[index] = time_thread
    sock.sendto(segment, server)
    time_thread.start()

# The timeout amount for each ACK
TIMEOUT = 0.05


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

# Opens the file to be sent for reading
f = open(filename, "rb")

# Flag that represents when the client has sent all of the data to the servers.
# Initalized to false.
finished = False


# While they are still bytes to be read in from the file
# continue to send the sequential segment  to all the servers.
# Follows the Stop-and-Wait ARQ scheme.
try:
    while True:

        # Obtains the MSS of read in bytes from the file
        file_data = rdt_send()

        # If there is no more data to be read from the file, the Client is done sending -> send them a FIN packet.
        if file_data is None:
            segment = utils.buildFINPacket()
            
        # Otherwise, builds the segment containing the file data to send to the Client
        else:
            segment = utils.buildDataPacket(file_data, segment_num)

        # Reinitializes the list of timer threads
        timer_threads.clear()

        # Sends the segment to each server
        for i in range(0, num_servers):
            sock.sendto( segment,  servers[i] )

            # Creates and starts a timer thread for each segment sent
            # The timer thread will execute the "timeout_handler" function with the list of passed in arguments
            # after the amount in TIMEOUT has occured from this thread starting
            timer = threading.Timer(TIMEOUT, timeout_handler, [servers[i], segment, i])
            timer_threads.append(timer)
            timer.start()

        # Initializes the list of acknowledged ACK packets to False
        server_acks = [False]*num_servers

        # Initalizes number of ACKs to 0
        num_acks = 0

        # Waits until obtains an ACK from each server for the
        # specific segment sequence number that was sent
        while True:
        
            # Retrieves the ACK message and address from the server
            data, addr = sock.recvfrom(1024)

            # Checks if packet is an ACK
            is_ACK = False
            
            # Checks if the server sent a FIN packet (acts as an acknowledgement to the client's sent FIN packet)
            if data[6:8] == b'\xff\xff':
                # Sets finished flag to True
                finished = True
                # Sets the segment number back to 0
                segment_num = 0
                seg_num = 0
                is_ACK = True
                
            # Otherwise, retrieves the current segment number from the first 32 bits of the header
            else:
                seg_num = int.from_bytes( data[:4], byteorder='big')
                
            # Makes sure this packet sent is an ACK packet
            if data[6:8] == b'UU':
                is_ACK = True
            
            # Ignores this packet if not the correct sequence number or not an ACK (or FIN)
            if seg_num == segment_num and is_ACK:  
                # Sets the retrieved ACK packets for the corresponding servers to True in the list of ACKs
                for i in range(0, num_servers):
                    if not server_acks[i] and servers[i][0] == addr[0]:
                        server_acks[i] = True
                        # increments the number of acks found
                        num_acks = num_acks + 1
                        # cancels the timer since packet has been acknowledged
                        timer_threads[i].cancel()

            # If all of the ACKs have been acknowledged for this segment,
            # proceeds to send the next segment to the servers
            if num_acks == num_servers:
                break
        # Client has finished sending all of the data from the file
        if finished:
            break
        # Increments the sequence number of the segments by 1
        segment_num = segment_num + 1

# If exception occurs print an error message and close all resources
# before exiting
except Exception as e:
    print("Exception occured!")
    f.close()
    sock.close()
    for thread in timer_threads:
        thread.cancel()
        thread.join()
    exit(1)

# Close all resources before exiting the program
f.close()
sock.close()
for thread in timer_threads:
    thread.cancel()
    thread.join()
print("Exiting normally")



