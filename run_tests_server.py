import subprocess
import socket
print( socket.gethostbyname(socket.gethostname()))
LISTENING_PORT = "10000"
PROB_LOSS =  [".01", ".02", ".03", ".04", ".05", ".06", ".07", ".08", ".09", ".10" ]
run_num = 0
current_args = []
INITIAL_ARGS = []
for curr_prob_loss in PROB_LOSS :
    for run in range(3) :
        INITIAL_ARGS.clear() 
        INITIAL_ARGS = [ "python3", "p2mpServer.py", LISTENING_PORT, curr_prob_loss ]
        file_name = "output" + str(run_num + 1) + ".txt"
        run_num += 1

        current_args.clear()
        current_args = INITIAL_ARGS.copy()
        current_args.insert( 3, file_name )
        subprocess.run( current_args )
        print( "closed. running again" )
