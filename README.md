# CSC401_Project2 #

## Prerequisites ##

Install Python version 3.5 for this project

Run this program on an Ubuntu 16.04 system

Input this command into a terminal window to install the _numpy_ library:
```
sudo apt-get install python3-numpy
```

## Run Program ##

To run this program:

  1) In order to run the P2MP Server, the receiver of the file, open a terminal window and input
```
python3 p2mpserver.py <port#> <filename> <p>
```
  The port# is the port this udp connection is listening on.
  The filename is name of the file that is to be downloaded from the client "sender".
  The variable "p" is the packet probablity loss. Must be a decimal number between 0.0 and 1.0.
  
  2) Repeat this step to add more Servers to this program.

  3) In order to run the P2MP Client, the sender of the file, open a terminal window and input
  
```
python3 p2mpclient.py <server1> <server2> <..serverX..> <port#> <filename> <MSS>
```
  The "servers" are the IP addresses of each of the connected servers (in step 1) that the file will be sent to.
  There must be atleast one server given as a command line argument. 
  There is no limit on the amount of servers that can be passed in as command line arguments.
  
  The port# is the port this udp connection is listening on.
  
  The filename is the full path of the file that is to be transferred from this Client to the connected Servers.
  
  The MSS is the maximum amount of bytes from the transferred file to be sent with each segment.
  
