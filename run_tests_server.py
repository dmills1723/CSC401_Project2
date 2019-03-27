import subprocess
run_num = 0
current_args = []
INITIAL_ARGS = [ "python3", "p2mpServer.py", "10000", "0" ]
while True :
	file_name = "textbook_run" + str(run_num) + ".txt"
	run_num += 1
	current_args.clear()
	current_args = INITIAL_ARGS.copy()
	current_args.insert( 3, file_name )
	print( current_args )
	subprocess.run( current_args )
	print( "closed. running again" )
