#! /usr/bin/python
# coding: utf-8

from django.db import models
from datetime import datetime

#########################
##  File Upload Class  ##
#########################
class Document(models.Model):
	description = models.CharField(max_length=255, blank=True)
	document = models.FileField(upload_to='documents/')
	uploaded_at = models.DateTimeField(auto_now_add=True)

#########################
## Abstract Base Class ##
#########################

from django.core.wsgi import get_wsgi_application
import sys

# 조직도 공통정보
class PersonnelCommonInfo(models.Model):
	name = models.CharField(max_length=255, help_text='명칭을 입력하십시오.', default='명칭없음')
	location = models.CharField(max_length=255, help_text='그룹이 위치한 주소를 임력하십시오.', null=True, blank=True)
	administrator = models.CharField(max_length=255, help_text='관리자 사번을 입력하십시오.', null=True, blank=True)
	policyname = models.CharField(max_length=255, help_text='자료전송정책을 선택하십시오.', default='자료전송정책없음')
	urlpolicyname  = models.CharField(max_length=255, help_text='URL연계정책을 선택하십시오.', default='URL연계정책없음')

	class Meta:
		app_label="camodels"
	#	abstract = True

# URL연계 공통정보
class URLCommonInfo(models.Model):
	domain = models.CharField(max_length=20, help_text='WebProxy서버 주소 입니다.', default='WebProxy 서버주소없음', null=True, blank=True)
	port = models.IntegerField(help_text='WebProxy 서버포트 입니다.', default=0, null=True, blank=True)

	class Meta:
		app_label="camodels"
	#	abstract = True

# 메일연계 공통정보
class MailCommonInfo(models.Model):
	domain = models.CharField(max_length=20, help_text='WebProxy서버 주소 입니다.', default='WebProxy 서버주소없음', null=True, blank=True)
	port = models.IntegerField(help_text='WebProxy 서버포트 입니다.', default=0, null=True, blank=True)
	syncinterval = models.IntegerField(help_text='내부망 발신메일서버 동기화 간격입니다.', default=0, null=True, blank=True)
	usessl = models.BooleanField(default=True)

	class Meta:
		app_label="camodels"
	#	abstract = True

# 승인절차 공통정보
class ApproveProcessCommonInfo(models.Model):
	date = models.DateTimeField(default=datetime.now, blank=True, help_text='로그 생성 서버 시간 입니다.')
	state = models.CharField(max_length=20, help_text='승인상태입니다.', default='상태', null=True, blank=True)
	requester = models.CharField(max_length=255, help_text='승인신청자입니다.', default='승인신청자없음', null=True, blank=True)
	approver = models.CharField(max_length=255, help_text='승인자입니다.', default='승인자없음', null=True, blank=True)
	sendtype = models.CharField(max_length=20, help_text='전송형태입니다.', default='전송형태없음', null=True, blank=True)
	mediatype = models.CharField(max_length=20, help_text='매체형식입니다.', default='매체형식없음', null=True, blank=True)
	direction = models.CharField(max_length=20, help_text='전송방향입니다.', default='전송방향없음', null=True, blank=True)
	reason = models.CharField(max_length=255, help_text='전송사유입니다.', default='전송사유없음', null=True, blank=True)
	dlpinformation = models.TextField(help_text='개인정보 검출내역입니다.', default='개인정보없음', null=True, blank=True)

	class Meta:
		app_label="camodels"
	#	abstract = True

# 발신전송정책 공통정보
class TransmissionPolicyCommonInfo(models.Model):
	usetransmission = models.BooleanField(default=False, help_text='외부망 전송기능 사용여부입니다.')
	useexternalservice = models.BooleanField(default=False, help_text='외부서비스연계 사용여부입니다.')
	useapprove = models.BooleanField(default=False, help_text='승인기능 사용여부입니다.')
	useclipboard = models.BooleanField(default=False, help_text='클립보드발신기능 사용여부입니다.')
	usecertifiate = models.BooleanField(default=False, help_text='공인인증서발신기능 사용여부입니다.')
	usewebproxy = models.BooleanField(default=False, help_text='URL연계기능 사용여부입니다.')
	usemail = models.BooleanField(default=False, help_text='메일발신기능 사용여부입니다.')

	class Meta:
		app_label="camodels"
	#	abstract = True

# 발신파일정책 공통정보
class FilesPolicyCommonInfo(models.Model):
	maximumfilesize = models.IntegerField(help_text='전체파일의 전송 가능한  최대용량입니다.', default=0, null=True, blank=True)
	onetimefilesize = models.IntegerField(help_text='1회 전송 가능한 최대용량입니다.', default=0, null=True, blank=True)
	maximumfiles = models.IntegerField(help_text='1회 전송시 최대 파일 갯수 입니다.', default=0, null=True, blank=True)
	reasonlength = models.IntegerField(help_text='전송사유 최대길이 입니다.', default=0, null=True, blank=True)
	checkcompressfile = models.BooleanField(default=True, help_text='압축파일을 검사합니다.')
	sendfolder = models.BooleanField(default=True, help_text='폴더를 전송 합니다.')
	whiteextension = models.BooleanField(default=True, help_text='전송 가능한 확장자입니다.')
	blackextension = models.BooleanField(default=True, help_text='전송 불가능한 확장자입니다.')

	class Meta:
		app_label="camodels"
	#	abstract = True

# 발신외부서비스연계정책  공통정보
class ExternalServicePolicyCommonInfo(models.Model):
	enableservice = models.BooleanField(default=True, help_text='외부서비스연계 사용여부입니다.')
	services = models.CharField(max_length=20, help_text='외부서비스연계 내역입니다.', default='WebProxy 서버주소없음', null=True, blank=True)
	clientvaccine = models.BooleanField(default=True, help_text='P C백신 사용여부입니다.')
	servervaccine = models.BooleanField(default=True, help_text='서버백신 사용여부입니다.')
	forgerydetection = models.BooleanField(default=True, help_text='위변조검사 사용여부입니다.')

	class Meta:
		app_label="camodels"
	#	abstract = True

# 발신승인정책 공통정보 
class ApprovePolicyCommonInfo(models.Model):
	step = models.IntegerField(help_text='승인단계 입니다.', default=0, null=True, blank=True)
	oneselfallowed = models.BooleanField(default=True, help_text='승인자 본인승인가능 여부입니다.')
	samepositionallowed = models.BooleanField(default=True, help_text='동일망에서만 승인가능 여부입니다.')
	checkpassword = models.BooleanField(default=True, help_text='승인시 패스워드 사용여부입니다.')
	mandate = models.BooleanField(default=True, help_text='승인위임기능 사용여부입니다.')
	exceptextension = models.CharField(max_length=255, help_text='승인예외 확장자입니다.', null=True, blank=True)
	externalapprover = models.CharField(max_length=255, help_text='해당정책 사용 부서의 외부 대표승인자입니다.', null=True, blank=True)
	secuapprover = models.CharField(max_length=255, help_text='해당정책 사용 부서의 개인정보 검출파일  승인자입니다.', null=True, blank=True)

	class Meta:
		app_label="camodels"
	#	abstract = True

#클립보드정책 공통정보
class ClipboardPolicyCommonInfo(models.Model):
	maximumtextsize = models.IntegerField(help_text='문서 클립보드전송 최대크기입니다.', default=0, null=True, blank=True)
	maximumimagesize = models.IntegerField(help_text='이미지 클립보드전송 최대크기입니다.', default=0, null=True, blank=True)

	class Meta:
		app_label="camodels"
	#	abstract = True

#수신정책 공통정보
class ReceptionPolicyCommonInfo(models.Model):
	usereception = models.BooleanField(default=True)
	useclientvaccine = models.BooleanField(default=True)
	useclipboard = models.BooleanField(default=True)
	usecertificate = models.BooleanField(default=True)
	usereceivemail = models.BooleanField(default=True)

	class Meta:
		app_label="camodels"
	#	abstract = True

# 비고 공통정보
class ReferenceCommonInfo(models.Model):
	reference = models.CharField(max_length=255, help_text='비고', null=True, blank=True)

	class Meta:
		app_label="camodels"
	#	abstract = True
