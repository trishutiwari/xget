# xget
A python program to filter regular and encrypted network traffic

Useful for programming exams with internet access in colleges/schools as it helps prevents cheating.

REQUIREMENTS:

	2) The program is currently platform dependent, and will only run on linux distributions. This will be changed in the future.

FUNCTIONING:

	1) Start: As soon as the program starts, it overwrites the /etc/resolv.conf file. This file specifies the nameserver that the OS uses for its DNS queries. Instead of the default nameserver, we add our custom nameserver running at localhost:53.

	2) dns_server.py: The nameserver bound to localhost:53. This nameserver does nothing but return 127.0.0.1 type A queries and ::1 for type AAAA queries. Hence, this directs all web traffic to our filtering programs running at localhost:80 and localhost:443

	3) http.py: This program serves as a proxy server. It looks at the incoming traffic at port 80, and if it passes all filters, then sends the request to the actual server. Otherwise, a HTTP 403 (Forbidden) response is sent back to the client.

	4) https.py: Same purpose as http.py, except that this takes care of all the ssl traffic at port 443.

	5) Stop: Stopping the program would restore /etc/resolv.conf and kill the above program.

TO USE:
	1) Just run xget_start.py (with root privledges)



