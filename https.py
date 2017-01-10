#!/usr/bin/env python

import sys, socket, ssl, threading
from dependencies import *

#------BETWEEN PROXY AND CLIENT--------#

#creating socket that supports IPv4 and is relaible. This is for reciecing client side data
proxysock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

#creating ssl context and loading certificates
context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
context.load_cert_chain(certfile="cert.pem", keyfile="key.pem")

port = 443

#bind port on all interfaces
try:
	proxysock.bind(('',port))
except OSError:
	print "[*]Cannot start https.py: port " + str(port) + " is being used by another process. Make sure to free the port before starting the server."
	sys.exit(1)

#queues up a maximum of 20 client connections
proxysock.listen(20)

print "[*] Server started, listening on port" + str(port)

#------MAIN LOOP--------#

counter = 0
main_thread = threading.currentThread()

while 1:
	try:
		(clientsock, addr) = proxysock.accept()
		context.wrap_socket(clientsock,server_side=True)
		#handle each connection on a seperate thread
		threadclient = thread(clientsock,port)
		threadclient.daemon = True
		threadclient.start()
	except KeyboardInterrupt:
		print "\n\n[*] User requested https.py to be aborted..."
		print "[*] Closing port " + str(port) + "..."
		proxysock.shutdown(socket.SHUT_RDWR)
		proxysock.close()
		print "    Successful"
		print "[*] Terminating all running threads..."
		#terminate threads
		for t in threading.enumerate():
			if t is main_thread:
        			continue
			t.terminate = True #flag allows cleanup actions to be performed
		print "    Successful" 
		print "[*] Server shutting down." 
		sys.exit(0)
	except Exception as e:
		print e
		exc_type, exc_value, exc_traceback = sys.exc_info()
    		traceback.print_tb(exc_traceback, limit=5, file=sys.stdout)
		print "[*] Closing port " + str(port) + "..."
		proxysock.shutdown(socket.SHUT_RDWR)
		proxysock.close()
		sys.exit(1)
