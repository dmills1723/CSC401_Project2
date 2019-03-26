import utils
import ref
from bitstring import BitArray as BA


bitstring_pl = BA( b'ABCDEFGHIJKLMNOPQRS' )
print( hex( utils.calcChecksum( bitstring_pl ) ))
print( hex( ref.ichecksum( 'ABCDEFGHIJKLMNOPQRS' )))

exit()

bitstring_pl = BA( b'ABCDEFGHIJKLMNOPQRS' )
seqnum = 255

print( "bitstring: %s\n" %bitstring_pl )
print( "seqnum   : %s\n" %seqnum )
print( "data head: 5555\n" )
checksum = utils.calcChecksum( bitstring_pl )
print( "checksum: %x\n" %checksum)
print( "\n\n" )
print( utils.buildDataPacket( bitstring_pl, seqnum ))
print( "\n\n" )
print( utils.buildDataPacket( bitstring_pl, seqnum ).bin )
print( "\n\n" )
print( utils.buildACKPacket( seqnum ) )
