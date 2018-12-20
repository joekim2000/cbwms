#! /usr/bin/python
# coding: utf-8
##########################################################
# site dependent user import script
##########################################################
from django.db import models
from django.forms import ModelForm
from django.conf import settings
from cbwms.settings import common

from datetime import datetime

import sys
import os
import pwd
import grp

PROJECT_ROOT = getattr(settings, "PROJECT_ROOT", None)
APPS_ROOT = PROJECT_ROOT + "/apps/caengine/bin"
sys.path.append(APPS_ROOT)
import caengineconf

PROJECT_ROOT = getattr(settings, "PROJECT_ROOT", None)
APPS_ROOT = PROJECT_ROOT + "/apps/caengine/script"
sys.path.append(APPS_ROOT)
import custom # depends on site
import subprocess

# MS-SQL
#import pymssql
# Oracle
#import cx_Oracle
from subprocess import Popen

## using the plaster to set a different encoding would make no difference anyway.
#from importlib import reload
#reload(sys)
#sys.setdefaultencoding('utf8')

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
        #print(arg)
        obj = Popen(arg, shell=True, stdin=None, stdout=None, stderr=None, close_fds=True)
        obj.wait()
        #print("Complete")
	
def Run(cfg):
	
	if True:
		self.cfg = cfg

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

		#fnw = open('/home/DATA/INF/sysinform/raw.dat', 'w')
		fnw = open(config.import_file, 'w')
		# Name, Jikgeup, Number, ID, Dept Name, Dept Code, Group Name, Group Code
        	# 이름,직급,사번,ID,부서명,부서코드,그룹명,그룹코드,email
	        # 파트 = 부서명
        	# 팀 = 그룹 (부서들)
		deptfile = open("/home/eai_ftp/vFTS_Dept.txt", 'r')
		deptdata = []
		while(True):
			deptline = deptfile.readline()
			deptsplit = euckr2utf8(deptline)
			deptassign = deptsplit.split('\n')
			deptdata.append(deptassign[0])
			if(deptline == ""):
				break
		personfile = open("/home/eai_ftp/vFTS_Person.txt", 'r')
		while(True):
			personline = personfile.readline()
			personassign = euckr2utf8(personline)
 
			persondata = personassign.split('|')
			
			if (persondata[0] == ""):
				break

			# 이름
			NAME = persondata[1]
			# 직급
			POSITION = persondata[9]
			# 직급코드
			POSITIONCODE = persondata[10]
			# 직위코드
			JIKWICODE = persondata[8]
			# 사번
			PERSONNUMBER = persondata[0]
			# ID
			PERSONID = persondata[0]
			# 부서명
			for i in xrange(0,len(deptdata)):
				dept = deptdata[i]
				if (dept == ""):
					break
				deptsplit = dept.split('|')
				if (deptsplit[0] == persondata[3]):
					break
			# 부서이름
			DEPTNAME = deptsplit[1]
			# 부서코드
			if (persondata[3] == "SM1_BSBK"):
				persondata[3] = "982"
			if (persondata[3] == "SM2_BSBK"):
				persondata[3] = "981"

			DEPTCODE = persondata[3]
			# 팀명
			TEAMNAME = deptsplit[1]
			#그룹코드
			TEAMCODE = persondata[3]
			# EMAIL
			if ((persondata[12] == None) or (persondata[12] == "")):
				EMAIL = "없음"
			else:
				EMAIL = persondata[12]

			possplit = POSITIONCODE.split('_')
			if POSITIONCODE:
				if (possplit[2] == "BSFG"):
					DIVNAME = "금융지주"
					DIVID = "FINANCIALGROUP"
				elif (possplit[2] == "BSSM"):
					DIVNAME = "BNK시스템"
					DIVID = "BNKSYSTEM"
				else:
					DIVNAME = "부산은행"
					DIVID = "BUSANBANK"
			
			s = (',').join([NAME,POSITION,POSITIONCODE,PERSONNUMBER,PERSONID,DEPTNAME,DEPTCODE,TEAMNAME,TEAMCODE,EMAIL,DIVNAME,DIVID,JIKWICODE])
			print(s)
			fnw.write(s + ',' + '\r\n')
			count = count + 1

		print("Total: ", count)
		fnw.close()

		#Send('raw.dat')

		return True


if __name__ == "__main__":
	print("Start")
	config = caengineconf.config(APPS_ROOT + '/etc/caengined.conf', False)
	if Run(config):
		sys.exit(0)
	else:
		sys.exit(1)

