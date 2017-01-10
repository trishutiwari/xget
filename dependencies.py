#!/usr/bin/env python

import threading,socket,ssl,logging,traceback,sys
from dnslib import DNSRecord,DNSQuestion,DNSHeader,QTYPE

logging.basicConfig(level=logging.DEBUG,format='[%(levelname)s] (%(threadName)-10s) %(message)s',)

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

def get_hostname(data):
	data = data.decode('utf-8')
	if "POST" in data[:5]:
		hostname = None
	elif "GET" in data[:5]: #only allow get request to get through
		hostname_start = data.find("Host: ")+6
		hostname_end = data.find('\n',hostname_start,)
		hostname = str(data[hostname_start:hostname_end-1])
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
	else:
		hostname = None
		logging.debug( "Hostname is None; user sent prohibited request")
	return hostname

def connect(hostname,port):
	serversock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	if port == 443:
		context = ssl.create_default_context()
		serversock = context.wrap_socket(serversock, server_hostname=hostname)
		logging.debug( "SSL connection established with " + hostname)
	serversock.connect((hostname,port))
	logging.debug( "regular HTTP connection established with " + hostname)
	return serversock
		

def recieve(stream,length,threadinst):
	#get the first chunck of data to pull out the hostname
	chunks = []
        bytesrecvd = 0
	try:
		while bytesrecvd < length:
		    chunk = stream.recv(min(length - bytesrecvd, 2048))
		    if chunk == '':
		        raise RuntimeError("Socket connection broken")
		    chunks.append(chunk)
		    bytesrecvd = bytesrecvd + sys.getsizeof(chunk)
		return ''.join(chunks)
	except Exception as e:
		exc_type, exc_value, exc_traceback = sys.exc_info()
    		traceback.print_tb(exc_traceback, limit=5, file=sys.stdout)
		logging.debug( e )
		threadinst.terminate = True

def recieve_sans_length(stream,threadinst):
	stream.settimeout(1)
	data = b''
	try:
		while True:
			data+=stream.recv(2048)
	except socket.timeout:
		return data
	

def send(stream,data,threadinst):
	try:	
		stream.sendall(data)
		return 0
	except Exception as e:
		exc_type, exc_value, exc_traceback = sys.exc_info()
    		traceback.print_tb(exc_traceback, limit=5, file=sys.stdout)
		logging.debug( e )
		logging.debug( "Could not send data, perhaps due to connection reset by peer" )
		#if there is nothing to send, the connection has been reset by peer.
		threadinst.terminate = True
		return 1	

class thread(threading.Thread):
	def __init__(self, clientsock,port):
		threading.Thread.__init__(self)
		self.clientsock = clientsock
		self.serversock = None
		self.connected = False
		self.request = None
		self.hostname = None
		self.terminate = False
		self.port = port
		self.contentlength = None
		self.response = None
		self.header = None
	def run(self):
		try:
			self.clientsock.settimeout(4)
			while not self.terminate:
				#recieve the web request from the client
				self.request = self.clientsock.recv(2048)
				#print self.request[:
				self.hostname = get_hostname(self.request)
				if self.hostname == None:
					clientsock.sendall("HTTP/1.1 403 Forbidden Protocol\r\n\r\n".encode('utf-8'))
				if not self.connected:
					self.serversock = connect(self.hostname,self.port)
					self.connected = True
				url = self.request[:self.request.find("\r\n")].decode('utf-8')
				logging.debug("Sending request to server: " + url)
				if "png" in url or "jpeg" in url or "jpg" in url or "gif" in url: 
					#not loading as many images as possible for faster performance
					send(self.clientsock,"HTTP/1.1 404 Image Not Found\r\n\r\n".encode('utf-8'),self)
					continue
				#send the webserver the client's request
				send(self.serversock,self.request,self)
				logging.debug( "Request successfully sent to server " + self.hostname)
				#recieve the data from the webserver
				self.header = self.serversock.recv(4096)
				self.header, self.response = get_header(self.header)
				send(self.clientsock,self.header,self)
				self.contentlength = get_content_length(self.header) - sys.getsizeof(self.response)
				if self.contentlength == None:
					self.response+=recieve(self.serversock,self.contentlength,self)
				else:
					self.response+=recieve_sans_length(self.serversock,self) #some webservers don't include content length :(
				logging.debug( "Recieved response from server " + self.hostname )
				#shuttle all this data back to the client
				send(self.clientsock,self.response,self)
				logging.debug( "Succesfully sent response to client" )
				
		except socket.timeout:
			try:
				#self.clientsock.shutdown(socket.SHUT_RDWR)
				self.clientsock.close()
				#self.serversock.shutdown(socket.SHUT_RDWR)
				self.serversock.close()
			except AttributeError as ae:
				logging.debug( ae )
				logging.debug( "Trying to close a closed socket" )
			logging.debug( "Successfully terminated thread")
		except Exception as e:
			#self.clientsock.shutdown(socket.SHUT_RDWR)
			#self.clientsock.close()
			#self.serversock.shutdown(socket.SHUT_RDWR)
			#self.serversock.close()
			exc_type, exc_value, exc_traceback = sys.exc_info()
	    		traceback.print_tb(exc_traceback, limit=5, file=sys.stdout)
			logging.debug( e )
