#! /usr/bin/python
# coding: utf-8
##########################################################
# site dependent user import script
##########################################################

import sys
import os
import datetime
import pwd
import grp

from shutil import copyfile

reload(sys)
sys.setdefaultencoding('utf8')

def RemoveFile(filename):
	if os.path.exists(filename):
		os.remove(filename)

# 패스워드 불필요한 데이터 제거
def CleanupPasswd():
	__FileLocation__ = os.path.abspath(__file__)
	__CurrentPath__, __msgfile__ = os.path.split(__FileLocation__)
	etcPath = __CurrentPath__[:-6] + "etc/"
	filename = etcPath + "caenginepwd.conf"
	if not os.path.exists(filename):
		confile = open(filename, "w")
		confile.write('admin,')
		confile.close()

	confile = open(filename, "r")
	conf = confile.read(-1)
	confile.close
	confadmin = conf.split(',')
   
	pwfile = '/opt/JionLab/passwd/etc/passwd'
	with open(pwfile, 'r') as pf:
		lines = pf.readlines()
	pwlines = [line.rstrip('\n') for line in open(pwfile)]

	usfile = '/opt/JionLab/caengine/etc/user.dat'
	with open(usfile, 'r') as uf:
		lines = uf.readlines()
	uslines = [line.rstrip('\n') for line in open(usfile)]

	inipwfile = '/opt/JionLab/passwd/etc/initpasswd'
	if os.path.exists(inipwfile):
		RemoveFile(inipwfile)
	fnw = open(inipwfile, 'w')

	ussplit = []
	pwsplit = []
	for linepw in pwlines:
		pwsplit = linepw.split(':')
		for eachadmin in confadmin:
			if eachadmin == pwsplit[0]:
				print linepw
				fnw.write(linepw + '\n')
		for lineus in uslines:
			ussplit = lineus.split(',')
			# KRX ussplit[3]이고 다른 사이트는 점검해서 처리
 			if ussplit[3] == pwsplit[0]:
				print linepw
				fnw.write(linepw + '\n')
	fnw.close()
	pf.close()
	uf.close()

	# initpasswd 파일 검토 후 풀것
	'''
	d = datetime.datetime.now()
	dateinfo = d.strftime("%Y%m%d%H%M%S")
	copyfile(pwfile, pwfile + '.' + dateinfo)
	os.remove(pwfile)
	copyfile(inipwfile, pwfile)
	os.remove(inipwfile)
	uid = pwd.getpwnam("corebrdg").pw_uid
	gid = grp.getgrnam("corebrdg").gr_gid
	os.chown(pwfile, uid, gid)
	os.chown( pwfile + '.' + dateinfo, uid, gid)
	'''

def Run():

	if True:
		# hjkim 20170515 패스워드 불필요한 데이터 제거
		CleanupPasswd()

		return True

if __name__ == "__main__":
	print "Start"
	if Run():
		sys.exit(0)
	else:
		sys.exit(1)
