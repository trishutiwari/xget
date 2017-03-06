#!/usr/bin/env python

import threading,socket,logging,traceback,sys,ssl,StringIO,gzip,zlib
from dnslib import DNSRecord,DNSQuestion,DNSHeader,QTYPE
import zlib


logging.basicConfig(level=logging.DEBUG,format='[%(levelname)s] (%(threadName)-10s) %(message)s',)

def replace_content_encoding(request):
	encoding_start = request.find("Accept-Encoding: ") + len("Accept-Encoding: ")
	encoding_end = request.find("\r\n",encoding_start,)
	content_encoding = request[encoding_start:encoding_end]
	request = request.replace(content_encoding,'gzip')
	logging.debug( "Encoding: " + content_encoding )
	return request

def filter_response(response):
	try:
		response = zlib.decompress(response, 32 + zlib.MAX_WBITS)
		response = response.replace("https","http")
		print "SUCCESSFULLY DECOMPRESSED!!! FUCK YEAH! <3 <3  <3 <3  <3 <3  <3 <3  <3 <3  <3 <3  <3 <3  <3 <3  <3 <3 "
		return response
	except Exception as e:
		logging.debug(e)
		print "Not compressed! :( (((((((((((((((((((((((((((((((((((((((((((((((" 
		#response = response.replace("https","http")
		return response

def get_header(data):
        offset = data.find("\r\n\r\n") + len("\r\n\r\n")
        header,content = data[:offset],data[offset:]
        return header,content

def get_content_length(resp):
	start = resp.find("Content-Length: ") + len("Content-Length: ")
	end = resp.find('\r\n',start,)
	length = resp[start:end].strip()
	return int(length)

def dns_query(hostname):
	dnssock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
	#doing a dns query for hostname manually since we have overridden the /etc/resolv.conf file with our own dummy nameserver
	query = DNSRecord(DNSHeader(rd=1),q=DNSQuestion(hostname))
	#logging.debug( query )
	dnssock.sendto(query.pack(),("8.8.8.8",53)) # any nameserver ip
	response,addr = dnssock.recvfrom(8192)
	dnssock.close()
	response = DNSRecord.parse(response)
	for resource_record in response.rr:
		if resource_record.rtype == QTYPE.A:
			hostname = str(resource_record.rdata)
			break
	logging.debug("IP address: " + hostname)
	return hostname

def get_hostname(data):
	hostname_start = data.find("Host: ")+6
	hostname_end = data.find('\r\n',hostname_start,)
	hostname = str(data[hostname_start:hostname_end])
	return hostname, dns_query(hostname)

def get_hostname_url_ssl(data):
	url_start = data.find("Location: ") + len("Location: ")
	url_end = data.find('\r\n',url_start,)
	url = str(data[url_start:url_end])
	hostname_start = url.find("://") + 3
	hostname_end = url.find('/',hostname_start,)
	hostname = url[hostname_start:hostname_end]
	req = ("GET " + url[hostname_end:] + " HTTP/1.1").encode('utf-8')
	return hostname, dns_query(hostname), url, req
	

