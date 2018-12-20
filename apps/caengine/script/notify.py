#! /usr/bin/python
# coding: utf-8
##########################################################
# site dependent user import script
##########################################################

import urllib2
import datetime

# mType: (1:Request, 2:Approve, 3: Reject)
# id:userid, name: username, msg: Message, ip: Client IP
def SendMsg(mType, ReqID, AprID, name, msg, ip):
	if ReqID != AprID:
		if mType == 1:
			print "Request", ReqID, AprID, name, msg
		elif mType == 2:
			print "Approve", ReqID, AprID, name, msg
		elif mType == 3:
			print "Reject", ReqID, AprID, name, msg


def test():
	try:
		print datetime.datetime.now()
		response = urllib2.urlopen(url="http://www.googlea.com",timeout=1)
		print response.getcode()
	except:
		print "Error"
	finally:
		print datetime.datetime.now()
