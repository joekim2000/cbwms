#! /usr/bin/python
# coding: utf-8
#=========================================================================================
# DB Access Module
#=========================================================================================
import user
import Mandate

class DBUtil():
	def __init__(self, cfg, head, logger):
		self.logger = logger
		self.head = '[' + head + '] '

	def Info(self, message):
		msg = self.head + message
		if self.logger == None:
			print msg
		else:
			self.logger.info(msg) 

	def Debug(self, message):
		msg = '[' + self.head + '] ' + message
		if self.logger == None:
			print msg
		else:
			self.logger.debug(msg) 

	def getRowValues(self, cr, isOneLine = False):
		'''cursor에서 전체 row를 가져온다 '''
		result = []
		for row in cr:
			keys = row.keys()
			tmp = {}
			for i in range(0, len(keys)):
				tmp[keys[i]] = row[i]
			result.append(tmp)
			if (isOneLine): # 한 줄만 가져온다.
				break
		return result

class DBWrapper(DBUtil):
	def __init__(self, cfg, logger):
	'''DB 종류, 파일명등'''
	'''cfg = {}: key-value pair,  logger = logger 개체'''
		self.cfg = cfg
		DBUtil.__init__(cfg, logger, 'SQLite3')
		self.Info('Start')

		dbfile = self.cfg.get('etcpath','/opt/JionLab/caengine/etc/caengine.db')
		if not os.path.exists(dbfile):
			self.Info('Create DataBase');

		conn = sqlite3.connect(dbfile)
		self.Info('Connect DataBase');
		conn.text_factory = str
		conn.row_factory = sqlite3.Row

		self.user = user.User(conn, logger)
		self.dept = DeptInfo.DeptInfo(conn, logger)
		#self.mandate = Mandate.Mandate(conn, logger)
			

#####################################################
# General Local Function


#=====================================================================================
# DB Manual Access
#=====================================================================================
if __name__ == "__main__":
	if len(sys.argv) == 2:
		if sys.argv[1] == '-v':
			Version()
		else:
			main(False, 'loop' == sys.argv[1])
	else:
		main(False, False)
