#!/usr/bin/env python

import threading,socket,logging,traceback,sys,ssl
from dnslib import DNSRecord,DNSQuestion,DNSHeader,QTYPE

logging.basicConfig(level=logging.DEBUG,format='[%(levelname)s] (%(threadName)-10s) %(message)s',)

def filter_request(url):
	if "POST" in url: #No POST requests allowed
		return "HTTP/1.1 403 Forbidden Protocol\r\n\r\n".encode('utf-8')
	if "png" in url or "jpeg" in url or "jpg" in url or "gif" in url: 
		#not loading as many images as possible for faster performance
		return "HTTP/1.1 404 Image Not Found\r\n\r\n".encode('utf-8')
	return None
	

def get_header(data):
        offset = data.find("\r\n\r\n") + len("\r\n\r\n")
        header,content = data[:offset],data[offset:]
        return header,content

def get_content_length(resp):
	start = resp.find("Content-Length: ") + len("Content-Length: ")
	end = resp.find('\r\n',start,)
	length = resp[start:end].strip()
	try:
		return int(length)
	except Exception as e:
		return None
		logging.debug(resp)
		logging.debug( e )
		exc_type, exc_value, exc_traceback = sys.exc_info()
    		traceback.print_tb(exc_traceback, limit=5, file=sys.stdout)

def dns_query(hostname):
	dnssock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
	#doing a dns query for hostname manually since we have overridden the /etc/resolv.conf file with our own dummy nameserver
	query = DNSRecord(DNSHeader(rd=1),q=DNSQuestion(hostname))
	#logging.debug( query
	dnssock.sendto(query.pack(),("8.8.8.8",53)) # any nameserver ip
	response,addr = dnssock.recvfrom(8192)
	dnssock.close()
	response = DNSRecord.parse(response)
	for resource_record in response.rr:
		if resource_record.rtype == QTYPE.A:
			hostname = str(resource_record.rdata)
			break
	return hostname

def get_hostname(data):
	hostname_start = data.find("Host: ")+6
	hostname_end = data.find('\r\n',hostname_start,)
	hostname = str(data[hostname_start:hostname_end])
	return dns_query(hostname)

def get_hostname_url_ssl(data):
	url_start = data.find("Location: ") + len("Location: ")
	url_end = data.find('\r\n',url_start,)
	url = str(data[url_start:url_end])
	hostname_start = url.find("://") + 3
	hostname_end = url.find('/',hostname_start,)
	hostname = url[hostname_start:hostname_end]
	req = ("GET " + url[hostname_end:]).encode('utf-8')
	return dns_query(hostname), url, req
	

