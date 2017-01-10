#!/usr/bin/env python3

import subprocess
try:
	nameserverfile = "/etc/resolv.conf"

	subprocess.Popen("cp "+ nameserverfile +" ./resolv.conf.backup",shell=True)

	resolv = open (nameserverfile,'w')

	resolv.write("nameserver 127.0.0.1")

	dns = subprocess.Popen("dns_server.py")

	https = subprocess.Popen("https.py")

	http = subprocess.Popen("http.py")

	while 1:
		pass

except KeyboardInterrupt:
	subprocess.Popen("cp ./resolv.conf.backup " + nameserverfile,shell=True)
	dns.kill()
	https.kill()
	http.kill()


