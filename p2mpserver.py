'''
    @file: p2mpserver.py
    
    This script implements the server part of the system. A user specifies
    the port the server listens on, the filename to write a received file to,
    and probabilistic loss value between 0 and 1. Once a file has been
    received and written, the program will exit.
    
    USAGE:   python3 p2mpserver.py <port_num> <filename> <loss_probability>
    EXAMPLE: python3 p2mpserver.py 7735 output.txt .05
'''

import sys
import socket
import numpy as np
import utils

# Gets command line arguments
def getArgs(args):

    if len(args) != 4:
        print("Usage: python3 p2mpserver.py <port_num> <filename> <loss_probability>")
        exit()

    portNum = args[1]
    fileName = args[2]
    pLoss = args[3]

    return True, portNum, fileName, pLoss

# Server port, file name to write, probability loss of packet
success, port, filename, p = getArgs(sys.argv)

# If correct number of command line arguments
# Assign them to their corresponding values
if success:
    SERVER_PORT = int(port)
    FILE_NAME = filename
    P_LOSS = float(p)
else:
    sys.exit(1)

# Creates the UDP socket and binds to the passed in port number
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind(('', SERVER_PORT))

print( "Server is Running." )
print( "Listening at %s:%d\n" %(socket.gethostbyname(socket.gethostname()), SERVER_PORT ) )

# is packet in-sequence
inseq = False

# is checksum correct
check = False

# prev seq num, initialized to -1 bc seq nums start from 0
prevseqnum = -1

# seq num in header of packet
seqnum = 0

# checksum in header of packet
checksum = 0

# calculated seq num of packet
calccheck = 0

# if correct checksum, ACK to send for received packet
ACK = None

# if incorrect checksum, ACK for last received in-sequence packet
prevACK = None

# open file for writing
f = open(FILE_NAME, 'wb')

# Retrieve segments from the "sender" until the FIN packet has been sent (representing the entire file has been sent )
try:
    while True:
        data, addr = sock.recvfrom(1064) # buffer size is 1064 bytes

        # check in-sequence
        seqnum = int.from_bytes(data[:4], byteorder='big')

        # generate random number for packet loss
        rand = np.random.uniform(0, 1)

        # if the random number is less than equal to probablity loss
        # drop the packet and display the packet loss message
        if rand <= P_LOSS:
            print('Packet loss, sequence number = ', str(seqnum) )

        # continue if > p, otherwise drop packet
        if rand > P_LOSS:
            if data[6:8] == b'\xff\xff':
                FIN = utils.buildFINPacket()
                sock.sendto(FIN, addr)
                break

            # compute checksum using utility function
            databits = data[8:]
            calccheck = utils.calcChecksum(databits)
    
            # checks if insequence and sets the boolean flag accordingly
            if seqnum == (prevseqnum + 1):
                inseq = True
            else:
                inseq = False

            # check checksum value
            checksum = int.from_bytes( data[4:6], byteorder='big' )
            
            # compare checksum vs calculated checksum value
            # set the boolean flag to whether or not they are equal
            if checksum == calccheck:
                check = True
            else:
                check = False

            # SUCCESS: if checksum correct and in-sequence, send ACK segment for packet to client (UDP)
            if inseq and check:
                # send ACK for packet
                ACK = utils.buildACKPacket(seqnum)
                sock.sendto(ACK, addr)
                prevACK = ACK
                prevseqnum = seqnum
                f.write(data[8:])
                f.flush()

            # if checksum correct and out-of-sequence, send ACK for last received in-sequence packet to client (UDP)
            if not inseq and check:
                prevACK = utils.buildACKPacket(prevseqnum)
                sock.sendto(prevACK, addr)

    # File has finished downloaded
    print('File has finished downloading.')
    
    # Close all resources and exit the program
    sock.close()
    f.flush()
    f.close()
    print("Successfully exited program\n")
    
# Keyboard Interrupt Exception occured.
# Close all resources and exit the program
except KeyboardInterrupt:
    sock.close()
    f.flush()
    f.close()
    print("\nSuccessfully exited program\n")
    sys.exit(0)
