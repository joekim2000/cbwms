#! /usr/bin/python
# coding: utf-8
#======================================================================

import sys
import os
import shutil
import datetime
import traceback
import subprocess
import re
import json
import smtplib
import email
from email.MIMEMultipart import MIMEMultipart
from email.MIMEText import MIMEText
from email.MIMEBase import MIMEBase
from email.MIMEImage import MIMEImage
from email import Encoders
from email.header import Header
from PIL import Image

reload(sys)
sys.setdefaultencoding('utf-8')


RootPath = ''

class SendMail():
        def __init__(self, server, id, pw, bodyattach = True):
                # 160527
                # self.DPath = '/home/DATA/BACKUP/.MAIL/'

                self.bodyattach = bodyattach
                self.FilterUser = []
                self.FilterDomain = []
                try:
                        self.mail = smtplib.SMTP(server)
                        #self.mail.ehlo()
                        #self.mail.starttls()
                        #self.mail.ehlo()
			if id != '':
                        	self.mail.login(id, pw)
			#print 'Open Success'
                except:
                        exc_type, exc_value, exc_traceback = sys.exc_info()
                        self.mail = None
			print 'Open Fail'

        def SetFilter(self, userlist = [], domainlist = []):
                self.FilterUser = userlist
                self.FilterDomain = domainlist

        def JsonToInfo(self, jsontext):
                j = json.loads(jsontext)
                return j

        def listToString(self, list, seperator = ',', emptytext = ''):
                result = emptytext
                if (list != None) and (len(list) != 0):
                        tmp = []
                        for each in list:
                                tmp.append(str(Header(each.encode('utf-8'), 'utf-8')))
                        result = seperator.join(tmp)
                return result

	def listJsonToText(self, list):
		result = []
                if (list != None) and (len(list) != 0):
                        for each in list:
				if type(each) == type([]):
					tmp = self.listJsonToText(each)
					for each2 in tmp:
						result.append(each2)
				else:
                                	result.append(each.encode('utf-8'))
		if len(result) == 0:
			result = [u'없음']
                return result

	def filesListToString(self, list, uid):
		result = []
		ahead = '<a href="http://10.211.55.125:8780/'
		atail = '">'
		aend = '</a>'

                if (list != None) and (len(list) != 0):
                        for each in list:
				if type(each) == type([]):
					tmp = self.listToString(each, ',')
					for each2 in tmp:
						each2 = ahead + uid + "-=-" + each2 + atail + each2 + aend
						result.append(each2)
				else:
                                	result.append(each.encode('utf-8'))
		if len(result) == 0:
			result = [u'없음']
                			
                return result

	def filesListJsonToText(self, list, uid):
		result = []
		ahead = '<a href="http://10.211.55.125:8780/'
		atail = '">'
		aend = '</a>'

                if (list != None) and (len(list) != 0):
                        for each in list:
				if type(each) == type([]):
					tmp = self.listJsonToText(each)
					for each2 in tmp:
						# 20170817 첨부파일 다운로드 시 적용
						#each2 = ahead + uid + "-=-" + each2 + atail + each2 + aend
						result.append(each2)
				else:
                                	result.append(each.encode('utf-8'))
		if len(result) == 0:
			result = [u'없음']
                			
                return result

	def CropImage(self, filename):
        	im = Image.open(filename)
	        w, h= im.size

        	#print w, h
	        cnt = 1
        	while True:
                	if (h<(cnt * 1500)):
	                        nh = (h - (cnt - 1)*1500)
        	        else:
                	        nh = 1500
	                if nh <= 0:
        	                break
                	#print 0, (cnt - 1)*1500, w, (cnt-1)*1500 + nh
	                cImg = im.crop((0, (cnt - 1)*1500, w, (cnt-1)*1500 + nh))
        	        cImg.save('/home/DATA/MAIL/CROP/' + str(cnt) + '.png')
                	cnt += 1

	        #print cnt - 1
        	return cnt - 1

	def SetEmlInfoNSendMail(self, eml, uid):
		mail = MIMEMultipart("related")
		mail['Date'] = eml['Date']
			
		# hjkim 20170216 발신자, 수신자 참조자 깨지는 문제로 바꿈
		#mail['From'] = self.listToString(eml['From'], ',')
		#mail['To'] = self.listToString(eml['To'], ',')
		mail['From'] = ','.join(self.listJsonToText(eml['From'])) #self.listToString(eml['From'], ',')
		mail['To'] = ','.join(self.listJsonToText(eml['To']))     #self.listToString(eml['To'], ',')

		#if len(eml['Cc']) > 0:
		#	mail['Cc'] = self.listToString(eml['Cc'], ',')
		if len(eml['Cc']) > 0:
			mail['Cc'] = ','.join(self.listJsonToText(eml['Cc']))     #self.listToString(eml['Cc'], ',')

		# hjkim 20170504 외부에서 온 메일을 알리기위한 심벌 추가
		mail['Subject'] = '✔ ' + eml['Subject']

		mail.preamble = 'Image Mail'
		mailAlternative = MIMEMultipart('alternative')
		mail.attach(mailAlternative)
		mailText = MIMEText('Image Mail', 'plain', 'utf-8')
		mailAlternative.attach(mailText)

		try:
			f = self.listJsonToText(eml['From'])

			To = self.ReceiverFilter(self.listJsonToText(eml["To"]))
			Cc = self.ReceiverFilter(self.listJsonToText(eml["Cc"]))
			hasBcc = False
			if (eml["Bcc"] != None) and (len(eml["Bcc"]) > 0):
				hasBcc = True
			Bcc = self.ReceiverFilter(self.listJsonToText(eml["Bcc"]))

			recv = []
			for each in To:
				s = self.RecvConvert(each.encode('utf-8'))
				recv.append(s)
			for each in Cc:
				s = self.RecvConvert(each.encode('utf-8'))
				recv.append(s)
			if hasBcc:
				recv = []
				print 'BCC User'
				for each in Bcc:
					s = self.RecvConvert(each.encode('utf-8'))
					recv.append(s)

			fx = self.RecvConvert(' '.join(f))

			if len(recv) == 0:
				return 'Etc', '수신자 없음'

			fileData = []
			if(eml['Files'] != None):
				fileData  = eml['Files']
			else:
				fileData[0] = None

			# hjkim 20170217 웰컴저축은행 도메인을 꺾어서 전송해야 하므로
			returnValue = []
			for line in recv:
				#idx = line.find('@')
				#if(idx != -1):
				#	splitData = line.split("@")
				#	username = splitData[0]
				#	if (splitData[1].lower() != 'welcomebank.co.kr'):
				#		continue

				with open('/opt/JionLab/caengine/script/template.html', 'r') as f:
					html = f.read()

				fs = '<tr><td>'
				fe = '</td></tr>'

				# hjkim 20170330 전체승인 추후 변경 하여야함
				#aprvstart = '<a href="http://10.211.55.125:3000/?login=login" type="button" target="_self" onClick="http://10.211.55.125:3000">'
				#aprvend = '</a>'

				#files = self.listJsonToText(eml['Files'])
		
				html = html.replace('{{filekey}}', fs + (fe+fs).join(self.filesListJsonToText(fileData, uid)) + fe)

				## 20170409 전체 승인을 일단 빼고
				#html = html.replace('{{filekey}}', fs + (fe+fs).join(self.filesListJsonToText(eml['Files'], uid)) + fe + aprvstart + '전체승인' + aprvend)

				if os.path.exists(self.ifile):
					nImg = self.CropImage(self.ifile)

					imgkey = ''
					for n in range(0, nImg):
						h = Header('외부메일본문-' + str(n) + '.png', 'utf-8')

						f = open('/home/DATA/MAIL/CROP/' + str(n+1) + '.png', 'rb')
						mailImage = MIMEImage(f.read())
						f.close()

						mailImage.add_header("Content-Disposition", "attachment;filename=" + str(h))
						mailImage.add_header("Content-ID", "<body" + str(n) + ">")
						mail.attach(mailImage)
						imgkey += '<img src="cid:body' + str(n) + '" alt="" title="">\n'
	
					html = html.replace('{{imgkey}}', imgkey)
					with open('/tmp/test.html', 'w') as fhtml:
						fhtml.write(html)

					f = open('/opt/JionLab/caengine/script/outmail_logo.png', 'rb')
					mailImage2 = MIMEImage(f.read())
					f.close()
					mailImage2.add_header("Content-Disposition", "attachment;filename=logo")
					mailImage2.add_header("Content-ID", "<logo>")
					mail.attach(mailImage2)

					#f = open('/opt/JionLab/caengine/script/bul_r.png', 'rb')
					#mailImage3 = MIMEImage(f.read())
					#f.close()
					#mailImage3.add_header("Content-Disposition", "attachment;filename=bul_r")
					#mailImage3.add_header("Content-ID", "<bul_r>")
					#mail.attach(mailImage3)
 
				mailHTML = MIMEText(html, 'html', 'utf-8')
				mailAlternative.attach(mailHTML)
					
				eml = mail.as_string()
				self.mail.sendmail(fx, line, eml)
				
			# 웰컴저축은행 20170217
			#	returnValue.insert(0,splitData[0] + "@gwsb.welcomefg.co.kr,")                        
			#self.mail.sendmail(fx, returnValue, eml)
			#self.mail.sendmail(fx, recv, eml)

			return 'Success', ''
		except:
			exc_type, exc_value, exc_traceback = sys.exc_info()
			lines = traceback.format_exception(exc_type, exc_value, exc_traceback)
			msg = ','.join(lines)
			return 'Error', msg
			
		return 'Success', ''

        def ReceiverFilter(self, list):
                result = []
                for each in list:
			each2 = each.lower()
			if len(self.FilterUser) > 0:
                        	for user in self.FilterUser:
                                	if each2.find(user) >= 0:
                                        	if not (each in result):
                                                	result.append(each)
                                                	break
			if len(self.FilterDomain) > 0:
                        	for domain in self.FilterDomain:
                                	if each2.find(domain) >= 0:
                                        	if not (each in result):
                                                	result.append(each)
                                                	break
			if (len(self.FilterUser) == 0) and (len(self.FilterDomain) == 0):
				result.append(each)
                return result

	def RecvConvert(self, addr):
		# split <>
		p1 = addr.find('<')
		p2 = 0
		if (p1 >= 0):
			p2 = addr.find('>', p1)
		if (p1 >=0) and (p2 > p1):
			return addr[p1+1:p2]
		else:
			return addr

        def Close(self):
                self.mail.quit()

        def Run(self, uid, logger = None):
		self.jfile = RootPath + '/' + uid + '.json'
		self.ifile = RootPath + '/' + uid + '.jpg'
	
		if os.path.exists(self.jfile) and os.path.exists(self.ifile):
			with open(self.jfile, 'r') as f:
                        	s = f.read()
                	eml = self.JsonToInfo(s)

			if logger != None:
                                msg = ' '.join(['Send', str(uid),
                                                'D[' + eml['Date'].encode('utf-8') + ']',
                                                'F[' + ','.join(self.listJsonToText(eml['From'])) + ']',
                                                'T[' + ','.join(self.listJsonToText(eml['To'])) + ']',
                                                'C[' + ','.join(self.listJsonToText(eml['Cc'])) + ']',
                                                'B[' + ','.join(self.listJsonToText(eml['Bcc'])) + ']',
                                                'S[' + eml['Subject'].encode('utf-8') + ']',
                                                'F[' + ','.join(self.listJsonToText(eml['Files'])) + ']'
						])
                                logger.info(msg)
                                msg = ''

			try:
	                	result, msg = self.SetEmlInfoNSendMail(eml, uid)
			except:
	                        exc_type, exc_value, exc_traceback = sys.exc_info()
        	                lines = traceback.format_exception(exc_type, exc_value, exc_traceback)
                	        msg = ','.join(lines)
                        	result = 'Error'
		else:
			result = 'Wait'
			msg = 'json or image file not found'

		if (result != 'Wait'):
			os.remove(self.ifile)
			os.remove(self.jfile)
			#print '#'
		return result, msg
