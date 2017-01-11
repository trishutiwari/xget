# xget
A python program to filter regular and encrypted network traffic

Useful for programming exams with internet access in colleges/schools as it helps prevent cheating.

REQUIREMENTS:

	1) The program is currently platform dependent, and will only run on linux distributions. This will be changed in the future.

FUNCTIONING:

	1) Start: As soon as the program starts, it overwrites the /etc/resolv.conf file. This file specifies the nameserver that the OS uses for its DNS queries. Instead of the default nameserver, we add our custom nameserver running at localhost:53. It also clears the browser's cache, so that it doesn't remeber which websites connect over HTTPS. This step allows us to monitor SSL traffic.

	2) dns_server.py: The nameserver bound to localhost:53. This nameserver does nothing but return 127.0.0.1 type A queries and ::1 for type AAAA queries. Hence, this directs all web traffic to our filtering programs running at localhost:80 and localhost:443

	3) proxy_server.py: This program serves as a proxy server. It inspect both regular HTTP and SSL encrypted data.
		HTTP Traffic: 
		It looks at the incoming traffic at port 80, and if it passes all filters, then sends the request to the actual server. Otherwise, a HTTP 403 (Forbidden) response is sent back to the client.

		SSL traffic: 
		Encrypted traffic is monitored via the same principles, but additional steps have to be taken. When the user enters a domain like "facebook.com" in the browser's address bar, the browser looks into its cache to check if the connection is to be made over HTTP or HTTPS. However, since we cleared the cache during the program's startup, the browser doesn't know which of the schemes is the correct one. And so, the browser first attempts a connection over HTTP. The proxy lets this request pass to the end server, which then sends a re-direct response to the https version of the website. The proxy, however, does not let this redirect response reach the client's browser (and so the browser never comes to know that the network traffic was supposed to be encrypted). Instead, as soon as the proxy recieves the redirect location, it itself opens an SSL encrypted connection with the end server and send the same GET request that the client had originally sent over HTTP. The proxy then recieves the response and decrypts it (this is possible because the SSL connection is between the proxy and the end server). It then sends this decrypted response to the client. Then, any subsequent (allowed) requests from the client are forwared to the end server after the proxy replaces the HOST header in the request with the correct HTTPS HOST domain name.

	5) Stop: Stopping the program would restore /etc/resolv.conf and kill the above programs.

TO USE:

	1) Just run xget_start.py (with root privledges)

TO DO:
	
	1) Perform code cleanup
	2) Make the program platform independent
	3) Implement the linux version of the program as a service
	4) Implement proper log files



