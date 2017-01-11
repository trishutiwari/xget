#!/usr/bin/env python3

import subprocess, sys

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
	
	try:

		dns = subprocess.Popen("./dns_server.py")

		proxy = subprocess.Popen("./proxy_server.py")
		
		dns_exit = dns.poll()
	
		proxy_exit = proxy.poll()
	
		 #NEED TO FIX

		print (dns_exit, proxy_exit)

		if dns_exit or proxy_exit:
			raise RuntimeError

		print("Successful")

	except Exception:
		
		print("Failed")
		
		sys.exit(1)
		

	while 1:
		pass

except KeyboardInterrupt:
	subprocess.run("cp ./resolv.conf.backup " + nameserverfile,shell=True)
	dns.kill()
	proxy.kill()


