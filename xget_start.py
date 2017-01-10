#!/usr/bin/env python3

import subprocess

nameserverfile = "/var/run/NetworkManager"

subprocess.Popen("cp "+ nameserverfile +" ./resolv.conf.backup",shell=True)

resolv = open (nameserverfile,'w')

resolv.write("nameserver 127.0.0.1")

subprocess.Popen("dnsserver.py")

subprocess.Popen("https.py")

subprocess.Popen("http.py")


