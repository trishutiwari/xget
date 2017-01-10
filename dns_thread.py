#!/usr/bin/env python

from dnslib import DNSRecord,DNSQuestion,DNSHeader,RR,A,AAAA,QTYPE
import socket, threading

class dns_thread(threading.Thread):
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


