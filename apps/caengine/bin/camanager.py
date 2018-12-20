#! /usr/bin/python
# coding: utf-8

#=========================================================================================
# import django module
#=========================================================================================
from django.db import models
from django.forms import ModelForm
from django.conf import settings
from datetime import date, datetime

#=========================================================================================
# import python module
#=========================================================================================
import os
import shutil
import hashlib
import time
import sys
import glob
import datetime
import Queue
import traceback
# import pwd
# import grp

PROJECT_ROOT = getattr(settings, "PROJECT_ROOT", None)
from cbwms.settings import common
import caenginedb
import caengineconf
import caengineimport
import caengineAPT

APPS_ROOT = PROJECT_ROOT + "/apps/caengine/script"
sys.path.append(APPS_ROOT)
import custom # depends on site
import notify

import subprocess
sys.path.append(PROJECT_ROOT)
from apps.camodels.modelsframe.personnel import Company, Department, Team, Employee, MembershipforDept, MembershipforTeam
from django.core.exceptions import ObjectDoesNotExist

APPS_ROOT = PROJECT_ROOT + "/apps/caengine/etc"
sys.path.append(APPS_ROOT)


#import imp
#imp.load_source('caenginedb', '/opt/JionLab/caengine/bin/caenginedb')

# use APT

# Send message to messanger
#import msg

# for squid reload
from subprocess import call

# for send outmail file
from subprocess import Popen

import hashlib
# from pyDes import * # 메일 반출 시 패스워드 암호 해제 기능, 외부망 설치 시 풀어줄것

#=========================================================================================
# 스크립트 설정
#=========================================================================================
cfg = caengineconf.config('', __name__ == "__main__")

#if __name__ == "__main__":
#	cfg = caengineconf.config('/opt/JionLab/caengine/etc/caengined.conf', True)
#else:
#	cfg = caengineconf.config('/opt/JionLab/caengine/etc/caengined.conf')

linebreak = '\t\n'
div = '\t'

# 임시 백업 폴더로 이동
# 별개 프로그램이 최종 백업 폴더로 파일 이동 시킴
backupPath = cfg.rootPath + '/Backup'
infPath = cfg.rootPath + '/INF'
putPath = cfg.rootPath + '/PUT'
getPath = cfg.rootPath + '/GET'
if cfg.fcpmode == 'dual':
	outPath = cfg.rootPath + '/Outbound'
else:
	outPath = cfg.rootPath + '/GET'

logPath = cfg.rootPath + '/LOG'

mailInfoPath = cfg.rootPath + '/MAIL/INF'

logQ = Queue.Queue()

#=========================================================================================
# 지정된 사용자 폴더 안에 있는 모든 msg 파일을 처리하고 종료한다.
#=========================================================================================
class msgHandler:
	def putLog(self, ReqID, AprID, info, err):
		log = []
		d = datetime.datetime.now()
		log.append(d)
		log.append(ReqID)
		log.append(AprID)
		if err != '':
			info['COM'].type = 'Error'
		log.append(info)
		log.append(err)
		logQ.put(log)
	
	# 후결 승인자가 맞는지 확인	
	def CheckAphInfo(self, ReqID, AprID):
		filename = infPath + '/' + ReqID + '.aph'
		msg = ''
		if os.path.exists(filename):
			msgFile = open(filename)
			msg = msgFile.read(-1)
			msgFile.close
			msg = msg.split('\n')
			
		if msg != '':
			item = msg[0].split(div) # division_id, start, end, ID
			st = datetime.datetime.strptime(item[1],'%Y%m%d-%H%M%S')
			ed = datetime.datetime.strptime(item[2],'%Y%m%d-%H%M%S')
			d = datetime.datetime.now()
			if (d > ed):								
				RemoveFile(filename)
			elif (AprID == item[3]):				
				return True
				
		return False

	# 승인 내역 기록
	def SetAprInfo(self, info, AprID, type):			
		aprlist = info['APR']
		for apr in aprlist:
			if apr.id == AprID:
				apr.type = type
				d = datetime.datetime.now()
				apr.date = d.strftime("%Y%m%d")
				apr.time = d.strftime("%H%M%S%f")[:7]

#=====================================================================================
# DB 대용 함수 시작
#=====================================================================================
	def ReadUserInform(self, userID):
		filename = infPath + '/' + userID + '.uif'
		if os.path.exists(filename):
			msgFile = open(filename)
			msg = msgFile.read(-1)
			msgFile.close
			return msg[3:]
		else:
			return ''	
			
	def ReadAprInform(self, dif):
		filename = infPath + '/' + dif + '.dif'
		if os.path.exists(filename):
			msgFile = open(filename)
			msg = msgFile.read(-1)
			msgFile.close
			return msg[3:].split('\n')
		else:
			return ''	
			
	#후결 정보
	def ReadAphInform(self, userid):
		filename = infPath + '/' + userid + '.aph'
		msg = ''
		if os.path.exists(filename):
			msgFile = open(filename)
			msg = msgFile.read(-1)
			msgFile.close
			msg = msg.split('\n') #msg[3:].split('\n')
		if msg != '':
			item = msg[0].split(div) # division_id, start, end, ID
			st = datetime.datetime.strptime(item[1],'%Y%m%d-%H%M%S')
			ed = datetime.datetime.strptime(item[2],'%Y%m%d-%H%M%S')
			d = datetime.datetime.now()
			if (d > ed):								
				RemoveFile(filename)
			else:				
				return 'APH\t' + self.ReadUif(item[3]) + '\t' + item[1]
		return ''

	# 당직자 정보
	def ReadAptInform(self, divid):
		filename = infPath + '/sapr.inf'
		msg = ''
		result = []
		if os.path.exists(filename):
			msgFile = open(filename)
			msg = msgFile.read(-1)
			msgFile.close
			msg = msg[3:].split('\n')
		if msg != '':
			for eachapt in msg:
				item = eachapt.split(div) # divid, start, end, id
				if item[0] == divid:
					st = datetime.datetime.strptime(item[1] + '00','%Y%m%d-%H%M%S')
					ed = datetime.datetime.strptime(item[2] + '59','%Y%m%d-%H%M%S')
					d = datetime.datetime.now()
					if (d >= st) and (d <= ed):								
						result.append('APT\t' + self.ReadUif(item[3]) + '\t' + item[2])
		return result
			
	def ReadUif(self, userid):
		usr = self.ReadUserInform(userid)
		tmp = usr.split('\n')
		for each in tmp:
			items = each.split(div)
			if items[0] == 'USR':
				return div.join([items[1], items[2], items[6], items[7], items[9], items[10]])
				
		return ''
#=====================================================================================
# DB 대용 함수 끝
#=====================================================================================


#=====================================================================================
# 3망에서 온 로그를 내부망 로그에 업데이트
# Login, Download, DownloadDelete
#=====================================================================================
	# 타망에서 온 사용자 로그인 정보를 업데이트
	def WriteLogFromExtra(self, info, replacetype):
		self.MsgPrn(info, '3망 로그')
		info['COM'].type = replacetype
		self.putLog(self.userid, '-1', info, "")

#=====================================================================================
# 3망에서 내부망으로 로그 보내기
# Login, Download, DownloadDelete
#=====================================================================================
	# 로그를 내부망으로 전송하기
	def SendLogToInternal(self, info, replacetype):
		comDate = info['COM'].date
		comTime = info['COM'].time
		info['COM'].type = replacetype

		dstPath = cfg.rootPath + '/Outbound/'
		CreateDirectory(dstPath)
		CreateDirectory(dstPath + self.userid)
		CreateDirectory(dstPath + 'PUB')

		# Log 출력
		filen = self.WriteMsgToFile(info, dstPath + self.userid, comDate + "-" + comTime + ".msg")
		p, filex = os.path.split(filen)
		filename, ext = filex.split('.')

		# notify
		with open(dstPath + '/PUB/' + self.userid + "~" + filename + ".m", 'w') as file:
			file.write("뭘까요?")
######################################################################################################


	def GetDeptCode(self, usr):
		tmp = usr.split('\n')
		for each in tmp:
			items = each.split(div)
			if items[0] == 'USR':
				return items[9]		
		return ''
			
	def GetDivCode(self, usr):
		tmp = usr.split('\n')
		for each in tmp:
			items = each.split(div)
			if items[0] == 'USR':
				return items[11]		
		return ''
			
	def GetUserInform(self, userID):
		result = []
		
		# get userid.inf
		usr = self.ReadUserInform(userID)
		if usr == '':
			return ''
		result.append(usr)
		
		# get Hugyeol
		aph = self.ReadAphInform(userID)
		
		# get user dept inf
		if aph == '':
			dif_code = self.GetDeptCode(usr)
			aprs = self.ReadAprInform(dif_code)

			for apr in aprs:
				if apr == '' :
					continue
				items = apr.split(div)
				if (items[1] == userID):
					continue
				tmp = 'APR\t' + self.ReadUif(items[1])
				result.append(tmp)
		else:
			result.append(aph)
			
		# get super approver
		if aph == '':
			apts = self.ReadAptInform(self.GetDivCode(usr))
			for apt in apts:
				result.append(apt)
			
		return linebreak.join(result) #self.db.GetUserInform(userID)

	# 사용자 승인 권한 확인
	def GetUserApprove(self, userID):
		#return self.db.GetUserApprove(userID)
		usr = self.ReadUserInform(userID)
		tmp = usr.split('\n')
		for each in tmp:
			items = each.split(div)
			if items[0] == 'USR':
				return items[4] == 'True'
				
		return False

	# 후결 승인자 설정
	def SetAphInfo(self, ReqID, AprID, st, ed):
		msg = ''
		
		# Remove Aph data
		if AprID == '':
			RemoveFile(infPath + '/' + ReqID + '.aph')
		else:
			apr = self.GetUserInform(AprID, direction)
			if apr != '':
				divid = self.GetDivCode(apr)
				if divid != '':
					msg = div.join([divid, st.strftime('%Y%m%d-%H%M%S'), ed.strftime('%Y%m%d-%H%M%S'), AprID])
			if msg != '':
				filename = infPath + '/' + ReqID + '.aph'
				with open(filename, 'w') as file:
					file.write(msg)

	# 사용자 정책 받아오기
	def GetUserPolicy(self, userid):
		return ''

	def GetUserList(self, deptcode):
		return ''
		
	# Msg를 파일로 생성하기
	def WriteMsgToFile(self, info, path, filename):
		if not os.path.exists(path):
			return ''
			
		msg = MakeMessage(datetime.datetime.now(), info, '')

		with open(path + '/' + filename + 'tmp', 'w') as file:
			file.write(linebreak.join(msg))
			
		# 파일 암호화
		newfilename = MsgEncrypt(path + '/' + filename + 'tmp')
			
		# 권한 변경, 
		# uid = pwd.getpwnam("corebrdg").pw_uid
		# gid = grp.getgrnam("corebrdg").gr_gid
		# os.chown(newfilename, uid, gid)
			
		# 대상 파일로 확장자 변경		
		shutil.move(newfilename, newfilename[:-3])
		return newfilename[:-3]

	def GetFileList(self, info):
		movefilelist = []
		filelist = info.get('FIL', None)
		if filelist != []:
			for eachfile in filelist:	
				movefilelist.append(eachfile.aliasname)
		
		return movefilelist

	def isOverTime(self, info, policy):
		# 시간외 자동 사후 결재를 사용하는 가?
		isUse = policy.get('2TOA', 0)
		if (isUse == 0):
			return False

		d = datetime.datetime.now()
		s = d.strftime('%Y%m%d')

		# 시간이 18:00 ~ 09:00 인가
		timerange = policy.get('2WTM', '0918') #0918
		tS = int(timerange[0:2])
		tE = int(timerange[2:4])
		if (d.hour < tS) or (d.hour >= tS):
			return True

		# 토, 일요일 인가
		if (d.weekday() == 5) or (d.weekday() == 6):
			return True
		# 등록된 공휴일인가
		tmp = policy.get('2RED', '')
		reddays = tmp.split('.')

		isUse = 0
		for eachday in reddays:
			if eachday == s:
				isUse = 1
				break

		return isUse > 0;

	def GetAprID(self, info, type):
		aprlist = info.get('APR', None)
		if aprlist != []:
			ReqID = info['REQ'].id
			self.AprID = '0'
			self.head = 'APR'
			for eachApr in aprlist:
				if (eachApr.type == type) and (self.AprID == '0'):
					self.AprID = eachApr.id
					self.head = eachApr.head					
					break
		
			if (self.head == 'APH') and (not self.CheckAphInfo(ReqID, self.AprID)):
				return '후결 승인 권한이 없습니다.'
			
			if self.AprID == '0':
				return '승인자를 찾을 수 없습니다 A'
			elif (self.AprID != 'admin') and (not self.GetUserApprove(self.AprID)):
				self.AprID = '0'
				return '승인 권한이 없습니다.'
			return ''
		else:
			return '승인자를 찾을 수 없습니다 B'
	
	def FolderIsID(self, userid):
		if (self.userid != userid):
			return '메타 파일의 위치와 폴더가 일치하지 않습니다.'
		else:
			return ''
	
	def MsgPrn(self, info, msg):
		cfg.TraceLog(None, info, msg)
		#cfg.prn('[' + info['COM'].direction + ', ' + self.userid + '] ' + msg)

	def CheckOutboundFilesExist(self, folder):
		list = glob.glob(cfg.rootPath + "/Outbound/" + folder + "*")
		#cfg.prn("CheckOutboundFilesExist: " + folder)
		return (len(list) > 0)

	def CheckOutboundList(self):
		for reqID in self.OutboundList.keys():
			# cfg.prn(reqID+","+self.OutboundList[reqID][0])
			if not self.CheckOutboundFilesExist(reqID):
				#  파일 전송이 끝나고 해야 한다.
				# Server noti
				with open(cfg.rootPath + "/Outbound/PUB/" + self.OutboundList[reqID], 'w') as file:
					file.write("뭘까요?")
				del self.OutboundList[reqID]

	# 지정한 승인자의 승인 대기 목록을 생성한다. infPath + "/" + 파일명 UD-개수.inf
	# 신청, 승인, 반려, 취소
	def CountApproveList(self, info, appID):
		# getPath + "/" + appID 내에 있는 .REQ 파일 검색 (그중 날짜-시간-ID.REQ 에서 ID가 다른것만 찾는다.
		list = glob.glob(getPath + "/" + appID + "/*.REQ")
		appfile = infPath + "/" + appID + ".inf"
		RemoveFile(appfile)
		self.MsgPrn(info, appfile)

		cnt = 0;
		for eachfile in list:
			tmp = eachfile.split('-')
			if len(tmp) > 3:
				if (tmp[2] != appID):
					# Info 출력
					os.popen("cat " + eachfile + " >> " + appfile);
					os.popen("echo -e " + '"\t"' + " >> " + appfile);
					cnt = cnt + 1

		self.MsgPrn(info, appID + "," + str(cnt))
		return

	# 3 망임. 파일을 내부로 이동 시킬것
	def Request_Extra(self, info):
		self.MsgPrn(info, '3망 파일 전송 신청')
		filelist = info['FIL']
		movefilelist = []

		ReqID = self.userid
		comDate = info['COM'].date
		comTime = info['COM'].time
		errS = self.FolderIsID(info['REQ'].id)

		dstPath = cfg.rootPath + '/Outbound/'
		CreateDirectory(dstPath)
		CreateDirectory(dstPath + ReqID)
		CreateDirectory(dstPath + 'PUB')

		cmd = "mv "+ putPath + '/' + ReqID + '/' + comDate + '-' + comTime + "* -t " + dstPath + ReqID + '/'
		os.system(cmd)

		self.OutboundList[ReqID + '/' + comDate + '-' + comTime] = self.extfl



		# Write Message to Admin, Req Log
		#self.putLog(ReqID, self.AprID, info, errS) #'-1'
		return True


	def Request2(self, info):
		if cfg.SetAlarm:
			# send info to Messanger
			msginstance = msg.UCWare("xxx.xxx.xxx.xxx:12555")

		filelist = info['FIL']
		movefilelist = []

		errS = ''
		ReqID = info['REQ'].id
		comDate = info['COM'].date
		comTime = info['COM'].time
		AprID2 = ReqID
		head2 = ''
		#self.FolderIsID(info['REQ'].id)

		# 파일 전송 정책
		isApp = True
		nApps = 1
		policy = self.GetUserPolicy(ReqID)

		if policy == '':
			errS = '정책을 찾을 수 없습니다.'
		else:
			pol = policy[info['COM'].direction]
			print pol
			nApps = int(pol.get('2NOA',1))

			# 승인자 결정
			if errS == '':
				# 승인 후 파일 전송, 신청자, 승인자 아이디가 다르거나 승인자 상태가 승인이 아닌 경우 승인으로 간다. 
				# SecuRequest는 통합 반출입시스템 문서보안 승인 요청 이다
				if (info['APR'][0].id != ReqID or info['APR'][0].type != 'Approve') and info['APR'][0].type != 'SecuApprove': #(poldir == 'BiDirection') or (poldir == info['COM'].direction):
					if info['APR'][0].type == 'Approve':
						errS = self.GetAprID(info, 'Approve')
					elif info['APR'][0].type == 'SecuRequest':
						errS = self.GetAprID(info, 'SecuRequest')
					else:
						errS = self.GetAprID(info, 'Request')
					AprID2 = self.AprID
					head2 = self.head
					if (nApps > 0) and (nApps != len(info['APR'])):
						errS = '승인자 수가 정책과 일치하지 않습니다'
					# 후결인데 오류가 났다.
					if (errS != '') and (head2 == 'APH'):
						if self.isOverTime(info, pol):
							errS = ''
				else:
					# 승인  불 필요
					isApp = False
					AprID2 = ReqID
					info['COM'].type = 'Approve'

			else:
				# 승인  불 필요
				isApp = False
				AprID2 = ReqID
				info['COM'].type = 'Approve'

		if errS == '' and AprID2 != '0':
			isWait = False;
			for eachfile in filelist:
				# check attached file
				filename = putPath + '/' + ReqID + '/' + eachfile.aliasname
				if not os.path.exists(filename):
					# 처리가 끝나지 않았다. 기다리자
					if os.path.exists(filename + '.fcp2'):
						isWait = True
						break;
					if cfg.APTFlag: # use APT
						if os.path.exists(filename + " (virus suspected - quarantined)"):
							errS = '바이러스 감염 파일입니다. (' + eachfile.name + ')'
							os.remove(filename + " (virus suspected - quarantined)")
							break  
						if os.path.exists(filename + " (APT suspected - quarantined)"):
							errS = '지능형 위협이 감지된 파일입니다. (' + eachfile.name + ')'
							info['REQ'].message = '지능형 위협이 감지된 파일입니다. (' + eachfile.name + ')'
							os.remove(filename + " (APT suspected - quarantined)")
							break  # Release Comment for APT service #
						else:
							isWait = True
							break
							errS = '첨부 파일을 찾을 수 없습니다 (' + eachfile.name + ')'
							break
					else: # not use APT
						if os.path.exists(filename + " (virus suspected - quarantined)"):
							errS = '바이러스 감염 파일입니다. (' + eachfile.name + ')'
							break  
						else:
							isWait = True
							break
							errS = '첨부 파일을 찾을 수 없습니다 (' + eachfile.name + ')'
							break

				filesize = str(os.path.getsize(filename))
				# md5s = GetHash(filename)

				# ByPass Hash Check
				md5s = eachfile.eHash

				# 암호화된 파일의 검증
				compareFile = (md5s != eachfile.eHash) or (filesize != eachfile.eSize)

				# Add Move File List
				if compareFile:
					errS = '파일 정보와 실제 파일이 다릅니다. (' + eachfile.name + ')'
					break

				movefilelist.append(eachfile.aliasname)

			if (isWait):
				return False;

		if errS == '':
			# Write Message to Apr
			cfg.TraceLog2(str(isApp), "Test")
			if isApp:
				# 승인요청 메시지
				self.WriteMsgToFile(info, getPath + '/' + AprID2, comDate + '-' + comTime + '-' + ReqID + '.REQ')
				cfg.TraceLog2(getPath + '/' + AprID2 + "/" + comDate + '-' + comTime + '-' + ReqID + '.REQ', "APP")
				self.CountApproveList(info, AprID2)
				notify.SendMsg(1, ReqID, AprID2, info['REQ'].name, info['REQ'].message, "Unknown IP")

				if cfg.SetAlarm:
					# send info to Messanger
					if (ReqID != self.AprID):
						msginstance.Send(ReqID,  info['REQ'].name, self.AprID, '0', info['REQ'].message)

				# 후결 승인인 경우
				if head2 == 'APH':
					# 후결 가능한지 확인
					# 바로 전송 화면으로 전달
					info['COM'].type = 'Approve'
					# Copy To me
					CopyFileList(putPath + '/' + ReqID, getPath + '/' + ReqID, movefilelist)

			# Move Attached File
			# 자가 승인인데 인터넷 전송인 경우 바로 Outbound로 파일을 보낸
			dstPath = outPath
			if (not isApp) and ((info['COM'].direction == 'XtraExport') or (info['COM'].direction == 'XtraImport')):
				dstPath = cfg.rootPath + '/Outbound'
			#Copty to Approve
			if AprID2 == ReqID:
				dstpath = outPath
			else:
				dstPath = getPath
			MoveFileList(putPath + '/' + ReqID, dstPath + '/' + AprID2, movefilelist)
			cfg.TraceLog2(dstPath + '/' + AprID2, "Test")
		else:
			info['COM'].type = 'Error'


		if (errS != ''):
			info['REQ'].message = errS

		RemoveFile(getPath + '/' + ReqID + '/' + comDate + '-' + comTime + '.REQ')
		RemoveFile(getPath + '/' + ReqID + '/' + comDate + '-' + comTime + '.ANS')

		# Write Message to Me
		if (not isApp) or (head2 == 'APH'): # 후결 승인 또는 승인 불 필요
			self.WriteMsgToFile(info, getPath + '/' + ReqID, comDate + '-' + comTime + '-' + AprID2 + '.ANS')
			dstPath = outPath
			if (info['COM'].type != 'Error') and ((info['COM'].direction == 'XtraExport') or (info['COM'].direction == 'XtraImport')):
				dstPath = cfg.rootPath + '/Outbound'
			self.WriteMsgToFile(info, dstPath + '/' + ReqID, comDate + '-' + comTime + '-' + AprID2 + '.ANS')
		else:
			self.WriteMsgToFile(info, getPath + '/' + ReqID, comDate + '-' + comTime + '-' + AprID2 + '.REQ')
			cfg.TraceLog2(getPath + '/' + ReqID + "/" + comDate + '-' + comTime + '-' + AprID2 + '.REQ', "Test")

		# Write Message to Admin, Req Log
		self.putLog(ReqID, AprID2, info, errS) #'-1'


		return True


	# filelist의 파일이 모두 정상이면 파일을 이동 시켜 준다.
	# 아니면 다시 대기
	def RequestWait(self):
		for waitmsgfile in self.RequestList.keys():
			info = self.RequestList[waitmsgfile]
			#  정상처리 되었다.
			if (self.Request2(info)):
				del self.RequestList[waitmsgfile]

        # Check squid update status
	def CheckSquidUpdate(self):
		if os.path.isfile(infPath + '/fbrdg/etc/squidupdate'):
			call(['/etc/init.d/fbrdg_squid','reload'])
			cfg.TraceLog2('서버에 웹프록시 설정 리로드됨', "[Import,admin]")
			RemoveFile(infPath + '/fbrdg/etc/squidupdate')

 	# 사용자 파일 전송 신청
	def Request(self, info):
		self.MsgPrn(info, '파일 전송 신청')

		waitext = '.REQ'
		if (len(info['APR']) == 1) and (info['APR'][0].id == info['REQ'].id) and (info['APR'][0].type == 'Approve'):
			self.MsgPrn(info, 'ANS')
			waitext = '.ANS'

		# 20140810, 파일 처리중임을 알리는 메시지를 알려준다.
		# if (errS == '') and self.AprID != '0':   #and isApp and (self.head != 'APH'):
		info['COM'].type = 'WaitForFile'
		waitmsgfile = self.WriteMsgToFile(info, getPath + '/' + info['REQ'].id, info['COM'].date + '-' + info['COM'].time + waitext)
		info['COM'].type = 'Request'

		self.RequestList[waitmsgfile] = info

		'''
		for eachfile in info['FIL']:
				# check attached file
				filename = putPath + '/' + info['REQ'].id + '/' + eachfile.aliasname
				shutil.move(filename, filename+'.fcp2')
		'''
		return True

	# 사용자 문서보안파일 전송 신청
	def SecuRequest(self, info):
		self.MsgPrn(info, '파일 전송 신청')

		waitext = '.REQ'
		if (len(info['APR']) == 1) and (info['APR'][0].id == info['REQ'].id) and (info['APR'][0].type == 'Approve'):
			self.MsgPrn(info, 'ANS')
			waitext = '.ANS'

		# 20140810, 파일 처리중임을 알리는 메시지를 알려준다.
		info['COM'].type = 'WaitForFile'
		waitmsgfile = self.WriteMsgToFile(info, getPath + '/' + info['REQ'].id, info['COM'].date + '-' + info['COM'].time + waitext)
		info['COM'].type = 'SecuRequest'

		self.RequestList[waitmsgfile] = info

		return True

	# 파일 전송 신청 취소
	def Cancel(self, info):
		self.MsgPrn(info, '파일 전송 신청 취소')
				
		errS = ''
		ReqID =  self.userid
		comDate = info['COM'].date
		comTime = info['COM'].time		
		errS = self.FolderIsID(info['REQ'].id)

		# 승인자 결정
		if errS == '':
			if info['APR'][0].type == 'SecuRequest': # 문서보안의 처리
				errS = self.GetAprID(info, 'SecuRequest')
			else:
				errS = self.GetAprID(info, 'Request')
			if self.AprID == '0':
				errS = self.GetAprID(info, 'HugyeolReq')
		
		if self.AprID != '0':
			filelist = self.GetFileList(info)		
			RemoveFileList(getPath + '/' + self.AprID, filelist)			
			RemoveFile(getPath + '/' + self.AprID + '/' + comDate + '-' + comTime + '-' + ReqID + '.REQ')
			self.CountApproveList(info, self.AprID)
	
		RemoveFile(getPath + '/' + ReqID + '/' + comDate + '-' + comTime + '-' + self.AprID + '.REQ')

		# Write Message to Admin, Req Log
		self.putLog(ReqID, '-1', info, errS)
		return errS == ''
		

	def decrypt(self, passphrase, key):
		m=md5.new()
		m.update(key)
		k = triple_des(m.digest(), ECB, padmode=PAD_PKCS5)
		result = k.decrypt(passphrase.decode('base64'))
		return result

	def GetAdminID(self):
		pwfile = '/opt/JionLab/passwd/etc/passwd'
		pwlines = [line.rstrip('\n') for line in open(pwfile)]

		pwsplit = []
		for linepw in pwlines:
			pwsplit = linepw.split(':')
			if len(pwsplit) >= 3:
				if(pwsplit[3] == 'Admin User'):
					rtnData = pwsplit[0]
					break
		return rtnData

	'''
	# 부산은행 버전
	# 20180304 부산은행 메일 ID 가 사용자 계정과 달라 메일 ID 테이블에서 가져옴
	def GetUserMailInfo(self, ReqID):
		mifrdata = ''
		if os.path.exists(infPath + '/mailinfo.inf'):
			mifr = open(infPath + '/mailinfo.inf', 'r')
			mifrdata = mifr.read(-1)
			mifr.close

		usermailid = 'NONE'
		if mifrdata != '':
			lines = mifrdata.split('\n')
			for each_line in lines:
				line = each_line.split('\t')
				if(line[0].find(ReqID) >= 0):
					usermail = line[1]
					existFlag = True
					break
		return usermail

# 승인된 이메일 파일 외부망 전송
	def SendMailtoOutbound(self, info, ReqID, outPathFile):
		rtnFlag = 0
		try:
			# 외부망으로 보내자
			mailfile = mailInfoPath + '/' + 'Outbound.mail'
			with open(mailfile, 'r') as f:
				mailinfo = f.read(-1)
			f.close()
			#iInfo = self.GetAdminID()
			#self.MsgPrn(info, "iInfo: " + iInfo)
			#pInfo = self.decrypt(mailinfo, iInfo)
			pInfo = self.decrypt(mailinfo, 'admin')

			usermailfile = mailInfoPath + '/' + ReqID + '.mail'
			with open(usermailfile, 'r') as uf:
				usermailinfo = uf.read(-1)
			uf.close()
			relayFile = '/opt/JionLab/caengine/script/relay'
			if os.path.exists(relayFile):
				os.remove(relayFile)

			with open(relayFile, 'w') as file:
				file.write('admin' + '\n' + pInfo)
			file.close()

			head, tail = ntpath.split(outPathFile)
			justName = os.path.splitext(tail)[0]

			userMail = self.GetUserMailInfo(ReqID)
			changedFile = justName + '_' + ReqID + '_' + userMail + '_' + usermailinfo + '.outmail'

			srcFile = getPath + '/' + self.userid + '/' + outPathFile
			copyFile = getPath + '/' + self.userid + '/' + changedFile
			shutil.copy(srcFile, copyFile)
			dstFile = 'lxsecot1r:' + cfg.rootPath + '/MAIL/OutMail/' + changedFile
			arg = """ """.join(["/opt/JionLab/fcp2/bin/fcp2 -f", copyFile, "-p 127.0.0.1:7776", dstFile, "-P", "/opt/JionLab/caengine/script/relay"])
			obj = Popen(arg, shell=True, stdin=None, stdout=None, stderr=None, close_fds=True)
			obj.wait()
			if os.path.exists(relayFile):
				os.remove(relayFile)
			if os.path.exists(copyFile):
				os.remove(copyFile)
			rtnFlag = 1
		except:
			self.MsgPrn(info, "예외")
			rtnFlag = 0

	return rtnFlag
	'''	

	# 승인된 이메일 파일 외부망 전송
	def SendMailtoOutbound(self, info, ReqID, outPathFile):
		rtnFlag = 0
		try:
			# 외부망으로 보내자
			mailfile = mailInfoPath + '/' + 'Outbound.mail'
			with open(mailfile, 'r') as f:
				mailinfo = f.read(-1)
			f.close()
			iInfo = self.GetAdminID()
			pInfo = self.decrypt(mailinfo, iInfo)

			usermailfile = mailInfoPath + '/' + ReqID + '.mail'
			with open(usermailfile, 'r') as uf:
				usermailinfo = uf.read(-1)
			uf.close()

			relayFile = '/opt/JionLab/caengine/script/relay'
			if os.path.exists(relayFile):
				os.remove(relayFile)

			with open(relayFile, 'w') as file:
				file.write(iInfo + '\n' + pInfo)
			file.close()

			changedFile = os.path.splitext(outPathFile)[0] + '_' + ReqID + '_' + usermailinfo + '.outmail'
			srcFile = getPath + '/' + self.userid + '/' + outPathFile
			copyFile = getPath + '/' + self.userid + '/' + changedFile
			shutil.copy(srcFile, copyFile)
			dstFile =  'CBOUT2:' + cfg.rootPath + '/MAIL/OutMail/' + changedFile
			arg = """ """.join(["/opt/JionLab/fcp2/bin/fcp2 -f", copyFile, "-p 127.0.0.1:7776", dstFile, "-P", "/opt/JionLab/caengine/script/relay"])
			obj = Popen(arg, shell=True, stdin=None, stdout=None, stderr=None, close_fds=True)
			obj.wait()
			if os.path.exists(relayFile):
				os.remove(relayFile)
			if os.path.exists(copyFile):
				os.remove(copyFile)
			rtnFlag = 1
		except:
			rtnFlag = 0


	def CheckOutMail(self, info, ReqID, filelist):
		rtnFlag = 0

		if filelist != []:
			for eachfile in filelist:
				ext = os.path.splitext(eachfile)
				if(ext[1] == '.outmail'):
					rtnFlag = self.SendMailtoOutbound(info, ReqID, eachfile)
		return rtnFlag

	# 파일 전송 승인
	def Approve(self, info):
		self.MsgPrn(info, '파일 전송 승인')
		
		if cfg.SetAlarm:
			# send info to Messanger
			msginstance = msg.UCWare("xxx.xxx.xxx.xxx:12555")

		AprID = self.userid
		ReqID = info['REQ'].id
		comDate = info['COM'].date
		comTime = info['COM'].time
		
		errS = self.GetAprID(info, 'Request')
		if (errS == '') and (AprID != self.AprID):
			errS = '메타 파일의 승인자와 폴더가 일치하지 않습니다.'
		
		if (errS == '') and (not self.GetUserApprove(AprID)):
			errS = '승인 권한이 없습니다 (' + AprID + ')'

		AprNextID = '-1'
		if errS == '':			
			# 승인 정보 설정
			self.SetAprInfo(info, AprID, 'Approve')
			self.GetAprID(info, 'Request')
			AprNextID = self.AprID
			filelist = self.GetFileList(info)	

			# if remain approve request
			if (AprNextID != '0') and (not self.GetUserApprove(AprNextID)):
				errS = '승인 권한이 없습니다 (' + AprNextID + ')'

		# 메일 파일 외부망 전송여부 결정
		mailFlag = 0
		mailFlag = self.CheckOutMail(info, ReqID, filelist)

		# Delete Files for APH, 승인자 폴더에서만 삭제한다
		# 2014.09.24
		filelist = self.GetFileList(info)
		RemoveFileList(getPath + '/' + self.AprID, filelist)

		# Delete Message to Apr, Req
		RemoveFile(getPath + '/' + AprID + '/' + comDate + '-' + comTime + '-' + ReqID + '.REQ')
		RemoveFile(getPath + '/' + ReqID + '/' + comDate + '-' + comTime + '-' + AprID + '.REQ')

		if errS == '':
			if AprNextID == '0':
				dstPath = outPath
				self.MsgPrn(info, info['COM'].direction)

				# Move 3rd Network
				if (info['COM'].direction == 'XtraExport') or (info['COM'].direction == 'XtraImport'):
					dstPath = cfg.rootPath + '/Outbound'

				# mailFlag가 1 이면 외부망으로 정상반출 되었으므로 목록에서 삭제
				if mailFlag == 1 or mailFlag == 2 or mailFlag == None:
 					# 지난 메일 받기를 위해 메일 파일 백업
					if cfg.filebackup:
						# Move Attached File to Outbound or ReqID
						MoveFileList(getPath + '/' + AprID, backupPath + '/' + ReqID, filelist)
					else:
						RemoveFileList(getPath + '/' + AprID, filelist)
					RemoveFile(getPath + '/' + AprID + '/' + comDate + '-' + comTime + '-' + ReqID + '.REQ')

					if mailFlag == 2 or mailFlag == None:
						self.MsgPrn(info, '메일반출 실패 => 승인요청자: ' + ReqID + '	승인자: ' + AprID)
						errS = '메일반출에 실패 하였습니다.\n승인요청을 다시 하십시오.\n동일한 오류가 지속되면 망연계 담당자에게 문의 바랍니다.'

					if cfg.SetAlarm:
						# send info to Messanger
						if (ReqID != AprID):
							if mailFlag == 2 or mailFlag == None:
								msginstance.Send(AprID, info['APR'][0].name, ReqID,  '3', info['REQ'].message)
							else:
								msginstance.Send(AprID, info['APR'][0].name, ReqID,  '1', info['REQ'].message)

				else:
					# Move Attached File to Outbound or ReqID
					MoveFileList(getPath + '/' + AprID, dstPath + '/' + ReqID, filelist)

					# Write Message to Req	
					msgfilename = self.WriteMsgToFile(info, getPath + '/' + ReqID, comDate + '-' + comTime + '-' + AprID + '.ANS')
					notify.SendMsg(2, AprID, ReqID, info['REQ'].name, info['REQ'].message, "Unknown IP")

					if cfg.SetAlarm:
						# send info to Messanger
						if (ReqID != AprID):
							msginstance.Send(AprID, info['APR'][0].name, ReqID,  '1', info['REQ'].message)

					# Move Meta File to outPath, Differed Mode
					if (getPath != dstPath): # outPath):
						dir, name = os.path.split(msgfilename)
						shutil.move(msgfilename, dstPath + '/' + ReqID + '/' + name)
			else:
				# Next Request
				info['COM'].type = 'Request'
				# Move Attached File to Next Apr
				MoveFileList(getPath + '/' + AprID, getPath + '/' + AprNextID, filelist)
				
				# Write Message to AprNextID
				self.WriteMsgToFile(info, getPath + '/' + AprNextID, comDate + '-' + comTime + '-' + ReqID + '.REQ')
		
				# Write Message to Req	
				self.WriteMsgToFile(info, getPath + '/' + ReqID, comDate + '-' + comTime + '-' + AprNextID + '.REQ')

				self.CountApproveList(info, AprNextID)

		self.CountApproveList(info, AprID)
		# Write Message to Admin, Req Log
		self.putLog(ReqID, AprID, info, errS)
		return errS == ''

	# 승인 반려
	def Reject(self, info):
		self.MsgPrn(info, '파일 전송 반려')

		if cfg.SetAlarm:
			# send info to Messanger
			msginstance = msg.UCWare("xxx.xxx.xxx.xxx:12555")

		AprID = self.userid
		ReqID = info['REQ'].id
		comDate = info['COM'].date
		comTime = info['COM'].time
		errS = self.GetAprID(info, 'Request')
		if (errS == '') and (AprID != self.AprID):
			errS = '메타 파일의 승인자와 폴더가 일치하지 않습니다.'
		
		if (errS == '') and (not self.GetUserApprove(AprID)):
			errS = '승인 권한이 없습니다 (' + AprID + ')'
			
		if errS == '':
			self.SetAprInfo(info, AprID, 'Reject')
		
		filelist = self.GetFileList(info)
						
		# Delete Message to Apr, Req
		RemoveFile(getPath + '/' + AprID + '/' + comDate + '-' + comTime + '-' + ReqID + '.REQ')
		RemoveFile(getPath + '/' + ReqID + '/' + comDate + '-' + comTime + '-' + AprID + '.REQ')

		# 지난 메일 받기를 위해 메일 파일 백업
		if cfg.filebackup:
			# Move Attached File to Outbound or ReqID
			MoveFileList(getPath + '/' + AprID, backupPath + '/' + ReqID, filelist)
		else:
			# Delete Attached File
			RemoveFileList(getPath + '/' + AprID, filelist)

		self.CountApproveList(info, AprID)

		# Write Message to Req		
		if errS == '':
			self.WriteMsgToFile(info, getPath + '/' + ReqID, comDate + '-' + comTime + '-' + AprID + '.ANS')
			notify.SendMsg(3, AprID, ReqID, info['REQ'].name, info['REQ'].message, "Unknown IP")

			if cfg.SetAlarm:
				# send info to Messanger
				if (ReqID != AprID):
					aprlist = info['APR']
					msginstance.Send(AprID, info['APR'][0].name, ReqID, '2', aprlist[0].rejectmsg)

		# Write Message to Admin, Req Log
		self.putLog(ReqID, AprID, info, errS)
		return True

	def DeleteAndLog(self, info, isLogWrite):
		self.MsgPrn(info, '파일 및 메시지 삭제')	
		
		errS = ''
		
		ReqID =  self.userid
		comDate = info['COM'].date
		comTime = info['COM'].time		
		errS = self.FolderIsID(info['REQ'].id)
		
		if errS == '':
			errS = self.GetAprID(info, 'Request')
		else:
			errS2 = self.GetAprID(info, 'Request')
			if self.AprID == self.userid: # 후결 삭제
				errs = ''
			else:
				self.AprID = '0'
		
		filelist = self.GetFileList(info)
	
		# Delete Attached File
		if cfg.filebackup:
			MoveFileList(getPath + '/' + ReqID, backupPath + '/' + ReqID, filelist)
		else:
			RemoveFileList(getPath + '/' + ReqID, filelist)
		
		print self.AprID, ReqID, self.userid
				
		# Delete Answer File
		if self.AprID == self.userid:
			RemoveFile(getPath + '/' + self.AprID + '/' + comDate + '-' + comTime + '-' + info['REQ'].id + '.REQ')
			info['COM'].type = 'Approve'
			self.putLog(self.AprID, '-1', info, '')
		else:
			RemoveFile(getPath + '/' + ReqID + '/' + comDate + '-' + comTime + '-' + self.AprID + '.ANS')
			RemoveFile(getPath + '/' + ReqID + '/' + comDate + '-' + comTime + '-' + self.AprID + '.REQ')
	
		# Write Message to Admin, Req Log
		if isLogWrite:
			self.putLog(ReqID, '-1', info, '') # error는 무시
		
		return errS == ''

	# 파일 및 메시지 삭제
	def DeleteAll(self, info):			
		return self.DeleteAndLog(info, False)

	# 파일을 받은 후 삭제. 로그 기록	
	def Download(self, info):
		self.MsgPrn(info, '파일 다운로드 완료 후 삭제')
		return self.DeleteAndLog(info, True)
		
	# 파일을 받지 않고 삭제. 로그 기록	
	def DownloadDelete(self, info):
		self.MsgPrn(info, '파일 다운로드 안 하고 삭제')
		return self.DeleteAndLog(info, True)

	# 사용자 들간, 또는 관리자랑 메시지 보내기
	def SendMsg(self, info):
		self.MsgPrn(info, '메시지 보내기')
		
		errS = ''
		ReqID =  self.userid
		comDate = info['COM'].date
		comTime = info['COM'].time		
		errS = self.FolderIsID(info['REQ'].id)
		
		if errS == '':
			errS = self.GetAprID(info, 'SendMsg')
			
		if errS == '':
			if self.AprID == 'admin':
				self.AprID = 'admin'  # 실제 관리자 아이디로 변환시킨다.
			# Write Message to admin		
			CreateDirectory(getPath + '/' + self.AprID)
			self.WriteMsgToFile(info, getPath + '/' + self.AprID, comDate + '-' + comTime + '-' + ReqID + '.REQ')	

		self.putLog(ReqID, '-1', info, errS)
		return errS == ''

	# 후결 신청
	def HugyeolReq(self, info):
		self.MsgPrn(info, '후결 신청')
		
		errS = ''
		ReqID =  self.userid
		comDate = info['COM'].date
		comTime = info['COM'].time		
		errS = self.FolderIsID(info['REQ'].id)
		
		if errS == '':
			errS = self.GetAprID(info, 'HugyeolReq')

		if errS == '':
			# Write Message to Apr
			self.WriteMsgToFile(info, getPath + '/' + self.AprID, comDate + '-' + comTime + '-' + ReqID + '.REQ')
		else:
			info['COM'].type = 'Error'
			info['REQ'].message = errS

		# Write Message to Me
		self.WriteMsgToFile(info, getPath + '/' + ReqID, comDate + '-' + comTime + '-' + self.AprID + '.REQ')

		# Write Message to Admin, Req Log
		self.putLog(ReqID, self.AprID, info, errS)
		return errS == ''

	# 후결 승인
	def HugyeolApp(self, info, AprID):
		self.MsgPrn(info, '후결 승인')

		AprID = self.userid
		ReqID = info['REQ'].id
		comDate = info['COM'].date
		comTime = info['COM'].time
		
		errS = self.GetAprID(info, 'HugyeolReq')
		if (errS == '') and (AprID != self.AprID):
			errS = '메타 파일의 승인자와 폴더가 일치하지 않습니다.'

		if (errS == '') and (not self.GetUserApprove(AprID)):
			errS = '승인 권한이 없습니다 (' + AprID + ')'

		# 다음 승인자가 있는지 확인한다.
		AprNextID = '-1'
		if errS == '':			
			# 승인 정보 설정
			self.SetAprInfo(info, AprID, 'HugyeolApp')
			self.GetAprID(info, 'HugyeolReq')
			AprNextID = self.AprID
			# if remain approve request
			if (AprNextID != '0') and (not self.GetUserApprove(AprNextID)):
				errS = '승인 권한이 없습니다 (' + AprNextID + ')'

		if errS == '':
			RemoveFile(getPath + '/' + AprID + '/' + comDate + '-' + comTime + '-' + ReqID + '.REQ')
			if AprNextID == '0':
				# 승인이 완료되었다
				# 후결 시간 기입
				tmp = info['REQ'].message.split('\n') # start end message
				if (len(tmp) >= 3):				
					sdt = tmp[0]
					edt = tmp[1]			
					st = datetime.datetime.strptime(sdt + ':00','%Y-%m-%d %H:%M:%S')
					ed = datetime.datetime.strptime(edt + ':59','%Y-%m-%d %H:%M:%S')					
				else:
					errS = '후결 시간 범위 설정이 틀립니다.'

				# 후결 시간을 설정한다.
				if errS == '':
					self.SetAphInfo(ReqID, AprID, st, ed)
					# Delete Message to Apr, Req
					RemoveFile(getPath + '/' + ReqID + '/' + comDate + '-' + comTime + '-' + AprID + '.REQ')
			else:
				info['COM'].type = 'HugyeolReq'
				# 다음 승인자가 있다.
				# Write Message to AprNextID
				self.WriteMsgToFile(info, getPath + '/' + AprNextID, comDate + '-' + comTime + '-' + ReqID + '.REQ')
				# Write Message to Req	
				self.WriteMsgToFile(info, getPath + '/' + ReqID, comDate + '-' + comTime + '-' + AprNextID + '.REQ')

		if errS != '':
			info['COM'].type = 'Error'
						
		# Write Message to Admin, Req Log
		self.putLog(ReqID, AprID, info, errS)
		
		return errS == ''

	# 후결 반려
	def HugyeolRej(self, info, AprID):
		self.MsgPrn(info, '후결 반려')
		
		AprID = self.userid
		ReqID = info['REQ'].id
		comDate = info['COM'].date
		comTime = info['COM'].time
				
		errS = self.GetAprID(info, 'HugyeolReq')
		if (errS == '') and (AprID != self.AprID):
			errS = '메타 파일의 승인자와 폴더가 일치하지 않습니다.'
		
		# 승인 내역 기록
		if errS == '':
			self.SetAprInfo(info, AprID, 'HugyeolRej')
		else:
			info['COM'].type = 'Error'
										
		# Delete Message to Apr, Req
		RemoveFile(getPath + '/' + AprID + '/' + comDate + '-' + comTime + '-' + ReqID + '.REQ')
		RemoveFile(getPath + '/' + ReqID + '/' + comDate + '-' + comTime + '-' + AprID + '.REQ')

		# Write Message to Req		
		self.WriteMsgToFile(info, getPath + '/' + ReqID, comDate + '-' + comTime + '-' + AprID + '.ANS')	

		# Write Message to Admin, Req Log
		self.putLog(ReqID, AprID, info, errS)
		return errS == ''

	# 후결 정보 삭제
	def HugyeolDelete(self, info):
		self.MsgPrn(info, '후결 정보 삭제')
		
		ReqID = self.userid
		comDate = info['COM'].date
		comTime = info['COM'].time
		errS = self.FolderIsID(info['REQ'].id)
		
		# 승인자 결정
		if errS == '':			
			errS = self.GetAprID(info, 'HugyeolApp')

		# 후결 정보 삭제
		if errS == '':
			self.SetAphInfo(ReqID, '', None, None)

		# Delete Answer File
		RemoveFile(getPath + '/' + ReqID + '/' + comDate + '-' + comTime + '-' + self.AprID + '.ANS')
	
		# Write Message to Admin, Req Log
		self.putLog(ReqID, '-1', info, errS)
		return errS == ''

	# 사용자 파일 전송 신청
	def Clipboard(self, info):
		self.MsgPrn(info, '클립보드')
		
		filelist = info['FIL']
		
		errS = ''
		ReqID = self.userid
		comDate = info['COM'].date
		comTime = info['COM'].time
		errS = self.FolderIsID(info['REQ'].id)
		clpfile = ''
		clphash = ''
		clpsize = 0;
		clpdir = 'None'
		policy = self.GetUserPolicy(ReqID)
		if policy == '':
			errS = '정책을 찾을 수 없습니다.'
		else:
			pol = policy[info['COM'].direction]
			#clpdir = pol['
			clpsize = int(pol['3CXT'])
		
		'''
		if clpdir != 'BiDirection':
			if info['COM'].direction != clpdir:
				errS = '클립보드 정책(전송방향)과 다릅니다.'
		'''
		#print "===================="
		#print len(info['REQ'].message), clpsize
		#print "===================="
		
		#if (clpsize > 0) and (len(info['REQ'].message) > clpsize):
		#	errS = '클립보드 정책(텍스트 크기)과 다릅니다.'
			
		if errS == '':
			for eachfile in filelist:
				# check attached file
				filename = putPath + '/' + ReqID + '/' + eachfile.aliasname
				if not os.path.exists(filename):
					errS = '첨부 파일을 찾을 수 없습니다 (' + eachfile.name + ')'
					break
					
				filesize = str(os.path.getsize(filename))
				# md5s = GetHash(filename)
			
				# ByPass Hash Check
				md5s = eachfile.eHash
			
				# 암호화된 파일의 검증
				compareFile = (md5s != eachfile.eHash) or (filesize != eachfile.eSize)
			
				# Add Move File List
				if compareFile:
					errS = '파일 정보와 실제 파일이 다릅니다. (' + eachfile.name + ')'
					break
				# First 3byte == 'CLP'			
				if errS == '':
					msgFile = open(filename)
					msg = msgFile.read(3)
					msgFile.close
					# 클립보드 확인 기능 더 보완하자.					
					if msg != 'CLP':
						errS = '클립보드 파일이 아닙니다'
						break
						
				clpfile = eachfile.aliasname	
				clphash = eachfile.eHash	
			
		dstfile = getPath + '/' + ReqID + '/' + info['COM'].direction + '.CLP'
		if errS == '' and clpfile != '':
			srcfile = putPath + '/' + ReqID + '/' + clpfile
			if os.path.exists(srcfile):
				CreateDirectory(getPath + '/' + ReqID)
				# RemoveFile(dstfile)
				shutil.move(srcfile, dstfile)
		else:
			with open(dstfile, 'w') as file:
				file.write(' ')
			info['COM'].type = 'Error'
			
		# Write Message to Me
		# self.WriteMsgToFile(info, getPath + '/' + ReqID, comDate + '-' + comTime + '-' + ReqID + '.CLP')
	
		# Write Message to Admin, Req Log
		self.putLog(ReqID, '-1', info, errS)
		return errS == ''

	# URL 전송
	def URL(self, info):
		self.MsgPrn(info, 'URL 전송')
		
		ReqID = self.userid
		comDate = info['COM'].date
		comTime = info['COM'].time
		errS = self.FolderIsID(info['REQ'].id)
		
		if errS == "":
			filename = self.WriteMsgToFile(info, getPath + '/' + ReqID, info['COM'].direction + '.JIONURL')
			shutil.move(filename, getPath + '/' + ReqID + '/' + info['COM'].direction + '.JIONURL')
			
		self.putLog(ReqID, '-1', info, errS)
		return errS == ''

    # 사용자 계정을 읽어 클라이언트에서 수신하도록 ANS 파일로 저장한다
	def MAILAccountRead(self, info):
		self.MsgPrn(info, 'Mail 정보 수신')
		# 사용자 계정을 등록한다
		REQ = info.get('REQ', None)
		if REQ == None:
			self.MsgPrn(info, 'Mail 정보REQ 없음')
			return False
		s = REQ.message.split('\r\n')
		if len(s) < 1:
			REQ.message = '계정정보가 틀립니다.'
		else:
			self.MsgPrn(info,  REQ.id)
			self.ReadAccount(REQ.id, info)
			REQ.message = ''
		self.putLog(REQ.id, '-1', info, REQ.message)

		return REQ.message == ''

	# 사용자별 메일계정 읽기
	def ReadAccount(self, userid, info):
		# id 파일을 만들고 거기에 메일 정보를 넣어서 외부망으로 보내버리자
		root = cfg.rootPath
		CreateDirectory(root + '/MAIL')
		CreateDirectory(root + '/MAIL/INF')
		CreateDirectory(root + '/MAIL/Outbound')
		CreateDirectory(root + '/MAIL/Outbound/INF')
		if os.path.exists(root + '/MAIL/INF/' + userid + '.mail'):
			with open(root + '/MAIL/INF/' + userid + '.mail', 'r') as file:
				COM = info.get('COM', None)
				REQ = info.get('REQ', None)

				comDate = COM.date
				comTime = COM.time

				msgout = file.read(-1)
				self.MsgPrn(info, 'joekim.mail 파일: ' + msgout)
				splitmsg = msgout.split('\n')
				mailpw = splitmsg[0]
				info['REQ'].message = mailpw
				self.MsgPrn(info, 'Mail REQ 정보: ' + info['REQ'].message)
				filename = self.WriteMsgToFile(info, getPath + '/' + userid, comDate + '-' + comTime + '-' + userid + '.ANS')

			with open(root + '/MAIL/Outbound/INF/' + userid + '.mail', 'r') as file:
				msg = file.read(-1)
				msg.split('\n')
				mailpw = msgout[0]
		else:
			self.MsgPrn(info,  "ID: " + userid + " 인 메일 계정이 없어 자료반출입 에이전트에서 계정등록 요청을 합니다."


	# 사용자 계정을 등록한다
	def RegistAccount(self, userid, mailpw):
		# id 파일을 만들고 거기에 메일 정보를 넣어서 외부망으로 보내버리자
		root = cfg.rootPath
		CreateDirectory(root + '/MAIL')
		CreateDirectory(root + '/MAIL/INF')
		CreateDirectory(root + '/MAIL/Outbound')
		CreateDirectory(root + '/MAIL/Outbound/INF')
		with open(root + '/MAIL/Outbound/INF/' + userid + '.mail', 'w') as file:
			file.write(mailpw)
		with open(root + '/MAIL/INF/' + userid + '.mail', 'w') as file:
			file.write(mailpw)
	
	# Mail 전송
        def MAILAccount(self, info):
                self.MsgPrn(info, 'Mail 정보 등록')
		# 사용자 계정을 등록한다
		REQ = info.get('REQ', None)
		if REQ == None:
			return False
		s = REQ.message.split('\n')
		if len(s) < 1:
			REQ.message = '계정정보가 틀립니다.'
		else:
			self.MsgPrn(info,  REQ.id)
			self.MsgPrn(info, s[0])
			self.RegistAccount(REQ.id, s[0])
			REQ.message = ''
		self.putLog(REQ.id, '-1', info, REQ.message)

                return REQ.message == ''
	
	# 사용자 시스템 정보
	def UserSysInfo(self, info):
		ReqID = self.userid
		COM = info.get('COM', None)
		REQ = info.get('REQ', None)

		comDate = COM.date
		comTime = COM.time
		comTime = comTime[:-1]
		datetime_object = datetime.datetime.strptime(comDate+comTime, '%Y%m%d%H%M%S')
		datetimestr = datetime_object.strftime('%Y-%m-%d %H:%M:%S')
		errS = self.FolderIsID(REQ.id)

		if errS == '':
			f = open(cfg.usersys_inf, 'r+')

			sysMessage = REQ.message.split('^')

			lines = []
			new_line = ''
			userFlag = False
			userIPFlag = False
			changedFlag = False
			ippos = 0
			for eachline in f:
				eachinfo = eachline.split('\t')
				if (eachinfo[0] == REQ.id):
					userFlag = True
					userip = eachinfo[9].split(' ')
					for eachip in userip:
						if (eachip == REQ.ip):
							userIPFlag = True
							break
						ippos += 1

					splitinfo = eachinfo[10].split('\n')
					if (userIPFlag == False):
						changedFlag = True
						if (eachinfo[2] == 'unknown'):
							new_line = eachinfo[0] + '\t' + eachinfo[1] + '\t' +  sysMessage[0] + '\t' +  sysMessage[1] + '\t' +  sysMessage[2] + '\t' +  sysMessage[3] + '\t' +  sysMessage[4] + '\t' +  sysMessage[5] + '\t' +  sysMessage[6] + '\t' + eachinfo[9] + ' '  + REQ.ip + '\t' + splitinfo[0] + '^' + datetimestr + '\n'
							self.MsgPrn(info, '사용자 시스템 Unknown  정보 업데이트: ' + new_line)
						else:
							new_line = eachinfo[0] + '\t' + eachinfo[1] + '\t' + eachinfo[2] + '\t' + eachinfo[3] + '\t' + eachinfo[4] + '\t' + eachinfo[5] + '\t' + eachinfo[6] + '\t' + eachinfo[7] + '\t' + eachinfo[8] + '\t' + eachinfo[9] + ' ' + REQ.ip + '\t' + splitinfo[0] + '^' + datetimestr + '\n'
							self.MsgPrn(info, '사용자 시스템 정보 업데이트: ' + new_line)
							lines = lines + [new_line]
							new_line = ''
					else:
						changedFlag = True
						timepos = 0
						applytimes = ''
						splittime = splitinfo[0].split('^')
						for timedata in splittime:
							if(timepos == ippos):
								applytimes = applytimes + datetimestr + '^'
							else:
								applytimes = applytimes + timedata + '^'
							timepos += 1
						applytimes = applytimes[:-1]
						new_line = eachinfo[0] + '\t' + eachinfo[1] + '\t' +  sysMessage[0] + '\t' +  sysMessage[1] + '\t' +  sysMessage[2] + '\t' +  sysMessage[3] + '\t' +  sysMessage[4] + '\t' +  sysMessage[5] + '\t' +  sysMessage[6] + '\t' + eachinfo[9] + '\t' + applytimes + '\n'
						self.MsgPrn(info, '사용자 시스템 Unknown  정보 업데이트: ' + new_line)
						lines = lines + [new_line]
						new_line = ''
				else:
					lines = lines + [eachline]

			if (userFlag == False):
				changedFlag = True
				new_line = REQ.id + '\t' + REQ.name + '\t' +  sysMessage[0] + '\t' +  sysMessage[1] + '\t' +  sysMessage[2] + '\t' +  sysMessage[3] + '\t' +  sysMessage[4] + '\t' +  sysMessage[5] + '\t' +  sysMessage[6] + '\t' + REQ.ip + '\t' + datetimestr + '\n'
				self.MsgPrn(info, '사용자 시스템 정보 신규 생성: ' + new_line)
				lines = lines + [new_line]
				new_line = ''

			if (changedFlag == True):
				# file pointer 위치를 처음으로 돌림
				f.seek(0)
				# 수정한 lines를 파일에 다시 씀
				f.writelines(lines)
				# 현재 file pointer 위치까지만 남기고 나머지는 정리
				f.truncate()
			f.close()
		else:
			msg = ''

		self.putLog(REQ.id, '-1', info, errS)

		return errS == ''

	# 사용자 정보 요청
	def UserInf(self, info):
		self.MsgPrn(info, '사용자 정보 요청')
		
		ReqID = self.userid
		COM = info.get('COM', None)
		REQ = info.get('REQ', None)

		comDate = COM.date
		comTime = COM.time
		errS = self.FolderIsID(REQ.id)
		
		if errS == '':			
			msg = self.GetUserInform(REQ.id, COM.direction)
			CreateDirectory(getPath + '/' + REQ.id)
		else:
			msg = ''
		
		if msg != '':
			eachitem = msg.split(',') #div)
			if len(eachitem) > 10:
				REQ.name = eachitem[2]
				REQ.jikgeup = eachitem[7]
				REQ.dept_code = eachitem[9]
				REQ.dept_name = eachitem[10]
				
		REQ.message = msg.replace(div,',')
		
		self.WriteMsgToFile(info, getPath + '/' + ReqID, comDate + '-' + comTime + '-' + REQ.id + '.ANS')	

		hash = GetHash2(REQ.ip)
		#  중복 로그인 방지
		with open(getPath + '/' + REQ.id + '/' + COM.direction + '.ip', 'w') as file:
			file.write(hash)

		self.putLog(REQ.id, '-1', info, errS)

		return errS == ''

	# 부서 사용자 정보 요청
	def RequestDeptUserList(self, info):
		self.MsgPrn(info, '부서 사용자 정보 요청')
		
		ReqID = self.userid
		comDate = info['COM'].date
		comTime = info['COM'].time
		errS = self.FolderIsID(info['REQ'].id)
		
		if errS == '':			
			# 외부승인자 지정 팀에서 승인위임 대상자 목록 가져오기위해 승인자 ID 넘겨주기
				msg = self.GetUserListExtMan(info['REQ'].dept_code, info['REQ'].id)
 		else:
			msg = ''
		info['REQ'].message = msg
		
		self.WriteMsgToFile(info, getPath + '/' + ReqID, comDate + '-' + comTime + '-' + ReqID + '.ANS')	
	
		self.putLog(ReqID, '-1', info, errS)
		return errS == ''
	
	# 승인 권한 위임
	def ChangeApprover(self, info):
		self.MsgPrn(info, '승인자 변경 요청')
		ReqID = self.userid
		comDate = info['COM'].date
		comTime = info['COM'].time
		errS = self.FolderIsID(info['REQ'].id)
		
		if errS == '':
			msg = 'Fail'	
			aprlist = info['APR']
			if (len(aprlist) > 0):
				# 승인위임자가 여러명일 경우의 처리
				for i in xrange(0,len(aprlist)):
					if self.ChangeApproverRight(ReqID, aprlist[i].id, aprlist[0].rejectmsg):
						msg = 'Success'
		else:
			msg = errS
		if msg == 'Fail':			
			info['REQ'].message = "권한위임실패" + info['REQ'].message
					
		self.WriteMsgToFile(info, getPath + '/' + ReqID, comDate + '-' + comTime + '-' + ReqID + '.ANS')
		
		# 위임 받는 사람에게 통보	
		if msg == 'Success':
			self.WriteMsgToFile(info, getPath + '/' + aprlist[0].id, comDate + '-' + comTime + '-' + ReqID + '.ANS')
			self.putLog(ReqID, aprlist[0].id, info, errS)
			if info['COM'].direction == 'Export':
				info['COM'].direction = 'Import'
			else:
				info['COM'].direction = 'Export'
			self.WriteMsgToFile(info, getPath + '/' + aprlist[0].id, comDate + '-' + comTime + '-' + aprlist[0].id + '.ANS')
		else:
			self.putLog(ReqID, '-1', info, errS)
		return errS == ''

	# 승인 권한 회수
	def RecallApprover(self, info):
		self.MsgPrn(info, '승인 권한 회수')
		ReqID = self.userid
		comDate = info['COM'].date
		comTime = info['COM'].time
		errS = self.FolderIsID(info['REQ'].id)
		
		if errS == '':
			if self.RecallApproveRight(ReqID):
				msg = 'Success'
			else:
				msg = 'Fail'	
		else:
			msg = errS

		if msg == 'Fail':			
			info['REQ'].message = "권한회수실패" + info['REQ'].message
					
		self.WriteMsgToFile(info, getPath + '/' + ReqID, comDate + '-' + comTime + '-' + ReqID + '.ANS')
		self.putLog(ReqID, '-1', info, errS)
		return errS == ''
		
	# 서버에 사용자 정보 업데이트
	def SysInform(self, info):
		self.MsgPrn(info, '서버에 사용자 정보 업데이트: admin')
		return True

	# 서버에 로그 기록
	def Log(self, info):
		self.MsgPrn(info, '로그 기록: ' + self.userid)
		self.putLog(self.userid, '-1', info, '')

	# 서버에 관리자 접속 허용 IP 변경
	def IPUpdate(self, info):
		self.MsgPrn(info, '관리자 접속 허용 PC IP 변경: admin')
		ReqID = self.userid
		comDate = info['COM'].date
		comTime = info['COM'].time
		
		if self.userid == cfg.admin_id:
			f = open(cfg.fcp2_passwd, 'r')
			fw = open(cfg.fcp2_passwd+'_new', 'w')
			
			for eachline in f:
				eachuser = eachline.split(':')
				if (len(eachuser) > 1) and (eachuser[0] == cfg.admin_id):
					eachinf = eachuser[2].split(',')
					ipold = eachinf[0]
					eachinf[0] = info['REQ'].message
					eachuser[2] = ",".join(eachinf)
					info['REQ'].message = "관리자변경_설정_접속허용IP_" + ipold + "_" + info['REQ'].message
					
				fw.write(":".join(eachuser))
			
			fw.close()
			f.close()
			
			shutil.copy(cfg.fcp2_passwd, cfg.fcp2_passwd + '.' + comDate + '.old')
			shutil.move(cfg.fcp2_passwd + '_new', cfg.fcp2_passwd)
			self.WriteMsgToFile(info, getPath + '/' + ReqID, comDate + '-' + comTime + '-' + ReqID + '.ANS')
			
			#Join("_", "관리자" + "변경", "설정", "접속허용IP", oldips, ipi.ToString()
			self.putLog(self.userid, '-1', info, '')
		else:
			info['COM'].type = 'Error'
		
	# 메타 파일을 분석한다.
	def GetMetaInfo(self, msg):
		# cfg.prn('메타 파일 읽기: ' + self.userid + ', <' + '><'.join(msg).replace('\t',' ') + '>')
		aprlist = []
		filelist = []
		result = {}
	
		for eachmsg in msg:
			if (eachmsg[3] != '\t'):
				continue
			key = eachmsg[:3]
			if (key == 'APR') or (key == 'APH') or (key == 'APT'): # 일반 승인, 후결, 당직자
				apr = APR(key, eachmsg)
				aprlist.append(apr)
			elif (key == 'FIL'):	# 복수개가 나올수 있음
				fil = FIL(eachmsg)
				filelist.append(fil)
			elif (key == 'COM'):
				com = COM(eachmsg)
				result[key] = com
			elif (key == 'REQ'):
				req = REQ(eachmsg)
				result[key] = req
	
		result['APR'] = aprlist
		result['FIL'] = filelist
	
		return result


	'''
	# 날짜가 오래된 파일은 삭제, .msg 파일은 목록에 추가
	def getMsgFiles(self, folder):
		result = []
		files = os.listdir(folder)
		for eachfile in files:
			filename = folder + '/' + eachfile
			filetime = datetime.datetime.fromtimestamp(os.path.getmtime(filename))
			d = datetime.datetime.now()
			if (fileStorageDate > 0) and ((d-f).days > fileStorageDate):
				os.remove(filename)
			elif filename.endswith('.msg'):
				result.append(filename)
		return result		
	
	def start(self, userid):	
		self.userid = userid
		putfolder = putPath + '/' + userid
		prn('Get Msg: ' + putfolder)
		files = self.getMsgFiles(putfolder)
		for eachfile in files:
			MsgProcess(userid, eachfile)
	'''
	# 사용자 정보를 타망으로 전송
	def CopySysInfo(self, info):
		self.MsgPrn(info, "CopySysInform")
		comDate = info['COM'].date
		comTime = info['COM'].time
		xtrsyspath = cfg.rootPath + "/Outbound/sysinform"
		CreateDirectory(cfg.rootPath + "/Outbound")
		CreateDirectory(xtrsyspath)
		filen = self.WriteMsgToFile(info, xtrsyspath, comDate + "-" + comTime + ".msg")
		p, filex = os.path.split(filen)
		filename, ext = filex.split('.')
		with open(xtrsyspath + "/admin~" + filename + ".m", 'w') as file:
			file.write("뭘까요?")
		# copy passwd
		shutil.copy("/opt/JionLab/passwd/etc/passwd", xtrsyspath + "/passwd")
		# copy user.inf
		shutil.copy(cfg.rootPath + "/INF/user.inf", xtrsyspath + "/user.inf")

	def MsgProcess(self, userid, eachfile):
		if not os.path.exists(eachfile):
			cfg.prn("Wait for File: " + eachfile)
			nCnt = 0
			while (os.path.exists(eachfile + '.fcp2')):
				time.sleep(0.05)
				nCnt = nCnt + 1
				if nCnt > 10:
					break;
			if not os.path.exists(eachfile):
				cfg.prn("File Not Found Exit: " + eachfile)
				return

		self.userid = userid		
		with open(eachfile, 'r') as f:
			msg = f.read(-1)

		eachmsg = msg.split(linebreak)
			
		info = self.GetMetaInfo(eachmsg)
		COM = info.get('COM', None)
		if COM == None:
			RemoveFile(eachfile)
			return
									
		msgtype = COM.type
		if msgtype == 'UserInf':
			result = self.UserInf(info)
			if cfg.extranet:
				self.SendLogToInternal(info, 'UserInfLog')
		# ============================================================
		# 3망에서 온 로그를 기입
		elif msgtype == 'UserInfLog':
			result = self.WriteLogFromExtra(info, 'UserInf')
		elif msgtype == 'DownloadLog':
			result = self.WriteLogFromExtra(info, 'Download')
		elif msgtype == 'DownloadDeleteLog':
			result = self.WriteLogFromExtra(info, 'DownloadDelete')
		#============================================================
		elif msgtype == 'Request':
			if cfg.extranet and ((COM.direction == 'Export2') or (COM.direction == 'Import2')):
				result = self.Request_Extra(info)
			else:
				result = self.Request(info)
		elif msgtype == 'SecuRequest':
			if cfg.extranet and (COM.direction == 'Import'):
				result = self.SecuRequest(info)
			else:
				result = self.Request(info)
		elif msgtype == 'Cancel':
			result = self.Cancel(info);
		elif msgtype == 'Approve':
			result = self.Approve(info)
		elif msgtype == 'Reject':
			result = self.Reject(info)
		elif msgtype == 'Delete':
			result = self.DeleteAll(info)
		elif msgtype == 'Download':			# 파일을 받은 후 삭제. 로그 기록
			result = self.Download(info)
			if cfg.extranet:
				self.SendLogToInternal(info, 'DownloadLog')
		elif msgtype == 'DownloadDelete':	# 파일을 받지 않고 삭제. 로그 기록
			result = self.DownloadDelete(info)
			if cfg.extranet:
				self.SendLogToInternal(info, 'DownloadDeleteLog')
		elif msgtype == 'SendMsg':
			result = self.SendMsg(info)
		elif msgtype == 'HugyeolReq':
			result = self.HugyeolReq(info)					
		elif msgtype == 'HugyeolApp':
			result = self.HugyeolApp(info, userid)					
		elif msgtype == 'HugyeolRej':
			result = self.HugyeolRej(info, userid)
		elif msgtype == 'HugyeolDelete':
			result = self.HugyeolDelete(info)
		elif msgtype == 'Clipboard':
			if cfg.extranet and ((COM.direction == 'Export2') or (COM.direction == 'Import2')):
				result = self.Request_Extra(info)
			else:
				result = self.Clipboard(info)
		elif msgtype == 'SysInform':
			result = self.SysInform(info)
			self.CopySysInfo(info)
		elif msgtype == 'Direct':
			result = self.Direct(info)
		elif msgtype == 'Log':
			result = self.Log(info)
		elif msgtype == 'ADInform':
			result = self.ADInform(info)
			info['COM'].type = 'SysInform'
			self.CopySysInfo(info)
		elif msgtype == 'IPUpdate':
			result = self.IPUpdate(info)
		elif msgtype == 'RequestDeptUserList':
			result = self.RequestDeptUserList(info)
		elif msgtype == 'MandateApprover':		# 승인 권한 위임
			result = self.ChangeApprover(info) 
		elif msgtype == 'RecallApprover':		# 승인 권한 회수
			result = self.RecallApprover(info) 
		elif msgtype == 'URL':
			result = self.URL(info)
		elif msgtype == 'MAILAccount':
			result = self.MAILAccount(info)
		# 사용자별 메일 계정 정보 읽기
		elif msgtype == 'MAILAccountRead':
			result = self.MAILAccountRead(info)
		# 사용자 시스템 정보 수집
		elif msgtype == 'UserSysInf':
			result = self.UserSysInfo(info)
		RemoveFile(eachfile)		

def MsgDecrypt(name, msgfilename):
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
	
	if cfg.secure_on:
		os.system('/opt/JionLab/fcp2/bin/ms_crypt -d -K ' + hashkey + ' ' + msgfilename)	
		
	hash2 = GetHash(msgfilename)
	if (hash2 != hash):
		#self.MsgPrn('파일 해쉬: ' + name + ',' + hash + ',' + hash2)
		cfg.prn('파일 해쉬: ' + name + ',' + hash + ',' + hash2)
		
		
	return hash2 == hash
	
def MsgEncrypt(msgfilename):
	# Get hash Key
	hash = GetHash(msgfilename)
	
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
	
	# print eachname[2]	
	if cfg.secure_on:
		os.system('/opt/JionLab/fcp2/bin/ms_crypt -e -K ' + hashkey + ' ' + msgfilename)
		
	name, ext = os.path.splitext(msgfilename)
	os.rename(msgfilename, name + '-' + hash + ext)
	return name + '-' + hash + ext

def CreateDirectory(directory):
	if not os.path.exists(directory):
		os.makedirs(directory)

def CopyFileList(srcpath, dstpath, filelist):
	for eachfile in filelist:
		print srcpath + '/' + eachfile,
		if os.path.exists(srcpath + '/' + eachfile):
			CreateDirectory(dstpath)
			print dstpath + '/' + eachfile
			shutil.copy(srcpath + '/' + eachfile, dstpath + '/' + eachfile)
			
def RenameFileList(srcpath, dstpath, aliaslist):
	for eachfile in aliaslist:
		if os.path.exists(srcpath + '/' + eachfile.aliasname):
			CreateDirectory(dstpath)
			# utf-8 --> euc-kr
			filename = unicode(eachfile.name,'utf-8').encode('euc-kr')
			shutil.move(srcpath + '/' + eachfile.aliasname, dstpath + '/' + filename)

def MoveFileList(srcpath, dstpath, filelist):
	for eachfile in filelist:
		if os.path.exists(srcpath + '/' + eachfile):
			CreateDirectory(dstpath)
			shutil.move(srcpath + '/' + eachfile, dstpath + '/' + eachfile)

def RemoveFile(filename):
	name, ext = os.path.splitext(filename)
	if ((ext == '.REQ') or (ext == '.ANS')):
		eachname = name.split('-') # date-time-option
		for fl in glob.glob(eachname[0] + '-' + eachname[1] + '-*' + ext):
			os.remove(fl)
	else:
		if os.path.exists(filename):
			os.remove(filename)

def RemoveFileList(srcpath, filelist):
	for eachfile in filelist:
		filename = srcpath + '/' + eachfile
		RemoveFile(filename)

# string to hex-string
def asctohex(string_in):
	a = ""
	for x in string_in:
		a = a + ("0"+((hex(ord(x)))[2:]))[-2:]
	return(a)

def GetHash(filename):
	md5 = hashlib.sha256()
	with open(filename, 'rb') as f:
		for chunk in iter(lambda: f.read(8192), b''):
			md5.update(chunk)
	md5s = asctohex(md5.digest())
	return md5s

def GetHash2(message):
	md5 = hashlib.sha256()
	md5.update(message)
	md5s = asctohex(md5.digest())
	return md5s

# 메타 데이터의 한 줄이 유효한지 검사
def DataValid(head, msg, length):
	eachdata = msg.split(div)
	if (eachdata[0] != head) or (len(eachdata) != length):
		eachdata = []
		eachdata.append(head)
		for i in range(length - 1):
			eachdata.append('')
			
	return eachdata
	
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

def MakeMessage(d, info, issue):
	msg = []	
	logDate = d.strftime("%Y%m%d")
	logTime = d.strftime("%H%M%S%f")[:7]
	msg.append(div.join(['VER', '1.0', info['COM'].type, logDate, logTime, issue]))
	
	com = info.get('COM', None)
	if com != None:
		msg.append(com.Get())

	req = info.get('REQ', None)
	if req != None:
		msg.append(req.Get())
	
	aprlist = info.get('APR', None)
	if aprlist != None:
		for apr in aprlist:
			msg.append(apr.Get())
			
	filelist = info.get('FIL', None)
	if filelist != None:
		for file in filelist:
			msg.append(file.Get())
	return msg
				
# Write Log Data
def WriteLog(d, ReqID, AprID, info, issue):
	comDate = d.strftime("%Y%m%d")
	logmsg = linebreak.join(MakeMessage(d, info, issue))

	# 전체 로그
	CreateDirectory(logPath)
	with open(logPath + '/' + comDate + '.log', 'a') as file:
		file.write(logmsg + linebreak)
	
	if (info['COM'].type == 'UserInf') or (info['COM'].type == 'Clipboard') or (info['COM'].type == 'SendMsg'):
		return
		
	# 신청자 로그
	if (ReqID != '-1'):
		CreateDirectory(getPath + '/' + ReqID + '/Log/')
		with open(getPath + '/' + ReqID + '/Log/' + comDate + '.log', 'a') as file:
			file.write(logmsg + linebreak)
	
	# 승인자 로그	
	if (AprID != ReqID) and (AprID != '-1'):
		CreateDirectory(getPath + '/' + AprID + '/Log/')
		with open(getPath + '/' + AprID + '/Log/' + comDate + '.log', 'a') as file:
			file.write(logmsg + linebreak)

#=========================================================================================
# Msg DB Handler
#=========================================================================================
class msgDBHandler(msgHandler):
	def __init__(self):
		if cfg.dbtype == 'mysql':
			self.db = caenginedb.MySQLDB(cfg)		# MySQL
		else: # cfg.dbtype == 'sqlite3'
			self.db = caenginedb.SQLite3DB(cfg)		# SQLite3
		self.extfl = ""
		self.OutboundList = {}
		self.RequestList = {}

	def __del__(self):
		self.db = None

	# 사용자 정보 가져오기
	def GetUserInform(self, userID, direction):
		result = self.db.GetUserInform(userID, direction)
		if type(result) == unicode:
			result = result.encode('utf-8','ignore')
		return result
		
	# 사용자 승인 권한 확인
	def GetUserApprove(self, userID):
		return self.db.GetUserApprove(userID)

	# 후결 승인자 설정
	def SetAphInfo(self, ReqID, AprID, st, ed):		
		self.db.SetLateApprover(ReqID, AprID, st, ed)

	# 후결 승인자가 맞는지 확인	
	def CheckAphInfo(self, ReqID, AprID):
		return self.db.CheckAphInfo(ReqID, AprID)

	# 서버에 사용자 정보 업데이트
	def SysInform(self, info):
		self.MsgPrn(info, '서버에 사용자 정보 업데이트: admin')
		
		self.db.ImportData()
		self.db.ImportSApp()
		
		info['REQ'].message = '서버에 사용자 정보 업데이트';
		self.putLog(self.userid, '-1', info, '')
		return True
		
	# 서버에 사용자 정보 업데이트
	def ADInform(self, info):
		self.MsgPrn(info, info['REQ'].message + 'admin')
		
		# True가 아닌 경우 사유가 포함되어 온다.
		if info['REQ'].message == 'True':
			info['REQ'].message = '사용자 정보 자동 업데이트'
			self.db.ImportData2(cfg.sysLDAP)
		
		self.putLog(self.userid, '-1', info, '')
		return True

	def GetUserPolicy(self, userid):
		return self.db.GetUserPolicy(userid)
			
	def GetUserList(self, deptcode):
		return self.db.GetUserList(deptcode)
	
	# 외부승인자 지정 팀에서 승인위임 대상자 목록 가져오기위해
	def GetUserListExtMan(self, deptcode, userID):
		return self.db.GetUserListExtMan(deptcode, userID)

	
	def ChangeApproverRight(self, currentUserID, mandateUserID, d):
		return self.db.ChangeApproverRight(currentUserID, mandateUserID, d)
	
	def RecallApproveRight(self, userid):
		return self.db.RecallApproveRight(userid)
		
#=========================================================================================
# Run 스크립트
#=========================================================================================
def msgComm(fl, h):
	msgfile = os.path.split(fl)			
	userid, msg = msgfile[1].split('~')						
	RemoveFile(fl)	

	# 3망 처리시에 필요하다
	h.extfl = userid + '~' + msg

	if (userid=="svr") and (msg=="import.m"):
		# Import user information
		# Run Import Script
		caengineimport.Run()
	else:
		h.MsgProcess(userid, putPath + '/' + userid + '/' + msg + 'sg')

def main(isDaemon, isLoop):

	# Mark Process
	if cfg.APTFlag: # use APT
		caengined2 = caengine2.Caengine2()
		caengined2.log.info('Main', 'Start caengine Service')
		caengined2.log.info('Main', 'Config <' + ', '.join("%s:%s" % item for item in vars(cfg).items()) + '>')
	else: # not use APT
		cfg.TraceLog2('Start caengine Service', 'Main')
		cfg.TraceLog2('Config <' + ', '.join("%s:%s" % item for item in vars(cfg).items()) + '>', "Main")

	if (not isDaemon) and isLoop:
		pid = str(os.getpid())
		with open('pid', 'w') as file:
			file.write(pid + '\n')
	else:
		RemoveFile('pid')

	h = msgDBHandler()
	while True:
		# PUT/PUB 폴더를 읽는다.
		# *.m 파일이 있는지 확인한다.
		# 파일명의 아이디에서 동일한 파일명의 *.msg 파일을 처리한다.
		# reqid~date-time-hash.m
		if isDaemon:
			try:
				if cfg.APTFlag: # use APT
					rtnCnt = caengined2.Run()
					for fl in glob.glob(putPath + '/PUB0/*.m'):
						if not os.path.isdir(fl):
							msgComm(fl, h)
							break
				else: # not use APT
					for fl in glob.glob(putPath + '/PUB/*.m'):
						if not os.path.isdir(fl):
							msgComm(fl, h)
							break
				h.CheckOutboundList()
				h.RequestWait()

				# Check update squid_acl.conf
				h.CheckSquidUpdate()
 			except:
				exc_type, exc_value, exc_traceback = sys.exc_info()
				fname = os.path.split(exc_traceback.tb_frame.f_code.co_filename)[1]

				lines = traceback.format_exception(exc_type, exc_value, exc_traceback)
				sexcept = ','.join(lines) #'!! ' + line for line in lines)
				cfg.TraceLog(None, None, sexcept, "Error")

				msgfile = os.path.split(fl)
				userid, msg = msgfile[1].split('~')

				d = datetime.datetime.now()
				info = {}
				com = COM(div.join(['COM', 'Error', 'Export', d.strftime("%Y%m%d"), d.strftime("%H%M%S%f")[:7]]))
				info['COM'] = com
				req = REQ(div.join(['REQ', userid, 'Unknown', '', '', '', '', '']))
				info['REQ'] = req
				WriteLog(d, userid, '-1', info, str(sys.exc_info()[0]))
		else:
			for fl in glob.glob(putPath + '/PUB/*.m'):
				if not os.path.isdir(fl):
					msgComm(fl, h)
			h.CheckOutboundList()
			h.RequestWait()

			# Check update squid_acl.conf
			h.CheckSquidUpdate()

		# Write Queue
		for i in range(logQ.qsize()):
			log = logQ.get()
			WriteLog(log[0], log[1], log[2], log[3], log[4])
		
		if not isDaemon:
			if not os.path.exists('pid'):
				break;	
	
		# Check CPU Usage
		#print datetime.datetime.now(), "CPU usage=%.2f%%" % (getCpuLoad()*100.0)
		time.sleep(0.05)
		
	h = None
	cfg.TraceLog2('Stop caengine Service', 'Main')

def Version():
	print "Ver.1.0.141226"

#=====================================================================================
# FileBridge Message Service Test
#=====================================================================================
if __name__ == "__main__":
	if len(sys.argv) == 2:
		if sys.argv[1] == '-v':
			Version()
		else:
			main(False, 'loop' == sys.argv[1])
	else:
		main(False, False)
