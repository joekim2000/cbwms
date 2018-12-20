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

# Oracle
#import cx_Oracle
from subprocess import Popen

reload(sys)
sys.setdefaultencoding('utf8')

def CreateDirectory(directory):
        if not os.path.exists(directory):
                os.makedirs(directory)

def euckr2utf8(euc):
        if euc == None:
                euc='NA'
        return  unicode(euc,'cp949').encode('utf-8')

# Send System Information Seoul to Busan
def Send(filename):
        srcfile = "/home/DATA/INF/sysinform/" + filename
        dstfile = "imdtsvp3:/home/DATA/INF/sysinform/" + filename
        arg = """ """.join(["/opt/JionLab/fcp2/bin/fcp2 -f", srcfile, "-p 10.200.7.1:7776", dstfile, "-P", "/opt/JionLab/caengine/script/user.dat"])
        #print arg
        obj = Popen(arg, shell=True, stdin=None, stdout=None, stderr=None, close_fds=True)
        obj.wait()
        #print "Complete"

# 패스워드 불필요한 데이터 제거
def CleanupPasswd():
	__FileLocation__ = os.path.abspath(__file__)
	__CurrentPath__, __msgfile__ = os.path.split(__FileLocation__)
	etcPath = __CurrentPath__[:-6] + "etc/"
	filename = etcPath + "caenginepwd.conf"
	if not os.path.exists(filename):
		confile = open(filename, "w")
		confile.write('admin')
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
		#CreateDirectory('/home/DATA/INF')
		#CreateDirectory('/home/DATA/INF/sysinform')

		os.putenv('NLS_LANG','KOREAN_KOREA.KO16MSWIN949')

		# MS-SQL
		#conn = pymssql.connect(server='HQVMSQL01.nsseshop.com', user='corebridgeuser', password='!nS#cbL2*jkL', database='COREBRIDGEDB')
		#cursor = conn.cursor()
		#cursor.execute("SELECT DISPLAY_NAME, PERSON_CODE, ENTER_DATE, UNIT_NAME, UNIT_CODE, TITLE_NAME, TITLE_CODE, LEVEL_NAME, LEVEL_CODE, EMAIL FROM ORG_PERSON_VDI")
		#row = cursor.fetchone()

		# ORACLE
		#connection=cx_Oracle.connect("HRM/WB02@//10.10.2.161:1521/DBIMP")
		#cursor=connection.cursor()
		#cursor.execute("SELECT EMP_NM, DUTY_NM, EMP_NO, EMP_NO, TEAM_NM, TEAM_CD, BU_DEPT_NM, BU_DEPT_CD, DUTY_CD, HEAD_DEPT_NM, DEPT_NM, HEAD_DEPT_CD, DEPT_CD, EMAIL FROM HRM.VWWB_EMPINFO WHERE HLD_STAT='Y'")
		count = 0

		fnw = open('/opt/JionLab/caengine/etc/user.dat', 'w')
		# Name, Jikgeup, Number, ID, Dept Name, Dept Code, Group Name, Group Code
		# 이름,직급,사번,ID,부서명,부서코드,그룹명,그룹코드,email
		# 파트 = 부서명
		# 팀 = 그룹 (부서들)
		insafile = open("/home/DATA/INF/MANGINSA.txt", 'r')
		while(True):
			line = insafile.readline()
			data = line.split('|')
			#data=cursor.fetchone()
			#if (data == None):
			#	break
			# 이름
			if (data[0] == ""):
				break
			NAME = data[4]
			# 직급
			POSITION = data[6]
			# 사번
			PERSONNUMBER = data[7]
			# ID
			PERSONID = data[8]
			# 부서명
			DEPTNAME = data[9]
			# 부서코드
			DEPTCODE = data[10]
			# 그룹명
			GROUPNAME = data[12]
			# 그룹코드
			GROUPCODE = data[13]
			# email
			EMAIL = data[11]

			DIVNAME = "금융그룹"
			DIVNAMEEN = "BANKGROUP"

			s = (',').join([NAME,POSITION,PERSONNUMBER,PERSONID,DEPTNAME,DEPTCODE,GROUPNAME, GROUPCODE, EMAIL, DIVNAME, DIVNAMEEN])

			print s
			fnw.write(s + '\r\n')
			count = count + 1

		print "Total: ", count
		fnw.close()

		# hjkim 20170515 패스워드 불필요한 데이터 제거
		#CleanupPasswd()
				
		#Send('raw.dat')

		return True

if __name__ == "__main__":
	print "Start"
	if Run():
		sys.exit(0)
	else:
		sys.exit(1)

