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

		# NAC MySQL DB 접속
		con = pymysql.connect(host='130.10.200.129', user='nacview', password='view!@#123', db='DBN_IPPlus', charset='utf8')
		cursor = con.cursor()

		# user_view4 table 정보 Query
		cursor.execute("select NM_IPSTR, MAC, USER_ID, USER_NAME, LoginTime, Email from user_view4")

		# mailtmp.inf 파일 삭제 후 신규 생성
		RemoveFile(infPath + '/mailtmp.inf');
		uifw = open(infPath + '/mailtmp.inf', 'w')
		
		# 사용자 ID, mail 정보을 담을 30,000개의 배열을 잡아줌, 부산은행 사용자는 약 4,000명
		userarray= [' ' for i in range(30000)] 
		AppendCnt = 0
		
		uifrdata = ''
		if os.path.exists(infPath + '/mailinfo.inf'):
 			uifr = open(infPath + '/mailinfo.inf', 'r')
			uifrdata = uifr.read(-1)
		else:
 			uifr = open(infPath + '/mailinfo.inf', 'w')
		uifr.close

		line = [] # 개별사용자 버퍼
		data = [] # user_view4 table의 한 열 (one row)
		while(True):
			data=cursor.fetchone()
			if (data == None):
				break

			userid = data[2]
			usermail = data[5]
			existFlag = False

			# mailinfo.inf와 비교 후 사용자가 이미 등록되어 있으면 mail 정보 변경에 따라 existusermail string 에 저장
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

			# 받아온 사용자 ID, mail 정보를 tab으로 묶어 s string에 전달
			s = ""
			if existFlag == True: # mailinfo.inf에 이미 있으면
				s = ('\t').join([existuserid,existusermail])
			else: # 없으면
				s = ('\t').join([userid,usermail])
			print 'user mail: ' + s	
			# s string 을 미리 잡아둔 array에 순차적으로 전달
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
		# DB 닫기
		con.commit()
		con.close()

		# 갱신된 사용자 정보 mailtmp.inf에 저장
		for user in userarray:
			if (user != ' '):
				uifw.write("%s\n" % user)
		uifw.close()

		# mailtmp.inf의  ownership을 corebrdg로 변경
		uid = pwd.getpwnam("corebrdg").pw_uid
		gid = grp.getgrnam("corebrdg").gr_gid
		os.chown('/home/DATA/INF/mailtmp.inf', uid, gid)

		# mailinfo.inf 파일을 당일 날짜로 백업
		currentTime = datetime.datetime.today()
		usersysforback = infPath + '/mailinfo.inf' + "." + currentTime.strftime("%Y%m%d")
		shutil.copy(infPath + '/mailinfo.inf', usersysforback)

		# mailinfo.inf 파일 삭제 후 mailtmp.inf파일을 mailinfo.inf로 복사
		RemoveFile(infPath + '/mailinfo.inf');
		shutil.copy(infPath + '/mailtmp.inf', infPath + '/mailinfo.inf')

		# mailinfo.inf의  ownership을 corebrdg로 변경
		os.chown(infPath + '/mailinfo.inf', uid, gid)

		return True


if __name__ == "__main__":
	if Run():
		sys.exit(0)
	else:
		sys.exit(1)
