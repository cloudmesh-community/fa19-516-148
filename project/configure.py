#!/usr/bin/env python3

# this script should be run as root
# don't run it on your personal computer or it will mess up your system!

import sys, os

if len(sys.argv) != 4:
	print("Usage: configure.py X Y Z   (X = color, Y = color num, Z = this Pi num)\nWill give hostname XZ and IP 192.168.Y.Z")
	sys.exit(0)

color = sys.argv[1]
colornum = sys.argv[2]
pinum = sys.argv[3]

hostname = color + pinum # 'red' + '47' = 'red47'


# write the new hostname to /etc/hostname
with open('/etc/hostname', 'w') as f:
	f.write(hostname + '\n')


# change last line of /etc/hosts to have the new hostname
# 127.0.1.1 raspberrypi   # default
# 127.0.1.1 red47         # new
with open('/etc/hosts', 'r') as f: # read /etc/hosts
	lines = [l for l in f.readlines()][:-1] # ignore the last line
	newlastline = '127.0.1.1 ' + hostname + '\n'

with open('/etc/hosts', 'w') as f: # and write the modified version
	for line in lines:
		f.write(line)
	f.write(newlastline)


# change the IP address of this Pi to the new addr
# use sed inplace to change '192.168.xxx.xxx/24' to '192.168.colornum.pinum/24'
# the regexp matches and replaces just '.x.x/24' where 'x' is 1 or more numbers
os.system("sed -ri 's/\.[0-9]+\.[0-9]+\/24/\.{}\.{}\/24/g' /etc/dhcpcd.conf".format(colornum, pinum))


# reboot
os.system('reboot')
