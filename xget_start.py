#!/usr/bin/env python3

import subprocess, sys, time

try:
	try:
		subprocess.run("python -c 'import dnslib'",shell=True,check=True)       
		print("[*] All external dependencies are in place...")
	except subprocess.CalledProcessError:
		print("[*] Installing external library dnslib...",end="")
		subprocess.run("sh lib_install.sh",shell=True)
		print("Successful")
	
	print("[*] Clearing firefox cache...",end="")

	subprocess.run("sh clear_cache.sh",shell=True)

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
		
		dns.wait(timeout = 1)
	
		proxy.wait(timeout = 1)
		
		print("Failed")
	
		raise KeyboardInterrupt

	except Exception:
		
		print("Successful")

	while 1:
		pass

except KeyboardInterrupt:
	subprocess.run("cp ./resolv.conf.backup " + nameserverfile,shell=True)
	try:
		dns.kill()
		proxy.kill()
	except Exception as e:
		print (e)


