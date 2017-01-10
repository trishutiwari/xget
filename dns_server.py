#!/usr/bin/env python

import socket,threading, sys
from dns_thread import *

dnssock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

port = 53

try:
	dnssock.bind(('',port))
except OSError:
	print "[*] Cannot start dnsserver.py: port " + str(port) + " is being used by another process. Make sure to free the port before starting server."
	sys.exit(1)

#dnssock.listen(20)
print "[*] dnsserver.py started; bound to port "+ str(port)
			
while 1:
	try:
		#handle each connection on a seperate thread
		packet,addr = dnssock.recvfrom(100000)
		threaddns = dns_thread(dnssock,packet,addr)
		threaddns.daemon = True
		threaddns.start() 
	except KeyboardInterrupt:
		print "\n[*] User requested dnsserver.py to be aborted..."
		print "[*] Closing port "+str(port)+"..."
		dnssock.close()
		print "    Successful"
		print "[*] All daemon threads terminated..."
		print "[*] Server shutting down."
		sys.exit(0)

		
