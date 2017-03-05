#!/usr/bin/env python3

import subprocess, sys, time

try:
	try:
		if sys.argv[1] == "--help" or sys.argv[1] == "-h":
			with open("help.txt",'r') as help:
				print(help.read())
				sys.exit(0)
		subprocess.run("python -c 'import dnslib'",shell=True,check=True)       
		print("[*] All external dependencies are in place...")
	except subprocess.CalledProcessError:
		print("[*] Installing external library dnslib...",end="")
		subprocess.run("sh lib_install.sh",shell=True)
		print("Successful")
	print("[*] Clearing browser cache...",end="")
	subprocess.run("sh clear_cache.sh",shell=True)
	print("Successful")
	nameserverfile = "/etc/resolv.conf"
	print("[*] Creating backup of /etc/resolv.conf...",end="")
	subprocess.run("cp "+ nameserverfile +" ./resolv.conf.backup",shell=True)
	print("Successful")
	print("[*] Overwriting /etc/resolv.conf...",end="")
	resolv = open (nameserverfile,'w')
	for arg in sys.argv[1:]:
		resolv.write("nameserver " + arg + '\n')
	print("Successful")
	subprocess.run("chmod +x *py",shell=True)
	print("[*] Starting processes...",end="")
	dns = subprocess.Popen("./dns_server.py")#,stderr=subprocess.STDOUT,stdout=subprocess.PIPE)
	proxy = subprocess.Popen("./proxy_server.py")#,stderr=subprocess.STDOUT,stdout=subprocess.PIPE)
	if dns.returncode or proxy.returncode:
		print("Failed")
		raise KeyboardInterrupt
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


