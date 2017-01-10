#!/usr/bin/env python3

import sys, socket, ssl

def myreceive(stream):
	chunks = []
	bytes_recd = 0
	while bytes_recd < 1000000:
		chunk = stream.recv(min(1000000 - bytes_recd, 2048))
		if chunk == b'':
			raise RuntimeError("socket connection broken")
		print(chunk)
		chunks.append(chunk)
		bytes_recd = bytes_recd + len(chunk)
	return b''.join(chunks)

def receive(stream):
	#get the first chunck of data to pull out the hostname
	data=stream.recv(2048)
	#keep collecting data until EOF
	while 1:
		newrecv = stream.recv(2048)
		print (data)
		if (data.decode('utf-8')[-4:] !='\r\n\r\n'):
			data+=newrecv
		else:
			data+=newrecv
			return data

context = ssl.SSLContext(ssl.PROTOCOL_SSLv23)

context.verify_mode = ssl.CERT_NONE

clientsock = socket.socket()

sslclient = context.wrap_socket(clientsock,server_hostname='bu.edu')

sslclient.connect(('www.facebook.com',443))

message = "GET / HTTP/1.1\r\nUser-Agent: Mozilla/5.0 (X11; Linux x86_64; rv:45.0) Gecko/20100101 Firefox/45.0\r\nConnection: keep-alive\r\nHost: www.google.com:443\r\n\r\n"

sslclient.send(message.encode('utf-8'))

print (receive(sslclient))

print ("Works!")

