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

class File():
	def __init__(self, logger, cfg):
		self.logger = logger
		self.cfg = cfg

	def Request(self, userid, metainfo, hDB):
		filelist = metainfo['FIL']
		movefilelist = []

		errS = ''
		ReqID = metainfo['REQ'].id
		comDate = metainfo['COM'].date
		comTime = metainfo['COM'].time
		AprID2 = ReqID
		head2 = ''

		# 파일 전송 정책
		isApp = True
		nApps = 1
		policy = hDB.GetUserPolicy(ReqID)

		if policy == '':
			errS = '정책을 찾을 수 없습니다.'
		else:
			pol = policy[metainfo['COM'].direction]
			print pol
			nApps = int(pol.get('2NOA',1))

		# 승인자 결정
		if errS == '':
			# 승인 후 파일 전송, 신청자, 승인자 아이디가 다르거나 승인자 상태가 승인이 아닌 경우 승인으로 간다.
			if metainfo['APR'][0].id != ReqID or metainfo['APR'][0].type != 'Approve': #(poldir == 'BiDirection') or (poldir == metainfo['COM'].direction):
				if metainfo['APR'][0].type == 'Approve':
					errS = self.GetAprID(info, 'Approve')
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
					if os.path.exists(filename + " (virus suspected - quarantined)"):
						errS = '바이러스 감염 파일입니다. (' + eachfile.name + ')'
	########################################################################
	# APT, 151015
						os.remove(filename + " (virus suspected - quarantined)")
						break
					if os.path.exists(filename + " (APT suspected - quarantined)"):
						errS = '지능형 지속가능 위협 추정 파일입니다. (' + eachfile.name + ')'
						info['REQ'].message = '지능형 지속 가능 위협 추정 파일입니다. (' + eachfile.name + ')'
						os.remove(filename + " (APT suspected - quarantined)")
						break
	########################################################################
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
				########################################################################
				# SEED256, 151218
				compareFile = False #(md5s != eachfile.eHash) or (filesize != eachfile.eSize)

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
				notify.SendMsg(1, ReqID, AprID2, metainfo['REQ'].name, metainfo['REQ'].message, "Unknown IP")

				# 후결 승인인 경우
				if head2 == 'APH':
					# 후결 가능한지 확인
					# 바로 전송 화면으로 전달
					info['COM'].type = 'Approve'
					# Copy Attached File
					#CopyFileList(getPath + '/' + AprID2, getPath + '/' + ReqID, movefilelist)
					# Copy To me
					CopyFileList(putPath + '/' + ReqID, getPath + '/' + ReqID, movefilelist)

			# Move Attached File
			# 자가 승인인데 인터넷 전송인 경우 바로 Outbound로 파일을 보낸
			dstPath = getPath
			if (not isApp) and ((info['COM'].direction == 'XtraExport') or (info['COM'].direction == 'XtraImport')):
				dstPath = cfg.rootPath + '/Outbound'

			#Copty to Approve
			dstPath = outPath
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
			dstPath = getPath
			if (info['COM'].type != 'Error') and ((info['COM'].direction == 'XtraExport') or (info['COM'].direction == 'XtraImport')):
				dstPath = cfg.rootPath + '/Outbound'
			self.WriteMsgToFile(info, dstPath + '/' + ReqID, comDate + '-' + comTime + '-' + AprID2 + '.ANS')
		else:
			self.WriteMsgToFile(info, getPath + '/' + ReqID, comDate + '-' + comTime + '-' + AprID2 + '.REQ')
			cfg.TraceLog2(getPath + '/' + ReqID + "/" + comDate + '-' + comTime + '-' + AprID2 + '.REQ', "Test")

		# Write Message to Admin, Req Log
		self.putLog(ReqID, AprID2, info, errS) #'-1'


		return True
