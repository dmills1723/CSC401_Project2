import subprocess
import socket
print( socket.gethostbyname(socket.gethostname()))
LISTENING_PORT = "10000"
PROB_LOSS = ".05"
run_num = 0
current_args = []
INITIAL_ARGS = [ "python3", "p2mpServer.py", LISTENING_PORT, PROB_LOSS ]
while True :
	file_name = "output" + str(run_num) + ".txt"
	run_num += 1
	current_args.clear()
	current_args = INITIAL_ARGS.copy()
	current_args.insert( 3, file_name )
	print( current_args )
	subprocess.run( current_args )
	print( "closed. running again" )
