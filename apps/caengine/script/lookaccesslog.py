#! /usr/bin/python
# coding: utf-8
##########################################################
# site dependent user import script
##########################################################

import sys
import os
# Oracle
#import cx_Oracle
import time
import datetime
#from datetime import datetime
import pwd
import grp

# hjkim 20170724 mysql import
import pymysql
pymysql.install_as_MySQLdb()

from subprocess import Popen
from shutil import copyfile

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

def CleanupPasswd():
        pwfile = '/opt/JionLab/passwd/etc/passwd'
        with open(pwfile, 'r') as pf:
                lines = pf.readlines()
        pwlines = [line.rstrip('\n') for line in open(pwfile)]

        usfile = '/opt/JionLab/caengine/etc/user.dat'
        with open(usfile, 'r') as uf:
                lines = uf.readlines()
        uslines = [line.rstrip('\n') for line in open(usfile)]

	inipwfile = '/opt/JionLab/passwd/etc/initpasswd'
        fnw = open(inipwfile, 'w')

        ussplit = []
        pwsplit = []
        for linepw in pwlines:
                pwsplit = linepw.split(':')
                for lineus in uslines:
                        ussplit = lineus.split(',')
                        if ussplit[2] == pwsplit[0]:
                                fnw.write(linepw + '\r\n')
        fnw.close()
        pf.close()
        uf.close()

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

def Run():

        if True:
                os.putenv('NLS_LANG','KOREAN_KOREA.KO16MSWIN949')

                # MySQL
		dbExist = False
		con = pymysql.connect(user="root", password="Qwer1234!@#$")
		cursor = con.cursor()
		cursor.execute("show databases;") 
		dbase = cursor.fetchall()
		for (db_name,) in dbase:
			if db_name == 'access':
				dbExist = True
		if dbExist == False:
			cursor.execute('CREATE DATABASE access;')
	                print("DB 생성 완료")
		else:
	                print("DB 확인 완료")

		con.commit()
		con.close()

                userExist = False
                con = pymysql.connect(user="root", password="Qwer1234!@#$")
                cursor = con.cursor()
                cursor.execute("select * from mysql.user where user='logrequest';")
                user = cursor.fetchall()
		for tup in user:
	                if tup[1] == "logrequest":
        	        	userExist = True

                if userExist == False:
                        cursor.execute("CREATE USER 'logrequest'@'localhost' IDENTIFIED BY 'Qwer1234!@#$';")
                        cursor.execute("GRANT ALL PRIVILEGES ON *.* TO 'logrequest'@'localhost' WITH GRANT OPTION;")
                        cursor.execute("CREATE USER 'logrequest'@'%' IDENTIFIED BY 'Qwer1234!@#$';")
                        cursor.execute("GRANT ALL PRIVILEGES ON *.* TO 'logrequest'@'%' WITH GRANT OPTION;")
                        cursor.execute("FLUSH PRIVILEGES;")
                        print("User 생성 완료")
                else:
                        print("User 확인 완료")

                con.commit()
                con.close()

		tblExist = False
		con = pymysql.connect(user='root', password='Qwer1234!@#$', db='access', charset='utf8')
		cursor = con.cursor()
		cursor.execute("show tables from access;") 
		table = cursor.fetchall()
		for (tbl_name,) in table:
			if tbl_name == 'access':
				tblExist = True
		if tblExist == False:
			query = "CREATE TABLE IF NOT EXISTS access (시간 varchar(32) NOT NULL, 주기 int(3) NOT NULL, 접속자 varchar(15) NOT NULL, 상태 varchar(24) NOT NULL, 접속량 int(16) NOT NULL, 접속방식 varchar(16) NOT NULL, 도메인 varchar(320) NOT NULL)"
			cursor.execute(query)
	                print("Table 생성 완료")
                else:
	                print("Table 확인 완료")
		con.commit()
		con.close()

		con = pymysql.connect(user='root', password='Qwer1234!@#$', db='access', charset='utf8')
		cursor = con.cursor()
		currentTime = datetime.datetime.today()
		TwentyFourHours = datetime.timedelta(hours=24)
		BeforeTwentyFourHours = currentTime - TwentyFourHours
		logforimport = "access.log." + BeforeTwentyFourHours.strftime("%Y%m%d")

		pwfile = '/var/log/JionLab/fbrdg/' + logforimport
		with open(pwfile, 'r') as pf:
			loglines = pf.readlines()
			#loglines = [line.rstrip('\n') for line in open(pwfile)]

		sql = """insert into access(시간,주기,접속자,상태,접속량,접속방식,도메인) values (%s, %s, %s, %s, %s, %s, %s)"""
		splitline = []
		getlines = ""
		values = []
                for logline in loglines:
			getlines = " ".join(logline.split())
			splitline = getlines.split(' ')
			Date, Time, Duration, UserIP, Status, Byte, Type, Domain = splitline
			splitTime = Time.split('.')
			DateTime = datetime.datetime.strptime(Date + ' ' + splitTime[0], '%d/%b/%Y %H:%M:%S')
			dstr = DateTime.strftime("%d/%b/%Y %H:%M:%S")
			values += [(dstr, Duration, UserIP, Status, Byte, Type, Domain)]
		cursor.executemany(sql, values)
		print "succeed"
		con.commit()
		con.close()

		'''	
		#con = pymysql.connect(host='localhost', user='root', password='Qwer1234!@#$', db='access', charset='utf-8')
                cursor = conn.cursor()
                cursor.execute("SELECT DISPLAY_NAME, PERSON_CODE, ENTER_DATE, UNIT_NAME, UNIT_CODE, TITLE_NAME, TITLE_CODE, LEVEL_NAME, LEVEL_CODE, EMAIL FROM ORG_PERSON_VDI")
                row = cursor.fetchone()

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
		'''

                return True


if __name__ == "__main__":
        if Run():
                sys.exit(0)
        else:
                sys.exit(1)

