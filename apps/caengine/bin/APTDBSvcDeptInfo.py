#! /usr/bin/python
# coding: utf-8
#=========================================================================================
# User Table Access
#=========================================================================================
import DB

class DeptInfo(DBUtil):
	"""승인 위임"""
	def __init__(self, hDB = None, logger = None):
		if (hDB == None):
			return
		
		self.hDB = hDB
		DBUtil.__init__(logger, 'DEPT')
		self.logger = logger
		self.__CreateTable()
		self.qryCreate = 'CREATE TABLE IF NOT EXISTS DeptInfo (id VARCHAR(20) PRIMARY KEY, name text, uDeptId VARCHAR(20),datekey text)'
		#self.qryExist = 'SELECT Count(*) FROM FBMandate WHERE approverID="{{app}}" and mandateID="{{man}}" and mStart="{{st}}" and mStart="{{en}}"'
		self.qryInsert = 'INSERT INTO DeptInfo VALUES ("{{id}}", "{{name}}", "{{uId}}", "{{dkey}}")'
		self.qryUpdate = 'UPDATE DeptInfo SET name="{{name}}", uDeptId="{{uId}}", datekey="{{dkey}}" WHERE id="{{id}}")'
		self.qryDelete = 'DELETE From DeptInfo WHERE datekey<>"{{dkey}}"'
		self.qryFind = 'SELECT * FROM DeptInfo WHERE id="{{ID}}"'

	def __CreateTable(self):
		'''사용자 테이블 생성'''
		if (self.hDB == None):
			return

		self.logger.debug('Create Table')
		cr = self.hDB.cursor()
		cr.execute(self.qryCreate)

	def __getQuery(self, qry, userid, name, uId, dkey):
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

