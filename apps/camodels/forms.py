from django import forms
import sys

from django.db import models
from django.forms import ModelForm
from datetime import date, datetime
from django.conf import settings

import sys
import os
import pwd
import grp

PROJECT_ROOT = getattr(settings, "PROJECT_ROOT", None)
import subprocess
sys.path.append(PROJECT_ROOT)
from apps.camodels.modelsframe.policy import InFilesPolicy, InExternalServicePolicy, InApprovePolicy, InClipboardPolicy, InWebProxyPolicy, InSendMailPolicy, InReceivedMailPolicy, InReceptionPolicy, InTransmissionPolicy, InPolicy, OutFilesPolicy, OutExternalServicePolicy, OutApprovePolicy, OutClipboardPolicy, OutSendMailPolicy, OutReceivedMailPolicy, OutReceptionPolicy, OutTransmissionPolicy, OutPolicy, DataPolicy, URLPolicy, URLWhitePolicy, URLBlackPolicy, URLExceptionPolicy, DataPolicyforEmployee, URLPolicyforEmployee
from apps.camodels.modelsframe.personnel import Employee

class PolicyForm(ModelForm):
	filesid = forms.IntegerField(required=True)

	def save(self):
		test = se
		#test.filesid

class InFilesPolicyForm(ModelForm):
	class Meta:
		model = InFilesPolicy
		fields = '__all__'
		#fields = ['filesid','maximumfilesize','onetimefilesize','maximumfiles','reasonlength','checkcompressfile','sendfolder','whiteextension','blackextension']

	def clean(self):
		cleaned_data = super(InFilesPolicyForm, self).clean()
		maximumfilesize = cleaned_data.get('maximumfilesize')
		onetimefilesize = cleaned_data.get('onetimefilesize')
		maximumfiles = cleaned_data.get('maximumfiles')
		reasonlength = cleaned_data.get('reasonlength')
		checkcompressfile = cleaned_data.get('checkcompressfile')
		sendfolder = cleaned_data.get('sendfolder')
		whiteextension = cleaned_data.get('whiteextension')
		blackextension = cleaned_data.get('blackextension')
		#if not name and not email and not message:
		#	raise forms.ValidationError('You have to write something!')

class InExternalServicePolicyForm(ModelForm):
	class Meta:
		model = InExternalServicePolicy
		fields = '__all__'
		#fields = ['extsvcid','enableservice','services','clientvaccine','servervaccine','forgerydetection']

class InApprovePolicyForm(ModelForm):
	class Meta:
		model = InApprovePolicy
		fields = '__all__'
		#fields = ['approveid','step','oneselfallowed','samepositionallowed','checkpassword','postfacto','mandate','exceptextension','externalapprover','secuapprover']

class InClipboardPolicyForm(ModelForm):
	class Meta:
		model = InClipboardPolicy
		fields = '__all__'
		#fields = ['clipboardid','maximumtextsize','maximumimagesize']

class InWebProxyPolicyForm(ModelForm):
	class Meta:
		model = InWebProxyPolicy
		fields = '__all__'
		#fields = ['webproxyid','innerdomain','outerdomain','port']

class InSendMailPolicyForm(ModelForm):
	class Meta:
		model = InSendMailPolicy
		fields = '__all__'
		#fields = ['sendmailid','domain','port','syncinterval','usessl']

class InReceivedMailPolicyForm(ModelForm):
	class Meta:
		model = InReceivedMailPolicy
		fields = '__all__'
		#fields = ['receivedmailid','domain','port','syncinterval','usessl']

class InReceptionPolicyForm(ModelForm):
	class Meta:
		model = InReceptionPolicy
		fields = '__all__'
		#fields = ['receptionid','rcvmailid']

class InTransmissionPolicyForm(ModelForm):
	class Meta:
		model = InTransmissionPolicy
		fields = '__all__'
		#fields = ['intransid','infilespolicy','inexternalservicepolicy','inapprovepolicy','inclipboardpolicy','inwebproxypolicy','insendmailpolicy','usetransmission','useexternalservice','useapprove','useclipboard','usecertifiate','usewebproxy','usemail']
 
class InPolicyForm(ModelForm):
	class Meta:
		model = InPolicy
		fields = '__all__'
		#fields = ['innerpolicyid','intransmissionpolicy','inreceptionpolicy','policyname']

class OutFilesPolicyForm(ModelForm):
	class Meta:
		model = OutFilesPolicy
		fields = '__all__'
		#fields = ['filesid','maximumfilesize','onetimefilesize','maximumfiles','reasonlength','checkcompressfile','sendfolder','whiteextension','blackextension']

class OutExternalServicePolicyForm(ModelForm):
	class Meta:
		model = OutExternalServicePolicy
		fields = '__all__'
		#fields = ['extsvcid','enableservice','services','clientvaccine','servervaccine','forgerydetection']

class OutApprovePolicyForm(ModelForm):
	class Meta:
		model = OutApprovePolicy
		fields = '__all__'
		#fields = ['approveid','step','oneselfallowed','samepositionallowed','checkpassword','mandate','exceptextension','externalapprover','secuapprover']

class OutClipboardPolicyForm(ModelForm):
	class Meta:
		model = OutClipboardPolicy
		fields = '__all__'
		#fields = ['clipboardid','maximumtextsize','maximumimagesize']

class OutSendMailPolicyForm(ModelForm):
	class Meta:
		model = OutSendMailPolicy
		fields = '__all__'
		#fields = ['sendmailid','domain','port','syncinterval','usessl']

class OutReceivedMailPolicyForm(ModelForm):
	class Meta:
		model = OutReceivedMailPolicy
		fields = '__all__'
		#fields = ['receivedmailid','domain','port','syncinterval','usessl']

class OutReceptionPolicyForm(ModelForm):
	class Meta:
		model = OutReceptionPolicy
		fields = '__all__'
		#fields = ['receptionid','rcvmailid']

class OutTransmissionPolicyForm(ModelForm):
	class Meta:
		model = OutTransmissionPolicy
		fields = '__all__'
		#fields = ['outtransid','outfilespolicy','outexternalservicepolicy','outapprovepolicy','outclipboardpolicy','outsendmailpolicy','usetransmission','useexternalservice','useapprove','useclipboard','usecertifiate','usemail']

class OutPolicyForm(ModelForm):
	class Meta:
		model = OutPolicy
		fields = '__all__'
		#fields = ['outerpolicyid','outtransmissionpolicy','outreceptionpolicy','policyname']

class DataPolicyForm(ModelForm):
	class Meta:
		model = DataPolicy
		#fields = ['datapolicyid','company','intransmissionpolicy','inreceptionpolicy','outtransmissionpolicy','outreceptionpolicy','policyname','pollingtime','securitylevel','jionupdate','systemupdate','userpasswordupdate','pcvaccine']
		fields = '__all__'

class URLPolicyForm(ModelForm):
	class Meta:
		model = URLPolicy
		fields = '__all__'
		#fields = ['assignurlpolicyid','company','name','starttime','endtime']

class URLWhitePolicyForm(ModelForm):
	class Meta:
		model = URLWhitePolicy
		fields = '__all__'
		#fields = ['whitepolicyid','assignurlpolicy','name','domain','port']

class URLBlackPolicyForm(ModelForm):
	class Meta:
		model = URLBlackPolicy
		fields = '__all__'
		#fields = ['blackpolicyid','assignurlpolicy','name','domain','port']

class URLExceptionPolicyForm(ModelForm):
	class Meta:
		model = URLExceptionPolicy
		fields = '__all__'
		#fields = ['exceptionpolicyid','assignurlpolicy','name','domain']

class DataPolicyforEmployeeForm(ModelForm):
	class Meta:
		model = DataPolicyforEmployee
		fields = '__all__'
		#fields = ['dplcyforempid','datapolicy','company']

class URLPolicyforEmployeeForm(ModelForm):
	class Meta:
		model = URLPolicyforEmployee
		fields = '__all__'
		#fields = ['uplcyforempid','urlpolicy','company']

class EmployeeForm(ModelForm):
	class Meta:
		model = Employee
		#fields = ['datapolicyid','company','intransmissionpolicy','inreceptionpolicy','outtransmissionpolicy','outreceptionpolicy','policyname','pollingtime','securitylevel','jionupdate','systemupdate','userpasswordupdate','pcvaccine']
		fields = '__all__'
