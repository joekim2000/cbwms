#! /usr/bin/python
# coding: utf-8
##########################################################
# site dependent user import script
##########################################################

import datetime
import grp
import os
import pwd
import sys
import shutil
import time

sys.path.append("/opt/JionLab/caengine/bin")
import caengineconf

# hjkim 20170724 mysql import
import pymysql
pymysql.install_as_MySQLdb()

from subprocess import Popen
from shutil import copyfile

reload(sys)
sys.setdefaultencoding('utf8')

cfg = caengineconf.config('', __name__ == "__main__")

infPath = cfg.rootPath + '/INF'

def RemoveFile(filename):
	if os.path.exists(filename):
		os.remove(filename)

def Run():
	if True:
		cfg = caengineconf.config('/opt/JionLab/caengine/etc/caengined.conf', False)
		os.putenv('NLS_LANG','KOREAN_KOREA.KO16MSWIN949')

		# NAC MySQL DB ����
		con = pymysql.connect(host='130.10.200.129', user='nacview', password='view!@#123', db='DBN_IPPlus', charset='utf8')
		cursor = con.cursor()

		# user_view4 table ���� Query
		cursor.execute("select NM_IPSTR, MAC, USER_ID, USER_NAME, LoginTime, Email from user_view4")

		# mailtmp.inf ���� ���� �� �ű� ����
		RemoveFile(infPath + '/mailtmp.inf');
		uifw = open(infPath + '/mailtmp.inf', 'w')
		
		# ����� ID, mail ������ ���� 30,000���� �迭�� �����, �λ����� ����ڴ� �� 4,000��
		userarray= [' ' for i in range(30000)] 
		AppendCnt = 0
		
		uifrdata = ''
		if os.path.exists(infPath + '/mailinfo.inf'):
 			uifr = open(infPath + '/mailinfo.inf', 'r')
			uifrdata = uifr.read(-1)
		else:
 			uifr = open(infPath + '/mailinfo.inf', 'w')
		uifr.close

		line = [] # ��������� ����
		data = [] # user_view4 table�� �� �� (one row)
		while(True):
			data=cursor.fetchone()
			if (data == None):
				break

			userid = data[2]
			usermail = data[5]
			existFlag = False

			# mailinfo.inf�� �� �� ����ڰ� �̹� ��ϵǾ� ������ mail ���� ���濡 ���� existusermail string �� ����
			if uifrdata != '':
				lines = uifrdata.split('\n')
				for each_line in lines:
					line = each_line.split('\t')
					if(line[0].find(userid) >= 0):
						existuserid = line[0]
						if(line[1] != usermail):
							existusermail = line[1]
						else:
							existusermail = usermail
						existFlag = True
						break

			# �޾ƿ� ����� ID, mail ������ tab���� ���� s string�� ����
			s = ""
			if existFlag == True: # mailinfo.inf�� �̹� ������
				s = ('\t').join([existuserid,existusermail])
			else: # ������
				s = ('\t').join([userid,usermail])
			print 'user mail: ' + s	
			# s string �� �̸� ��Ƶ� array�� ���������� ����
			skipflag = False
			appenduser = s.split('\t')
			for oneuser in userarray:
				splituser = oneuser.split('\t')
				if splituser[0].find(appenduser[0]) >= 0:
					skipflag = True
					break
			if skipflag == False:
				userarray[AppendCnt] = s 
				AppendCnt+=1
					
		print 'Total count: ' + str(AppendCnt-1)
		print 'Finished'
		# DB �ݱ�
		con.commit()
		con.close()

		# ���ŵ� ����� ���� mailtmp.inf�� ����
		for user in userarray:
			if (user != ' '):
				uifw.write("%s\n" % user)
		uifw.close()

		# mailtmp.inf��  ownership�� corebrdg�� ����
		uid = pwd.getpwnam("corebrdg").pw_uid
		gid = grp.getgrnam("corebrdg").gr_gid
		os.chown('/home/DATA/INF/mailtmp.inf', uid, gid)

		# mailinfo.inf ������ ���� ��¥�� ���
		currentTime = datetime.datetime.today()
		usersysforback = infPath + '/mailinfo.inf' + "." + currentTime.strftime("%Y%m%d")
		shutil.copy(infPath + '/mailinfo.inf', usersysforback)

		# mailinfo.inf ���� ���� �� mailtmp.inf������ mailinfo.inf�� ����
		RemoveFile(infPath + '/mailinfo.inf');
		shutil.copy(infPath + '/mailtmp.inf', infPath + '/mailinfo.inf')

		# mailinfo.inf��  ownership�� corebrdg�� ����
		os.chown(infPath + '/mailinfo.inf', uid, gid)

		return True


if __name__ == "__main__":
	if Run():
		sys.exit(0)
	else:
		sys.exit(1)
