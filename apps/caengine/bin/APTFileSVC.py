#! /usr/bin/python
# coding: utf-8
#=========================================================================================
# File PreProcess Access Module
#=========================================================================================
import os
import time
import shutil
import datetime
import subprocess

def CreateDirectory(newDir):
	if not os.path.exists(newDir):
		os.mkdir(newDir)

class Inspection():
	def __init__(self, cfg, logger):
		self.cfg = cfg
		self.logger = logger

	def Start(self, metainfo):
		'''	통합승인 적용방법
			파일을 모두 /DATA/PUT/DEXT/.... 로 복사한다
			metainfo.REQ.id = DEXT
			metainfo.FIL 에 파일 목록을 넣는다. 단, aliasname에 파일명을 활당한다.
			불러주고 기다린다.
			
		'''
		result = self.CheckFcp2(metainfo)

		if self.cfg.FileInspection.Vaccine and result:
			result = self.AntiVirus(metainfo)

		if self.cfg.FileInspection.APT and result:
			CreateDirectory(self.cfg.APT.Path)
			CreateDirectory(self.cfg.APT.ScanPath)
			CreateDirectory(self.cfg.APT.SuccessPath)
			CreateDirectory(self.cfg.APT.MalPath)
			CreateDirectory(self.cfg.APT.UnknownPath)
			result = self.APT(metainfo)

		if self.cfg.FileInspection.SEED256 and result:
			result = self.SEED256(metainfo)
 
	def CheckFcp2(self, metainfo):
		'''파일이 모두 있는 지 확인한다'''
		self.logger.info(metainfo.REQ.id, 'Fcp2: Start')
		metainfo.CreateWaitForFile(self.cfg.Data.Path + '/GET/', 'Fcp2 전송 확인중')
		hasfcp2 = True
		timelist = {}
		result = True
		while hasfcp2 and result:
			hasfcp2 = False
			for eachinfo in metainfo.FIL:
				filename = self.cfg.Data.Path + '/PUT/' + metainfo.REQ.id + '/' + eachinfo.aliasname
				if os.path.exists(filename + '.fcp2'):
					self.logger.info(metainfo.REQ.id, 'Fcp2: ' + filename)
					mtime = os.path.getmtime(filename + '.fcp2')
					if eachinfo.aliasname in timelist:
						if mtime == timelist[eachinfo.aliasname]:
							result = False
							self.logger.error(metainfo.REQ.id, 'Fcp2: maybe transfer not completed. ' + filename)
							break
					timelist[eachinfo.aliasname] = mtime
					# 변화가 없으면 에러처리하고 나간다.
					hasfcp2 = True
			if hasfcp2:
				time.sleep(2)	# 2초 기다린다.
		self.logger.info(metainfo.REQ.id, 'Fcp2: Complete')
		return result

	def AntiVirus(self, metainfo):
		'''목록에 있는 파일을 모두 검사한다.'''
		self.logger.info(metainfo.REQ.id, 'VAC: Start')
		result = True
		metainfo.CreateWaitForFile(self.cfg.Data.Path + '/GET/', '바이러스 검사중')
		for eachinfo in metainfo.FIL:
			filename = self.cfg.Data.Path + '/PUT/' + metainfo.REQ.id + '/' + eachinfo.aliasname
			if os.path.exists(filename):
				self.logger.debug(metainfo.REQ.id, 'VAC: Check ' + filename)
				p = subprocess.call([ 'python', self.cfg.FileInspection.AVscript, filename])
				if p == 1:
					self.logger.info(metainfo.REQ.id, 'VAC: Suspected ' + filename)
					shutil.move(filename, filename + ' (virus suspected - quarantined)')
					result = False
					break
			else:
				self.logger.error(metainfo.REQ.id, 'VAC: File Not Found. ' + filename)

		# 문제가 있는 경우 파일이름을 변경한다. 
		self.logger.info(metainfo.REQ.id, 'VAC: Complete')
		return result

	def APT(self, metainfo):
		'''목록에 있는 파일을 모두 APT 경로에 복사한다. 검사가 끝나기를 기다린다.'''
		self.logger.debug(metainfo.REQ.id, 'APT: Start')
		metainfo.CreateWaitForFile(self.cfg.Data.Path + '/GET/', '지능형 위험요소 검사 진행중')
		#metainfo.CreateWaitForFile(self.cfg.Data.Path + '/GET/', '지능형 지속 가능 위협 검사중')
		result = True

		# 파일을 Scan 경로에 모두 복사한다.
		for eachinfo in metainfo.FIL:
			filename = self.cfg.Data.Path + '/PUT/' + metainfo.REQ.id + '/' + eachinfo.aliasname
			if os.path.exists(filename):
				shutil.copy(filename, self.cfg.APT.ScanPath + '/' + metainfo.REQ.id + '~' + eachinfo.aliasname)
				self.logger.debug(metainfo.REQ.id, 'APT: scan ' + filename)		
			else:
				self.logger.error(metainfo.REQ.id, 'File Not Found. ' + filename)
				result = False
		if not result:
			self.APTDelete(metainfo)
			return result

		# 결과 경로를 감시해서 모든 파일이 나타나는지 확인한다.
		st = datetime.datetime.now()
		isScan = True
		isTimeout = False
		while isScan and (not isTimeout):
			isScan = False
			for eachinfo in metainfo.FIL:
				filename = '/' + metainfo.REQ.id + '~' + eachinfo.aliasname
				if os.path.exists(self.cfg.APT.SuccessPath + filename):
					self.logger.debug(metainfo.REQ.id, 'APT: Success ' + filename)
				elif os.path.exists(self.cfg.APT.MalPath + filename):
					self.logger.debug(metainfo.REQ.id, 'APT: Mal ' + filename)
				elif os.path.exists(self.cfg.APT.UnknownPath + filename):
					self.logger.debug(metainfo.REQ.id, 'APT: Unknown ' + filename)
				else:
					self.logger.debug(metainfo.REQ.id, 'APT: wait scan ' + filename)
					ts = datetime.datetime.now() - st
					isTimeout = (ts.seconds > self.cfg.APT.Timeout)
					isScan = True
			if isScan and (not isTimeout):
				time.sleep(5)	# 5초 대기

		if isTimeout:
			self.logger.info(metainfo.REQ.id, 'APT: Timeout')
		else:
			# Change FileName
			for eachinfo in metainfo.FIL:
				srcfilename = self.cfg.Data.Path + '/PUT/' + metainfo.REQ.id + '/' + eachinfo.aliasname
				filename = '/' + metainfo.REQ.id + '~' + eachinfo.aliasname
				if os.path.exists(self.cfg.APT.MalPath + filename):
					self.logger.info(metainfo.REQ.id, 'APT: Suspected ' + filename)
					shutil.move(srcfilename, srcfilename + ' (APT suspected - quarantined)')
					result = False
				elif os.path.exists(self.cfg.APT.UnknownPath + filename):
					if not self.cfg.APT.UnknownIsSuccess:
						self.logger.info(metainfo.REQ.id, 'APT: Suspected ' + filename)
						shutil.move(srcfilename, srcfilename + ' (APT suspected - quarantined)')
						result = False
					else:
						self.logger.info(metainfo.REQ.id, 'APT: Unknown ' + filename)
				
		self.APTDelete(metainfo)
		self.logger.info(metainfo.REQ.id, 'APT: Complete')
		return result

	def APTDelete(self, metainfo):
		'''File name and File Size'''
		for eachinfo in metainfo.FIL:
				filename = '/' + metainfo.REQ.id + '~' + eachinfo.aliasname
				delfile = ''
				if os.path.exists(self.cfg.APT.SuccessPath + filename):
					delfile = self.cfg.APT.SuccessPath + filename
				elif os.path.exists(self.cfg.APT.MalPath + filename):
					delfile = self.cfg.APT.MalPath + filename
				elif os.path.exists(self.cfg.APT.UnknownPath + filename):
					delfile = self.cfg.APT.UnknownPath + filename
				elif os.path.exists(self.cfg.APT.ScanPath + filename):
					delfile = self.cfg.APT.ScanPath + filename
				if delfile != '':
					try:
						os.remove(delfile)
					except:
						print '1 day clear'

	def SEED256(self, metainfo):
		'''목록에 있는 파일을 모두 암호화한다.'''
		result = True
		self.logger.debug(metainfo.REQ.id, 'SEED: Start')
		metainfo.CreateWaitForFile(self.cfg.Data.Path + '/GET/', '파일 암호화중')
		for eachinfo in metainfo.FIL:
			filename = self.cfg.Data.Path + '/PUT/' + metainfo.REQ.id + '/' + eachinfo.aliasname
			if os.path.exists(filename):
				self.logger.debug(metainfo.REQ.id, 'SEED: Encrypt ' + filename)
				subprocess.call([ 'python', self.cfg.FileInspection.SEEDscript, filename])
			else:
				self.logger.error(metainfo.REQ.id, 'File Not Found. ' + filename)
		self.logger.debug(metainfo.REQ.id, 'SEED: Complete')
		return result
