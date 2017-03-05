#!/usr/bin/env python

#reference for reversing the encoding ==> http://www.tcpipguide.com/free/t_HTTPDataTransferContentEncodingsandTransferEncodin.htm

from network_functions import *

import traceback,sys,zlib

class network_thread(threading.Thread):
	def __init__(self, clientsock,port):
		threading.Thread.__init__(self)
		self.clientsock = clientsock
		self.is_ssl = False
		self.hostnam_prev = None
		self.serversock = None
		self.connected = False
		self.request = None
		self.hostname = None
		self.terminate = False
		self.port = port
		self.content_length = None
		self.response = None
		self.header = None
		self.url = None
		self.domain = None
		self.response_code = None

	def connect(self):
		self.serversock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		if self.port == 443:
			context = ssl.SSLContext(ssl.PROTOCOL_SSLv23)
			context.verify_mode = ssl.CERT_REQUIRED
			context.load_verify_locations("/etc/ssl/certs/ca-certificates.crt")
			self.serversock = context.wrap_socket(self.serversock)
			logging.debug( "SSL connection established with " + self.domain)
		self.serversock.connect((self.hostname,self.port))
		self.connected = True
		

	def recieve_content_length(self,stream):
		chunks = []
		bytesrecvd = 0
		try:
			while bytesrecvd < self.content_length:
			    chunk = stream.recv(min(self.content_length - bytesrecvd, 2048))
			    if chunk == '':
				raise RuntimeError("Socket connection broken")
			    chunks.append(chunk)
			    bytesrecvd = bytesrecvd + sys.getsizeof(chunk)
			return ''.join(chunks)
		except Exception as e:
			logging.debug( e )
			self.terminate = True
			exc_type, exc_value, exc_traceback = sys.exc_info()
	    	traceback.print_tb(exc_traceback, limit=5, file=sys.stdout)

	def recieve_chunked_encoding(self,stream,length,length_recieved):
		data = b''
		chunk=stream.recv(int(length,16)-int(length_recieved)+2)
		data+=chunk
		print "the length recieved " + str(int(length,16)-int(length_recieved))
		try:
			while True:
				chunk=stream.recv(5)
				print "initial chunk with length: " + chunk
				self.content_length = chunk[:chunk.find("\r\n")]
				logging.debug("Length: " + self.content_length)
				recvd = chunk[chunk.find("\r\n") + len("\r\n"):]
				print "length recvd " + str(len(recvd))
				chunk = recvd + stream.recv(int(self.content_length,16)-len(recvd)+2)
				data+=chunk
				print "final chunk without length: " + chunk
		except Exception as e:
				print e
				return data

	def recieve(self,stream):
		try:
			self.content_length = get_content_length(self.header) - sys.getsizeof(self.response)
			self.response+=self.recieve_content_length(stream)
		except TypeError: #if server uses chunked encoding instead of content-length
			self.content_length = self.response[:self.response.find("\r\n")]
			self.response = self.response[self.response.find("\r\n") + len("\r\n"):]
			length_recieved = len(self.response)
			self.response+=self.recieve_chunked_encoding(stream,self.content_length,length_recieved)
			logging.debug( "Recieved response from server " + self.domain )
			print "################################ data length ################### " + str(len(self.response))
		
	def send(self,stream,data):
		try:	
			stream.sendall(data)
			return 0
		except Exception as e:
			logging.debug( e )
			logging.debug( "Could not send data, perhaps due to connection reset by peer" )
			#if there is nothing to send, the connection has been reset by peer.
			self.terminate = True
			exc_type, exc_value, exc_traceback = sys.exc_info()
	    	traceback.print_tb(exc_traceback, limit=5, file=sys.stdout)


	def ssl_handling(self):
		self.hostname_prev = self.hostname
		self.domain, self.hostname, self.url, req = get_hostname_url_ssl(self.header)
		logging.debug(self.domain + " " + self.hostname + " " + self.url + " " + req)
		self.serversock.shutdown(socket.SHUT_RDWR) #shutdown the old http socket with server
		self.serversock.close()
		logging.debug("Closed connection with old host")
		self.connected = False
		self.is_ssl = True
		self.request = self.request.replace(self.hostname_prev,self.hostname)
		self.request = self.request.replace(self.request[:self.request.find('\r\n')],req)
		if not self.connected:
			self.port = 443
			self.connect()
			self.serversock.settimeout(10)
		logging.debug("Sending request to SSL host: " + self.domain)
		self.send(self.serversock,self.request)
		self.header = self.serversock.recv(4096)
		self.header, self.response = get_header(self.header)
		self.response_code = self.header[:self.header.find("\r\n")].split(" ")[1] #update response code
		logging.debug(self.header)
		logging.debug("Response code: " + self.response_code)

	def run(self):
		try:
			self.clientsock.settimeout(4)
			while not self.terminate:
				#recieve the web request from the client
				self.request = self.clientsock.recv(2048)
				if self.request == None or self.request == "": #client connection has been reset
					raise socket.timeout
				self.request = replace_content_encoding(self.request)
				logging.debug(self.request)
				if self.is_ssl:
					self.request = self.request.replace(self.hostname_prev,self.hostname)
				self.domain , self.hostname = get_hostname(self.request)
				if not self.connected:
					self.connect()
					logging.debug("Successfully connected with server: " + self.domain)
				url = self.request[:self.request.find("\r\n")].decode('utf-8')
				logging.debug("Sending request to server: " + url)
				#send the webserver the client's request
				self.send(self.serversock,self.request)
				logging.debug( "Request successfully sent to server " + self.domain)
				#recieve the data from the webserver
				#print self.serversock.recv(16384)
				#sys.exit(0)
				self.header = self.serversock.recv(2048)
				self.header, self.response = get_header(self.header)
				print self.header
				print "Here is the chunked length: " + self.response[:5]
				self.response_code = self.header[:self.header.find("\r\n")].split(" ")[1]
				#logging.debug("Response code: " + self.response_code)
				#checking for redirect response codes
				while int(self.response_code) in [300,301,302,303,304,305,306,307,308] and "https" in self.header: #perform ssl stripping
					self.ssl_handling()
				self.send(self.clientsock,self.header)
				#logging.debug(self.header)
				self.recieve(self.serversock)
				#logging.debug(self.response[:30])
				self.response = filter_response(self.response) #reading response data for useful info >)
				#shuttle all this data back to the client
				logging.debug( "Removed all https references from response" )
				self.send(self.clientsock,self.response)
				logging.debug( "Succesfully sent response to client" )	
		except socket.timeout:
			try:
				self.clientsock.close()
				self.serversock.close()
			except AttributeError as ae:
				logging.debug( ae )
				logging.debug( "Trying to close a closed socket" )
			logging.debug( "Successfully terminated thread")
		except Exception as e:
			logging.debug( e )
			exc_type, exc_value, exc_traceback = sys.exc_info()
	    		traceback.print_tb(exc_traceback, limit=5, file=sys.stdout)
