#! /usr/bin/python
# coding: utf-8

import sys
import os
import ldap

sys.path.append("/opt/JionLab/caengine/bin")
import caengineconf
cfg = caengineconf.config('/opt/JionLab/caengine/etc/caengined.conf', False)

#reload(sys)
#sys.setdefaultencoding('euckr')

#print len(sys.argv), sys.argv
if (len(sys.argv)<3):
	sys.exit(1)

#idat = sys.argv[1].split('@')
#if len(idat) != 2:
#	sys.exit(1)
#id = sys.argv[1]
#filename = '/opt/JionLab/caengine/etc/' + id + '.ad'
 
#if not os.path.exists(filename):
#	sys.exit(1)

#fn = open(filename, 'r')
#ou = fn.read(-1)
#fn.close()

#print id, ou


#print idat[0], idat[1], sys.argv[2]

try:
	goodLuck = "waiting"

	id = sys.argv[1]
	passwd=sys.argv[2]
	
	f = open(cfg.fcp2_passwd, 'r')
	for eachline in f:
        	eachuser = eachline.split(':')
		if(eachuser[0] == id):
			goodLuck = "success"
			break
	f.close()



	#l=ldap.initialize("ldap://192.168.10.51")
	#l.protocol_version=3
	#l.set_option(ldap.OPT_REFERRALS,0)
	
	#id = "emtima"
	#passwd = "ns@123456"
	#username="cn="+id+",ou=ServiceAccounts,ou=VDImanage,ou=Member Server,dc=nsseshop,dc=com"
	#print username, passwd
	#m=l.simple_bind_s(username, passwd)
	#print m
	if(goodLuck == "success"):
		print "Success"
		sys.exit(0)
#	print '---------------------', m

#	print '--------------------'
#	print 'Info'
#	#r=l.search_s("ou=L10,ou=Users,ou=LIGInsure,dc=LigInsuredev,dc=com",ldap.SCOPE_SUBTREE,"(objectClass=*)")
#	#for dn, entry in r:
#	#	print "Process: ", repr(dn)
#	#	print "entry: ", entry
except ldap.LDAPError, e:
#	print 'Error: ', e
	print "Fail"
	sys.exit(1)
