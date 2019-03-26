import sys
import socket
import numpy as np
from bitstring import BitArray
import utils


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
    sockIP = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sockIP.connect(("8.8.8.8", 80))

    # Gets this computer's IP address from the socket connection.
    ip_addr = sockIP.getsockname()[0]

    sockIP.close()
    return ip_addr


# Server port, file name to write, probability loss of packet
success, port, f, p = getArgs(sys.argv)

if success:
    SERVER_PORT = int(port)
    FILE_NAME = f
    P_LOSS = float(p)
else:
    sys.exit(1)

SERVER_IP = '127.0.0.1'

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind((SERVER_IP, SERVER_PORT))

print("socket success\n")

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

# has last Packet been sent
lastPacket = False

f = open(FILE_NAME, 'wb')

try:
    while True:
        data, addr = sock.recvfrom(1064) # buffer size is 1024 bytes
        print("Message:", data)

        # generate random number for packet loss
        rand = np.random.uniform(0, 1)
        bits = BitArray(bytes=data)
        seqnum = bits[:32]
        print("Sequence number: ", str(seqnum.int))
        #print(rand)
        if rand <= P_LOSS:
            print("Packet Loss, sequence number = ", str(seqnum.int))

        # continue if > p, otherwise drop packet
        if rand > P_LOSS:

            # stop-and-wait processing rules - get data
            #bits = BitArray(bytes=data)
            #bits.append(data)

            # compute checksum using utility function
            databits = bits[64:]
            checksum = utils.calcChecksum(databits)
            calccheck = BitArray(uint=checksum, length=16)
            #calccheck = BitArray(utils.calcChecksum(databits), 16)

            # check in-sequence
            #seqnum = bits[:32]
            if seqnum.int == (prevseqnum + 1):
                inseq = True
            else:
                inseq = False
            #print(inseq)
            # check checksum value
            checksum = bits[32:48]
            if checksum == calccheck:
                check = True
            else:
                check = False
            #print(check)

            # SUCCESS: if checksum correct and in-sequence, send ACK segment for packet to client (UDP)
            if inseq and check:
                # send ACK for packet
                ACK = utils.buildACKPacket(seqnum.int)
                sock.sendto(ACK.bytes, addr)
                prevACK = ACK
                prevseqnum = seqnum.int

                # then, write received data to file
                databits = bits[64:]
                print(databits.bytes)
                #BitArray(databits).tofile(f)
                print("Made it here.")
                f.write(databits.bytes)
                f.flush()
            # if checksum correct and out-of-sequence, send ACK for last received in-sequence packet to client (UDP)
            if not inseq and check:
                prevACK = utils.buildACKPacket(prevseqnum)
                sock.sendto(prevACK.bytes, addr)

        # if last packet is sent, exit
        if lastPacket:
            break
    f.flush()
    sock.close()
    f.close()
    print("Successfully exited program\n")
    sys.exit(0)

except KeyboardInterrupt:
    f.flush()
    sock.close()
    f.close()
    print("\nSuccessfully exited program\n")
    sys.exit(0)
