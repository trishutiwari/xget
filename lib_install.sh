#!/bin/bash

cd /usr/bin

wget "https://pypi.python.org/packages/d2/49/d9430826e6678cab9675e343c795e3e0c3ca568b9dfcc145b5d5490c3b17/dnslib-0.9.6.tar.gz"

tar -xvf dnslib*tar.gz

rm dnslib*tar.gz

cd dnslib*

python setup.py

