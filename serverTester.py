import socket

SERVER_IP = '127.0.0.1'

SERVER_PORT = 7735

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind((SERVER_IP, SERVER_PORT))

while True:
    data, addr = sock.recvfrom(1064)  # buffer size is 1024 bytes

    print("Message:", str(data))
    if data == '':
        break

    response_bytes = "ACK".encode('ascii')
    sock.sendto(response_bytes, addr)

print("Done")
