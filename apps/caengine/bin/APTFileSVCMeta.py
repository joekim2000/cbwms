#! /usr/bin/python
# coding: utf-8
#=========================================================================================
# Meta Info
#=========================================================================================
import os
import shutil
import datetime
import hashlib
import glob

linebreak = '\t\n'
div = '\t'

class Info():
	"""object <-> text file, meta file handling"""
	def __init__(self, fileName='', userid=''):
		self.ID = userid
		self.Load(fileName)

	def Load(self, fileName):
		if fileName == '':
			return
		if (not os.path.exists(fileName)):
			print 'File Not Founs: ' + fileName
			
		# Open file
		msgFile = open(fileName)
		msg = msgFile.read(-1)
		msgFile.close
		lines = msg.split(linebreak)

		aprlist = []
		filelist = []
		result = {}
	
		for eachline in lines:
			if (eachline[3] != '\t'):
				continue
			key = eachline[:3]
			if (key == 'APR') or (key == 'APH') or (key == 'APT'): # 일반 승인, 후결, 당직자
				apr = APR(key, eachline)
				aprlist.append(apr)
			elif (key == 'FIL'):	# 복수개가 나올수 있음
				fil = FIL(eachline)
				filelist.append(fil)
			elif (key == 'COM'):
				self.COM = COM(eachline)
			elif (key == 'REQ'):
				self.REQ = REQ(eachline)
	
		self.APR = aprlist
		self.FIL = filelist

	def Save(self, path, ext):
		if not os.path.exists(path):
			os.makedirs(path)

		filename = self.COM.date + "-" + self.COM.time + '-' + self.APR[0].id + "." + ext
		msg = self.MakeMessage(datetime.datetime.now(), '')

		with open(path + '/' + filename + 'tmp', 'w') as file:
			file.write(linebreak.join(msg))
			
		# 파일 암호화
		newfilename = self.MsgEncrypt(path + '/' + filename + 'tmp')
			
		# 권한 변경, 
		# uid = pwd.getpwnam("corebrdg").pw_uid
		# gid = grp.getgrnam("corebrdg").gr_gid
		# os.chown(newfilename, uid, gid)
			
		# 대상 파일로 확장자 변경		
		shutil.move(newfilename, newfilename[:-3])
		return newfilename[:-3]

	def Save2(self, path, ext):
		if not os.path.exists(path):
			os.makedirs(path)

		filename = self.COM.date + "-" + self.COM.time + "." + ext
		msg = self.MakeMessage(datetime.datetime.now(), '')
		
		newfilename = path + '/' + filename + 'tmp'
		
		with open(path + '/' + filename + 'tmp', 'w') as file:
			file.write(linebreak.join(msg))
		

		# 대상 파일로 확장자 변경		
		shutil.move(newfilename, newfilename[:-3])
		return newfilename[:-3]


	def DeleteMetaAndAttachment(self):
		return

	def DeleteWaitForFile(self, getPath):
		if self.COM.type == "Request":
			ext = self.GetExt()
			fpath = getPath + "/" + self.ID
			filename = self.COM.date + "-" + self.COM.time + "-*" + ext
			for fl in glob.glob(fpath + '/' + filename):
				os.remove(fl)

	def CreateWaitForFile(self, getPath, message = ''):
		if self.COM.type == "Request":
			self.DeleteWaitForFile(getPath)
			self.COM.type = "WaitForFile"
			tmp = self.REQ.message
			if (message != ''):
				self.REQ.message = message
			ext = self.GetExt()
			self.Save(getPath + "/" + self.ID, ext)
			self.COM.type = "Request"
			self.REQ.message = tmp

	def GetExt(self):
		ext = 'REQ'
		if (len(self.APR) == 1) and (self.APR[0].id == self.REQ.id) and (self.APR[0].type == 'Approve'):
			ext = 'ANS'
		return ext


	def MakeMessage(self, d, issue):
		msg = []	
		logDate = d.strftime("%Y%m%d")
		logTime = d.strftime("%H%M%S%f")[:7]
		msg.append(div.join(['VER', '1.0', self.COM.type, logDate, logTime, issue]))
		
		if self.COM != None:
			msg.append(self.COM.Get())

		if self.REQ != None:
			msg.append(self.REQ.Get())
		
		if self.APR != None:
			for apr in self.APR:
				msg.append(apr.Get())
				
		if self.FIL != None:
			for file in self.FIL:
				msg.append(file.Get())
		return msg

	def MsgDecrypt(self, name, msgfilename):
		# Get hash Key
		eachname = name.split('-')
		
		# hash key eachname[2]
		hash = eachname[len(eachname) - 1]
		last2 = hash[-2]
		last1 = hash[-1]
		idx1 = int(last1, 16)
		idx2 = int(last2, 16)
		last1 = hash[idx1]
		last2 = hash[idx2]
		hashkey = hash[:idx1] + last2 + hash[idx1 + 1:]
		hashkey = hash[:idx2] + last1 + hash[idx2 + 1:]
		
		#if cfg.secure_on:
		#	os.system('/opt/JionLab/fcp2/bin/ms_crypt -d -K ' + hashkey + ' ' + msgfilename)	
			
		hash2 = GetHash(msgfilename)
		if (hash2 != hash):
			print '파일 해쉬: ' + name + ',' + hash + ',' + hash2

		return hash2 == hash
		
	def MsgEncrypt(self, msgfilename):
		# Get hash Key
		hash = self.GetHash(msgfilename)
		
		# hash key eachname[2]
		last2 = hash[-2]
		last1 = hash[-1]
		idx1 = int(last1, 16)
		idx2 = int(last2, 16)
		# print last2, last1, idx1, idx2
		# print eachname[2]
		last1 = hash[idx1]
		last2 = hash[idx2]
		hashkey = hash[:idx1] + last2 + hash[idx1 + 1:]
		hashkey = hashkey[:idx2] + last1 + hashkey[idx2 + 1:]
		
		#if cfg.secure_on:
		#	os.system('/opt/JionLab/fcp2/bin/ms_crypt -e -K ' + hashkey + ' ' + msgfilename)
			
		name, ext = os.path.splitext(msgfilename)
		os.rename(msgfilename, name + '-' + hash + ext)
		return name + '-' + hash + ext

	def GetHash(self, filename):
		md5 = hashlib.sha256()
		with open(filename, 'rb') as f:
			for chunk in iter(lambda: f.read(8192), b''):
				md5.update(chunk)
		md5s = self.asctohex(md5.digest())
		return md5s

	def asctohex(self, string_in):
		a = ""
		for x in string_in:
			a = a + ("0"+((hex(ord(x)))[2:]))[-2:]
		return(a)

# 공통 데이터	
class COM(object):
	def __init__(self, msg = ''):
		self.head = 'COM'
		self.Set(msg)
		
	def Set(self, msg):
		eachdata = DataValid(self.head, msg, 5)
		self.type = eachdata[1]
		self.direction = eachdata[2]
		self.date = eachdata[3]
		self.time = eachdata[4]
	
	def Get(self):
		return div.join([self.head, self.type, self.direction, self.date, self.time])

# 신청자 데이터
class REQ(object):
	def __init__(self, msg = ''):
		self.head = 'REQ'
		self.Set(msg)
		
	def Set(self, msg):
		eachdata = DataValid(self.head, msg, 8)
		self.id = eachdata[1]
		self.name = eachdata[2]
		self.dept_code = eachdata[3]
		self.dept_name = eachdata[4]
		self.jikgeup = eachdata[5]
		self.ip = eachdata[6]
		self.message = eachdata[7]
	
	def Get(self):
		return div.join([self.head, self.id, self.name, self.dept_code, self.dept_name,
						 self.jikgeup, self.ip, self.message])

# 승인자 데이터
class APR(object):
	def __init__(self, head, msg = ''):
		self.head = head
		self.Set(msg)
		
	def Set(self, msg):	
		eachdata = DataValid(self.head, msg, 11)
		if eachdata[1] == '':
			eachdata = DataValid(self.head, msg, 10)
		self.id = eachdata[1]
		self.name = eachdata[2]
		self.dept_code = eachdata[3]
		self.deptname = eachdata[4]
		self.jikqeup = eachdata[5]
		self.type = eachdata[6]
		self.date = eachdata[7]
		self.time = eachdata[8]
		self.rejectmsg = eachdata[9]
		if (len(eachdata) >= 11):
			self.ip = eachdata[10]
		else:
			self.ip = '0.0.0.0'
	def Get(self):
		return div.join([self.head, self.id, self.name, self.dept_code, self.deptname,
						 self.jikqeup, self.type, self.date, self.time, self.rejectmsg, self.ip])

# 파일 데이터
class FIL(object):
	def __init__(self, msg = ''):
		self.head = 'FIL'
		self.Set(msg)
		
	def Set(self, msg):
		eachdata = DataValid(self.head, msg, 7)
		self.aliasname = eachdata[1]
		self.nSize = eachdata[2]
		self.nHash = eachdata[3]
		self.eSize = eachdata[4]
		self.eHash = eachdata[5]
		self.name = eachdata[6]
	
	def Get(self):
		return div.join([self.head, self.aliasname, self.nSize, self.nHash,
						 self.eSize, self.eHash, self.name])

# 메타 데이터의 한 줄이 유효한지 검사
def DataValid(head, msg, length):
	eachdata = msg.split(div)
	if (eachdata[0] != head) or (len(eachdata) != length):
		eachdata = []
		eachdata.append(head)
		for i in range(length - 1):
			eachdata.append('')
			
	return eachdata

#--------------------------------------------------------------
#	Test
#--------------------------------------------------------------
if __name__ == "__main__":
	meta = MetaInfo('Temp/test.REQ')
	print meta.COM.id
	print meta.COM.Get()
	print meta.REQ.Get()
	print len(meta.APR), meta.APR[0].Get()
	print len(meta.FIL), meta.FIL[0].Get()