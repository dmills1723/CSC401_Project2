'''
    file:   RFCServer.py
    author: Daniel Mills (demills)

    Implementation of a multithreaded server that provides two services.
       1) RFCQuery : A peer requests this peer's current RFC index.
       2) GetRFC   : A peer requests to download a specific RFC document from this peer.
    The RFCServer should be instantiated by this host's client before a this host 
    registers with the RegistrationServer.
'''

import socket
import threading
import time
import signal, os
import ProtocolTranslator as PT
import PeerUtils as PU

'''
    Class for threads spawned by the server to handle a single request
    and response with a peer.
'''
class PeerThread(threading.Thread):

    '''
        Initializes a PeerThread: 
            - Calls Thread's init method.
            - Instantiates instance variables:
                ip_addr    : Peer's IP address. 
                socket     : Socket opened for handling a single peer.
                port       : Peer's port bound to socket.
                rfc_index  : Recently updated copy of the rfc_index.
                index_lock : Mutex for accessing the rfc_index.
    '''
    def __init__(self, ip_addr, port, socket, rfc_index, rfc_index_lock ):
        threading.Thread.__init__(self)
        self.ip_addr = ip_addr
        self.port = port
        self.socket = socket
        self.rfc_index = rfc_index
        self.index_lock = rfc_index_lock

    '''
        Returns whether this host has an RFC file locally.
    '''
    def hasLocalRFC(self, rfc_num):
        rfc_path = os.path.join(os.path.curdir, "RFCs", "rfc%s.txt" % rfc_num)
        return os.path.isfile(rfc_path)

    '''
        Method executed by a call to PeerThread.start(). A TCP socket has 
        already been opened with the peer. The peer's request on this socket 
        is received and processed. 
    '''
    def run(self):
        request_bytes = self.socket.recv(1024)

        # convert the request in bytes to string
        request = str(request_bytes.decode('ascii'))

        # obtains the method of this protocol
        method = request.splitlines()[0]

        # Returns the current RFC index.
        if method == "RFCQuery":
            # Acquire lock on rfc_index
            self.index_lock.acquire()

            # Check that the RFC index is non-empty. 
            # This is passed to ProtocolTranslator.rfcQueryResponseToProtocol
            nonEmptyIndex = (self.rfc_index.size() > 0)

            print( self.rfc_index )
            # Updates locally stored RFCs TTLs to 7200 plus current time.
            self.rfc_index.update_ttls_for_rfcquery()

            # sends back a response message with the cookie
            response = PT.rfcQueryResponseToProtocol(nonEmptyIndex, str( self.rfc_index ))

            # Releases mutex lock on the RFC index.
            self.index_lock.release()

        # Returns the specified RFC, if it exists locally.
        elif method == "GetRFC":
            rfc_num = PT.getRfcQueryToElements(request)

            # Checks if local file for RFC exists. Passes this to ProtocolTranslator below.
            has_file = self.hasLocalRFC(rfc_num)

            response = PT.rfcQueryResponseToProtocol( has_file, PU.getRFCFileText( rfc_num ) )

        # Returns a "BAD REQUEST" response, since the request didn't 
        # match the expected "GetRFC" or "RFCQuery".
        else:
            response = PT.genericBadRequestResponseToProtocol()

        # translates the response protocol into bytes
        response_bytes = response.encode('ascii')

        # sends the response to the peer client
        self.socket.send(response_bytes)


        # Closes the socket connection with the peer.
        self.socket.close()

'''
    A server for handling incoming peers making RFCQuery and GetRFC requests.
'''
class RFCServer():
    '''
        Initializes the RFCServer:
            - Creates and binds a socket to listen for incoming peers.
            - Sends the client the port chosen to listen on.
            - Instantiates instance variables:
                rfc_index: Initial RFCIndex passed from ClientPeer.
                serv_sock: Socket the server listens for peers on.
                serv_pipe: Pipe for communication with ClientPeer.
                serv_port: Port number the server is listening on.
        Then, starts the main server function "runServer()". The server will
        remain in this function until PeerClient sends a SIGTERM from PeerClient.

    '''
    def __init__(self, serv_pipe, rfc_index):
        # Initializes the RFC index.
        self.rfc_index = rfc_index

        # Creates socket to listen for incoming peers on.
        self.serv_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.serv_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)


        # Gets this computer's IP address which the socket will listen on.
        ip_addr = self.getIPAddress()

        # Binds socket to a random, available port.
        self.serv_sock.bind((ip_addr, 0))

        # Gets the port number "serv_sock" is bound to ...
        self.serv_port = self.serv_sock.getsockname()[1]

        # ... and sends it back to the Client.
        self.serv_pipe = serv_pipe
        self.serv_pipe.send(self.serv_port)

    '''
        Returns this computer's IP address. 
    '''

    def getIPAddress(self):
        # Creates socket to Google's nameserver.
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.connect(("8.8.8.8", 80))

        # Gets this computer's IP address from the socket connection.
        ip_addr = sock.getsockname()[0]

        sock.close()
        return ip_addr

    '''
        Joins threads opened in run() and closes the server's socket.
    '''
    def cleanup(self, worker_threads):
        self.serv_sock.close()
        for thread in worker_threads:
            thread.join()
        print("finished cleanup. exiting....")

    '''
        Main thread for running the server. Within an infinite while-loop,
        incoming peers are listened for and passed off to a PeerThread upon
        connection. Before each PeerThread is dispatched to handle the peer,
        the RFC index is updated (if an updated version is available).
    '''
    def run(self):
        worker_threads = []

        self.rfc_index_lock = threading.Lock()

        # Loops infinitely, accepting connections and passing them
        # off to PeerThreads. A SIGINT will break out of this loop.
        while True:
            try:
                self.serv_sock.listen(5)
                (client_sock, (ip_addr, port)) = self.serv_sock.accept()

                # Check if an updated RFC index has been sent from the client.
                # Update the RFC index if so.

                if (self.serv_pipe.poll()):
                    self.rfc_index_lock.acquire()
                    self.rfc_index = self.serv_pipe.recv()
                    self.rfc_index_lock.release()

                peer_thread = PeerThread(ip_addr, port, client_sock, self.rfc_index, self.rfc_index_lock)
                peer_thread.start()

                worker_threads.append(peer_thread)

            except KeyboardInterrupt:
                self.cleanup(worker_threads)
                break
