#! /usr/bin/python
# coding: utf-8
##########################################################
# site dependent user import script
##########################################################
from django.db import models
from django.forms import ModelForm
from datetime import date, datetime
from django.conf import settings
from cbwms.settings import common

import sys
import os
import bin.caengineconf
import pwd
import grp
import shutil
import time

PROJECT_ROOT = getattr(settings, "PROJECT_ROOT", None)
APPS_ROOT = PROJECT_ROOT + "/apps/caengine/script"
sys.path.append(APPS_ROOT)
import custom # depends on site
import subprocess
sys.path.append(PROJECT_ROOT)
from apps.camodels.modelsframe.personnel import Company, Team, Employee
from django.core.exceptions import ObjectDoesNotExist

APPS_ROOT = PROJECT_ROOT + "/apps/caengine/bin"
sys.path.append(APPS_ROOT)
import caengineconf

# hjkim 20170724 mysql import
import pymysql
pymysql.install_as_MySQLdb()

from subprocess import Popen
from shutil import copyfile

reload(sys)
sys.setdefaultencoding('utf8')

def Run():
	if True:
		cfg = caengineconf.config(PROJECT_ROOT + 'apps/caengine/etc/caengined.conf', False)
		os.putenv('NLS_LANG','KOREAN_KOREA.KO16MSWIN949')

		# MySQL
		con = pymysql.connect(host='130.10.200.129', user='nacview', password='view!@#123', db='DBN_IPPlus', charset='utf8')
		cursor = con.cursor()

		cursor.execute("select NM_IPSTR, MAC, USER_ID, USER_NAME, USER_DEPT_1, USER_DEPT_2, USER_DEPT_3, DEPT_CD, LoginTime from user_view3")

		uifw = open(cfg.usersystmp_inf, 'w')
		line = []
		userarray= [' ' for i in range(30000)]
		notAppendCnt = 0
		data = []

		while(True):
			data=cursor.fetchone()
			if (data == None):
				break
			loginip = data[0]
			usermac = data[1]
			userid = data[2]
			username = data[3]
			userdept1 = data[4]
			userdept2 = data[5]
			userdept3 = data[6]
			deptid = str(data[7])
			logintime = data[8]

			existFlag = False
 			uifr = open(cfg.usersys_inf, 'r')
			for paragraph in uifr:
				lines = paragraph.split('\n')
				for each_line in lines:
					line = each_line.split('\t')
					if(line[0].find(userid) >= 0 and line[10].find(loginip) >= 0):
						existuserid = line[0]
						existusername = line[1]
						winos = line[2]
						osversion = line[3]
						x86 = line[4]
						syslocale = line[5]
						inputlocale = line[6]
						netruntime = line[7]
						agent = line[8]
						existloginip = line[9]
						existlogintime = line[10]
						existFlag = True
						break
				if existFlag == True:
					break
			uifr.close()
						
			s = ""
			for cnt in range(0,30000):
				if (userarray[cnt][0] == ' '):
					notAppendCnt = cnt
					break
				else:
					line = userarray[cnt].split('\t')
					if existFlag == False:				
						s = ('\t').join([userid,username,winos,osversion,x86,syslocale,inputlocale,netruntime, agent, existloginip + " " + loginip, existlogintime + "^" + logintime])
					else:
						s = ('\t').join([userid,username," "," "," "," "," "," "," ",  line[9], line[10]])

					userarray[cnt] = s
					print s
		con.commit()
		con.close()

		for user in userarray:
			if (user != ' '):
				uifw.write("%s\n" % user)

		uifw.close()
		currentTime = datetime.datetime.today()
		usersysforback = cfg.usersys_inf + "." + currentTime.strftime("%Y%m%d")
		shutil.copy(cfg.usersys_inf, usersysforback)
		shutil.copy(cfg.usersystmp_inf, cfg.usersys_inf)

		return True


if __name__ == "__main__":
	if Run():
		sys.exit(0)
	else:
		sys.exit(1)
