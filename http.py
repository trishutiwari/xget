#!/usr/bin/env python

import sys, socket, threading, traceback
from dependencies import *

#------BETWEEN PROXY AND CLIENT--------#

#creating socket that supports IPv4 and is relaible. This is for reciecing client side data
proxysock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

port = 80

#bind port on all interfaces
try:
	proxysock.bind(('',port))
except OSError:
	print "[*] port" + str(port) + "is being used by another process. Make sure to free the port before starting server."
	sys.exit(1)

#queues up a maximum of 20 client connections
proxysock.listen(20)

print "[*] Server started, listening on port " + str(port)

#------MAIN LOOP--------#

counter = 0
main_thread = threading.currentThread()
while 1:
	try:
		#print "waiting for connection from browser"
		(clientsock, addr) = proxysock.accept()
		#handle each connection on a seperate thread
		#request = clientsock.recv(2048)
		#if request == None:
		#	clientsock.shutdown(socket.SHUT_RDWR)
		#	clientsock.close()
		#	continue
		threadclient = thread(clientsock,port)
		threadclient.daemon = True
		threadclient.start()
		#print "new thread started " + str(counter)
	except KeyboardInterrupt:
		print "\n\n[*] User requested http.py to be aborted..."
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
		print "[*] Terminating all running threads...Successful"
		for t in threading.enumerate():
			if t is main_thread:
        			continue
			t.terminate = True #flag allows cleanup actions to be performed
		sys.exit(1)
