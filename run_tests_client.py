import time 
import os 
import sys
import subprocess

PORT_NUM = "10000"
FILE_TO_SEND = "big_file.txt"
NUM_SERVERS = len( sys.argv ) - 1

##################
##### Task 1 #####
##################

print( "----------- Starting Test 1 ---------------" )

TASK_1_MSS = "500"
servers = sys.argv[1:6]
INITIAL_ARGS = [ "python3", "p2mpclient.py" ]

current_args = []
for run in range( 5 ) :
    for num_servers_per_run in range( NUM_SERVERS ) :
        current_args.clear() 
        current_args += INITIAL_ARGS
        current_args += servers[0:num_servers_per_run + 1]
        current_args += [ PORT_NUM, FILE_TO_SEND, TASK_1_MSS ]
        print( current_args )
        start = time.time()
        subprocess.run( current_args )
        end = time.time()
        print( "TASK:1,RUN:%d,NUMSERVERS:%d,TIME:%f" %( run + 1, num_servers_per_run + 1, end - start ))
        input( "Press enter to run next test." )

##################
##### Task 2 #####
##################

mss = [ "100", "200", "300", "400", "500", "600", "700", "800", "900", "1000" ]
for run in range( 5 ) :
    for curr_mss in mss :
        current_args.clear() 
        current_args += INITIAL_ARGS
        current_args += servers[0:3]
        current_args += [ PORT_NUM, FILE_TO_SEND, curr_mss ]
        print( current_args )
        start = time.time()
        current_args.clear()
        current_args = [ "sleep", "1" ]
        subprocess.run( current_args )
        end = time.time()
        print( "TASK:2,RUN:%d,MSS:%s,TIME:%f" %( run + 1, curr_mss, end - start ))
