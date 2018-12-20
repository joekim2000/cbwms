#! /usr/bin/python
# coding: utf-8

#import mysql.connector
import sqlite3
from types import *
import datetime
import sys
import os
import caengineconf
import glob

header = 'CAS,ver1.0'
dbName = 'caengine'
div = '\t'

class DB:
	def __init__(self, conn):
		self.cfg.TraceLog2('Open DataBase', 'DB')
		self.conn = conn
		self.CreateTable()
	
	def __del__(self):
		self.conn.close()
		self.cfg.TraceLog2('Close DataBase', 'DB')

	# Create Database
	def CreateDataBase(self):
		return

	def CreateTable(self):
		cr = self.conn.cursor()
		
		# Create Table
		cr.execute('''CREATE TABLE IF NOT EXISTS FBPolicy (id VARCHAR(21) PRIMARY KEY, name text, pif text)''')
		cr.execute('''CREATE TABLE IF NOT EXISTS FBGroup (id VARCHAR(20) PRIMARY KEY, name text, pif_id VARCHAR(20), isImport boolean, datekey text)''')
		cr.execute('''CREATE TABLE IF NOT EXISTS FBDept (id VARCHAR(20) PRIMARY KEY, name text, group_id VARCHAR(20), pif_id VARCHAR(20), isImport boolean, datekey text)''')
		cr.execute('''CREATE TABLE IF NOT EXISTS FBUser (id VARCHAR(20) PRIMARY KEY, name text,
				  isUser boolean, isApprover boolean, isMaster boolean,
				  IP text, JikGeup text,
				  pif_id text, dept_id text, 
				  OTApprover_id text, OTStart datetime, OTEnd datetime, isImport boolean, datekey text)''')
				  # 후결 정보
		
		# extended 고객에 따라 변경 추가 되는 데이터를 넣는다.
		# 추가 값
		#	appmanager
		#		True: 관리자 승인 권한 우선, False: 동기화된 승인 권한 우선
		#	appmandate: 승인 권한 위임
		#		"": 권한 위임 없음.  A-id: 승인 권한 위임. id는 위임 받은 자.  B-date-time-id: 승인 위임 받은 자.
		#	appsync:
		#		True: 승인 권한 있음. False: 승인 권한 없음
		cr.execute("CREATE TABLE IF NOT EXISTS FBUserExtend (id VARCHAR(20) PRIMARY KEY, extvalue text, appmanager boolean, appmandate text, appsync boolean)")
				  
		# 부서별 승인자 정보				  
		cr.execute('''CREATE TABLE IF NOT EXISTS FBDApprover (dept_id VARCHAR(20), user_id VARCHAR(20), datekey text)''')
		
		# 당직자 정보
		cr.execute('''CREATE TABLE IF NOT EXISTS FBSApprover (div_id VARCHAR(20), start datetime, end datetime, id text)''')
		self.UpdateTable2(cr)

	def UpdateTable2(self, cr):
		try:
			cr.execute("ALTER TABLE FBUserExtend ADD COLUMN appmanager boolean")
			self.cfg.TraceLog2('Append appmanager', 'DB')
		except:
			self.cfg.TraceLog2('No Append appmanager', 'DB')

		try:
			cr.execute("ALTER TABLE FBUserExtend ADD COLUMN appmandate text")
			self.cfg.TraceLog2('Append appmandate', 'DB')
		except:
			self.cfg.TraceLog2('No Append appmandate', 'DB')

		try:
			cr.execute("ALTER TABLE FBUserExtend ADD COLUMN appsync boolean")
			self.cfg.TraceLog2('Append appsync', 'DB')
		except:
			self.cfg.TraceLog2('No Append appsync', 'DB')

		# 150903
 		try:
			cr.execute("ALTER TABLE FBPolicy ADD COLUMN datekey text")
			self.cfg.TraceLog2('Append FBPolicy', 'DB')
		except:
			self.cfg.TraceLog2('No Append FBPolicy', 'DB')



	# Append Field at FBUser
	def UpdateTable(self):
		cr = self.conn.cursor()
		# Append Field, extend
		try:
			cr.execute("ALTER TABLE FBUser ADD COLUMN extend string")	# 14
			self.cfg.TraceLog2('Append extend', 'DB')
		except:
			self.cfg.TraceLog2('No Append extend', 'DB')
	
	# Update Approver for other department
	def UpdateDAP(self, cr, dif_id, uif_id, datekey):
		key = "dept_id='" + dif_id + "' and user_id='" + uif_id + "'"
		cr.execute("SELECT Count(*) FROM FBDApprover WHERE " + key)
		row = cr.fetchone()
		qry = ''
		if (row == None) or (row[0] == 0):		
			qry = 'INSERT INTO FBDApprover VALUES (\'' + ('\',\'').join([dif_id, uif_id, datekey]) + '\')'
		else:
			qry = "UPDATE FBDApprover SET datekey='" + datekey + "' WHERE " + key
		cr.execute(qry)

	# 150903
	def UpdatePolicy(self, cr, id, name, pif, datekey):
		cr.execute('SELECT Count(*) FROM FBPolicy WHERE id=\'' + id + '\'')
		row = cr.fetchone()
		qry = ''
		if (row == None) or (row[0] == 0):		
			qry = 'INSERT INTO FBPolicy VALUES (\'' + ('\',\'').join([id, name, pif, datekey]) + '\')'
		else:
			# 150903
			qry = "UPDATE FBPolicy SET name=\'" + name + "\', pif=\'" + pif + "\', datekey=\'" + datekey + "\' WHERE id=\'" + id + "\'"
		cr.execute(qry)
	
	def UpdateGroup(self, cr, id, name, pif_id, isImport, datekey):
		cr.execute('SELECT Count(*) FROM FBGroup WHERE id=\'' + id + '\'')
		row = cr.fetchone()
		if (row == None) or (row[0] == 0):		
			qry = 'INSERT INTO FBGroup VALUES (\'' + ('\',\'').join([id, name, pif_id, isImport, datekey]) + '\')'
		else:
			qry = 'UPDATE FBGroup SET name=\'' + name
			if isImport == "False":
				qry = qry + '\', pif_id=\'' + pif_id 
			qry = qry + '\', isImport=\'' + isImport + '\', datekey=\'' + datekey + '\' WHERE id=\'' + id + '\''
		cr.execute(qry)

	def UpdateDept(self, cr, id, name, pif_id, group_id, isImport, datekey):
		cr.execute('SELECT Count(*) FROM FBGroup WHERE id=\'' + group_id + '\'')
		row = cr.fetchone()

		if (row == None) or (row[0] == 0):
			self.cfg.TraceLog2('Group Not Found', 'DB')
		else:
			cr.execute('SELECT Count(*) FROM FBDept WHERE id=\'' + id + '\'')
			row = cr.fetchone()
			if (row == None) or (row[0] == 0):
				qry = 'INSERT INTO FBDept VALUES (\'' + ('\',\'').join([id, name, group_id, pif_id, isImport, datekey]) + '\')'
			else:
				qry = 'UPDATE FBDept SET name=\'' + name
				if isImport == "False":
					qry = qry + '\', pif_id=\'' + pif_id 
				qry = qry + '\', isImport=\'' + isImport + '\', datekey=\'' + datekey + '\' WHERE id=\'' + id + '\''
		cr.execute(qry)

	def UpdateUser(self, cr, id, name, isUser, isApp, isMaster, ip, jikgeup, dept_id, pif_id, isImport, datekey, isAuto):
		cr.execute('SELECT Count(*) FROM FBDept WHERE id=\'' + dept_id + '\'')
		row = cr.fetchone()
		if (row == None) or (row[0] == 0):
			self.cfg.TraceLog2('Department Not Found', 'DB')
		else:
			cr.execute('SELECT Count(*) FROM FBUser WHERE id=\'' + id + '\'')
			row = cr.fetchone()
			if (row == None) or (row[0] == 0):
				qry = 'INSERT INTO FBUser VALUES (\'' + ('\',\'').join(
							[id, name, isUser, isApp, isMaster, ip, jikgeup, pif_id, dept_id, '', '', '', isImport, datekey]) + '\')'
			else:
				cr.execute("SELECT * FROM FBUser WHERE id='" + id + "'")
				row = cr.fetchone()
				# 자동: 이름, 부서, 직급, 날짜, 자동임을 표시 만
				# 자동 아님:	AD에서 온 경우: 변경 고정되는것(권한, 아이피, 정책), 동기화 시키면 원복되는것(이름, 직급, 부서 등), 날짜 변경 안함
				#			파일에서 온 경우: 모두 업데이트
				qry = 'UPDATE FBUser SET name=\'' + name + '\','
				if not isAuto:
					qry += self.BoolConvert("isUser", isUser) + ","
					qry += self.BoolConvert("isApprover", isApp) + ","
					qry += self.BoolConvert("isMaster", isMaster) + ","
					qry += 'IP=\'' + ip + '\','
					qry += 'pif_id=\'' + pif_id + '\','
				else:
					qry += self.BoolConvert("isImport", isImport) + ","

				qry += 'JikGeup=\'' + jikgeup + '\', '
				qry += 'dept_id=\'' + dept_id + '\','				
				
				if isAuto or (row[12] == 'False'):
					qry += 'datekey=\'' + datekey + '\' '
				else:
					qry = qry[:-1]
				qry += ' WHERE id=\'' + id + '\''	
			#print qry
			cr.execute(qry)

	# appmanager: 승인 권한을 관리자에서 지정
	# isAuto: True: 관리자 프로그램, False: 인사 정보 연동
	def UpdateUserExtend(self, cr, id, extend, appmanager, appsync, appmandate, isAuto):
		cr.execute('SELECT Count(*) FROM FBUserExtend WHERE id=\'' + id + '\'')
		row = cr.fetchone()
		if (row == None) or (row[0] == 0):
			# 인사정보 연동인데, 새로 추가면 관리자 우선을 끈다
			qry = 'INSERT INTO FBUserExtend VALUES (\'' + ('\',\'').join([id, extend, appmanager, "", appsync]) + '\')'
		else:
			qry = "UPDATE FBUserExtend SET extvalue=\'" + extend + "\'"
			if isAuto:
				# 인사 정보 동기화에는 동기화 승인권만 변경
				qry += ", " + self.BoolConvert("appsync", appsync)
			else:
				# 관리자 정보 변경시에는 관리자 우선만 변경
				# hjkim 20170130 승인위임은 에이전트에서 처리되므로 DB 데이터 그대로 적용
				extend = self.SearchTable(cr, 'FBUserExtend', "id='" + id + "'")
				aextvalue = self.getRowValues(extend[0])				
				appmandate = aextvalue.get("appmandate", "")
				
				qry += ", " + self.BoolConvert("appmanager", appmanager)
				qry += ", " + self.BoolConvert("appmandate", appmandate)

			qry += ' WHERE id=\'' + id + '\''
				
		cr.execute(qry)

	def ApplyUserINF(self, userid):
		cr = self.conn.cursor()			
		cr.execute("SELECT * FROM FBUserExtend WHERE id='" + userid + "'")
		row = cr.fetchone()
		table =  self.getRowValues(row)
		# appmanager boolean, appmandate text, appsync boolean
		appman = table.get("appmanager", "True")	# 없으면 관리자 승인이 우선이다.
		appmandate = table.get("appmandate", "")	# 없으면 권한 위임 안함
		appsync = table.get("appsync", "False")		# 없으면 동기화 승인은 권한 없음

		commA = self.hasApproveRight2(cr, userid, appman, appmandate, appsync)

		# appmandate가 B-로 시작한다.
		if (commA): 
			if (appmandate != None) and (appmandate != "") and (appmandate[0:2] == "A-" or appmandate[0:2] == "B-"):
				self.ExportData(cr)

	def RemoveData(self, cr, table, isImport, datekey):
		qry = 'Delete From ' + table + ' WHERE isImport=\'' + isImport + '\' and datekey<>\'' + datekey +'\''
		cr.execute(qry)
	
	def RemoveData2(self, cr, table, datekey):
		# 150903
		qry = "Delete From " + table + " WHERE (datekey<>'" + datekey +"') or (datekey is null)"
		cr.execute(qry)

	# SQLite DB row to dictionary
	def getRowValues(self, row):
		result = {};
		if row != None:
			keys = row.keys()
			for i in range(0, len(keys)):
				result[keys[i]] = row[i]
		return result

	def hasApproveRight2(self, cr, userid, appman, appmandate, appsync):
		result = False
		if appman == None:
			appman = "True"
		if appmandate == None:
			appmandate = ""
		if appsync == None:
			appsync = "False"

		if appman == "True":
			# Manager set first
			cr.execute("SELECT * FROM FBUser WHERE id='" + userid + "'")
			row = cr.fetchone()			
			table =  self.getRowValues(row)
			result = (table.get("isApprover", "False") == "True")
		else:
			# Sync info first
			result = (appsync == "True")

		# Mandate approver higher priority
		# Check Manddate approver
		if (not result):
			# A-Approver, B-employee
			result = ((appmandate != None) and (appmandate != "") and (appmandate[0:2] == "B-"))
				
		return result

	def hasApproveRight(self, cr, userID, checkmandate = True):		
		cr.execute("SELECT * FROM FBUserExtend WHERE id='" + userID + "'")
		row = cr.fetchone()
		table =  self.getRowValues(row)
		# appmanager boolean, appmandate text, appsync boolean
		appman = table.get("appmanager", "True")	# 없으면 관리자 승인이 우선이다.
		appmandate = table.get("appmandate", "")	# 없으면 권한 위임 안함
		appsync = table.get("appsync", "False")		# 없으면 동기화 승인은 권한 없음
		# 승인 권한 위임 받은 것은 확인 안한다
		if not checkmandate:
			appmandate = ""

		return self.hasApproveRight2(cr, userID, appman, appmandate, appsync)
	
	# d : date range
	def ChangeApproverRight(self, currentUserID, mandateUserID, d):
                cr = self.conn.cursor()
                commA = self.hasApproveRight(cr, currentUserID, False)
                commB = self.hasApproveRight(cr, mandateUserID, False)

                if commA and (not commB):
                        # hjkim 20170220 승인자가 승인위임자를 여러명 저장할 수있도록 하기 위해 이미 등록된 승인 위임자도 포함해서 등록
                        cr.execute("SELECT * FROM FBUserExtend WHERE id='" + currentUserID + "'")
                        row = cr.fetchone()
                        table =  self.getRowValues(row)
                        getmandate = table.get("appmandate", "")

                        if (getmandate != None) and (getmandate != "") and (getmandate[0:2] == "A-"):
                                qry = "Update FBUserExtend Set appmandate='" + getmandate + ",A-" + mandateUserID +"'"
                        else:
                                qry = "Update FBUserExtend Set appmandate='A-" + mandateUserID +"'"

                        qry += " WHERE id='" + currentUserID + "'"
                        self.cfg.TraceLog2("query: " + qry, 'DB')
                        cr.execute(qry)

                        qry = "Update FBUserExtend Set appmandate='B-" + d + "-" + currentUserID +"'"
                        qry += " WHERE id='" + mandateUserID + "'"
                        cr.execute(qry)
                        self.conn.commit()
                        self.ExportData(cr)
                        return True
                else:
                        self.cfg.TraceLog2("승인 권한 위임 실패 " + currentUserID + " to " + mandateUserID, 'DB')
                        return False

	# 승인 권한을 회수한다.
	def RecallApproveRight(self, userid):
                cr = self.conn.cursor()
                cr.execute("SELECT * FROM FBUserExtend WHERE id='" + userid + "'")
                row = cr.fetchone()
                table =  self.getRowValues(row)
                # appmanager boolean, appmandate text, appsync boolean
                appman = table.get("appmanager", "True")        # 없으면 관리자 승인이 우선이다.
                appmandate = table.get("appmandate", "")        # 없으면 권한 위임 안함
                appsync = table.get("appsync", "False")         # 없으면 동기화 승인은 권한 없음

                # hjkim 20170220 승인위임자가 여러명인 경우의 회수를 위해
                splitman = []
                splitman = appmandate.split(',')
                for i in xrange(0,len(splitman)):
					commA = self.hasApproveRight2(cr, userid, appman, splitman[i], appsync)
					# appmandate가 B-로 시작한다.
					if (commA):
						# hjkim 20170220 승인위임자가 여러명인 경우의 회수를 위해
						if (splitman[i] != None) and (splitman[i] != "") and (splitman[i][0:2] == "A-"):
							self.cfg.TraceLog2("Clear Mandata Approver", 'DB')
							qry = "Update FBUserExtend Set appmandate='' WHERE id='" + splitman[i][2:] + "'"
							cr.execute(qry)

							qry = "Update FBUserExtend Set appmandate='' WHERE id='" + userid + "'"
							cr.execute(qry)
							self.conn.commit()
                self.ExportData(cr)

    # hjkim 20170220  외부승인자 지정 팀에서 승인위임 대상자 목록 가져오기위해
	def GetUserListExtMan(self, deptcode, userID):
		cr = self.conn.cursor()
		cr.execute("SELECT * FROM FBUser WHERE dept_id='" + deptcode + "'")
		result = []

		for row in cr:
			table =  self.getRowValues(row)
			if table != {}:
				# ID, Name, Jikguep, isApprover
				ID = table.get('id', '')
				Name = table.get('name', '')
				Jikguep = table.get('JikGeup', '')
				isApprover = table.get('isApprover', 'False')
				user =ID + '*' + Name + '*' + Jikguep + '*' + isApprover
				result.append(user)

		# hjkim 20170220 외부승인자의 처리
		# Output DAP
		rows = self.GetTable(cr, 'FBDApprover', '')
		for row in rows:
			comp = self.RowToString(row)
			if(comp[1] == userID):
				cr.execute("SELECT * FROM FBUser WHERE dept_id='" + comp[0] + "'")
				for row in cr:
					table =  self.getRowValues(row)
					if table != {}:
						# ID, Name, Jikguep, isApprover
						ID = table.get('id', '')
						Name = table.get('name', '')
						Jikguep = table.get('JikGeup', '')
						isApprover = table.get('isApprover', 'False')
						user =ID + '*' + Name + '*' + Jikguep + '*' + isApprover
						result.append(user)

		return ('\n').join(result)

	def GetUserList(self, deptcode):
		cr = self.conn.cursor()
		cr.execute("SELECT * FROM FBUser WHERE dept_id='" + deptcode + "'")
		result = []

		for row in cr:
			table =  self.getRowValues(row)
			if table != {}:
				# ID, Name, Jikguep, isApprover
				ID = table.get('id', '')
				Name = table.get('name', '')
				Jikguep = table.get('JikGeup', '')
				isApprover = table.get('isApprover', 'False')
				user =ID + '*' + Name + '*' + Jikguep + '*' + isApprover
				result.append(user)
		return ('\n').join(result)
			
	def BoolConvert(self, key, value):
		return key + "=" + value
		
	def DateToString(self, value):
		if type(value) == datetime.datetime:
			return value.strftime('%Y-%m-%d %H:%M:%S')
		else:
			return value
	
	def StringToDate(self, value):
		if type(value) == datetime.datetime:
			return value
		elif (type(value) == str) and (value != ''):
			return datetime.datetime.strptime(value,'%Y-%m-%d %H:%M:%S')		
		
		return None
	
	def SearchTable(self, cr, table, condition):
		result = []
		if condition == '':
			cr.execute("SELECT * FROM " + table)
		else:
			cr.execute("SELECT * FROM " + table + " WHERE " + condition)
	
		for row in cr:
			result.append(row)
		
		return result
		
	# DB to user.inf
	def ExportData(self, cr):
		filename = self.cfg.rootPath + '/INF/user.inf'
		fn = open(filename, 'w')
		fn.write("FB\tver1.2" + '\r\n')
		#print "FB\tver1.2"

		# Output PIF
		rows = self.GetTable(cr, 'FBPolicy', '')		
		for row in rows:
			comp = self.RowToString(row)
			tmp = ('\t').join(['PIF', comp[1], comp[2].replace(',','\t')])
			fn.write(tmp + '\r\n')

		# Output DIV
		rows = self.GetTable(cr, 'FBGroup', '')		
		for row in rows:
			comp = self.RowToString(row)
			tmp = ('\t').join(['DIV', comp[0], comp[1], comp[2]])
			fn.write(tmp + '\r\n')
			
			# Output DIF
			difs = self.SearchTable(cr, 'FBDept', "group_id='" + comp[0] + "'")
			for dif in difs:
				comp = self.RowToString(dif)
				tmp = ('\t').join(['DIF', comp[0], comp[1], comp[3]])
				fn.write(tmp + '\r\n')
				
				# Output UIF
				uifs = self.SearchTable(cr, 'FBUser', "dept_id='" + comp[0] + "'")
				for uif in uifs:
					comp = self.RowToString(uif)
					extend = self.SearchTable(cr, 'FBUserExtend', "id='" + comp[0] + "'")
					aextvalue = self.getRowValues(extend[0])

					extvalue = aextvalue.get("extvalue", "");
					appmanager = aextvalue.get("appmanager", "");
					appmandate = aextvalue.get("appmandate", "");
					appsync = aextvalue.get("appsync", "");
					if appmanager == None:
						appmanager = "False"
					if appmandate == None:
						appmandate = ""
					else:
						if len(appmandate) > 2:
							head = appmandate[0:2]
							if (head != "A-") and (head != "B-"):
								appmandate = "";
						else:
							appmandate = ""
					if appsync == None:
						appsync = "False"
					print extvalue, appsync
					tmp = ('\t').join(['UIF', comp[0], comp[1], comp[2], comp[3], comp[4], comp[5], comp[6], comp[7], extvalue, appmanager, appsync, appmandate])
					fn.write(tmp + '\r\n')
		
		# Output DAP
		rows = self.GetTable(cr, 'FBDApprover', '')		
		for row in rows:
			comp = self.RowToString(row)
			tmp = ('\t').join(['DAP', comp[0], comp[1]])
			fn.write(tmp + '\r\n')
		
		fn.close()
	
	#--------------------------------------------------------------------------
	# 141007: 정책 정보 업데이트 기능 추가
	# 모든 기존 정책 파일 삭제
	def RemovePolicyFile(self):
		for fl in glob.glob(self.cfg.rootPath + '/GET/PUB/*.rev'):
			os.remove(fl)
			
	# 정책 파일을 최신 정보로 변경해 준다.
	def UpdatePolicyFile(self, policyname, policy, revision):
		filename = self.cfg.rootPath + '/GET/PUB/' + policyname + '.' + revision + '.rev'
		filename = unicode(filename,'utf-8').encode('euc-kr')
		with open(filename, 'w') as file:
					file.write(policy)
	#--------------------------------------------------------------------------

	# user.inf 파일 정보를 읽어서 DB 에 넣어 준다.
	# 관리자 프로그램 업데이트 정보
	def ImportData(self):
		filename = self.cfg.rootPath + '/INF/user.inf'
		if not os.path.exists(filename):
			self.cfg.prn('Import User Inform: Not found ' + filename)
			return
			
		#-------------------------------------
		# 141007: 정책 정보 업데이트 기능 추가
		# 기존 정책 파일 삭제
		self.RemovePolicyFile();
		#-------------------------------------
		with open(filename, 'r') as reqFile:
			msgA = reqFile.read(-1)  # read all data
		msg = msgA.split('\r\n')
	
		d = datetime.datetime.now().strftime('%Y%m%d-%H%M%S')
		cr = self.conn.cursor()
		dept_id = ''
		div_id = ''
		for eachmsg in msg:
			eachitem = eachmsg.split(div)
			
			if eachitem[0] == 'PIF':
				pif = []
				for i in range(2,len(eachitem)):
					pif.append(eachitem[i])
				
				# 150903
				self.UpdatePolicy(cr, eachitem[1], eachitem[1], (',').join(pif), d)
				#-------------------------------------
				# 141007: 정책 정보 업데이트 기능 추가
				# 기존 정책 파일 삭제
				t = eachitem[2].split(' ') # REV:을 찾는다
				rev = 0
				for eitem in t:
					if eitem[0:3] == 'REV':
						r = eitem.split(':')
						rev = r[1]
						break;
				self.UpdatePolicyFile(eachitem[1], eachmsg, rev);
				#-------------------------------------

			elif eachitem[0] == 'DIV':
				self.UpdateGroup(cr, eachitem[1], eachitem[2], eachitem[3], 'False', d)
				div_id = eachitem[1]
			elif eachitem[0] == 'DIF':						
				self.UpdateDept(cr, eachitem[1], eachitem[2], eachitem[3], div_id, 'False', d)
				dept_id = eachitem[1]
			elif eachitem[0] == 'UIF':
				self.UpdateUser(cr, eachitem[1], eachitem[2], eachitem[3], eachitem[4],
									eachitem[5], eachitem[6], eachitem[7], dept_id, eachitem[8], 'False', d, False)
				lenstr = str(len(eachitem))
				extend = ""
				appmanager = "False"
				appsync = "False"
				appmandate = ""
				if len(eachitem) >= 10:
					extend = eachitem[9]
				if len(eachitem) >= 11:
					appmanager = eachitem[10]
				if len(eachitem) >= 12:
					appsync = eachitem[11]
				#                                       사번     승인자수동   승인장자동   승인위임      인사정보자동
				self.UpdateUserExtend(cr, eachitem[1], extend, appmanager, appsync, appmandate, False)
			elif eachitem[0] == 'DAP':
				self.UpdateDAP(cr, eachitem[1], eachitem[2], d)
		# 150903
		self.RemoveData2(cr, 'FBPolicy', d)	

		self.RemoveData(cr, 'FBGroup', 'False', d)
		self.RemoveData(cr, 'FBDept', 'False', d)
		self.RemoveData(cr, 'FBUser', 'False', d)
		self.RemoveData2(cr, 'FBDApprover', d)

		self.conn.commit()
		
	
	# 외부 인사 정보 연동용
	def ImportData2(self, filename):
		#filename = filename
		if not os.path.exists(filename):
			self.cfg.prn('Import User Inform: Not found ' + filename)
			return
		
		# 파일에서 데이터를 읽어서 DB에 업데이트 한다.
		# 단, 현재 날짜시간 데이터를 같이 넣는다
		# Import, datekey field 추가
		with open(filename, 'r') as reqFile:
			msgA = reqFile.read(-1)  # read all data
		msg = msgA.split('\r\n')
		
		d = datetime.datetime.now().strftime('%Y%m%d-%H%M%S')
		cr = self.conn.cursor()
		dept_id = ''
		div_id = ''
		for eachmsg in msg:
			eachitem = eachmsg.split(div)
			
			if eachitem[0] == 'DIV':
				self.UpdateGroup(cr, eachitem[1], eachitem[2], eachitem[3], 'True', d)
				div_id = eachitem[1]
			elif eachitem[0] == 'DIF':						
				self.UpdateDept(cr, eachitem[1], eachitem[2], eachitem[3], div_id, 'True', d)
				dept_id = eachitem[1]
			elif eachitem[0] == 'UIF':
				self.UpdateUser(cr, eachitem[1], eachitem[2], eachitem[3], eachitem[4],
									eachitem[5], eachitem[6], eachitem[7], dept_id, eachitem[8], 'True', d, True)
				extend = ""
				appmanager = "False"
				appsync = "False"
				appmandate = ""
				if len(eachitem) >= 10:
					extend = eachitem[9]
				if len(eachitem) >= 11:
					appmanager = eachitem[10]
				if len(eachitem) >= 12:
					appsync = eachitem[11]
				#                                       사번     승인자수동   승인장자동   승인위임      인사정보자동
				self.UpdateUserExtend(cr, eachitem[1], extend, appmanager, appsync, appmandate, True)
			elif eachitem[0] == 'DAP':
				self.UpdateDAP(cr, eachitem[1], eachitem[2], d)

		self.RemoveData(cr, 'FBGroup', 'True', d)
		self.RemoveData(cr, 'FBDept', 'True', d)
		self.RemoveData(cr, 'FBUser', 'True', d)
		
		self.conn.commit()
		self.ExportData(cr)

	# 당직자 설정
	def ImportSApp(self):
		filename = self.cfg.rootPath + '/INF/sapr.inf'
		
		if not os.path.exists(filename):
			return
		
		with open(filename, 'r') as reqFile:
			msgA = reqFile.read(-1)  # read all data
		msg = msgA.split('\n')
		cr = self.conn.cursor()
		
		# delete all old inform
		cr.execute("DELETE FROM FBSApprover");
		
		for eachmsg in msg:
			eachitem = eachmsg.split(div)
			st = datetime.datetime.strptime(eachitem[1],'%Y%m%d-%H%M')
			ed = datetime.datetime.strptime(eachitem[2],'%Y%m%d-%H%M')
			self.UpdateSApp(eachitem[0], eachitem[3], st, ed)
	
		self.conn.commit()		
		
	
	def GetEachPolicy(self, value):
		pif = {}
		pifs = value.split(' ')
		for eachpif in pifs:
			property = eachpif.split(':')
			if len(property) == 2:
				pif[property[0]] = property[1]
		return pif
	
	def ValidDataLength(self, rowu, reqlen):
		if rowu == None:
			return False
		if len(rowu) == 0:
			return False
		if len(rowu[0]) < reqlen:
			return False
		return True

	def FindNetPolicy(self, src, dst, pifs):
		result = None
		for eachPif in pifs:
			result = self.GetEachPolicy(eachPif)
			try:
				if (result['SRC'] == src) and (result['DST'] == dst):
					break
			except:
				result = None

		return result

	# 지정한 사용자의 정책을 가져온다
	def GetUserPolicy(self, userid):
		cr = self.conn.cursor()

		# 사용자 정책 가져오기
		rowu = self.GetTable(cr, 'FBUser', userid)
		if not self.ValidDataLength(rowu, 9): #(rowu == None): # or (len(rowu) < 9) :
			self.cfg.TraceLog2("User Not Found", 'DB')
			return ''
			
		pif_id =  rowu[0][7]			
		if type(pif_id) == unicode:
			a = u'상위'
		else:
			a = '상위'
		
		if pif_id == a:
			# 부서 정책 찾기
			rowd = self.GetTable(cr, 'FBDept', rowu[0][8])
			if rowd == None :
				self.cfg.TraceLog2("Department Not Found", 'DB')
				return ''
			pif_id = rowd[0][3]
		
		# Get Division Policy
		if pif_id == a:
			row = self.GetTable(cr, 'FBGroup', rowd[0][2])
			if rowd == None :
				self.cfg.TraceLog2("Division Not Found", 'DB')
				return ''
			pif_id = row[0][2]
			
		row = self.GetTable(cr, 'FBPolicy', pif_id)
		if row == None:
			return ''

		pif = row[0][2].split(',')		
		result = {}

		# XtraNet, 3rd Network
		result['Export2'] = self.FindNetPolicy('2','1',pif) # self.GetEachPolicy(pif[3])
		result['Import2'] = self.FindNetPolicy('2','0',pif) # self.GetEachPolicy(pif[3])
		result['Export'] = self.FindNetPolicy('0','1',pif) # self.GetEachPolicy(pif[1])
		result['Import'] = self.FindNetPolicy('1','0',pif) # self.GetEachPolicy(pif[2])
		result['XtraExport'] = self.FindNetPolicy('0','2',pif) # self.GetEachPolicy(pif[1])
		result['XtraImport'] = self.FindNetPolicy('1','2',pif) # self.GetEachPolicy(pif[2])

		if result['Export'] == None:
			result['Export'] = self.GetEachPolicy(pif[1])
		if result['Import'] == None:
			result['Import'] = self.GetEachPolicy(pif[2])

		return result
	

	def isMandateApprover(self, userid, exceptid):
		cr = self.conn.cursor()
		cr.execute("SELECT * FROM FBUserExtend WHERE id='" + userid + "'")
		row = cr.fetchone()
		table =  self.getRowValues(row)
		appid = table.get('appmandate','XXXX')
		#if appid[0] == 'A':
		return (appid !='') and (appid != ('A-'+exceptid)) and (appid[0] == 'A')
		#else:
		#	return userid

	# 부서의 승인자 목록을 가져온다
	def GetApproverList(self, dept_id, dept_name, exceptuserid = ""):
		cr = self.conn.cursor()
		cr2 = self.conn.cursor()
		cr3 = self.conn.cursor()
		d = datetime.datetime.now()
		result = []

		# 동일 부서에서 승인자 목록 가져오기
		cr.execute("SELECT * FROM FBUser WHERE dept_id='" + dept_id + "'")
		for row in cr:
			# 본인은 제외			
			if row[0] == exceptuserid:
				continue
			isApp = self.hasApproveRight(cr2, row[0])
			# 승인 권한이 있다.
			if isApp:
				if self.isMandateApprover(row[0], exceptuserid):
					continue
				table = self.getRowValues(row)
				aprlist = []
				aprlist.append("APR");
				aprlist.append(table.get("id", ""));
				aprlist.append(table.get("name", ""));
				aprlist.append(table.get("IP", "127.0.0.1"));
				aprlist.append(table.get("JikGeup", "127.0.0.1"));
				aprlist.append(dept_id);
				aprlist.append(dept_name);
				result.append((',').join(aprlist))
	
		# 타 부서인데 승인자 겸직자
		qry = "SELECT * FROM FBDApprover WHERE dept_id='" + dept_id + "'"
		cr.execute(qry)
		for row in cr:
			if row[1] == exceptuserid:
				continue			
			isApp = self.hasApproveRight(cr2, row[1])
			print row[1], isApp
			if isApp:
				cr3.execute("SELECT * FROM FBUser WHERE id='" + row[1] + "'")
				row = cr3.fetchone()
				table = self.getRowValues(row)
				if table.get("id", "") == "":
					continue
				dept_id2 = table.get("dept_id", "")
				cr3.execute("SELECT * FROM FBDept WHERE id='" + dept_id2 + "'")
				row2 = cr3.fetchone()
				table2 = self.getRowValues(row2)
				aprlist = []
				aprlist.append("APR");
				aprlist.append(table.get("id", ""));
				aprlist.append(table.get("name", ""));
				aprlist.append(table.get("IP", "127.0.0.1"));
				aprlist.append(table.get("JikGeup", "127.0.0.1"));
				aprlist.append(dept_id2);
				aprlist.append(table2.get("name",""));
				result.append((',').join(aprlist))

		# 당직자(슈퍼 승인자) 정보 가져오기
		dkey = d.strftime('%Y-%m-%d %H:%M:%S')
		qry = "SELECT * FROM FBSApprover WHERE start<='" + dkey + "' and end>='" + dkey + "'"
		cr.execute(qry)	
		for row in cr:
			dtime = self.DateToString(row[2])
				
			cr.execute("SELECT * FROM FBUser WHERE " + self.BoolConvert('isApprover', 'True') + " and id='" + row[3] + "'")
			for row2 in cr:
				# 본인은 제외
				if type(row[0]) == unicode:
					rid = row2[0].encode('utf-8')
				else:
					rid = row2[0]
				if userid != rid:
					aprtmp = (',').join(self.RowToString(['APT', row2[0], row2[1], row2[5], row2[6], rowd[0][0], rowd[0][1], dtime]))
					result.append(aprtmp)
			break

		return result

	# 지정한 사용자 관련 정보를 가져온다.
	def GetUserInform(self, userid, direction):
		cr = self.conn.cursor()
		result = []
		isHugyeul = False
		# 사용자 정보 가져오기
		success, user = self.GetData(cr, 'FBUser', userid)
		if not success:
			self.cfg.TraceLog2("User Not Found", 'DB')
			return ''
		'''
		rowu = self.GetTable(cr, 'FBUser', userid)
		
		if not self.ValidDataLength(rowu, 12): #(rowu == None):# or (len(rowu) < 9) :
			self.cfg.prn("Not Found User")
			return ''
		'''		
		
		# User Additional Information
		success, user_ext = self.GetData(cr, 'FBUserExtend', userid)
		if success:		
			appman = user_ext.get("appmanager", "True")	# 없으면 관리자 승인이 우선이다.
			appmandate = user_ext.get("appmandate", "")	# 없으면 권한 위임 안함
			appsync = user_ext.get("appsync", "False")		# 없으면 동기화 승인은 권한 없음
			isapp = self.hasApproveRight2(cr, userid, appman, appmandate, appsync)


		# 부서 정보 가져오기
		dept_id = user.get('dept_id', '')
		pif_id =  user.get('pif_id', '')
		
		success, dept = self.GetData(cr, 'FBDept', dept_id)
		if not success:
			self.cfg.TraceLog2("Department Not Found", 'DB')
			return ''

		'''
		dept_id = rowu[0][8]	
		pif_id =  rowu[0][7] #개인 정책
		rowd = self.GetTable(cr, 'FBDept', dept_id)
		if rowd == None :
			self.cfg.prn("Not Found Dept")
			return ''
		'''

		usr = (',').join(self.RowToString(['USR',  user.get('id', ''), user.get('name', ''), user.get('isUser', 'False'),
											str(isapp), user.get('isMaster', ''), user.get('IP', ''), user.get('JikGeup', ''),
											pif_id, dept.get('id', ''),dept.get('name', ''), dept.get('group_id', ''), appmandate]))
		result.append(usr)
	
		# Get User Policy
		policys = self.GetUserPolicy(userid)
		p = policys[direction].get('2PFT', None)

		# 후결 일때만 의미가 있음
		d = datetime.datetime.now()	
		st = self.StringToDate(user.get('OTStart', ''))
		ed = self.StringToDate(user.get('OTEnd', ''))
	
		# 후결인지 확인
		if (p != 'None') and (user.get('OTApprover_id', '') != '') and (type(st) == datetime.datetime) and (type(ed) == datetime.datetime) and (d >= st) and (d <= ed):
			cr.execute("SELECT * FROM FBUser WHERE id='" + rowu[0][9] + "'")
			row = cr.fetchone()
			if row != None:
				aprtmp = (',').join(self.RowToString(['APH', row[0], row[1], row[5], row[6], rowd[0][0], rowd[0][1], rowu[0][11]]))
				result.append(aprtmp)
				isHugyeul = True
		else:
			# 승인자 정보 가져오기
			print dept_id
			print userid
			listu = self.GetApproverList(dept_id, dept.get('name', ''), userid)
			for eachapp in listu:
				result.append(eachapp)

		# 정책 가져오기
		if type(pif_id) == unicode:
			a = u'상위'
		else:
			a = '상위'
		
		# Get Dept Policy
		if pif_id == a:
			pif_id = dept.get('pif_id', '')
	
		# Get Division Policy
		if pif_id == a:
			succcess, div = self.GetData(cr, 'FBGroup', dept.get('group_id', ''))
			pif_id = div.get('pif_id', '')

		success, pif = self.GetData(cr, 'FBPolicy', pif_id)
		if not success:
			return ''
		pifs = (',').join(self.RowToString(['PIF', pif.get('name', ''), pif.get('pif', '')]))
		result.append(pifs)
		
		return ('\n').join(result)

	# 지정된 자가 승인 권한이 있는지 확인
	def GetUserApprove(self, userid):
		cr = self.conn.cursor()
		rows = self.GetTable(cr, 'FBUser', userid)
		if len(rows) > 0:
			return self.RowToString([rows[0][3]])[0]
		else:
			return False

	# 당직자 설정
	def UpdateSApp(self, divid, appid, st, ed):
		cr = self.conn.cursor()
		qry = "INSERT INTO FBSApprover VALUES ('" + ("','").join([divid, st.strftime('%Y-%m-%d %H:%M:%S'), ed.strftime('%Y-%m-%d %H:%M:%S'), appid]) + "')"
		cr.execute(qry)
		self.conn.commit()

	# 후결 승인 설정
	def SetLateApprover(self, userid, appid, start, ed):
		cr = self.conn.cursor()
		cr.execute("SELECT Count(*) FROM FBUser WHERE id='" + userid + "'")
		row = cr.fetchone()
		if (row == None) or (row[0] == 0):
			return
		else:
			qry = "UPDATE FBUser SET "
			qry += "OTApprover_id='" + appid +"',"
			qry += "OTStart='" + start.strftime('%Y-%m-%d %H:%M:%S') + "',"
			qry += "OTEnd='" + ed.strftime('%Y-%m-%d %H:%M:%S') + "' "
			qry += "WHERE id='" + userid + "'"
			cr.execute(qry)			
			
		self.conn.commit()
	
	# 후결 승인자가 맞는지 확인	
	def CheckAphInfo(self, userid, appID):
		cr = self.conn.cursor()
		rowu = self.GetTable(cr, 'FBUser', userid)

		if not self.ValidDataLength(rowu, 12): #(rowu == None):# or (len(rowu) < 12) :
			self.cfg.prn("Not Found User")
			return False

		d = datetime.datetime.now()	
		st = self.StringToDate(rowu[0][10])
		ed = self.StringToDate(rowu[0][11])
	
		# 후결인지 확인	
		if (rowu[0][9] == appID) and (type(st) == datetime.datetime) and (type(ed) == datetime.datetime) and (d >= st) and (d <= ed):
			return True
		return False
				
							
	def RowToString(self, row):
		result = []
		for each in row:
			if type(each) == int:				
				if each == 1:
					result.append('True')
				else:
					result.append('False')
			elif type(each) == datetime.datetime:
				result.append(self.DateToString(each))
			elif type(each) == NoneType:
				result.append('')
			else:
				result.append(each)
			
		return result
	
	def GetData(self, cr, table, id):
		isFind = False
		result = {}
		cr.execute("SELECT * FROM " + table + " WHERE id='" + id + "'")
		
		for row in cr:
			result = self.getRowValues(row)
			isFind = True
			break;

		return isFind, result

	def GetTable(self, cr, table, id):
		result = []
		if id == '':
			cr.execute("SELECT * FROM " + table)
		else:
			cr.execute("SELECT * FROM " + table + " WHERE id='" + id + "'")
		
		for row in cr:
			result.append(row)

		return result
			
	def ShowTable(self, cr, table, id):
		rows = self.GetTable(cr, table, id)

		for row in rows:
			comp = self.RowToString(row)
			tmp = (',').join(comp)
			print tmp

# MySQL DB  Interface			
class MySQLDB(DB):
	def __init__(self, cfg):
		self.cfg = cfg
		self.cfg.TraceLog2('Connect DataBase', 'MySQL')
		self.conn = mysql.connector.connect(host=self.db_ip,user=self.cfg.db_user,passwd=self.cfg.db_userpw,charset='utf8')
		self.CreateDataBase()
		conn = mysql.connector.connect(host=self.db_ip,user=self.cfg.db_user,passwd=self.cfg.db_userpw,database=dbName,charset='utf8')
		conn.text_factory = str
		DB.__init__(self, conn)

	def CreateDataBase(self):		
		self.cfg.TraceLog2('Create DataBase', 'MySQL')
		cr = self.conn.cursor()
		cr.execute('CREATE DATABASE IF NOT EXISTS ' + dbName + ' DEFAULT CHARACTER SET utf8 COLLATE utf8_general_ci')
		cr.commit()

# SQLite DB Interface
class SQLite3DB(DB):		
	def __init__(self, cfg):
		self.cfg = cfg
		self.cfg.TraceLog2('Connect DataBase', 'SQLite3')
		dbfile = self.cfg.etcPath + 'cbengine.db'

		if not os.path.exists(dbfile):
			self.cfg.TraceLog2('Create DataBase', 'SQLite3')
		conn = sqlite3.connect(dbfile)
		conn.text_factory = str
		conn.row_factory = sqlite3.Row
			
		DB.__init__(self, conn)
	
	def BoolConvert(self, key, value):
		return key + "='" + value + "'"

	def ShowDB(self):
		cr = self.conn.cursor()
		print '--------------------------------------------'
		self.ShowTable(cr, 'FBPolicy', '')
		print
	
		print '--------------------------------------------'
		self.ShowTable(cr, 'FBGroup', '')
		print
	
		print '--------------------------------------------'
		self.ShowTable(cr, 'FBDept', '')
		print
			
		print '--------------------------------------------'	
		self.ShowTable(cr, 'FBUser', '')
		print
		
#=====================================================================================
# Test Functions	
#=====================================================================================
def Test(cfg, isDBType, isCreate, isImport, userid, otherid = ""):
	if isDBType == 'sqlite':		# SQLite3
		db = SQLite3DB(cfg)
	elif isDBType == 'mysql':		# MySQL
		db = MySQLDB(cfg)
	else:
		print 'Error'
		return
	
	if userid == 'show':
		db.ShowDB()
		sys.exit(0)
	if userid == 'GAL':
		db.GetApproverList('RDA1','RDA')
		sys.exit(0)

	if isCreate:
		db.CreateTable()
	
	if isImport:
		db.ImportData()
		db.ImportSApp()
	
	'''
	# 후결 설정
	st = datetime.datetime.strptime('2013-08-08 00:20:00','%Y-%m-%d %H:%M:%S')
	ed = datetime.datetime.strptime('2013-08-09 23:30:59','%Y-%m-%d %H:%M:%S')				
	db.SetLateApprover(userid, '80001', st, ed)
	'''
	
	'''
	# 당직자 설정
	st = datetime.datetime.strptime('2013-08-29 00:20:00','%Y-%m-%d %H:%M:%S')
	ed = datetime.datetime.strptime('2013-08-29 17:30:59','%Y-%m-%d %H:%M:%S')
	db.UpdateSApp('NH', '80001', st, ed)
	'''
	
	if (otherid == 'dept'):
		print db.GetUserList(userid)
	elif (otherid == 'recall'):
		print db.RecallApproveRight(userid)
	else:
		if otherid != "":
			# 승인 권한 변경 테스트
			db.ChangeApproverRight(userid, otherid, "141015-235959")
			db = None
			return
	
		print '------------------------------'
		print 'Export'
		print '------------------------------'
 		print db.GetUserInform(userid, 'Export')
		print '------------------------------'
		print 'Import'
		print '------------------------------'
		print db.GetUserInform(userid, 'Import')
		print '------------------------------'
		print db.GetUserApprove(userid)
		print db.CheckAphInfo(userid, '80001')
		print '-APP--------------------------'
		print db.hasApproveRight(db.conn.cursor(), userid)
		print '------------------------------'

	db = None

def Test2(cfg, isDBType):
	if isDBType == 'sqlite':		# SQLite3
		db = SQLite3DB(cfg)
	elif isDBType == 'mysql':		# MySQL
		db = MySQLDB(cfg)
	else:
		print 'Error'
		return

	cr = db.conn.cursor()
	db.ExportData(cr)
	db = None

if __name__ == "__main__":		
	cfg = caengineconf.config('', isMain = True)
	if (len(sys.argv) == 2) and sys.argv[1]=="export":
		Test2(cfg, "sqlite")
		sys.exit(0)

	if len(sys.argv) == 3:
		Test(cfg, sys.argv[1], False, False, sys.argv[2])
	elif len(sys.argv) == 4:
		Test(cfg, sys.argv[1], False, False, sys.argv[2], sys.argv[3])
	elif len(sys.argv) == 5:
		Test(cfg, sys.argv[1], sys.argv[3].lower() == 'true', sys.argv[4].lower() == 'true', sys.argv[2])
	else:
		print "usage: %s [sqlite | mysql] id create import" % sys.argv[0]
