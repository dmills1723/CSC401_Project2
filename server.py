import sys
import socket


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
    SERVER_PORT = port
    FILE_NAME = file
    P_LOSS = p
else:
    sys.exit(1)

SERVER_IP = getIPAddress()

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind((SERVER_IP, SERVER_PORT))

while True:
    data, addr = sock.recvfrom(1024)  # buffer size is 1024 bytes
    print("Message:", data)

    # compute checksum

    # check if in-sequence

    # if checksum incorrect, do nothing

    # if checksum correct and in-sequence, send ACK segment for packet to client (UDP)
    # then, write received data to file

    # if checksum correct and out-of-sequence, send ACK for last received in-sequence packet to client (UDP)
