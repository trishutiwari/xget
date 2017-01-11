#!/usr/bin/env python

from network_functions import *
import traceback,sys

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
		

	def recieve(self,stream):
		#get the first chunck of data to pull out the hostname
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

	def recieve_sans_length(self,stream):
		stream.settimeout(2)
		data = b''
		try:
			while True:
				data+=stream.recv(2048)
		except socket.timeout:
			try:
				return data
			except UnboundLocalError:
				self.terminate = True
		except ssl.SSLError:
				return data
		
	

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
			#return 1	


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
		self.send(self.serversock,self.request)
		self.header = self.serversock.recv(4096)
		self.header, self.response = get_header(self.header)

	def run(self):
		try:
			self.clientsock.settimeout(4)
			while not self.terminate:
				#recieve the web request from the client
				self.request = self.clientsock.recv(2048)
				if self.is_ssl:
					self.request = self.request.replace(self.hostname_prev,self.hostname)
				logging.debug(self.request)
				self.domain , self.hostname = get_hostname(self.request)
				if not self.connected:
					self.connect()
					logging.debug("Successfully connected with server: " + self.domain)
				url = self.request[:self.request.find("\r\n")].decode('utf-8')
				logging.debug("Sending request to server: " + url)
				#-------------------------FILTERING DATA HERE---------------------#
				response = filter_request(url)
				if response != None:
					self.clientsock.sendall(self.response)
					continue
				#send the webserver the client's request
				self.send(self.serversock,self.request)
				logging.debug( "Request successfully sent to server " + self.domain)
				#recieve the data from the webserver
				self.header = self.serversock.recv(4096)
				self.header, self.response = get_header(self.header)
				response_code = self.header[:self.header.find("\r\n")].split(" ")[1]
				logging.debug("Response code: " + response_code)
				#checking for redirect response codes
				if int(response_code) in [300,301,302,303,304,305,306,307,308]:
					if "https" in self.header: #overhead with ssl connections as we need to perform ssl stripping
						self.ssl_handling()
				self.send(self.clientsock,self.header)
				try:
					self.content_length = get_content_length(self.header) - sys.getsizeof(self.response)
					self.response+=self.recieve(self.serversock)
				except TypeError:
					self.response+=self.recieve_sans_length(self.serversock) #some webservers don't include content length :(
				logging.debug( "Recieved response from server " + self.domain )
				#shuttle all this data back to the client
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
			#exc_type, exc_value, exc_traceback = sys.exc_info()
	    	#traceback.print_tb(exc_traceback, limit=5, file=sys.stdout)
