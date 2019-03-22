import sys
import socket
import random
from bitstring import BitArray, BitStream


def getArgs(args):

    if len(args) != 4:
        print("Usage: python3 p2mpserver.py <Port Name> <File Name> <Packet Loss Probability (0-1)>")
        return False

    portNum = args[1]
    fileName = args[2]
    pLoss = args[3]

    return True, portNum, fileName, pLoss


def getIPAddress():
    # Creates socket to Google's nameserver.
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.connect(("8.8.8.8", 80))

    # Gets this computer's IP address from the socket connection.
    ip_addr = sock.getsockname()[0]

    sock.close()
    return ip_addr


# Server port, file name to write, probability loss of packet
success, port, file, p = getArgs(sys.argv)

if success:
    SERVER_PORT = int(port)
    FILE_NAME = file
    P_LOSS = float(p)
else:
    sys.exit(1)

SERVER_IP = getIPAddress()

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind((SERVER_IP, SERVER_PORT))

print("socket success\n")

inseq = False
check = False
prevseqnum = -1
seqnum = 0
checksum = 0
headercheck = 0
ACK = None
lastACK = None

while True:
    data, addr = sock.recvfrom(1024)  # buffer size is 1024 bytes
    print("Message:", data)

    # generate random number for packet loss
    rand = random.uniform(0, 1)

    # continue if > p, otherwise drop packet
    if rand > p:

        # stop-and-wait processing rules - get data
        bits = BitArray(data)

        # compute checksum using utility function
        headercheck = 0

        # check in-sequence
        seqnum = bits[:32]
        if seqnum == (prevseqnum + 1):
            inseq = True
        else:
            inseq = False

        prevseqnum = seqnum

        # check checksum value
        checksum = bits[32:48]
        if checksum == headercheck:
            check = True
        else:
            check = False

        # if checksum correct and in-sequence, send ACK segment for packet to client (UDP)
        if inseq and check:
            # send ACK for packet
            # sock.sendto(MESSAGE, (UDP_IP, UDP_PORT))
            # then, write received data to file
            file = open(file, 'wb')
            databits = bits[64:]
            BitArray(databits).tofile(file)
            file.close()

        # if checksum correct and out-of-sequence, send ACK for last received in-sequence packet to client (UDP)
        if not inseq and check:
            # sock.sendto(MESSAGE, (UDP_IP, UDP_PORT))