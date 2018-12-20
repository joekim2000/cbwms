#! /usr/bin/python
# coding: utf-8

from django.db import models
from django.forms import ModelForm
from datetime import date, datetime
from django.conf import settings
#from cbwms.settings import common

import sys
import os
import pwd
import grp


# mysql client import
#import pymysql
#:pymysql.install_as_MySQLdb()

PROJECT_ROOT = getattr(settings, "PROJECT_ROOT", None)
from cbwms.settings import common
import caengineconf

APPS_ROOT = PROJECT_ROOT + "/apps/caengine/script"
sys.path.append(APPS_ROOT)
import custom # depends on site

import subprocess
sys.path.append(PROJECT_ROOT)
from apps.camodels.modelsframe.personnel import Company, Department, Team, Employee, MembershipforDept, MembershipforTeam, Resources 
from django.core.exceptions import ObjectDoesNotExist

APPS_ROOT = PROJECT_ROOT + "/apps/caengine/etc"
sys.path.append(APPS_ROOT)

def Prepare(cfg):
	#Verify_User = custom.Run(cfg)
	#return Verify_User
	return True # 임시, 배포시 수정

#  Config 파일을 읽어서 작동한다.
class UserImport:
	def __init__(self, cfg):
		self.cfg = cfg

		# Read /opt/JionLab/passwd/etc/passwd file
		self.userlist = []
		'''
		with open(self.cfg.fcp2_passwd, 'r') as f:
			contents = f.read()
		contents = contents.rstrip("\n").decode('utf-16')
		contents = contents.split("\r\n")
		'''
		f = open(self.cfg.fcp2_passwd, 'r')
		for eachline in f:
		#for eachline in contents:
			eachuser = eachline.split(':')
			if len(eachuser) > 1:
				self.userlist.append(eachuser[0])
		f.close()
		# user default password
		self.pwfile =  self.cfg.rootPath + '/INF/TMP/userpw'
		if not os.path.exists(self.cfg.rootPath + '/INF'):
			os.makedirs(self.cfg.rootPath + '/INF')
		
		if not os.path.exists(self.cfg.rootPath + '/INF/TMP'):
			os.makedirs(self.cfg.rootPath + '/INF/TMP')
		else:
			if os.path.exists(self.pwfile):
				os.remove(self.pwfile)

		if self.cfg.import_userpw != '':
			with open(self.pwfile, 'w') as f:
				f.write('\n' + self.cfg.import_userpw + '\n')
		else:
			self.pwfile = ''

	def CheckUserandAppend(self, userid, username):
		isExist = False
		#print('userid: ' + userid)
		for eachid in self.userlist:
			if userid == eachid:
				#print('userid: ' + userid + ', eachid: ' + eachid)
				isExist = True
				break

		if not isExist:
			# Append User
			f = open(self.cfg.fcp2_passwd, 'a')
			s = userid + ':#############,JQ:127.0.0.1,00-00-00-00-00-00'
			s = s + ',' + self.cfg.rootPath + '/PUT/' + userid
			s = s + ',' + self.cfg.rootPath + '/GET/' + userid
			s = s + ',-----,-L-R-:' + username
			self.userlist.append(userid)
			print('Append: ' + s)
			f.write(s + '\n')
			f.close()
			if self.pwfile != '':
				subprocess.call([self.cfg.daemonPath + '/fcp2/bin/fcp2passwd', '-I', self.pwfile, '-p', '10.211.55.78:7776', userid])

	def MakeUserDirectory(self, userdir):
		if not os.path.isdir(self.cfg.rootPath + '/GET/' + userdir):
			os.makedirs(self.cfg.rootPath + '/GET/' + userdir)
		if not os.path.isdir(self.cfg.rootPath + '/PUT/' + userdir):
			os.makedirs(self.cfg.rootPath + '/PUT/' + userdir)

		uid = pwd.getpwnam("corebrdg").pw_uid
		gid = grp.getgrnam("corebrdg").gr_gid
		os.chown(self.cfg.rootPath + '/GET/' + userdir, uid, gid)
		os.chown(self.cfg.rootPath + '/PUT/' + userdir, uid, gid)

	def ResourceInfotoEmployee(self, dept, emp, userid, cursor):
		try:
			if(not os.path.isfile(self.cfg.usersys_inf)):
				print("사용자 자원정보가 없습니다.")
				return

			'''
			# 부산은행 현장 테스트 필요
			# os, osversion 등은 반출입시스템 로그인 시 mysql DB resources field에 등록 하여야함
			querystr = "select NM_IPSTR, MAC, USER_ID, USER_NAME, USER_DEPT_1, USER_DEPT_2, USER_DEPT_3, DEPT_CD, LoginTime from user_view3 where USER_ID=" + userid
			cursor.execute(querystr)
			data=cursor.fetchone()
			if (data == None):
				return False
			for eachdata in data:
				if Resources.objects.filter(employee_id=resources[0]).exists():
                                	res = Resources.objects.filter(employee_id=resources[0])
					for eachres in res:
						if data[0] == eachres.ip:
							eachres.lastlogin = data[8]
							eachres.employee = emp
							eachres.save()
							break
				else:
					res = Resources(employee_id=data[2], os='', osversion='', x86_x64='', systemlocale='', inputlocale='', dotnetruntime='', jionagent='', ip=eachdata[0], lastlogin=data[8]
					res.employee = emp
					res.save()
			'''

			# 테스트 환경예서 임시로 사용
			f = open(self.cfg.usersys_inf, 'r')
			resFlag = False
			for eachline in f:
				resources = eachline.split('\t')
				if resources[0] == userid:
					ips = resources[9].split(' ')
					times = resources[10].split('^')
					if Resources.objects.filter(employee_id=resources[0]).exists():
						res = Resources.objects.filter(employee_id=resources[0])
						if not res:
							break
						timecnt = 0
						for eachres in res: 
							for eachip in ips:				
								if eachip == eachres.ip:
									eachres.os = resources[2]
									eachres.osversion = resources[3]
									eachres.x86_x64 = resources[4]
									eachres.systemlocale = resources[5]
									eachres.inputlocale = resources[6]
									eachres.dotnetruntime = resources[7]
									eachres.jionagent = resources[8]
									eachres.lastlogin = times[timecnt]
									timecnt += 1
									eachres.employee = emp
									eachres.save()
									resFlag = True
									break

						if not resFlag:
							timecnt = 0
							for eachip in ips:
								res = Resources(employee_id=resources[0], os=resources[2], osversion=resources[3], x86_x64=resources[4], systemlocale=resources[5], inputlocale=resources[6], dotnetruntime=resources[7], jionagent=resources[8], ip=eachip, lastlogin=times[timecnt])
								res.employee = emp
								res.save()
								timecnt += 1
					else:
						timecnt = 0
						for eachip in ips:
							res = Resources(employee_id=resources[0], os=resources[2], osversion=resources[3], x86_x64=resources[4], systemlocale=resources[5], inputlocale=resources[6], dotnetruntime=resources[7], jionagent=resources[8], ip=eachip, lastlogin=times[timecnt])
							res.employee = emp
							res.save()
							timecnt += 1
		except Exception as e:
			# 로그로 대체할것
			print('자원정보 DB 등록오류\n' +  str(e))	

	def UpdateUserInfo(self, eachval, approverFlag):
		updateflag = False
		dept = Department.objects.get(departmentid=eachval[6])
		team = Team.objects.get(teamid=eachval[6])
		emp = Employee.objects.get(employeeid=eachval[3])

		deptemp = MembershipforDept.objects.get(mbsfordptid=eachval[3])
		teamemp = MembershipforTeam.objects.get(mbsfortmid=eachval[3])

		# 부서변경
		if deptemp.department.departmentid != eachval[6]:
			updateflag = True
			deptemp.delete()
			deptemp = MembershipforDept(mbsfordptid=eachval[3], employee=emp, department=dept, date_joined=date(1, 1, 1), date_resigned=date(1, 1, 1))
			deptemp.save()
			if approverFlag:
				print('부서변경: 사번=' + eachval[3] + ', 사용자계정=' + eachval[4] + ', 이름=' + eachval[0] + ', 직급코드=' + eachval[2] + ', 직급=' + eachval[1] + ', 직책코드=' + eachval[2] + ', 직책=' + eachval[1] + ', 부서=' + eachval[5] + ', 승인자')
			else:
				print('부서변경: 사번=' + eachval[3] + ', 사용자계정=' + eachval[4] + ', 이름=' + eachval[0] + ', 직급코드=' + eachval[2] + ', 직급=' + eachval[1] + ', 직책코드=' + eachval[2] + ', 직책=' + eachval[1] + ', 부서=' + eachval[5] + ', 사용자')

		# 팀 변경
		if teamemp.team.teamid != eachval[6]:
			updateflag = True
			teamemp.delete()
			teamemp = MembershipforTeam(mbsfortmid=eachval[3], employee=emp, team=team, date_joined=date(1, 1, 1), date_resigned=date(1, 1, 1))
			teamemp.save()
			if approverFlag:
				print('팀변경: 사번=' + eachval[3] + ', 사용자계정=' + eachval[4] + ', 이름=' + eachval[0] + ', 직급코드=' + eachval[2] + ', 직급=' + eachval[1] + ', 직책코드=' + eachval[2] + ', 직책=' + eachval[1] + ', 팀=' + eachval[5] + ', 승인자')
			else:
				print('팀변경: 사번=' + eachval[3] + ', 사용자계정=' + eachval[4] + ', 이름=' + eachval[0] + ', 직급코드=' + eachval[2] + ', 직급=' + eachval[1] + ', 직책코드=' + eachval[2] + ', 직책=' + eachval[1] + ', 팀=' + eachval[5] + ', 사용자')

		# 직급 변경
		if emp.positionid != eachval[2]:
			print ('emp.positionid: ' + emp.positionid + ', eachval[2]: ' + eachval[2])
			emp.delete()
			if approverFlag:
				emp = Employee.objects.create(employeeid=eachval[3], employeenumber=eachval[4], name=eachval[0], positionid=eachval[2], position=eachval[1], dutyid=eachval[2], duty=eachval[1], approverflag=True)
			else:
				emp = Employee.objects.create(employeeid=eachval[3], employeenumber=eachval[4], name=eachval[0], positionid=eachval[2], position=eachval[1], dutyid=eachval[2], duty=eachval[1], approverflag=False)
			updateflag = True
			teamemp.delete()
			teamemp = MembershipforTeam(mbsfortmid=eachval[3], employee=emp, team=team, date_joined=date(1, 1, 1), date_resigned=date(1, 1, 1))
			teamemp.save()
			deptemp.delete()
			deptemp = MembershipforDept(mbsfordptid=eachval[3], employee=emp, department=dept, date_joined=date(1, 1, 1), date_resigned=date(1, 1, 1))
			deptemp.save()
			if approverFlag:
				print('직급변경: 사번=' + eachval[3] + ', 사용자계정=' + eachval[4] + ', 이름=' + eachval[0] + ', 직급코드=' + eachval[2] + ', 직급=' + eachval[1] + ', 직책코드=' + eachval[2] + ', 직책=' + eachval[1] + ', 팀=' + eachval[5] + ', 승인자')
			else:
				print('직급변경: 사번=' + eachval[3] + ', 사용자계정=' + eachval[4] + ', 이름=' + eachval[0] + ', 직급코드=' + eachval[2] + ', 직급=' + eachval[1] + ', 직책코드=' + eachval[2] + ', 직책=' + eachval[1] + ', 팀=' + eachval[5] + ', 사용자')
 
		#if not updateflag:
		#	print('이미 등록된 사용자: ' + '사번=' + eachval[3] +', 이름=' + eachval[0] + ', 직급=' + eachval[1] + ', 부서=' + eachval[5])

	def Run(self):
		'''
		# NAC DB 접속
		con = pymysql.connect(host='130.10.200.129', user='nacview', password='view!@#123', db='DBN_IPPlus', charset='utf8')
		cursor = con.cursor()
		'''
		cursor = '' # 테스트를 위한 더미 변수

		# Open User File
		# 이름, 직급,   직급코드,    사번,        ID,      부서명,  부서코드, 팀명,   팀코드,  메일, 회사명, 회사코드, 직위코드
		# NAME,POSITION,POSITIONCODE,PERSONNUMBER,PERSONID,DEPTNAME,DEPTCODE,TEAMNAME,TEAMCODE,EMAIL,DIVNAME,DIVID,  JIKWICODE

		if(not os.path.isfile(self.cfg.import_file)):
			print("사용자 정보가 없습니다.")
			return

		fn = open(self.cfg.import_file, 'r', encoding='utf-8')
		users = fn.read(-1)
		fn.close()

		# Configure Data
		eachusers = users.split('\n')
		div = []
		for eachman in eachusers:
			eachval = eachman.split(',')
			eachlen = len(eachval)
			divlen = len(div)
			if eachlen < self.cfg.userInfoLength:
				break
			if divlen == 0:
				div.append(eachval[11].strip())
				if not Company.objects.filter(companyid=eachval[11]).exists():
					company = Company(companyid=eachval[11], name=eachval[10], policyname=self.cfg.import_policy, urlpolicyname=self.cfg.import_policy_url)
					company.save()
					print('회사코드=' + eachval[11] +', 회사명=' + eachval[10] + ', 자료전송정책명=' + self.cfg.import_policy + ', url연계정책명=' + self.cfg.import_policy_url)
				#else:
				#	print('이미 등록된 사용자: ' + '회사코드=' + eachval[11] +', 회사명=' + eachval[10])
			else:
				divflag = False
				for eachdiv in div:
					if eachdiv == eachval[11].strip():
						divflag = True	
				if not divflag:
					div.append(eachval[11].strip())
					if not Company.objects.filter(companyid=eachval[11]).exists():
						company = Company(companyid=eachval[11], name=eachval[10], policyname=self.cfg.import_policy, urlpolicyname=self.cfg.import_policy_url)
						company.save()
						print('회사코드=' + eachval[11] +', 회사명=' + eachval[10] + ', 자료전송정책명=' + self.cfg.import_policy + ', url연계정책명=' + self.cfg.import_policy_url)
					#else:
					#	print('이미 등록된 회사: ' + '회사코드=' + eachval[11] +', 회사명=' + eachval[10])
		for eachdiv in div:
			if not eachdiv:
				break
			#isfirstdiv = True
			dif = []
			for eachman in eachusers:
				if not eachman:
					break
				eachval = eachman.split(',')
				eachlen = len(eachval)
				if eachlen < self.cfg.userInfoLength:
					break
				try:
					if eachdiv == eachval[11].strip():
						diflen = len(dif)
						if diflen == 0:
							dif.append(eachval[6].strip())
							# 회사 DB 읽기.
							if not Company.objects.filter(companyid=eachval[11]).exists():
								company = Company(companyid=eachval[11], name=eachval[10], policyname=self.cfg.import_policy, urlpolicyname=self.cfg.import_policy_url)
								company.save()
								print('회사코드=' + eachval[11] +', 회사명=' + eachval[10] + ', 자료전송정책명=' + self.cfg.import_policy + ', url연계정책명=' + self.cfg.import_policy_url)

							# 부서 DB 등록.
							if not Department.objects.filter(departmentid=eachval[6]).exists():
								company = Company(companyid=eachval[11], name=eachval[10], policyname=self.cfg.import_policy, urlpolicyname=self.cfg.import_policy_url)
								dept = Department(departmentid=eachval[6], name=eachval[5], policyname=self.cfg.import_policy, urlpolicyname=self.cfg.import_policy_url, company_id=eachval[11])
								dept.save()
								print('부서코드=' + eachval[6] +', 부서명=' + eachval[5] + ', 자료전송정책명=' + self.cfg.import_policy + ', url연계정책명=' + self.cfg.import_policy_url + ', 회사코드=' + eachval[11])
							#else:
							#	print('이미 등록된 부서: ' + '부서코드=' + eachval[6] +', 부서명=' + eachval[5])

							# 부서 휘하에 팀이 있는 경우에는부서 단위로 루프 돌릴 것
							if not Team.objects.filter(teamid=eachval[6]).exists():
								team = Team(teamid=eachval[6], name=eachval[5], policyname=self.cfg.import_policy, urlpolicyname=self.cfg.import_policy_url, company_id=eachval[11])
								team.save()
								print('팀코드=' + eachval[6] +', 부서명=' + eachval[5] + ', 자료전송정책명=' + self.cfg.import_policy + ', url연계정책명=' + self.cfg.import_policy_url + ', 회사코드=' + eachval[11])
							#else:
							#	print('이미 등록된 팀: ' + '팀코드=' + eachval[6] +', 팀명=' + eachval[5])
						else:
							difflag = False
							for eachdif in dif:
								if eachdif == eachval[6].strip():
									difflag = True
							if not difflag:
								# 부서코드배열 등록
								dif.append(eachval[6].strip())

								# 회사 DB 등록.
								if not Department.objects.filter(departmentid=eachval[6]).exists():
									dept = Department(departmentid=eachval[6], name=eachval[5], policyname=self.cfg.import_policy, urlpolicyname=self.cfg.import_policy_url, company_id=eachval[11])
									dept.save()
									print('부서코드=' + eachval[6] +', 부서명=' + eachval[5] + ', 자료전송정책명=' + self.cfg.import_policy + ', url연계정책명=' + self.cfg.import_policy_url + ', 회사코드=' + eachval[11])
								#else:
								#	print('이미 등록된 부서: ' + '부서코드=' + eachval[6] +', 부서명=' + eachval[5])
	
								# 부서 휘하에 팀이 있는 경우에는부서 단위로 루프 돌릴 것
								if not Team.objects.filter(teamid=eachval[6]).exists():
									team = Team(teamid=eachval[6], name=eachval[5], policyname=self.cfg.import_policy, urlpolicyname=self.cfg.import_policy_url, company_id=eachval[11])
									team.save()
									print('팀코드=' + eachval[6] +', 부서명=' + eachval[5] + ', 자료전송정책명=' + self.cfg.import_policy + ', url연계정책명=' + self.cfg.import_policy_url + ', 회사코드=' + eachval[11])
								#else:
								#	print('이미 등록된 팀: ' + '팀코드=' + eachval[6] +', 팀명=' + eachval[5])
				except Exception as e:
					# 로그로 대체할것
					print('회사정보 DB 등록 및 부서명 추가 오류\n' +  str(e))	
					break	
			for eachdif in dif:
				for eachman in eachusers:
					if not eachman:
						break
					eachval = eachman.split(',')
					try:
						# 부서코드 비교
						if eachdif == eachval[6].strip():
							if not Department.objects.filter(departmentid=eachval[6]).exists():
								dept = Department(departmentid=eachval[6], name=eachval[5], policyname=self.cfg.import_policy, urlpolicyname=self.cfg.import_policy_url, company_id=eachval[11])
								dept.save()
								print('부서코드=' + eachval[6] +', 부서명=' + eachval[5] + ', 자료전송정책명=' + self.cfg.import_policy + ', url연계정책명=' + self.cfg.import_policy_url)
							else:
								dept = Department.objects.get(departmentid=eachval[6])
							if not Team.objects.filter(teamid=eachval[6]).exists():
								team = Team(teamid=eachval[6], name=eachval[5], policyname=self.cfg.import_policy, urlpolicyname=self.cfg.import_policy_url, company_id=eachval[11])
								team.save()
								print('부서코드=' + eachval[6] +', 부서명=' + eachval[5] + ', 자료전송정책명=' + self.cfg.import_policy + ', url연계정책명=' + self.cfg.import_policy_url)
							else:
								team = Team.objects.get(teamid=eachval[6])
							try:
								# 부산읜행의 승인자 추출
								apprvflag = False
								poscode = eachval[2].split('_')
								if len(poscode) == 3 and poscode[1].isdigit():
									if (poscode[2] == 'BSBK' and (int(poscode[1]) >= 100 and int(poscode[1]) <= 140)) or (poscode[2] == 'BSFG' and (int(poscode[1]) == 100 or (int(poscode[1]) >= 110 and int(poscode[1]) <= 140) or (int(poscode[1]) >= 410 and int(poscode[1]) <= 440))):
										apprvflag = True
								if eachval[12] == "P_101_BSFG" or eachval[12] == "P_102_BSFG" or eachval[12] == "P_103_BSFG" or eachval[12] == "P_106_BSFG" or eachval[12] == "P_107_BSFG" or eachval[12] == "P_172_BSFG" or eachval[12] == "P_173_BSFG" or eachval[12] == "P_174_BSFG" or eachval[12] == "P_175_BSFG" or eachval[12] == "P_176_BSFG":
									apprvflag = True
								if apprvflag:
									# OU 사번, 6으로 시작하는 사번은 외주 인력
									if ((eachval[3][0] != 'O') and (eachval[3][0] != '6')):
										if not Employee.objects.filter(employeeid=eachval[3]).exists():
											emp = Employee.objects.create(employeeid=eachval[3], employeenumber=eachval[4], name=eachval[0], positionid=eachval[2], position=eachval[1], dutyid=eachval[2], duty=eachval[1], approverflag=True)
											deptemp = MembershipforDept(mbsfordptid=eachval[3], employee=emp, department=dept, date_joined=date(1, 1, 1), date_resigned=date(1, 1, 1))
											deptemp.save()
											teamemp = MembershipforTeam(mbsfortmid=eachval[3], employee=emp, team=team, date_joined=date(1, 1, 1), date_resigned=date(1, 1, 1))
											teamemp.save()
											print('사번=' + eachval[3] + ', 사용자계정=' + eachval[4] + ', 이름=' + eachval[0] + ', 직급코드=' + eachval[2] + ', 직급=' + eachval[1] + ', 직책코드=' + eachval[2] + ', 직책=' + eachval[1] + ', 부서=' + eachval[5] + ', 승인자')
										elif Department.objects.filter(departmentid=eachval[6]).exists():
											self.UpdateUserInfo(eachval, True)
									else:
										if not Employee.objects.filter(employeeid=eachval[3]).exists():
											emp = Employee.objects.create(employeeid=eachval[3], employeenumber=eachval[4], name=eachval[0], positionid=eachval[2], position=eachval[1], dutyid=eachval[2], duty=eachval[1], approverflag=False)
											deptemp = MembershipforDept(mbsfordptid=eachval[3], employee=emp, department=dept, date_joined=date(1, 1, 1), date_resigned=date(1, 1, 1))
											deptemp.save()
											teamemp = MembershipforTeam(mbsfortmid=eachval[3], employee=emp, team=team, date_joined=date(1, 1, 1), date_resigned=date(1, 1, 1))
											teamemp.save()
											print('사번=' + eachval[3] + ', 사용자계정=' + eachval[4] + ', 이름=' + eachval[0] + ', 직급코드=' + eachval[2] + ', 직급=' + eachval[1] + ', 직책코드=' + eachval[2] + ', 직책=' + eachval[1] + ', 부서=' + eachval[5] + ', 사용자')
										elif Department.objects.filter(departmentid=eachval[6]).exists():
											self.UpdateUserInfo(eachval, False)
								else:
									if not Employee.objects.filter(employeeid=eachval[3]).exists():
										emp = Employee.objects.create(employeeid=eachval[3], employeenumber=eachval[4], name=eachval[0], positionid=eachval[2], position=eachval[1], dutyid=eachval[2], duty=eachval[1], approverflag=False)
										deptemp = MembershipforDept(mbsfordptid=eachval[3], employee=emp, department=dept, date_joined=date(1, 1, 1), date_resigned=date(1, 1, 1))
										deptemp.save()
										teamemp = MembershipforTeam(mbsfortmid=eachval[3], employee=emp, team=team, date_joined=date(1, 1, 1), date_resigned=date(1, 1, 1))
										teamemp.save()
										print('사번=' + eachval[3] + ', 사용자계정=' + eachval[4] + ', 이름=' + eachval[0] + ', 직급코드=' + eachval[2] + ', 직급=' + eachval[1] + ', 직책코드=' + eachval[2] + ', 직책=' + eachval[1] + ', 부서=' + eachval[5] + ', 사용자')
									elif Department.objects.filter(departmentid=eachval[6]).exists():
										self.UpdateUserInfo(eachval, False)

								# 사용자 자원정보 등록
								emp = Employee.objects.get(employeeid=eachval[3])
								self.ResourceInfotoEmployee(dept, emp, eachval[3], cursor)

								# 신규사용자 자료 전송 폴더 생성
								self.MakeUserDirectory(eachval[3])

								# 신규사용자 passwd 등록
								self.CheckUserandAppend(eachval[3].strip(), eachval[0].strip())

							except Exception as e:
								# 로그로 대체할것
								print('안쪽 부서정보 DB 등록 오류\n' +  str(e))
					except Exception as e:
						# 로그로 대체할것
						print('바깥쪽 부서정보 DB 등록 오류\n' +  str(e))

def Run():
	config = caengineconf.config(APPS_ROOT + '/etc/caengined.conf', False)
	if Prepare(config):
		imp = UserImport(config)
		imp.Run()

		#noti = caengineconf.notify(config)
		#noti.UpdateUserImport('True')
if __name__ == "__main__":
	Run()
