import bitstring
import sys
import time
from bitstring import BitArray

# The constant "1010101010101010" used as a header indicating the packet is an ACK.
ACK_PACKET_HEADER = 0xAAAA

# The constant "0101010101010101" used as a header indicating the packet contains data.
DATA_PACKET_HEADER = 0x5555

# The constant "1111111111111111" used as a header indicating the packet is a FIN.
ONES_WORD = 0xFFFF

# Number of bits in a byte.
BYTE_SIZE = 8

# Number of bits in a word.
WORD_SIZE = 16

# Constant value that serves as a placeholder header so ACK and data packets have
# the same structure. Takes the place of the checksum in the data packet structure.
ZERO_WORD = 0x0000

''' 
    Adds two 16-bit words. If there was an overflow, 1 is added
    to the result. 

    Note that the result of the addition is treated as a 16-bit 
    result with overflow, but in fact, python automatically 
    increases the size of an integer type if there is an overflow.

    @param wordA: 16-bit word summand 
    @param wordB: 16-bit word summand
    @return 16-bit sum as an integer
'''
def carryAroundAdd( wordA, wordB ) :
    result = wordA + wordB

    # If there was an overflow, this will be 1.
    overflow = result >> 16

    # Returns right-most 16-bits of result plus the overflow bit.
    return ( result & 0xFFFF ) + overflow

# NOTE: This could be optimized with the multiprocessing.Pool.map() function.
''' 
    Iterates through the paylod of a packet by 16-bit words and calculates 
    the "internet checksum" as specified in RFC 1071. 

    @param  message: A bitarray of a packet
    @return 16-bit checksum as an integer
'''
def calcChecksum( message ) :
    start = time.time()
    # Zeroes out the checksum to "0x0000".
    checksum = ZERO_WORD

    # If the message is not a multiple of 16 bits, its last 'word' is only 
    # a single byte, so zeroes are appended to make it a full 16-bit word.
    bitsLastWord = len( message ) % WORD_SIZE
    length = time.time()
    if ( bitsLastWord == 8 ) :
        message.insert( '0x00', len( message ) - BYTE_SIZE + 1 )


    # If the last 'word' isn't a word (16 bits) or a 
    # half-word (8 bits), something went wrong.
    elif ( bitsLastWord != 0 ) :
        print( "\nThis should never happen!\n" )
        exit(1)

    # Number of 16-bit words in the message, excluding the checksum header.
    numWords = int(( len( message ) / WORD_SIZE ))
    
    length_div = time.time()

    # Index in bitarray of start of current word.
    startBit = 0

    # Iterates through all 16-bit words, adding each to the current sum.
#    for i in range( numWords) :
    for word in message.cut(16) :
        # Index in bitarray of end of current word.
        #endBit = startBit + WORD_SIZE 

        # Converts the binary word to an integer.
        startA = time.time()

        #intValueOfWord = int( message.bin[ startBit:endBit ], 2 )
        endA = time.time()

        #checksum = carryAroundAdd( checksum, intValueOfWord )
        checksum = carryAroundAdd( checksum, word.int)

        endB = time.time()

        #print( "convert %f:  " %(endA - startA) , file=sys.stdout)
        #print( "add %f:   " %(endB- endA) , file=sys.stdout)

        # Increments startBit by WORD_SIZE.
        #startBit = endBit
   
    checksum = ~checksum
    return checksum & 0xFFFF
'''
    print( "length %f:   \n" %(length - start) , file=sys.stdout)
    print( "insert %f:   \n" %(insert - start) , file=sys.stdout)
    print( "length_div %f:   \n" %(length_div - start) , file=sys.stdout)
    print( "loop %f:   \n" %(loop - start) , file=sys.stdout)
    print( "convert %f:   \n" %(endA - startA) , file=sys.stdout)
    print( "add %f:   \n" %(endB- endA) , file=sys.stdout)
'''
 

''' 
    Given the sequence number of a received data packet, 
    constructs an ACK packet and returns it.

    @param  seqNum: 32-bit sequence number 
    @return ACK packet as a BitArray
'''
def buildDataPacket( payload, seqNum ) :
    one = time.time()
    
    # Converts the sequence number to a 32-bit bitarray.
    seqNumBits = BitArray( uint=seqNum, length=32 )

    two = time.time()

    # Calculates the checksum and converts it to a 16-bit bitarray.
    checksum = calcChecksum( payload )

    three = time.time()

    checksumBits = BitArray( uint=checksum, length=16 ) 

    four = time.time()
    
    # Converts the DATA_PACKET_HEADER to a 16-bit bitarray.
    dataPacketBits = BitArray( uint=DATA_PACKET_HEADER, length=16 )

    five = time.time()

    # Builds the packet from its component headers and payload.
    seqNumBits.append( checksumBits )

    six = time.time()

    seqNumBits.append( dataPacketBits )

    seven = time.time()

    seqNumBits.append( payload )

    eight = time.time()
    #print( seqNumBits )

    return seqNumBits 
'''
    print( "two %f:   \n" %(two - one) , file=sys.stdout)
    print( "three %f: \n" %(three - one) , file=sys.stdout) 
    print( "four %f:  \n" %(four - one) , file=sys.stdout)
    print( "five %f:  \n" %(five - one) , file=sys.stdout)
    print( "six %f:   \n" %(six - one) , file=sys.stdout)
    print( "seven %f: \n" %(seven - one) , file=sys.stdout)
    print( "eight %f: \n" %(eight - one) , file=sys.stdout)
'''


''' 
    Given the sequence number of a received data packet, 
    constructs an ACK packet and returns it.

    @param  seqNum: 32-bit sequence number 
    @return ACK packet as a BitArray
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

'''
    Builds and returns a FIN packet used by the client to indicate no more
    data packets will be sent.
    
    Format is: 00000000
               0000FFFF

    @return FIN packet as a BitArray
'''
def buildFINPacket() :
    
    # Creates a BitArray of 48 leading zeroes, as placeholders for the
    # sequence number and checksum fields (FIN packet doesn't need them).
    FINPacket = BitArray( uint=0, length=48 )

    # Appends 16 ones 
    zeroBits = BitArray( uint=1, length=16 )
    FINPacket.append( zeroBits )

    return FINPacket
