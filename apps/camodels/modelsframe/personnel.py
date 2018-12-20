#! /usr/bin/python
# coding: utf-8

from django.db import models
from datetime import date, datetime
from django.utils import timezone
import pytz

from .common import PersonnelCommonInfo, ApproveProcessCommonInfo

######################
## Models Personnel ##
######################

###########################
## Personnel Information ##
###########################
# 직원정보
class Employee(models.Model):
	employeeid = models.CharField(max_length=255, primary_key=True, default='1357', unique=True)
	employeenumber = models.CharField(max_length=255, help_text='사번입니다.', default='사번없음')
	name = models.CharField(max_length=255, help_text='직원 이름입니다..', default='이름없음')
	positionid = models.CharField(max_length=255, help_text='직급id입니다.', default='직급없음')
	position = models.CharField(max_length=255, help_text='직급입니다.', default='직급없음')
	dutyid = models.CharField(max_length=255, help_text='직책id입니다.', default='직책없음')
	duty = models.CharField(max_length=255, help_text='직책입니다.', default='직책없음')
	mail = models.CharField(max_length=255, help_text='메일 주소입니다.', default='mail@address.co.kr')
	approverflag = models.BooleanField(default=False)
	administratorflag = models.BooleanField(default=False)
	#mandate = models.CharField(max_length=255, help_text='승인위임 내역입니다.')

	def __unicode__(self):
		return u'%s %s %s %s %s %s' % (self.name, self.position, self.duty, self.mail, self.mandate, self.reference)

	class Meta:
		app_label="camodels"

# 팀원 입사정보
# 회사정보
class Company(models.Model):
	companyid = models.CharField(max_length=255, primary_key=True, default='1357', unique=True)
	name = models.CharField(max_length=255, help_text='명칭을 입력하십시오.', default='명칭없음')
	location = models.CharField(max_length=255, help_text='그룹이 위치한 주소를 임력하십시오.', null=True, blank=True)
	administrator = models.CharField(max_length=255, help_text='관리자 사번을 입력하십시오.', null=True, blank=True)
	policyname = models.CharField(max_length=255, help_text='자료전송정책을 선택하십시오.', default='자료전송정책없음')
	urlpolicyname  = models.CharField(max_length=255, help_text='URL연계정책을 선택하십시오.', default='URL연계정책없음')

	def __unicode__(self):
		return u'%s %s %s %s %s %s' % (self.name, self.location, self.administrator, self.policyname, self.urlpolicyname, self.reference)

	class Meta:
		app_label="camodels"

# 부서정보
class Department(models.Model):
	departmentid = models.CharField(max_length=255, primary_key=True, default='1357', unique=True)
	company = models.ForeignKey(Company, on_delete=models.CASCADE, default='1357')
	employee = models.ManyToManyField(Employee, through='MembershipforDept')
	name = models.CharField(max_length=255, help_text='명칭을 입력하십시오.', default='명칭없음')
	location = models.CharField(max_length=255, help_text='그룹이 위치한 주소를 임력하십시오.', null=True, blank=True)
	administrator = models.CharField(max_length=255, help_text='관리자 사번을 입력하십시오.', null=True, blank=True)
	policyname = models.CharField(max_length=255, help_text='자료전송정책을 선택하십시오.', default='자료전송정책없음')
	urlpolicyname  = models.CharField(max_length=255, help_text='URL연계정책을 선택하십시오.', default='URL연계정책없음')

	def __unicode__(self):
		return u'%s %s %s %s %s %s' % (self.name, self.location, self.administrator, self.policyname, self.urlpolicyname, self.reference)

	class Meta:
		app_label="camodels"

# 팀정보
class Team(models.Model):
	teamid = models.CharField(max_length=255, primary_key=True, default='1357', unique=True)
	company = models.ForeignKey(Company, on_delete=models.CASCADE, default='1357')
	employee = models.ManyToManyField(Employee, through='MembershipforTeam')
	name = models.CharField(max_length=255, help_text='명칭을 입력하십시오.', default='명칭없음')
	location = models.CharField(max_length=255, help_text='그룹이 위치한 주소를 임력하십시오.', null=True, blank=True)
	administrator = models.CharField(max_length=255, help_text='관리자 사번을 입력하십시오.', null=True, blank=True)
	policyname = models.CharField(max_length=255, help_text='자료전송정책을 선택하십시오.', default='자료전송정책없음')
	urlpolicyname  = models.CharField(max_length=255, help_text='URL연계정책을 선택하십시오.', default='URL연계정책없음')

	def __unicode__(self):
		return u'%s %s %s %s %s %s' % (self.name, self.location, self.administrator, self.policyname, self.urlpolicyname, self.reference)

	class Meta:
		app_label="camodels"

# 부서/팀의 외부승인자
class ExternalApprover(models.Model):
	externalapproverid = models.AutoField(primary_key=True)
	department = models.ManyToManyField(Department)
	team = models.ManyToManyField(Team)
	externalapprover = models.CharField(max_length=255, help_text='외부승인자입니다.', default='승인자없음', null=True, blank=True)

	def __unicode__(self):
		return u'%s %s' % (self.externalapprover, self.reference)

	class Meta:
		app_label="camodels"

#####################
## Approve Process ##
#####################
# 승인절차
class ApproveProcess(models.Model):
	approveprocessid = models.IntegerField(primary_key=True)
	employee = models.ManyToManyField(Employee, through='MembershipforProc')
	date = models.DateTimeField(default=datetime.now, blank=True, help_text='로그 생성 서버 시간 입니다.')
	state = models.CharField(max_length=20, help_text='승인상태입니다.', default='상태', null=True, blank=True)
	requester = models.CharField(max_length=255, help_text='승인신청자입니다.', default='승인신청자없음', null=True, blank=True)
	approver = models.CharField(max_length=255, help_text='승인자입니다.', default='승인자없음', null=True, blank=True)
	sendtype = models.CharField(max_length=20, help_text='전송형태입니다.', default='전송형태없음', null=True, blank=True)
	mediatype = models.CharField(max_length=20, help_text='매체형식입니다.', default='매체형식없음', null=True, blank=True)
	direction = models.CharField(max_length=20, help_text='전송방향입니다.', default='전송방향없음', null=True, blank=True)
	reason = models.CharField(max_length=255, help_text='전송사유입니다.', default='전송사유없음', null=True, blank=True)
	dlpinformation = models.TextField(help_text='개인정보 검출내역입니다.', default='개인정보없음', null=True, blank=True)

	def __unicode__(self):
		return u'%s %s %s %s %s %s %s %s %s' % (self.state, self.requester, self.approver, self.sendtype, self.mediatype, self.direction, self.reason, self.dlpinformation, self.reference)

	class Meta:
		app_label="camodels"

# 승인절차 로그정보
class ApproveProcessLog(models.Model):
	approveprocesslogid = models.IntegerField(primary_key=True)
	approveprocess_approveprocessid = models.ForeignKey(ApproveProcess, on_delete=models.CASCADE, default='1357')
	date = models.DateTimeField(default=datetime.now, blank=True, help_text='로그 생성 서버 시간 입니다.')
	state = models.CharField(max_length=20, help_text='승인상태입니다.', default='상태', null=True, blank=True)
	requester = models.CharField(max_length=255, help_text='승인신청자입니다.', default='승인신청자없음', null=True, blank=True)
	approver = models.CharField(max_length=255, help_text='승인자입니다.', default='승인자없음', null=True, blank=True)
	sendtype = models.CharField(max_length=20, help_text='전송형태입니다.', default='전송형태없음', null=True, blank=True)
	mediatype = models.CharField(max_length=20, help_text='매체형식입니다.', default='매체형식없음', null=True, blank=True)
	direction = models.CharField(max_length=20, help_text='전송방향입니다.', default='전송방향없음', null=True, blank=True)
	reason = models.CharField(max_length=255, help_text='전송사유입니다.', default='전송사유없음', null=True, blank=True)
	dlpinformation = models.TextField(help_text='개인정보 검출내역입니다.', default='개인정보없음', null=True, blank=True)

	def __unicode__(self):
		return u'%s %s %s %s %s %s %s %s' % (self.state, self.requester, self.approver, self.sendtype, self.mediatype, self.direction, self.reason, self.dlpinformation)

	class Meta:
		app_label="camodels"

##########################
## Mandate Information ##
##########################
# 승인위임정보
class Mandate(models.Model):
	mandateid = models.IntegerField(primary_key=True)
	employee = models.ForeignKey(Employee, on_delete=models.CASCADE, default='1357')
	approveprocess_approveprocessid = models.ForeignKey(ApproveProcess, on_delete=models.CASCADE, default='1357')
	startdate = models.DateTimeField(default=datetime.now, blank=True, help_text='승인위임 시작시간을 입력하십시오.')
	enddate = models.DateTimeField(default=datetime.now, blank=True, help_text='승인위임 종료시간을을 입력하십시오.')
	requester = models.CharField(max_length=255, help_text='승인신청자를 확인하십시오.', default='승인신청자없음', null=True, blank=True)
	approver = models.CharField(max_length=255, help_text='승인자를 확인하십시오.', default='승인자없음', null=True, blank=True)

	def __unicode__(self):
		return u'%s %s %s' % (self.requester, self.approver, self.reference)

	class Meta:
		app_label="camodels"

##########################
## Employee Information ##
##########################
# 부서원 입사정보
class MembershipforDept(models.Model):
	mbsfordptid = models.CharField(max_length=255, primary_key=True, default='1357', unique=True)
	employee = models.ForeignKey(Employee, on_delete=models.CASCADE, default='1357')
	department = models.ForeignKey(Department, on_delete=models.CASCADE, default='1357')
	date_joined = models.DateField(default=datetime.now, blank=True, help_text='입사일을 입력하십시오.')
	date_resigned = models.DateField(auto_now_add=False, blank=True, help_text='퇴사일을 입력하십시오.')
	joined_reason = models.CharField(max_length=255, help_text='입사 사유를 입력하십시오.', null=True, blank=True)
	
	class Meta:
		app_label="camodels"
# 팀원 입사정보
class MembershipforTeam(models.Model):
	mbsfortmid = models.CharField(max_length=255, primary_key=True, default='1357', unique=True)
	employee = models.ForeignKey(Employee, on_delete=models.CASCADE, default='1357')
	team = models.ForeignKey(Team, on_delete=models.CASCADE, default='1357')
	date_joined = models.DateField(default=datetime.now, blank=True, help_text='입사일을 입력하십시오.')
	date_resigned = models.DateField(auto_now_add=False, blank=True, help_text='퇴사일을 입력하십시오.')
	joined_reason = models.CharField(max_length=255, help_text='입사 사유를 입력하십시오.', null=True, blank=True)
	
	class Meta:
		app_label="camodels"

# 승인절차 입사정보
class MembershipforProc(models.Model):
	approveprocess = models.ForeignKey(ApproveProcess, on_delete=models.CASCADE, default='1357')
	employee = models.ForeignKey(Employee, on_delete=models.CASCADE, default='1357')
	date_joined = models.DateField(default=datetime.now, blank=True, help_text='입사일을 입력하십시오.')
	date_resigned = models.DateField(auto_now_add=False, blank=True, help_text='퇴사일을 입력하십시오.')
	joined_reason = models.CharField(max_length=255, help_text='입사 사유를 입력하십시오.', null=True, blank=True)
	
	class Meta:
		app_label="camodels"

##########################
## Matarial Information ##
##########################
# 승인절차의 전송파일정보
class Files(models.Model):
	fileid = models.IntegerField(primary_key=True)
	approveprocess_approveprocessid = models.ForeignKey(ApproveProcess, on_delete=models.CASCADE, default='1357')
	path = models.CharField(max_length=512, help_text='파일경로입니다.', default='파일경로없음', null=True, blank=True)
	filename = models.CharField(max_length=256, help_text='파일이름입니다.', default='파일이름없음', null=True, blank=True)
	filetype = models.CharField(max_length=20, help_text='파일형식입니다.', default='파일형식없음', null=True, blank=True)
	filesize = models.IntegerField(help_text='파일크기입니다.', default=0, null=True, blank=True)
	attribute = models.CharField(max_length=20, help_text='파일속성정보입니다.', default='파일속성정보없음', null=True, blank=True)
	encoding = models.BooleanField(help_text='사용자 암호화 여부입니다.', null=False, blank=True, default=False)
	innercompressfile = models.TextField(help_text='압축파일내 파일정보입니다.', default='압축파일내 파일정보없음', null=True, blank=True)

	def __unicode__(self):
		return u'%s %s %s %s %s %s' % (self.path, self.filename, self.filetype, self.filesize, self.attribute, self.innercompressfile)

	class Meta:
		app_label="camodels"
	#	abstract = True

# 직원별 자원정보
class Resources(models.Model):
	resourcesid = models.AutoField(primary_key=True)
	employee = models.ForeignKey(Employee, on_delete=models.CASCADE, default='1357')
	os = models.CharField(max_length=255, help_text='OS를 확인하십시오.', default='OS', null=True, blank=True)
	osversion = models.CharField(max_length=255, help_text='OS Vession을 확인하십시오.', default='OS Version 없음', null=True, blank=True)
	x86_x64 = models.CharField(max_length=255, help_text='32비트/64비트 패키지를 확인하십시오.', default='x86_x64 없음', null=True, blank=True)
	systemlocale = models.CharField(max_length=255, help_text='시스템 문자 형식을 확인하십시오.', default='시스템문자형식없음', null=True, blank=True)
	inputlocale = models.CharField(max_length=255, help_text='입력 문자형식을 확인하십시오.', default='입력문자형식없음',null=True, blank=True)
	dotnetruntime = models.CharField(max_length=255, help_text='닷넷 버전을 확인하십시오.', default='닷넷런타임없음',null=True, blank=True)
	jionagent = models.CharField(max_length=255, help_text='자료반출입에이전트 버전을 확인하십시오.', default='자료반출입에이전트버전없음',null=True, blank=True)
	ip = models.CharField(max_length=512, help_text='직원 PC IP 입니다.', default='ip정보없음', null=True, blank=True)
	lastlogin = models.DateTimeField(default=datetime.now, blank=True, help_text='최종 로그인 시간 입니다.')

	def __unicode__(self):
		return u'%s %s %s %s %s %s %s %s %s' % (self.os, self.osversion, self.x86_x64, self.systemlocale, self.inputlocale, self.dotnetruntime, self.jionagent, self.ip, self.reference)

	class Meta:
		app_label="camodels"

