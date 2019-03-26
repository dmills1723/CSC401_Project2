import sys
import socket
import numpy as np
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
success, port, filename, p = getArgs(sys.argv)

if success:
    SERVER_PORT = int(port)
    FILE_NAME = filename
    P_LOSS = float(p)
else:
    sys.exit(1)

#SERVER_IP = getIPAddress()
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
        #print("Message:", data)

        # generate random number for packet loss
        rand = np.random.uniform(0, 1)
        #print(rand)

        # continue if > p, otherwise drop packet
        if rand > P_LOSS:

            # compute checksum using utility function
            databits = data[8:]

            finalcheck = databits[6:]
            if finalcheck == 0:
                print('FIN packet received')
                break

            calccheck = utils.calcChecksum(databits)

            # check in-sequence
            seqnum = int.from_bytes( data[:4], byteorder='big')
            if seqnum == (prevseqnum + 1):
                inseq = True
            else:
                inseq = False

            # check checksum value
            checksum = int.from_bytes( data[4:6], byteorder='big' )
            # print( checksum )
            # print( calccheck )
            if checksum == calccheck:
                check = True
            else:
                check = False

            # print( "check %s" %check )
            # SUCCESS: if checksum correct and in-sequence, send ACK segment for packet to client (UDP)
            if inseq and check:
                # send ACK for packet
                ACK = utils.buildACKPacket(seqnum)
                sock.sendto(ACK, addr)
                prevACK = ACK
                prevseqnum = seqnum
                f.write(data[8:])

            # if checksum correct and out-of-sequence, send ACK for last received in-sequence packet to client (UDP)
            if not inseq and check:
                prevACK = utils.buildACKPacket(prevseqnum)
                sock.sendto(prevACK.bytes, addr)

        else:
            seqnum = int.from_bytes( data[:4], byteorder='big')
            print("Timeout, sequence number = ", str(seqnum))

    sock.close()
    f.close()
    print("Successfully exited program\n")
    sys.exit(0)

except KeyboardInterrupt:
    sock.close()
    f.close()
    print("\nSuccessfully exited program\n")
    sys.exit(0)
