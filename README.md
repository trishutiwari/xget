# xget
A python program to filter regular and encrypted network traffic

REQUIREMENTS:

1) A valid SSL certificate that should be named "cert.pem" with a key called "key.pem". The default certificate is self-signed, which will not be enough to monitor SSL traffic.

2) The program is currently platform dependent, and will only run on linux distributions. This will be changed in the future.

FUNCTIONING

1) Start: As soon as the program starts, it overwrites the /etc/resolv.conf file. This file specifies the nameserver that the OS uses for its DNS queries. Instead of the default nameserver, we add our custom nameserver running at localhost:53.

2) dns_server.py: The nameserver bound to localhost:53. This nameserver does nothing but return 127.0.0.1 type A queries and ::1 for type AAAA queries. Hence, this directs all web traffic to our filtering programs running at localhost:80 and localhost:443

3) http.py: This program serves as a proxy server. It looks at the incoming traffic at port 80, and if it passes all filters, then sends the request to the actual server

4) https.py: Same purpose as http.py, except that this takes care of all the ssl traffic at port 443.



