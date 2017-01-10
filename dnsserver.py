#!/usr/bin/env python

import socket,threading, sys
from dnslib import DNSRecord,DNSQuestion,DNSHeader,RR,A,AAAA,QTYPE

dnssock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

port = 53

try:
	dnssock.bind(('',port))
except OSError:
	print "[*] Cannot start dnsserver.py: port " + str(port) + " is being used by another process. Make sure to free the port before starting server."
	sys.exit(1)

#dnssock.listen(20)
print "[*] dnsserver.py started; bound to port "+ str(port)

class thread(threading.Thread):
	def __init__(self, dnssock,packet,addr):
		threading.Thread.__init__(self)
		self.dnssock = dnssock
		self.packet = packet
		self.addr = addr
	def run(self):
			request = DNSRecord.parse(self.packet)
			strrequest = str(request)
			hostname = request.q.qname
			#this is actually a phony dnsserver that sends 127.0.0.1 for all queries
			if "AAAA" in strrequest:
				response = DNSRecord(DNSHeader(id=request.header.id, qr=1,aa=1,ra=1,ad=1),q=request.q,a=RR(hostname,QTYPE.AAAA,rdata=AAAA("::1"),ttl=100))	
			else:
				response = DNSRecord(DNSHeader(id=request.header.id, qr=1,aa=1,ra=1,ad=1),q=request.q,a=RR(hostname,rdata=A("127.0.0.1"),ttl=100))
			self.dnssock.sendto(response.pack(),self.addr)
			
while 1:
	try:
		#handle each connection on a seperate thread
		packet,addr = dnssock.recvfrom(100000)
		threaddns = thread(dnssock,packet,addr)
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

		
