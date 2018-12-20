#! /usr/bin/python
# coding: utf-8

from django.db import models
from django.forms import ModelForm
from datetime import datetime

from .common import FilesPolicyCommonInfo, ExternalServicePolicyCommonInfo, ApprovePolicyCommonInfo, TransmissionPolicyCommonInfo, ClipboardPolicyCommonInfo, URLCommonInfo, MailCommonInfo
from .personnel import Company

########################
## Transaction Policy ##
########################
# 내부망발신 파일정책
class InFilesPolicy(models.Model):
	ZERO = 0
	ONE = 1
	TWO = 2
	THREE = 3
	FOUR = 3
	MAX_SIZE = (
		(ZERO, '제한없음'),
		(ONE, '10 M'),
		(TWO, '100 M'),
		(THREE, '500 M'),
		(FOUR, '1 G'),
	)
	ONETIME_SIZE = (
		(ZERO, '제한없음'),
		(ONE, '5 개'),
		(TWO, '10 개'),
	)

	REASON_LENGTH = (
		(ZERO, '제한없음'),
		(ONE, '5 글자 이상'),
		(TWO, '10 글자 이상'),
	)

	filesid = models.AutoField(primary_key=True)
	maximumfilesize = models.IntegerField(help_text='전체파일의 전송 가능한  최대용량입니다.', default=0, null=True, choices=MAX_SIZE, verbose_name=u"첨부파일 최대크기")
	onetimefilesize = models.IntegerField(help_text='1회 전송 가능한 최대용량입니다.', default=0, null=True, choices=MAX_SIZE, verbose_name=u"1회전송 파일크기 합")
	maximumfiles = models.IntegerField(help_text='1회 전송시 최대 파일 갯수 입니다.', default=0, null=True, choices=ONETIME_SIZE, verbose_name=u"파일갯수")
	reasonlength = models.IntegerField(help_text='전송사유 최대길이 입니다.', default=0, null=True, verbose_name=u"전송사유 길이", choices=REASON_LENGTH)
	checkcompressfile = models.BooleanField(default=True, help_text='압축파일을 검사합니다.', verbose_name=u"압축파일 검사")
	sendfolder = models.BooleanField(default=True, help_text='폴더를 전송 합니다.', verbose_name=u"폴더전송")
	whiteextension = models.BooleanField(default=True, help_text='전송 가능한 확장자입니다.', verbose_name=u"전송가능 확장자")
	blackextension = models.BooleanField(default=True, help_text='전송 불가능한 확장자입니다.', verbose_name=u"전송불가 확장자")

	def __unicode__(self):
		return u'%s' % (self.reference)

	class Meta:
		app_label="camodels"

# 내부망발신 외부서비스연계정책
class InExternalServicePolicy(models.Model):
	extsvcid = models.AutoField(primary_key=True)
	enableservice = models.BooleanField(default=True, help_text='외부서비스연계 사용여부입니다.', verbose_name=u"외부서비스 연계")
	services = models.CharField(max_length=20, help_text='외부서비스연계 내역입니다.', default='WebProxy 서버주소없음', null=True, verbose_name=u"외부서비스 연계내역")
	clientvaccine = models.BooleanField(default=True, help_text='PC백신 사용여부입니다.', verbose_name=u"PC백신")
	servervaccine = models.BooleanField(default=True, help_text='서버백신 사용여부입니다.', verbose_name=u"서버백신")
	forgerydetection = models.BooleanField(default=True, help_text='위변조검사 사용여부입니다.', verbose_name=u"위변조 검사")

	def __unicode__(self):
		return u'%s %s' % (self.services, self.reference)

	class Meta:
		app_label="camodels"

# 내부망발신 승인정책
class InApprovePolicy(models.Model):
	ZERO = 0
	ONE = 1
	TWO = 2
	THREE = 3
	APPROVE_LEVEL = (
		(ZERO, '사용안함'),
		(ONE, '1단계'),
		(TWO, '2단계'),
	)

	POST_FACTO = (
		(ZERO, '사용안함'),
		(ONE, '승인후사용'),
		(TWO, '시간외사용'),
		(THREE, '항상사용'),
	)

	approveid = models.AutoField(primary_key=True)
	step = models.IntegerField(help_text='승인단계 입니다.', default=0, null=True, choices=APPROVE_LEVEL, verbose_name=u"승인단계")
	oneselfallowed = models.BooleanField(default=True, help_text='승인자 본인승인가능 여부입니다.', verbose_name=u"본인승인 가능")
	samepositionallowed = models.BooleanField(default=True, help_text='동일망에서만 승인가능 여부입니다.', verbose_name=u"동일망에서만 승인")
	checkpassword = models.BooleanField(default=True, help_text='승인시 암호확인 여부입니다.', verbose_name=u"승인시 암호확인")
	postfacto = models.IntegerField(help_text='사후승인사용 여부입니다.', default=0, null=True, choices=POST_FACTO, verbose_name=u"사후승인")
	mandate = models.BooleanField(default=True, help_text='승인위임기능 사용여부입니다.', verbose_name=u"승인위임")
	exceptextension = models.CharField(max_length=255, help_text='승인예외 확장자입니다.', null=True, verbose_name=u"승인예외 확장자")
	externalapprover = models.CharField(max_length=255, help_text='해당정책 사용 부서의 외부 대표승인자입니다.', null=True, verbose_name=u"외부승인자")
	secuapprover = models.CharField(max_length=255, help_text='해당정책 사용 부서의 개인정보 검출파일  승인자입니다.', null=True, verbose_name=u"개인정보검출 승인자")

	def __unicode__(self):
		return u'%s %s %s %s' % (self.exceptextension, self.externalapprover, self.secuapprover, self.reference)

	class Meta:
		app_label="camodels"

# 내부망발신 클립보드정책
class InClipboardPolicy(models.Model):
	ZERO = 0
	ONE = 1
	TWO = 2
	THREE = 3
	FOUR = 4
	MAX_TEXT_SIZE = (
		(ZERO, '제한없음'),
		(ONE, '1000'),
		(TWO, '10000'),
	)
	MAX_IMAGE_SIZE = (
		(ZERO, '제한없음'),
		(ONE, '10 M'),
		(TWO, '100 M'),
		(THREE, '500 M'),
		(FOUR, '1 G'),
	)

	clipboardid = models.AutoField(primary_key=True)
	maximumtextsize = models.IntegerField(help_text='문서 클립보드전송 최대길이입니다.', default=0, null=True, choices=MAX_TEXT_SIZE, verbose_name=u"문자길이")
	maximumimagesize = models.IntegerField(help_text='이미지 클립보드전송 최대크기입니다.', default=0, null=True, choices=MAX_IMAGE_SIZE, verbose_name=u"이미지크기")

	def __unicode__(self):
		return u'%s' % (self.reference)

	class Meta:
		app_label="camodels"

# 내부망발신 WebProxy정책
class InWebProxyPolicy(models.Model):
	webproxyid = models.AutoField(primary_key=True)
	innerdomain = models.TextField(help_text='전송 금지할 내부도메인 목록입니다.', default='내부도메인없음', null=True, verbose_name=u"전송금지 내부도메인")
	outerdomain = models.CharField(max_length=20, help_text='URL연계서버 주소입니다.', default='URL연계서버 주소없음', null=True, verbose_name=u"URL연계서버 주소")
	port = models.IntegerField(help_text='WebProxy서버 포트입니다.', default=0, null=True, verbose_name=u"URL연계서버 포트")

	def __unicode__(self):
		return u'%s %s %s' % (self.domain, self.innerdomain, self.reference)

	class Meta:
		app_label="camodels"

# 내부망발신 메일정책
class InSendMailPolicy(models.Model):
	ZERO = 0
	ONE = 1
	TWO = 2
	THREE = 3
	SYNC_INTERVAL = (
		(ZERO, '0'),
		(ONE, '1'),
		(TWO, '10'),
	)

	sendmailid = models.AutoField(primary_key=True)
	domain = models.CharField(max_length=20, help_text='내부망 발신메일서버 주소입니다.', default='메일서버 주소없음', null=True, verbose_name=u"내부망 메일서버 주소")
	port = models.IntegerField(help_text='내부망 발신메일서버 포트입니다.', default=0, null=True, verbose_name=u"내부망 메일서버 포트")
	syncinterval = models.IntegerField(help_text='내부망 발신메일서버 동기화 간격입니다.', default=0, null=True, choices=SYNC_INTERVAL, verbose_name=u"동기화 간격")
	usessl = models.BooleanField(default=True, verbose_name=u"SSL 사용")

	def __unicode__(self):
		return u'%s %s' % (self.domain, self.reference)

	class Meta:
		app_label="camodels"

# 내부망수신 메일정책
class InReceivedMailPolicy(models.Model):
	ZERO = 0
	ONE = 1
	TWO = 2
	THREE = 3
	SYNC_INTERVAL = (
		(ZERO, '0'),
		(ONE, '1'),
		(TWO, '10'),
	)

	receivedmailid = models.AutoField(primary_key=True)
	domain = models.CharField(max_length=20, help_text='내부망 수신메일서버 주소입니다.', default='메일서버 주소없음', null=True, verbose_name=u"내부망 메일서버 주소")
	port = models.IntegerField(help_text='내부망 수신메일서버 포트입니다.', default=0, null=True, verbose_name=u"내부망 메일서버 포트")
	syncinterval = models.IntegerField(help_text='내부망 수신메일서버 동기화 간격입니다.', default=0, null=True, choices=SYNC_INTERVAL, verbose_name=u"동기화 간격")
	usessl = models.BooleanField(default=True, verbose_name=u"SSL 사용")

	def __unicode__(self):
		return u'%s %s' % (self.domain, self.reference)

	class Meta:
		app_label="camodels"

# 내부망수신 정책
class InReceptionPolicy(models.Model):
	inreceptid = models.AutoField(primary_key=True)
	inrcvmailid = models.ForeignKey(InReceivedMailPolicy, on_delete=models.CASCADE, verbose_name=u"내부망수신 메일정책")

	class Meta:
		app_label="camodels"

# 내부망 전송정책
class InTransmissionPolicy(models.Model):
	ZERO = 0
	ONE = 1
	TWO = 2
	APPROVE_LEVEL = (
		(ZERO, '사용안함'),
		(ONE, '1단계'),
		(TWO, '2단계'),
	)

	intransid = models.AutoField(primary_key=True)
	usetransmission = models.BooleanField(default=False, help_text='파일반출기능 사용여부입니다.', verbose_name=u"파일반출")
	infilespolicy = models.OneToOneField(InFilesPolicy, on_delete=models.CASCADE, verbose_name=u"파일반출 세부정책")

	useexternalservice = models.BooleanField(default=False, help_text='외부서비스연계 사용여부입니다.', verbose_name=u"외부서비스연계")
	inexternalservicepolicy = models.OneToOneField(InExternalServicePolicy, on_delete=models.CASCADE, verbose_name=u"외부서비스연계 세부정책")

	useapprove = models.IntegerField(default=False, help_text='승인기능 사용여부입니다.', choices=APPROVE_LEVEL, verbose_name=u"승인단계")
	inapprovepolicy = models.OneToOneField(InApprovePolicy, on_delete=models.CASCADE, verbose_name=u"승인단계 세부정책")

	useclipboard = models.BooleanField(default=False, help_text='클립보드반출기능 사용여부입니다.', verbose_name=u"클립보드반출")
	inclipboardpolicy = models.OneToOneField(InClipboardPolicy, on_delete=models.CASCADE, verbose_name=u"클립보드반출 세부정책")

	usecertifiate = models.BooleanField(default=False, help_text='공인인증서반출기능 사용여부입니다.', verbose_name=u"공인인증서반출")

	usewebproxy = models.BooleanField(default=False, help_text='URL연계기능 사용여부입니다.', verbose_name=u"웹사이트연계")
	inwebproxypolicy = models.OneToOneField(InWebProxyPolicy, on_delete=models.CASCADE, verbose_name=u"웹사이트연계 세부정책")

	usemail = models.BooleanField(default=False, help_text='메일반출기능 사용여부입니다.', verbose_name=u"메일반출")
	insendmailpolicy = models.OneToOneField(InSendMailPolicy, on_delete=models.CASCADE, verbose_name=u"메일반출 세부정책")

	def __unicode__(self):
		return u'%s' % (self.reference)

	class Meta:
		app_label="camodels"

# 내부망 정책
class InPolicy(models.Model):
	innerpolicyid = models.AutoField(primary_key=True)
	intransmissionpolicy = models.OneToOneField(InTransmissionPolicy, on_delete=models.CASCADE, verbose_name=u"내부망 반출정책")
	inreceptionpolicy = models.OneToOneField(InReceptionPolicy, on_delete=models.CASCADE, verbose_name=u"내부망 반입정책")
	#inreceivemailpolicy = models.OneToOneField(InReceivedMailPolicy, on_delete=models.CASCADE)
	policyname = models.CharField(max_length=20, help_text='정책명 입니다.', null=True, verbose_name=u"정책명")

	def __unicode__(self):
		return u'%s %s' % (self.policyname, self.reference)

	class Meta:
		app_label="camodels"

# 외부망발신 파일정책
class OutFilesPolicy(models.Model):
	ZERO = 0
	ONE = 1
	TWO = 2
	THREE = 3
	FOUR = 3
	MAX_SIZE = (
		(ZERO, '제한없음'),
		(ONE, '10 M'),
		(TWO, '100 M'),
		(THREE, '500 M'),
		(FOUR, '1 G'),
	)
	ONETIME_SIZE = (
		(ZERO, '제한없음'),
		(ONE, '5 개'),
		(TWO, '10 개'),
	)

	REASON_LENGTH = (
		(ZERO, '제한없음'),
		(ONE, '5 글자 이상'),
		(TWO, '10 글자 이상'),
	)

	filesid = models.AutoField(primary_key=True)
	maximumfilesize = models.IntegerField(help_text='전체파일의 전송 가능한  최대용량입니다.', default=0, null=True, choices=MAX_SIZE, verbose_name=u"첨부파일 최대크기")
	onetimefilesize = models.IntegerField(help_text='1회 전송 가능한 최대용량입니다.', default=0, null=True, choices=MAX_SIZE, verbose_name=u"1회전송 파일크기 합")
	maximumfiles = models.IntegerField(help_text='1회 전송시 최대 파일 갯수 입니다.', default=0, null=True, choices=ONETIME_SIZE, verbose_name=u"파일갯수")
	reasonlength = models.IntegerField(help_text='전송사유 최대길이 입니다.', default=0, null=True, verbose_name=u"전송사유 길이", choices=REASON_LENGTH)
	checkcompressfile = models.BooleanField(default=True, help_text='압축파일을 검사합니다.', verbose_name=u"압축파일 검사")
	sendfolder = models.BooleanField(default=True, help_text='폴더를 전송 합니다.', verbose_name=u"폴더전송")
	whiteextension = models.BooleanField(default=True, help_text='전송 가능한 확장자입니다.', verbose_name=u"전송가능 확장자")
	blackextension = models.BooleanField(default=True, help_text='전송 불가능한 확장자입니다.', verbose_name=u"전송불가 확장자")

	def __unicode__(self):
		return u'%s' % (self.reference)

	class Meta:
		app_label="camodels"

# 외부망발신 외부서비스연계정책
class OutExternalServicePolicy(models.Model):
	extsvcid = models.AutoField(primary_key=True)
	enableservice = models.BooleanField(default=True, help_text='외부서비스연계 사용여부입니다.', verbose_name=u"외부서비스 연계")
	services = models.CharField(max_length=20, help_text='외부서비스연계 내역입니다.', default='WebProxy 서버주소없음', null=True, verbose_name=u"외부서비스 연계내역")
	clientvaccine = models.BooleanField(default=True, help_text='PC백신 사용여부입니다.', verbose_name=u"PC백신")
	servervaccine = models.BooleanField(default=True, help_text='서버백신 사용여부입니다.', verbose_name=u"서버백신")
	forgerydetection = models.BooleanField(default=True, help_text='위변조검사 사용여부입니다.', verbose_name=u"위변조 검사")

	def __unicode__(self):
		return u'%s %s' % (self.services, self.reference)

	class Meta:
		app_label="camodels"

# 외부망발신 승인정책
class OutApprovePolicy(models.Model):
	ZERO = 0
	ONE = 1
	TWO = 2
	THREE = 3
	APPROVE_LEVEL = (
		(ZERO, '사용안함'),
		(ONE, '1단계'),
		(TWO, '2단계'),
	)

	POST_FACTO = (
		(ZERO, '사용안함'),
		(ONE, '승인후사용'),
		(TWO, '시간외사용'),
		(THREE, '항상사용'),
	)

	approveid = models.AutoField(primary_key=True)
	step = models.IntegerField(help_text='승인단계 입니다.', default=0, null=True, choices=APPROVE_LEVEL, verbose_name=u"승인단계")
	oneselfallowed = models.BooleanField(default=True, help_text='승인자 본인승인가능 여부입니다.', verbose_name=u"본인승인 가능")
	samepositionallowed = models.BooleanField(default=True, help_text='동일망에서만 승인가능 여부입니다.', verbose_name=u"동일망에서만 승인")
	checkpassword = models.BooleanField(default=True, help_text='승인시 패스워드 사용여부입니다.', verbose_name=u"승인시 암호확인")
	postfacto = models.IntegerField(help_text='사후승인사용 여부입니다.', default=0, null=True, choices=POST_FACTO, verbose_name=u"사후승인")
	mandate = models.BooleanField(default=True, help_text='승인위임기능 사용여부입니다.', verbose_name=u"승인위임")
	exceptextension = models.CharField(max_length=255, help_text='승인예외 확장자입니다.', null=True, verbose_name=u"승인예외 확장자")
	externalapprover = models.CharField(max_length=255, help_text='해당정책 사용 부서의 외부 대표승인자입니다.', null=True, verbose_name=u"외부승인자")
	secuapprover = models.CharField(max_length=255, help_text='해당정책 사용 부서의 개인정보 검출파일  승인자입니다.', null=True, verbose_name=u"개인정보검출 승인자")

	def __unicode__(self):
		return u'%s %s %s %s' % (self.exceptextension, self.externalapprover, self.secuapprover, self.reference)

	class Meta:
		app_label="camodels"

# 외부망발신 클립보드정책
class OutClipboardPolicy(models.Model):
	ZERO = 0
	ONE = 1
	TWO = 2
	THREE = 3
	FOUR = 4
	MAX_TEXT_SIZE = (
		(ZERO, '제한없음'),
		(ONE, '1000'),
		(TWO, '10000'),
	)
	MAX_IMAGE_SIZE = (
		(ZERO, '제한없음'),
		(ONE, '10 M'),
		(TWO, '100 M'),
		(THREE, '500 M'),
		(FOUR, '1 G'),
	)

	clipboardid = models.AutoField(primary_key=True)
	maximumtextsize = models.IntegerField(help_text='문서 클립보드전송 최대크기입니다.', default=0, null=True, choices=MAX_TEXT_SIZE, verbose_name=u"문자길이")
	maximumimagesize = models.IntegerField(help_text='이미지 클립보드전송 최대크기입니다.', default=0, null=True, choices=MAX_IMAGE_SIZE, verbose_name=u"이미지크기")

	def __unicode__(self):
		return u'%s' % (self.reference)

	class Meta:
		app_label="camodels"

# 외부망발신 메일정책
class OutSendMailPolicy(models.Model):
	ZERO = 0
	ONE = 1
	TWO = 2
	THREE = 3
	SYNC_INTERVAL = (
		(ZERO, '0'),
		(ONE, '1'),
		(TWO, '10'),
	)

	sendmailid = models.AutoField(primary_key=True)
	domain = models.CharField(max_length=20, help_text='외부망 발신메일서버 주소입니다.', default='WebProxy 서버주소없음', null=True, verbose_name=u"내부망 메일서버 주소")
	port = models.IntegerField(help_text='외부망 발신메일서버 포트입니다.', default=0, null=True, verbose_name=u"내부망 메일서버 포트")
	syncinterval = models.IntegerField(help_text='외부망 발신메일서버 동기화 간격입니다.', default=0, null=True, choices=SYNC_INTERVAL, verbose_name=u"동기화 간격")
	usessl = models.BooleanField(default=True, verbose_name=u"SSL 사용")

	def __unicode__(self):
		return u'%s %s' % (self.domain, self.reference)

	class Meta:
		app_label="camodels"

# 외부망수신 메일정책
class OutReceivedMailPolicy(models.Model):
	ZERO = 0
	ONE = 1
	TWO = 2
	THREE = 3
	SYNC_INTERVAL = (
		(ZERO, '0'),
		(ONE, '1'),
		(TWO, '10'),
	)

	receivedmailid = models.AutoField(primary_key=True)
	domain = models.CharField(max_length=20, help_text='외부망 발신메일서버 주소입니다.', default='WebProxy 서버주소없음', null=True, verbose_name=u"내부망 메일서버 주소")
	port = models.IntegerField(help_text='외부망 발신메일서버 포트입니다.', default=0, null=True, verbose_name=u"내부망 메일서버 포트")
	syncinterval = models.IntegerField(help_text='외부망 발신메일서버 동기화 간격입니다.', default=0, null=True, choices=SYNC_INTERVAL, verbose_name=u"동기화 간격")
	usessl = models.BooleanField(default=True, verbose_name=u"SSL 사용")

	def __unicode__(self):
		return u'%s %s' % (self.domain, self.reference)

	class Meta:
		app_label="camodels"

# 외부망수신 정책
class OutReceptionPolicy(models.Model):
	outreceptid = models.AutoField(primary_key=True)
	outrcvmailid = models.ForeignKey(OutReceivedMailPolicy, on_delete=models.CASCADE, verbose_name=u"내부망수신 메일정책")

	class Meta:
		app_label="camodels"

# 외부망 전송정책
class OutTransmissionPolicy(models.Model):
	ZERO = 0
	ONE = 1
	TWO = 2
	APPROVE_LEVEL = (
		(ZERO, '사용안함'),
		(ONE, '1단계'),
		(TWO, '2단계'),
	)

	outtransid = models.AutoField(primary_key=True)
	usetransmission = models.BooleanField(default=False, help_text='파일반입기능 사용여부입니다.', verbose_name=u"파일반입")
	outfilespolicy = models.OneToOneField(OutFilesPolicy, on_delete=models.CASCADE, verbose_name=u"파일반입 세부정책")

	useexternalservice = models.BooleanField(default=False, help_text='외부서비스연계 사용여부입니다.', verbose_name=u"외부서비스연계")
	outexternalservicepolicy = models.OneToOneField(OutExternalServicePolicy, on_delete=models.CASCADE, verbose_name=u"외부서비스연계 세부정책")

	useapprove = models.IntegerField(default=False, help_text='승인기능 사용여부입니다.', choices=APPROVE_LEVEL, verbose_name=u"승인단계")
	outapprovepolicy = models.OneToOneField(OutApprovePolicy, on_delete=models.CASCADE, verbose_name=u"승인단계 세부정책")

	useclipboard = models.BooleanField(default=False, help_text='클립보드반입기능 사용여부입니다.', verbose_name=u"클립보드반입")
	outclipboardpolicy = models.OneToOneField(OutClipboardPolicy, on_delete=models.CASCADE, verbose_name=u"클립보드반입 세부정책")

	usecertifiate = models.BooleanField(default=False, help_text='공인인증서반입기능 사용여부입니다.', verbose_name=u"공인인증서반입")

	usemail = models.BooleanField(default=False, help_text='메일반입기능 사용여부입니다.', verbose_name=u"메일반입")
	outsendmailpolicy = models.OneToOneField(OutSendMailPolicy, on_delete=models.CASCADE, verbose_name=u"메일반입 세부정책")

	def __unicode__(self):
		return u'%s' % (self.reference)

	class Meta:
		app_label="camodels"

# 내부망 정책
class OutPolicy(models.Model):
	outerpolicyid = models.AutoField(primary_key=True)
	outtransmissionpolicy = models.OneToOneField(InTransmissionPolicy, on_delete=models.CASCADE, verbose_name=u"외부망 반출정책")
	outreceptionpolicy = models.OneToOneField(InReceptionPolicy, on_delete=models.CASCADE, verbose_name=u"외부망 반입정책")
	#inreceivemailpolicy = models.OneToOneField(InReceivedMailPolicy, on_delete=models.CASCADE)
	policyname = models.CharField(max_length=20, help_text='정책명 입니다.', null=True, verbose_name=u"정책명")

	def __unicode__(self):
		return u'%s %s' % (self.policyname, self.reference)

	class Meta:
		app_label="camodels"

# 자료전송정책
class DataPolicy(models.Model):
	ZERO = 0
	ONE = 1
	TWO = 2
	THREE = 3
	FOUR = 4
	FIVE = 5
	UPDATE_LIST_PERIOD = (
		(ZERO, '사용안함'),
		(ONE, '5 초'),
		(TWO, '10 초'),
		(TWO, '30 초'),
		(TWO, '60 초'),
	)
	SECURITY_LEVEL = (
		(ZERO, '사용안함'),
		(ONE, '무결성'),
		(TWO, '무결성+암호화'),
	)
	SYSTEM_UPDATE = (
		(ZERO, '사용안함'),
		(ONE, 'DRM 클라이어트'),
		(TWO, 'DLP 클라이언트'),
		(THREE, 'PMS 클라이언트'),
		(FOUR, '매체제어 클라이언트'),
		(FIVE, 'PC보안 클라이언트'),
	)
	USER_PASSWORD_UPDATE = (
		(ZERO, '사용안함'),
		(ONE, '1주'),
		(TWO, '4주'),
		(THREE, '8주'),
		(FOUR, '16주'),
		(FIVE, '사용자정의'),
	)
	VACCINE = (
		(ZERO, '사용안함'),
		(ONE, '안랩 V3'),
		(TWO, 'sofos'),
		(THREE, '알약'),
	)

	datapolicyid = models.AutoField(primary_key=True)
	#company = models.ManyToManyField(Company, through='DataPolicyforEmployee', through_fields=('datapolicy', 'company'), verbose_name=u"회사명")
	company = models.ManyToManyField(Company, verbose_name=u"회사명")

	#intransmissionpolicy = models.OneToOneField(InTransmissionPolicy, on_delete=models.CASCADE, verbose_name=u"내부망 반출정책")
	#inreceptionpolicy = models.OneToOneField(InReceptionPolicy, on_delete=models.CASCADE, verbose_name=u"내부망 반입정책")

	#outtransmissionpolicy = models.OneToOneField(OutTransmissionPolicy, on_delete=models.CASCADE, verbose_name=u"외부망 반출정책")
	#outreceptionpolicy = models.OneToOneField(OutReceptionPolicy, on_delete=models.CASCADE, verbose_name=u"외부망 반입정책")

	policyname = models.CharField(max_length=255, help_text='정책명입니다.', null=True, verbose_name=u"정책명")
	pollingtime = models.IntegerField(help_text='목록갱신 주기입니다.', default=0, null=True, choices=UPDATE_LIST_PERIOD, verbose_name=u"목록갱신주기")
	securitylevel = models.IntegerField(help_text='보안등급입니다.', default=0, null=True, choices=SECURITY_LEVEL, verbose_name=u"보안등급")
	jionupdate = models.BooleanField(help_text='자료반출입에이전트 업데이트배포 활성화 여부입니다.', null=False, default=False, verbose_name=u"자료반출입")
	systemupdate = models.IntegerField(help_text='외부프로그램 업데이트배포 활성화 여부 입니다.', default=0, null=True, choices=SYSTEM_UPDATE, verbose_name=u"외부프로그램")
	userpasswordupdate = models.IntegerField(help_text='사용자패스워드 갱신주기입니다.', default=0, null=True, choices=USER_PASSWORD_UPDATE, verbose_name=u"사용자암호")
	pcvaccine = models.IntegerField( help_text='PC백신을 선택입니다.', default=0, null=True, choices=VACCINE, verbose_name=u"PC 백신")

	def __unicode__(self):
		return u'%s %s' % (self.policyname, self.reference)
	
	class Meta:
		app_label="camodels"

################
## URL Policy ##
################
# URL 정책할당
class URLPolicy(models.Model):
	assignurlpolicyid = models.AutoField(primary_key=True)
	company = models.ManyToManyField(Company)
	name = models.CharField(max_length=255, help_text='URL연계 사이트 이름입니다.', default='WebProxy 서버주소없음', null=True)
	starttime = models.TimeField(default=0, help_text='입사일을  입력하십시오.')
	endtime = models.TimeField(default=24, help_text='입사일을  입력하십시오.')

	def __unicode__(self):
		return u'%s %s' % (self.name, self.reference)

	class Meta:
		app_label="camodels"

# URL연계 정책
class URLWhitePolicy(models.Model):
	whitepolicyid = models.AutoField(primary_key=True)
	assignurlpolicy = models.ManyToManyField(URLPolicy)
	name = models.CharField(max_length=255, help_text='URL연계 사이트 이름입니다.', default='WebProxy 서버주소없음', null=True)
	domain = models.CharField(max_length=20, help_text='WebProxy서버 주소 입니다.', default='WebProxy 서버주소없음', null=True)
	port = models.IntegerField(help_text='WebProxy 서버포트 입니다.', default=0, null=True)

	def __unicode__(self):
		return u'%s %s %s' % (self.name, self.domain, self.reference)

	class Meta:
		app_label="camodels"

# URL제한 정책
class URLBlackPolicy(models.Model):
	blackpolicyid = models.AutoField(primary_key=True)
	assignurlpolicy = models.ManyToManyField(URLPolicy)
	name = models.CharField(max_length=255, help_text='URL제한 사이트 이름입니다.', default='WebProxy 서버주소없음', null=True)
	domain = models.CharField(max_length=20, help_text='WebProxy서버 주소 입니다.', default='WebProxy 서버주소없음', null=True)
	port = models.IntegerField(help_text='WebProxy 서버포트 입니다.', default=0, null=True)

	def __unicode__(self):
		return u'%s %s %s' % (self.name, self.domain, self.reference)

	class Meta:
		app_label="camodels"

# URL연계예외 정책
class URLExceptionPolicy(models.Model):
	exceptionpolicyid = models.AutoField(primary_key=True)
	assignurlpolicy = models.ManyToManyField(URLPolicy)
	name = models.CharField(max_length=255, help_text='망연계 접속하면 안되는 예외사이트 이름입니다.', default='WebProxy 서버주소없음', null=True)
	domain = models.CharField(max_length=255, help_text='망연계 접속하면 안되는 예외사이트 도메인입니다.', default='WebProxy 서버주소없음', null=True)

	def __unicode__(self):
		return u'%s %s %s' % (self.name, self.domain, self.reference)

	class Meta:
		app_label="camodels"

##########################
## Policy to Employee Information ##
##########################
# 부서원 입사정보
class DataPolicyforEmployee(models.Model):
        dplcyforempid = models.CharField(max_length=255, primary_key=True, default='1357', unique=True)
        datapolicy = models.ForeignKey(DataPolicy, on_delete=models.CASCADE, default='1357')
        company = models.ForeignKey(Company, on_delete=models.CASCADE, default='1357')

        class Meta:
                app_label="camodels"

class URLPolicyforEmployee(models.Model):
        uplcyforempid = models.CharField(max_length=255, primary_key=True, default='1357', unique=True)
        urlpolicy = models.ForeignKey(URLPolicy, on_delete=models.CASCADE, default='1357')
        company = models.ForeignKey(Company, on_delete=models.CASCADE, default='1357')

        class Meta:
                app_label="camodels"