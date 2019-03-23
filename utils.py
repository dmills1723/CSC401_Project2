import bitstring
from bitstring import BitArray

# The constant "1010101010101010" used as a header indicating the packet is an ACK.
ACK_PACKET_HEADER = 0xAAAA

# Number of bits in a byte.
BYTE_SIZE = 8

# The constant "0101010101010101" used as a header indicating the packet contains data.
DATA_PACKET_HEADER = 0x5555

# Number of bits in a word.
WORD_SIZE = 16

# Constant value that serves as a placeholder header so ACKs and data packets have
# the same structure. Takes the place of the checksum in the data packet structure.
ZERO_WORD = 0x0000

''' 
    Adds two 16-bit words. If there was an overflow, 1 is added
    to the result. 

    Note that is treating the result of the addition as a 16-bit 
    result with overflow, but in fact, python automatically 
    increases the size of an integer if there is an overflow.
'''
def carryAroundAdd( wordA, wordB ) :
    result = wordA + wordB

    # If there was an overflow this will be 1.
    overflow = result >> 16

    # Returns right-most 16-bits of result plus the overflow bit.
    return ( result & 0xFFFF ) + overflow

# NOTE: This could be optimized with the multiprocessing.Pool.map() function.
''' 
    Calculates the "internet checksum" as specified in RFC 1071. 
    The 3rd 16-bit word of the message is the "checksum", and it is
    ignored in the calculation.

    @param message a bitarray of a packet
'''
def calcChecksum( message ) :
    # Zeroes out the checksum to "0x0000".
    checksum = ZERO_WORD

    # If the message is not a multiple of 16 bits, its last 'word' is only 
    # a single byte, so zeroes are appended to make it a full 16-bit word.
    bitsLastWord = len( message ) % WORD_SIZE
    if ( bitsLastWord == 8 ) :
        message.insert( '0x00', len( message ) - BYTE_SIZE + 1 )

    # If the last 'word' isn't a word (16 bits) or a 
    # half-word (8 bits), something went wrong.
    elif ( bitsLastWord != 0 ) :
        print( "\nThis should never happen!\n" )
        exit()

    # Number of 16-bit words in the message, excluding the checksum header.
    numWords = int( ( len( message ) / WORD_SIZE ))
    
    # Index in bitarray of start of current word.
    startBit = 0

    # Iterates through all 16-bit words, adding each to the current sum.
    for i in range( numWords) :
        # Index in bitarray of end of current word.
        endBit = startBit + WORD_SIZE 

        # Converts the binary word to an integer.
        intValueOfWord = int( message.bin[ startBit:endBit ], 2 )
        checksum = carryAroundAdd( checksum, intValueOfWord )

        # Increments startBit by WORD_SIZE.
        startBit = endBit
   
    checksum = ~checksum
    return checksum & 0xFFFF

''' 
    Given the sequence number of a received data packet, 
    constructs an ACK packet and returns it.

    @param  seqNum: 32-bit sequence number 
    @return ACK packet as a bitarray
'''
def buildDataPacket( payload, seqNum ) :
    
    # Converts the sequence number to a 32-bit bitarray.
    seqNumBits = BitArray( uint=seqNum, length=32 )

    # Calculates the checksum and converts it to a 16-bit bitarray.
    checksum = calcChecksum( payload )
    checksumBits = BitArray( uint=checksum, length=16 ) 
    
    # Converts the DATA_PACKET_HEADER to a 16-bit bitarray.
    dataPacketBits = BitArray( uint=DATA_PACKET_HEADER, length=16 )

    # Builds the packet from its component headers and payload.
    seqNumBits.append( checksumBits )
    seqNumBits.append( dataPacketBits )
    seqNumBits.append( payload )

    return seqNumBits 

''' 
    Given the sequence number of a received data packet, 
    constructs an ACK packet and returns it.

    @param  seqNum: 32-bit sequence number 
    @return ACK packet as a bitarray
'''
def buildACKPacket( seqNum ) :

    # Converts the sequence number to a 32-bit bitarray.
    seqNumBits = BitArray( uint=seqNum, length=32 )

    # Converts ZERO_BITS (0x0000) to a bitarray
    zeroBits = BitArray( uint=ZERO_WORD, length=16 )

    # Converts the ACK_PACKET_HEADER to a 16-bit bitarray.
    ackPacketBits = BitArray( uint=ACK_PACKET_HEADER, length=16 )

    
    # Builds the packet from its component headers and payload.
    seqNumBits.append( zeroBits )
    seqNumBits.append( ackPacketBits )

    return seqNumBits
