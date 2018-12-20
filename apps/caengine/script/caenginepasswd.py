#! /usr/bin/python
# coding: utf-8

import sys
import os
 
def Run():
	pwfile = '/opt/JionLab/passwd/etc/passwd'
	with open(pwfile, 'r') as pf:
		lines = pf.readlines()
	pwlines = [line.rstrip('\n') for line in open(pwfile)]

	usfile = '/opt/JionLab/caengine/etc/user.dat'
        with open(usfile, 'r') as uf:
                lines = uf.readlines()
        uslines = [line.rstrip('\n') for line in open(usfile)]

	fnw = open('/opt/JionLab/passwd/etc/initpasswd', 'w')

 	ussplit = []
	pwsplit = []
	for linepw in pwlines:
		pwsplit = linepw.split(':')
		for lineus in uslines:
			ussplit = lineus.split(',')
			if ussplit[3] == pwsplit[0]:
				print linepw
				fnw.write(linepw + '\r\n')
	fnw.close()
	pf.close()
	uf.close()
 
if __name__ == "__main__":
        Run()


