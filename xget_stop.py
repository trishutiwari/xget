#!/usr/bin/env python3

import subprocess

nameserverfile = "/var/run/NetworkManager"
processes = ["https.py","http.py","dnsserver.py"]

for proc in processes:
	psaux = subprocess.Popen("ps aux | grep "+proc ,stdout=subprocess.PIPE,shell=True)

	line = str(psaux.stdout.readline()) #single line output
	
	psaux.exit(0)

	lst = line.split("	") #fix this!
	
	print(lst)

	pid = lst[1]

	#subprocess.Popen("kill -9 " + pid)

#restoring /etc/resolv.conf

subprocess.Popen("cp ./resolv.conf.backup " + nameserverfile,shell=True)


