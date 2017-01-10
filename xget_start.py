#!/usr/bin/env python3

import subprocess
try:
	try:
		subprocess.run("python -c 'import dnslib'",shell=True,check=True)       
		print("[*] All external dependencies are in place...")
	except subprocess.CalledProcessError:
		print("[*] Installing external library dnslib...",end="")
		subprocess.run("sh lib_install.sh",shell=True)
		print("Successful")
	
	nameserverfile = "/etc/resolv.conf"

	print("[*] Creating backup of /etc/resolv.conf...",end="")

	subprocess.run("cp "+ nameserverfile +" ./resolv.conf.backup",shell=True)
	
	print("Successful")
	
	print("[*] Overwriting /etc/resolv.conf...",end="")
	
	resolv = open (nameserverfile,'w')

	resolv.write("nameserver 127.0.0.1")
	
	print("Successful")
	
	subprocess.run("chmod +x *py",shell=True)

	print("[*] Starting processes...",end="")

	dns = subprocess.Popen("./dns_server.py")

	https = subprocess.Popen("./https.py")

	http = subprocess.Popen("./http.py")

	print("Successful")

	while 1:
		pass

except KeyboardInterrupt:
	subprocess.run("cp ./resolv.conf.backup " + nameserverfile,shell=True)
	dns.kill()
	https.kill()
	http.kill()


