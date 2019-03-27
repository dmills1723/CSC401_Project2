import socket

# The constant "1010101010101010" used as a header indicating the packet is an ACK.
ACK_PACKET_BYTES = (0xAAAA).to_bytes(2, byteorder='big')

# The constant "0101010101010101" used as a header indicating the packet contains data.
DATA_PACKET_BYTES = (0x5555).to_bytes(2, byteorder='big')

# A FIN packet. 48 zeroes followed by 16 ones. "000000000000FFFF" in hex.
FIN_PACKET = (0xFFFF).to_bytes( 8, byteorder='big' )

# Constant value that serves as a placeholder header so ACK and data packets have
# the same structure. Takes the place of the checksum in the data packet structure.
ZERO_BYTES = (0).to_bytes(2, byteorder='big')

''' 
    Iterates through the paylod of a packet by 16-bit words and calculates 
    the "internet checksum" as specified in RFC 1071. 

    @param  message: payload of packet as a "bytes" object
    @return 16-bit checksum as an integer
'''
def calcChecksum( message ) :

    # Zeroes out the checksum to "0x0000".
    checksum = 0 

    # Number of bytes in message.
    msg_len = len( message )

    # This is 1 (true) if the message has an odd number of bytes.
    is_odd_length = msg_len % 2
        
    # Skips last 1 or 2 bytes depending on if msg_len is odd or even.
    two_less = msg_len - 2

    # Iterates through all 16-bit words, adding each to the current sum.
    for i in range( 0, two_less , 2) :
        intValueOfWord = ( message[ i ] << 8 ) + message[ i + 1 ]
        result = checksum + intValueOfWord
        checksum = ( result & 0xFFFF ) + ( result >> 16 )

    # If the message has an odd number of bytes, the last byte is padded
    # with 8 zeroes and added as the resultant 16-bit word to the checksum.
    if ( is_odd_length ) :
        intValueOfWord = message[ msg_len - 1]
        result = checksum + intValueOfWord
        checksum = ( result & 0xFFFF ) + ( result >> 16 )
        
    # If the message has an even number of bytes, the last two bytes are added normally.
    else :
        intValueOfWord = ( message[ msg_len - 2] << 8 ) + message[ msg_len - 1]
        result = checksum + intValueOfWord
        checksum = ( result & 0xFFFF ) + ( result >> 16 )

    return ~checksum & 0xFFFF

''' 
    Given the sequence number of a received data packet, 
    constructs an ACK packet and returns it.

    @param  seqNum: integer sequence number 
    @return ACK packet as a "bytes" object
'''
def buildDataPacket( payload, seqNum ) :
    
    # Turns the sequence number into a 4-byte representation.
    seqNumBytes = seqNum.to_bytes(4, byteorder='big')

    # Calculates the checksum, then converts it to a 2-byte representation.
    checksum = calcChecksum( payload )
    checksumBytes = checksum.to_bytes(2, byteorder='big')

    return b''.join((seqNumBytes, checksumBytes, DATA_PACKET_BYTES, payload))

''' 
    Given the sequence number of a received data packet, 
    constructs an ACK packet and returns it.

    Format is: [SEQNUM]
               0000AAAA

    @param  seqNum: 32-bit sequence number 
    @return ACK packet as a "bytes" object.
'''
def buildACKPacket( seqNum ) :

    seqNumBytes = seqNum.to_bytes(4, byteorder='big')
    return b''.join((seqNumBytes, ZERO_BYTES, ACK_PACKET_BYTES))

'''
    Returns a FIN packet used by the client to indicate no more
    data packets will be sent.
    
    Format is: 00000000
               0000FFFF

    @return FIN packet as a "bytes" object
'''
def buildFINPacket() :
    return FIN_PACKET

'''
    Returns this host's IP address.
'''
def getIPAddress():
    # Creates socket to Google's nameserver.
    sockIP = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sockIP.connect(("8.8.8.8", 80))

    # Gets this computer's IP address from the socket connection.
    ip_addr = sockIP.getsockname()[0]

    sockIP.close()
    return ip_addr

