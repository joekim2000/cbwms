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
import time
import json
import sqlite3

import smtplib
from smtplib import SMTPException, SMTPAuthenticationError
import string
import base64

import email
from email.header import decode_header
from email.parser import Parser
import logging
import logging.handlers
import base64
import hashlib
from os import sys, path
import caengineconfig
import random
import glob
import ntpath
import md5
from pyDes import *

import sys
reload(sys)  # Reload does the trick!
sys.setdefaultencoding('UTF8')
from subprocess import Popen

import gevent
from gevent.queue import Queue

SMTP_EHLO_OKAY = 250
SMTP_AUTH_CHALLENGE = 334
SMTP_AUTH_OKAY = 235

outPath = '/home/DATA/MAIL/OutMail'

class ExtractEmlFile():
        def GetMailAddress(self, msg, key):
                data = msg.get_all(key)
                if (data == None):
                        return

                cnv = email.utils.getaddresses(data)
                print key,
                result = []
                for tmp in cnv:
                        #print '----------------------', tmp[0]
                        name = ''.join(self.GetDecodeText(tmp[0]))
                        if (name != ''):
                                name = '"' + name + '" '
                        result.append(tmp[1])
                return result

        def GetEncodeName(self, msg, encodeSet):
                if encodeSet == None:
                        result = ''
                        if result == '':
                                result = self.GetEncodeName(msg, 'utf-8')
                        if result == '':
                                result = self.GetEncodeName(msg, 'euc-kr')
                        if result == '':
                                result = self.GetEncodeName(msg, 'gb18030')
                        if result == '':
                                result = self.GetEncodeName(msg, 'gbk')
                        if result == '':
                                result = self.GetEncodeName(msg, 'cp1252')
                        return result
                try:
                        s = msg.decode(encodeSet).encode('utf-8')
                        return encodeSet
                except:
                        return ''
                return result


        def DecodeText(self, text):
                i1 = 0
                i2 = 0
                while True:
                        i1 = text.find('=?', i2)
                        i2 = text.find('?=', i1)

                        if (i2 + 2) >= len(text):
                                break;

                        if (i1 >= 0) and (i2 >= 0) and (i2 > i1):
                                s = self.GetDecodeText(text[i1:i2+2])
                                sx = ''
                                text = text[:i1] + ''.join(s) + text[i2+2:]
                        if (i1 < 0) or (i2 < 0):
                                break;
                return text

        def GetDecodeText(self, text):
                result = []
                if (text != None):
                        text = text.replace('?==?', '?=\n=?')
                tmp = email.Header.decode_header(text)
                #print '-------------------------------------------------------'
                for each in tmp:
                        #print 'Parse Data:>>> ', each[1], each[0]
                        try:
                                if each[1]:
                                        codeset = each[1].lower()
                                        if (codeset == 'ks_c_5601-1987') or (codeset == 'euc-kr') or (codeset == 'ibm-euckr'):
                                                s = each[0].decode('cp949').encode('utf-8')
                                        elif (codeset == 'gb2312'):
                                                s = each[0].decode('gbk').encode('utf-8')
                                        elif (codeset == 'gb18030'):
                                                s = each[0].decode('gb18030').encode('utf-8')
                                        else:
                                                s = each[0].decode(each[1]).encode('utf-8').strip()
                                else:
                                        s = self.DecodeText(each[0]).strip()
                                        enc = self.GetEncodeName(s, None)
                                        if s != '':
                                                s = s.decode(enc).encode('utf-8')
                        except:
                                exc_type, exc_value, exc_traceback = sys.exc_info()
                                lines = traceback.format_exception(exc_type, exc_value, exc_traceback)
                                msg = ','.join(lines)
                                s = self.DecodeText(each[0]).strip()
                                s = '문자열 변환 불가'
                                print 'error', msg
                        #print 'Cnv:', s
                        result.append(s)
                return result

	def read_MSG(self, text):
                msg = email.message_from_string(text)
                result = {}
                result["From"] = self.GetMailAddress(msg, 'From')
                result["Date"] = self.GetMailAddress(msg, 'Date')
                result["Subject"] = self.GetMailAddress(msg, 'Subject')
                result["To"] = self.GetMailAddress(msg, 'To')
                result["Cc"] = self.GetMailAddress(msg, 'Cc')
                result["Bcc"] = self.GetMailAddress(msg, 'Bcc')

                if result["From"] == None:
                        result["From"] = []
                if result["Date"] == None:
                        result["Date"] = []
                if result["Subject"] == None:
                        result["Subject"] = []
                if result["To"] == None:
                        result["To"] = []
                if result["Cc"] == None:
                        result["Cc"] = []
                if result["Bcc"] == None:
                        result["Bcc"] = []

		return result

class SendEmltoCustomer():
	def __init__(self, cfg, logger, server, port):
		self.cfg = cfg
		self.logger = logger
		
		try:
			# hjkim 20170326 메일 첨부파일 수신 호출
			sendeml = ExtractEmlFile()
			emlFiles = []
			splitFrom = []
			splitTo = []
			rcvEmlFile = None
			emlFiles = glob.glob(outPath + "/*.outmail")
			if len(emlFiles) <= 0:
				return

			smtp = None
			smtp = smtplib.SMTP('127.0.0.1, '25')
			# smtp = smtplib.SMTP(server, port) # 외부망 메일서버 경유 버전의 경우 적용
			for emlfile in emlFiles:
				rcvEmlFile = emlfile
				head, tail = ntpath.split(emlfile)
				justName = os.path.splitext(tail)[0]
				splitName = justName.split('_')
				self.logger.info('파일 이름: ' + justName)
				if(len(splitName) >= 3):
					if(splitName[2] == 'NONE'):
						checkID = splitName[1] + '@internal_domain.co.kr'
					else:
						justID = splitName[2].split('@')
						checkID = justID[0] +  + '@external_domain.com'  
					# loginPW = self.decrypt(splitName[2], checkID) # 외부망 메일서버 경유 버전의 경우 적용
				else:
					if os.path.exists(emlfile):
						os.remove(emlfile)
					return

				f = open(emlfile, "r+")
				headers = Parser().parse(f)
				headers.replace_header('From', checkID)
				with open(emlfile, 'w') as outfile:
					outfile.write(headers.as_string())
				f.close()
				f = open(emlfile, "rb")
				message = f.read()
				mailer= sendeml.read_MSG(message)		
				f.close()

				hasBcc = False
				if (mailer["Bcc"] != None) and (len(mailer["Bcc"]) > 0):
					hasBcc = True

				fromEml = ''.join(mailer["From"])
				dateEml = ''.join(mailer["Date"])
				subjectEml = ''.join(mailer["Subject"])
				toEml = ','.join(mailer["To"])
				ccEml = ','.join(mailer["Cc"])
				bccEml = ','.join(mailer["Bcc"])
				
				toEmls = toEml.split(',')
				if len(ccEml) > 0:
					toEmls = toEmls + ccEml.split(',')
				if len(bccEml) > 0:
					toEmls = toEmls + bccEml.split(',')

				# smtp.starttls()  # 외부망 메일서버 경유 버전의 경우 적용
				# smtp.login(loginID, loginPW)   # 외부망 메일서버 경유 버전의 경우 적용

				if len(toEmls) > 0:
					for eachEml in toEmls:
						self.logger.info('발신: ' + fromEml + ', 날짜: ' + dateEml + ', 제목: ' + subjectEml + ', 수신: ' + eachEml)
						smtp.sendmail(fromEml, eachEml, message)
				if os.path.exists(emlfile):
					os.remove(emlfile)
			smtp.quit()

		except:
			exc_type, exc_value, exc_traceback = sys.exc_info()
			lines = traceback.format_exception(exc_type, exc_value, exc_traceback)
			msg = ','.join(lines)
			self.error(msg)
			self.logger.debug('Error Appear: ' + msg)
			print "error :" + msg
			if os.path.exists(rcvEmlFile):
				os.remove(rcvEmlFile)

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

	def decrypt(self, passphrase, key):	
		m=md5.new()
		m.update(key)
		k = triple_des(m.digest(), ECB, padmode=PAD_PKCS5)
		result = k.decrypt(passphrase.decode('base64'))
		return result

	def asbase64(self, msg):
		return string.replace(base64.encodering(msg), '\n', '')

	def error(self, msg):
		if (self.logger == None):
			print datetime.datetime.now().strftime('%m/%d/%y %H:%M:%S.%f'), 'error', msg
		else:
			self.logger.error(msg)

	def debug(self, msg):
		if (self.logger == None):
			print datetime.datetime.now().strftime('%m/%d/%y %H:%M:%S.%f'), 'debug', msg
		else:
			self.logger.debug(msg)

class Log():
	def __init__(self, logFile = '', format = '%m/%d/%Y %H:%M:%S.%f', isDebug = True, isConsoleOut = True):
		self.format = format
		self.logFile = logFile
		self.isConsole = isConsoleOut
		self.isDebug = isDebug

        def info(self, msg):
                self.Write('info', msg)

        def debug(self, msg):
		if (self.isDebug):
	                self.Write('debug', msg)

        def error(self, msg):
                self.Write('error', msg)

	def Write(self, mode, msg):
		dt = datetime.datetime.now()
		data= ' '.join( [ dt.strftime(self.format), mode, msg])
		if self.isConsole:
			print data
		if self.logFile == '':
			return
		if (os.path.exists(self.logFile)):
			mtime = datetime.datetime.fromtimestamp(os.path.getmtime(self.logFile))
			nkey = dt.strftime('%Y%m%d')
			mkey = mtime.strftime('%Y%m%d')
			if (nkey != mkey):
				shutil.move(self.logFile, self.logFile + '.' + mkey)
		with open(self.logFile, 'a') as f:
			f.write(data + '\n')


class Mail():
	def __init__(self, daemonName = 'cmail', isTest = False):
		self.LoadConfig(daemonName)

		self.isTest = isTest
		self.logger = Log(self.cfg.Log +'/' + daemonName + '.log', isDebug = True, isConsoleOut = isTest)

	def LoadConfig(self, daemonName):
		etcpath = path.dirname(path.dirname(path.abspath(__file__))) + "/etc/"
		cfgName = etcpath + daemonName + ".conf"
		print cfgName
		cfg = caengineconfig.Info(cfgName)

		self.cfg = cfg.Receive

	def Open(self, server, port, asynctasks):  # id, pw):
		while not asynctasks.empty():
			task = asynctasks.get()
			gevent.sleep(0)
        	        SendEmltoCustomer(self.cfg, self.logger, server, port)

        def Close(self):
		print "stop"

        def Stop(self):
                self.isStop = True

if __name__ == "__main__":
        import sys
        reload(sys)
        sys.setdefaultencoding('utf-8')

	if len(sys.argv) == 2:
		with open(sys.argv[1], 'r') as f:
			eml = f.read(-1)

		etcpath = path.dirname(path.dirname(path.abspath(__file__))) + "/etc/"
                cfgName = etcpath + "cmaild.conf"
                print cfgName
                cfg = caengineconfig.Info(cfgName).Receive

		SendEmltoCustomer(cfg, None, "", "")
