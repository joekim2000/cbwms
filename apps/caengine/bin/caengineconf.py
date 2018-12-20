#! /usr/bin/python
# coding: utf-8
import os
import shutil
import datetime
import hashlib
import socket
import syslog


class config:
	def __init__(self, filename = '', isMain = False):
		syslog.openlog('FBM', syslog.LOG_PID, syslog.LOG_LOCAL0)

		__FileLocation__ = os.path.abspath(__file__)
		__CurrentPath__, __msgfile__ = os.path.split(__FileLocation__)
		self.etcPath = __CurrentPath__[:-3] + 'etc/'
		filename = self.etcPath + 'caengined.conf'

		self.mainRun = isMain
		
		# 자료전송 로그 경로
		self.sysLogPath = '/var/log/JionLab/caengine'
		
		# 전송 파일의 루트
		self.rootPath = '/home/DATA'
		
		# 승인/자료전송 서비스 데몬 폴더
		self.daemonPath = '/opt/JionLab'

		# 전송 메시지 암호화
		self.secure_on = False
		
		# 자가승인 yes or no
		self.self_approve = False

		# Extra Network(3rd Network) 사용 여부		
		self.extranet = False

		# 파일 백업 경로
		self.backup_folder = self.rootPath + '/BACKUP'

		# 기간이 지난 백업 파일들 자동 삭제
		self.backupRetentionDate = 0
		
		# 기간이 지난 로그 파일들 자동 삭제
		self.caenginelogRetentionDate = 0
		
		# 기간이 지난 파일들 자동 삭제
		self.fileRetentionDate = 0
		
		# 개인별 승인 및 신청 로그 유지
		self.personRetentionDate = 0

		# 승인된 파일들 백업
		self.file_backup = False
		
		# fcp2 operation type - single: 내부망, dual: 내부망/외부망 설치
		self.fcpmode = 'single'
		
		# 관리자 아이디.
		self.admin_id = 'admin'
		
		# 사용자 시스템 정보
		self.usersys_inf = self.rootPath + '/INF/usersystem.inf'

		# 사용자 시스템 정보 임시파일
		self.usersystmp_inf = self.rootPath + '/INF/usersystmp.inf'

		# fcp2 사용자 정보 파일
		self.fcp2_passwd = self.daemonPath + '/passwd/etc/passwd'

		# 사용자 정보 원시 파일
		self.import_file = self.rootPath + '/INF/TMP/user.dat'

 		# AD 데이터 수집 파일
		self.sysLDAP = self.daemonPath + '/INF/TMP/ldap.inf'

		 # AD 키
		self.ad_exportkey = False

		 # AD 승인여부
		self.ad_approve = 'none'

		# 자동 입력시 자동으로 지정되는 기본 정책
		self.import_policy = 'JionLab'

		# 사용자 URL 정책
		self.import_policy_uul = 'JionLab'

		# 사용자 초기 암호
		self.import_userpw = 'p@ssword1'

		# 사용할 데이터베이스 지정. sqlite3, mysql
		self.dbtype = 'mysql'
		
		# 데이터베이스 서버 도메인
		self.db_ip = ''
		
		# 데이터베이스 로그인 포트
		self.db_port = ''

		# 데이터베이스 로그인 아이디
		self.db_user = ''
		
		# 데이터베이스 로그인 패스워드
		self.db_userpw = ''
		
		# 데이터베이스 이름
		self.db_name = ''
		
		# 데이터베이스 이름
		self.db_char = 'utf8'
	
		# 메신저 또는 메일 알림 여부
		self.setAlarm = False # use mail or messanger alarm

		# 사용자정보 길이                                                       #
		self.userInfoLength = 14

		# APT 사용여부
		self.APTFlag = False

		# 내부망/외부망전체: True, 내부망: False
		self.APTInOut = False


		if not os.path.exists(filename):
			return

		cfgfile = open(filename)
		conf = cfgfile.read(-1)
		cfgfile.close
		conf2 = conf.split('\n')
		for eachconf in conf2:
			if eachconf[:1] == '#':
				continue

			eachvalue = eachconf.split() # key = value
			if len(eachvalue) != 3:
				continue
			
			if eachvalue[0] == 'log_path':
				self.sysLogPath = eachvalue[2]
			elif eachvalue[0] == 'data_path':
				self.rootPath = eachvalue[2]
			elif eachvalue[0] == 'daemon_path':
				self.daemonPath = eachvalue[2]
			elif eachvalue[0] == 'secure':
				self.secure_on = (eachvalue[2].lower() == 'yes')
			elif eachvalue[0] == 'self_approve':
				self.self_approve = (eachvalue[2].lower() == 'yes')
			elif eachvalue[0] == 'extranet':
				self.extranet =  (eachvalue[2].lower() == 'yes')
			elif eachvalue[0] == 'backup_folder':
				self.backup_folder = self.rootPath + eachvalue[2]
			elif eachvalue[0] == 'backup_retention_date':
				self.backupRetentionDate = int(eachvalue[2])
			elif eachvalue[0] == 'caenginelog_retention_date':
				self.caenginelogRetentionDate = int(eachvalue[2])
			elif eachvalue[0] == 'file_retention_date':
				self.fileRetentionDate = int(eachvalue[2])
			elif eachvalue[0] == 'person_retention_date':
				self.personRetentionDate = int(eachvalue[2])
			elif eachvalue[0] == 'file_backup':
				self.file_backup = (eachvalue[2].lower() == 'yes')
			elif eachvalue[0] == 'fcpmode':
				self.fcpmode = eachvalue[2]
			elif eachvalue[0] == 'admin_id':
				self.admin_id = eachvalue[2]				
			elif eachvalue[0] == 'usersys_inf':
				self.usersys_inf = self.rootPath + eachvalue[2]				
			elif eachvalue[0] == 'usersystmp_inf':
				self.usersystmp_inf = self.rootPath + eachvalue[2]				
			elif eachvalue[0] == 'fcp2_passwd':
				self.fcp2_passwd = self.daemonPath + eachvalue[2]
			elif eachvalue[0] == 'import_file':
				self.import_file = self.rootPath + eachvalue[2]
			elif eachvalue[0] == 'import_policy':
				self.import_policy = eachvalue[2]
			elif eachvalue[0] == 'import_policy_url':
				self.import_policy_url = eachvalue[2]
			elif eachvalue[0] == 'import_userpw':
				self.import_userpw = eachvalue[2]
			elif eachvalue[0] == 'ldap_inf':
				self.sysLDAP = self.rootPath + eachvalue[2]
			elif eachvalue[0] == 'ad_exportkey':
				self.ad_exportkey =  (eachvalue[2].lower() == 'yes')
			elif eachvalue[0] == 'ad_approve':
				self.ad_approve = eachvalue[2]
			elif eachvalue[0] == 'dbtype':
				self.dbtype = eachvalue[2]
			elif eachvalue[0] == 'db_ip':
				self.db_ip = eachvalue[2]
			elif eachvalue[0] == 'db_port':
				self.db_port = eachvalue[2]
			elif eachvalue[0] == 'db_user':
				self.db_user = eachvalue[2]
			elif eachvalue[0] == 'db_userpw':
				self.db_userpw = eachvalue[2]
			elif eachvalue[0] == 'db_name':
				self.db_name = eachvalue[2]
			elif eachvalue[0] == 'db_cahr':
				self.db_char = eachvalue[2]
			elif eachvalue[0] == 'set_alarm':
				self.setAlarm =  (eachvalue[2].lower() == 'yes')
			elif eachvalue[0] == 'userinfo_length':
				self.userInfoLength = int(eachvalue[2])
			elif eachvalue[0] == 'file_backup':
				self.filebackup = (eachvalue[2].lower() == 'yes')
			elif eachvalue[0] == 'apt_flag':
				self.APTFlag =  (eachvalue[2].lower() == 'yes')
			elif eachvalue[0] == 'apt_inout':
				self.APTInOut =  (eachvalue[2].lower() == 'yes')
		
	def prn(self, info):		
		self.TraceLog(None, None, info, "OLD")
		return

		'''
		comDate = d.strftime("%Y%m%d")		
		log = d.strftime("%m/%d/%Y") + ' ' + d.strftime("%H:%M:%S.%f") + ' ' + info
		with open(self.sysLogPath + '/' + comDate + '.log', 'a') as file:
			file.write(log + '\n')

		if self.mainRun:
			print(log)
			
		return
		'''
	def TraceLog2(self, message, bracket = ''):
		self.TraceLog(None, None, message, bracket)

	def TraceLog(self, d, info, message, bracket = ''):
		if (d == None):
			d = datetime.datetime.now()
		dtext = d.strftime("%m/%d/%Y %H:%M:%S.%f")
		btext = []
		if info != None:
			com = info.get('COM', None)
			req = info.get('REQ', None)
			if com != None:
				btext.append(com.direction)
			if req != None:
				btext.append(req.id)
		else:
			btext.append(bracket)
		txt = dtext + ' [' + ",".join(btext) + '] ' + message
		syslog.syslog(syslog.LOG_INFO | syslog.LOG_LOCAL0, '[' + ",".join(btext) + '] ' + message)

		logfile = self.sysLogPath + '/caengined.log'
		if logfile == '':
			print(txt)
		else:
			if os.path.exists(logfile):
				dt = datetime.datetime.fromtimestamp(os.path.getmtime(logfile))
			else:
				dt = d

			if dt.strftime("%Y%m%d") < d.strftime("%Y%m%d"):
				shutil.move(logfile, logfile + '.' + dt.strftime("%Y%m%d"))
			with open(logfile, 'a') as f:
				f.write(txt + '\n')

class notify:
	def __init__(self, cfg):
		self.cfg = cfg
		
	def asctohex(self, string_in):
		a = ""
		for x in string_in:
			a = a + ("0"+((hex(ord(x)))[2:]))[-2:]
		return(a)

	def GetHash(self, filename):
		md5 = hashlib.sha256()
		with open(filename, 'rb') as f:
			for chunk in iter(lambda: f.read(8192), b''):
				md5.update(chunk)
		md5s = self.asctohex(md5.digest())
		return md5s
		
	# /DATA/PUT 에 AD 정보를 업데이트 하라고 요청한다.
	def UpdateUserImport(self, msglog):
		hostname = socket.gethostname()		
		d = datetime.datetime.now()
		date = d.strftime('%Y%m%d')
		time = d.strftime('%H%M%S%f')
		msg = ('\t').join(["\xef\xbb\xbfVER", "1.0", "ADInform" , "\n"])
		msg += ('\t').join(['COM', 'ADInform', 'Export', date, time, "\n"])
		msg += ('\t').join(['REQ', 'admin', hostname,'','','', '127.0.0.1', msglog])

		src = self.cfg.rootPath + '/PUT/admin/' + date + '-' + time + '.msg'
		fn = open(src, 'w');
		fn.write(msg)
		fn.close()
		hash = self.GetHash(src)
		target = self.cfg.rootPath + '/PUT/admin/' + date + '-' + time + '-' + hash + '.msg'
		shutil.move(src, target)
		self.notify(date, time, hash)		

	# Update notify	
	def notify(self, date, time, hash):
		src = self.cfg.rootPath + '/PUT/admin/admin~' + date + '-' + time + '-' + hash + '.m'
		target = self.cfg.rootPath + '/PUT/PUB/admin~' + date + '-' + time + '-' + hash + '.m'
		fn = open(src, 'w');
		fn.write("\xef\xbb\xbf뭘까요?")
		fn.close()
		shutil.move(src, target)
