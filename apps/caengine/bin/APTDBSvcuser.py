#! /usr/bin/python
# coding: utf-8
#=========================================================================================
# User Table Access
#=========================================================================================
import DB

class User(DBUtil):
	"""승인 위임"""
	def __init__(self, hDB = None, logger = None):
		if (hDB == None):
			return
		
		self.hDB = hDB
		DBUtil.__init__(logger, 'USER')
		self.logger = logger
		self.__CreateTable()
		self.qryCreate = '''CREATE TABLE IF NOT EXISTS FBUser (id VARCHAR(20) PRIMARY KEY, name text,
							isUser boolean, isApprover boolean, isMaster boolean,
							IP text, JikGeup text, pif_id text, dept_id text, 
							OTApprover_id text, OTStart datetime, OTEnd datetime, isImport boolean, datekey text)'''
		#self.qryExist = 'SELECT Count(*) FROM FBMandate WHERE approverID="{{app}}" and mandateID="{{man}}" and mStart="{{st}}" and mStart="{{en}}"'
		self.qryInsert = 'INSERT INTO FBMandate VALUES ("{{app}}", "{{man}}" , "{{st}}" , "{{en}}", "{{key}}")'
		self.qryDelete = 'Delete From FBMandate WHERE key <> "{{key}}"'
		self.qryFind = 'SELECT * FROM FBUser WHERE id="{{ID}}"'

	def __CreateTable(self):
		'''사용자 테이블 생성'''
		if (self.hDB == None):
			return

		self.logger.debug('Create Table')
		cr = self.hDB.cursor()
		cr.execute(self.qryCreate)
		self.__AddField(cr)

	def __AddField(self, cr):
		# 승인권한 위임
		try:
			cr.execute("ALTER TABLE FBUser ADD COLUMN isAppMandate boolean")
		except:
			print 'isAppMandate Field Exist'

		# 승인권한 인사정보 연동
		try:
			cr.execute("ALTER TABLE FBUser ADD COLUMN isAppExt boolean")
		except:
			print 'isAppExt Field Exist'

	def __getQuery(self, qry, userid):
		qry = qry.replace('{{ID}}', userid)
		print qry
		return qry

	def GetUserInfo(self, userid):
		result = {}
		qry = self.__getQuery(self.qryFind, userid)
		cr = self.hDB.cursor()
		cr.execute(qry)
		rows = DB.getRowValues(cr)
		if len(rows) > 0:
			result = rows[0]
		return result

