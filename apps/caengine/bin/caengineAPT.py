#! /usr/bin/python
# coding: utf-8
#=========================================================================================
# import python module
#=========================================================================================
from os import sys, path
import os
import glob
import time
import shutil
import threading

import caengineconf

import APTConfig
import APTConfigLogSVC
import APTFileSVC
import APTFileSVCMeta

class Caengine2:
	def __init__(self):
		#=================================================================================
		# Load Configure
		etcpath = path.dirname(path.dirname(path.abspath(__file__))) + "/etc/"
		self.cfg = APTConfig.Info(etcpath + "caengine2d.conf")

		self.caenginecfg = caengineconf.config('', __name__ == "__main__")

		#=================================================================================
		# Create Directory
		APTFileSVC.CreateDirectory(self.cfg.Data.Path)
		APTFileSVC.CreateDirectory(self.cfg.Data.Path + '/PUT')
		APTFileSVC.CreateDirectory(self.cfg.Data.Path + '/PUT/PUB')
		APTFileSVC.CreateDirectory(self.cfg.Data.Path + '/PUT/PUB0')
		APTFileSVC.CreateDirectory(self.cfg.Log.Path)

		#=================================================================================
		# Create APT Directory
		if self.cfg.FileInspection.APT:
			APTFileSVC.CreateDirectory(self.cfg.APT.Path)
			APTFileSVC.CreateDirectory(self.cfg.APT.ScanPath)
			APTFileSVC.CreateDirectory(self.cfg.APT.SuccessPath)
			APTFileSVC.CreateDirectory(self.cfg.APT.MalPath)
			APTFileSVC.CreateDirectory(self.cfg.APT.UnknownPath)
				
		#=================================================================================
		# Create Logger
		self.log = APTConfigLogSVC.Log(self.cfg)
		self.prclist = {}
		self.prclist2 = {}

	#=====================================================================================
	# Run Main Loop
	def Run(self):
		cnt = 0
		# Check complete process
		for key in self.prclist.keys():
			if not self.prclist[key].isAlive():
				self.Complete(key)

		putPath = self.cfg.Data.Path + '/PUT/'
		mlist = sorted(glob.glob(putPath + 'PUB/*.m'))

		for eachfile in mlist:
			# Get MetaInfo
			spath, sfile = os.path.split(eachfile)
			tmp = sfile.split('~')
			if len(tmp) != 2:
				continue
			if (sfile in self.prclist):
				continue
			if len(self.prclist) >= self.cfg.FileInspection.MaxThread:
				break;

			metafile = putPath + tmp[0] + "/" + tmp[1] + 'sg'
			if not os.path.exists(metafile):
				continue

			# hjkim 20180619 외부망 모두 처리할 경우 시작
			meta = APTFileSVCMeta.Info(metafile, tmp[0])
			if self.caenginecfg.APTInOut:
				# hjkim 20180619 내부망/외부망 모두 처리할 경우 시작
				if meta.COM.type != 'Request':
					self.Complete(sfile)
				else:
					self.log.info(tmp[0], 'Caengine2:Start ' + tmp[1][:16])
					# Make Thread Process
					inspection = APTFileSVC.Inspection(self.cfg, self.log)
					th = threading.Thread(target=inspection.Start, args=(meta,))
					th.start()
					self.prclist[sfile] = th
				# hjkim 20180619 내부망/외부망 모두 처리할 경우 끝
			else:
				# hjkim 20180619 외부망에서 내부망 반입의 경우에만 처리할 경우 시작
				if meta.COM.direction == 'Export':
					self.Complete(sfile)
				else:
					if meta.COM.type != 'Request':
						self.Complete(sfile)
					else:
						self.log.info(tmp[0], 'Caengine2:Start ' + tmp[1][:16])
						# Make Thread Process
						inspection = APTFileSVC.Inspection(self.cfg, self.log)
						th = threading.Thread(target=inspection.Start, args=(meta,))
						th.start()
						self.prclist[sfile] = th
				# hjkim 20180619 외부망에서 내부망 반입의 경우에만 처리할 경우 시작

		#cnt = len(self.prclist)
		#if (cnt > 0):
		#	self.log.debug('ADMIN', 'Run thread ' + str(cnt))
		return cnt

	def Run2(self):
		# 통합승인용
		for key in self.prclist2.keys():
			if not self.prclist2[key].isAlive():
				# *.d 파일 삭제
				del self.prclist2[keyfile]
				os.remove(self.cfg.Data.Path + '/PUT/PUB/' + keyfile)
				self.log.info('DEXT', 'Caengine2:Complete ' + keyfile)

		putPath = self.cfg.Data.Path + '/PUT/'
		mlist = sorted(glob.glob(putPath + 'PUB/*.d'))

		for eachfile in mlist:
			# Get MetaInfo
			spath, sfile = os.path.split(eachfile)
			if (sfile in self.prclist2):
				continue
			if len(self.prclist2) >= self.cfg.FileInspection.MaxThread:
				break;
			########################################################################################################
			# dext info file to meta
			meta = APTFileSVCMeta.Info(metafile, eachfile)
			meta.REQ.id = 'DEXT'
			########################################################################################################
			self.log.info('DEXT', 'Caengine2:Start ' + sfile)
			# Make Thread Process
			inspection = APTFileSVC.Inspection(self.cfg, self.log)
			th = threading.Thread(target=inspection.Start, args=(meta,))
			th.start()
			self.prclist2[sfile] = th

		cnt = len(self.prclist2)
		if (cnt > 0):
			self.log.debug('ADMIN', 'Run Dext thread ' + str(cnt))
		return cnt

	def Start(self, nloop = 0):
		'''nloop < 0 : daemon mode'''
		self.log.info('ADMIN', 'Start Caengine2')
		self.isRun = True
		while self.isRun:
			self.Run()		
			nloop -= 1
			if nloop == 0:
				break;
			if (nloop < 0):
				nloop = -1
			time.sleep(self.cfg.Data.Sleep)

		self.isRun = False
		self.log.info('ADMIN', 'Stop Caengine2')

	def Stop(self):
		self.isRun = False

	def Complete(self, keyfile):
		shutil.move(self.cfg.Data.Path + '/PUT/PUB/' + keyfile, self.cfg.Data.Path + '/PUT/PUB0/' + keyfile)
		if keyfile in self.prclist:
			del self.prclist[keyfile]
		tmp = keyfile.split('~')
		self.log.info(tmp[0], 'Caengine2:Complete ' + tmp[1][:16])

#=========================================================================================
# Test
if __name__ == "__main__":
	caengined2 = Caengine2()
	while True:
		n = caengined2.Run()
		#print n
		if (n == 0):
			break
		time.sleep(1)
		
