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
import imaplib
import email
from email.header import decode_header
import logging
import logging.handlers
import base64
import hashlib
from os import sys, path
import config
import random
import glob

import sys
reload(sys)  # Reload does the trick!
sys.setdefaultencoding('UTF8')
from subprocess import Popen

import gevent
from gevent.queue import Queue

putPath = '/home/DATA/MAIL/PUT'
getPath = '/home/DATA/MAIL/GET'

class RecvMailAttachment():
        def __init__(self, cfg, logger, server, id, pw, box = 'inbox'):
                self.cfg = cfg
		self.logger = logger
                try:
			if (self.cfg.UseSSL):
                        	self.mail = imaplib.IMAP4_SSL(server)
			else:
				self.mail = imaplib.IMAP4(server)

                        self.mail.login(id, pw)
                        self.mail.list()
                        self.mail.select(box)
			self.id = id
			print id
			print pw
			# hjkim 20170326 메일 첨부파일 수신 호출
			#p = multiprocessing.Process(target=self.ReceiveAttachment, args=(self.cfg,))
			#p.start()
			#p.join()

			self.ReceiveAttachment(self.cfg)

                except:
			exc_type, exc_value, exc_traceback = sys.exc_info()
                        lines = traceback.format_exception(exc_type, exc_value, exc_traceback)
                        msg = ','.join(lines)
			self.error(msg)
                        self.mail = None
			self.logger.debug('Error Appear: ' + msg)

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

        def Search(self, query):
                if (self.mail == None):
                        return []
                result, data = self.mail.uid('search', None, query)
		if data[0] == None:
			self.debug(result + ', Search Not Found')
			return None
		#self.debug(result + ',' + data[0])
                return data

	# hjkim 20170326 메일 첨부파일 수신 시작
	def CreateDirectory(self, directory):
        	if not os.path.exists(directory):
                	os.makedirs(directory)

	def JsonToInfo(self, jsontext):
        	j = json.loads(jsontext)
        	return j

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

        def ReceiveAttachment(self, cfg):
		jsonFiles = []
		jsonFiles = glob.glob(putPath + "/*.json")
                for jsonfile in jsonFiles:
                        getfname = os.path.basename(jsonfile)
                        splitname = getfname.split('-')
                        outPath = getPath + "/" + splitname[0] + "/"
                        self.CreateDirectory(outPath)
			if not os.path.exists(jsonfile):
				return
                        with open(jsonfile, 'r') as f:
                                getdata = f.read()
                                f.close()
                        os.remove(jsonfile)
                        attachinfo = self.JsonToInfo(getdata)

                        userip = ''.join(self.listJsonToText(attachinfo['userip']))
                        filename = ''.join(self.listJsonToText(attachinfo['filename']))
                        fcp2filename = ''.join(self.listJsonToText(attachinfo['fcp2filename']))
                        uidstr = ''.join(self.listJsonToText(attachinfo['uid']))
                        user = ''.join(self.listJsonToText(attachinfo['user']))
			uid = int(uidstr)
                        #eml_body = self.Fetch(int(uidstr))
                        resp, data = self.mail.uid('fetch', uid, '(BODY[])')
                        try:
                                email_body = data[0][1]
                                mail = email.message_from_string(email_body)
                                temp = self.mail.store(uid,'+FLAGS', '\\Seen')
                                self.mail.expunge()

                                cids = {}
                                for part in mail.walk():
                                        ctype = str(part.get_content_type())
                                        d = part.get("Content-Type", None)
                                        cid = part.get("Content-Id", None)
                                        attachment = part.get("Content-Disposition", None)
                                        if attachment:
                                                if (attachment.find('attachment') >= 0):
                                                        tmp = attachment.split(';')
                                                        for each in tmp:
                                                                each = each.strip()
                                                                if each.find('filename') == 0:
                                                                        sp = each.find('"')
                                                                        if sp < 0:
                                                                                sp = each.find('=') + 1
                                                                        fname = each[sp:]
                                                                        if (fname[0] == '"'):
                                                                                fname = fname[1:]
                                                                        if (fname[-1] == '"'):
                                                                                fname = fname[:-1]
										fname, encoding = email.Header.decode_header(fname)[0]
                                                                        if(filename == fname):
                                                                        	jsondata = json.dumps({ 'user': user, 'userip': userip, 'uid': uidstr, 'filename': fname, 'fcp2filename': fcp2filename},sort_keys = False, indent=4, separators=(',',': '))

                                                                                attach_path = os.path.join(outPath, fcp2filename)

                                                                                if not os.path.isfile(attach_path) :
                                                                                        with open(attach_path, 'wb') as fp:
                                                                                                fp.write(part.get_payload(decode=True))
                                                                                                fp.close()
                                                                                        dstfile = cfg.Desthost + ":" + attach_path
                                                                                        arg = """ """.join(["/opt/JionLab/fcp2/bin/fcp2 -f", attach_path, "-p", cfg.LocalIPPort, dstfile, "-P", "/opt/JionLab/caengine/script/relay"])

                                                                                        obj = Popen(arg, shell=True, stdin=None, stdout=None, stderr=None, close_fds=True)
                                                                                        obj.wait()
                                                                                        os.remove(attach_path)

                                                                                        jasoninname = outPath + user + "-" + uidstr + "-" + fcp2filename + "-in" + ".json"
                                                                                        with open(jasoninname, 'w') as open_file:
                                                                                                open_file.write(jsondata)
                                                                                                open_file.close()

                                                                                        dstjson = cfg.Desthost + ":" + jasoninname
                                                                                        arg = """ """.join(["/opt/JionLab/fcp2/bin/fcp2 -f", jasoninname, "-p", cfg.LocalIPPort, dstjson, "-P", "/opt/JionLab/caengine/script/relay"])

                                                                                        obj = Popen(arg, shell=True, stdin=None, stdout=None, stderr=None, close_fds=True)
                                                                                        obj.wait()
                                                                                        os.remove(jasoninname)
											self.logger.info('첨부파일 전송 완료: ' + fname)
			except:
				self.logger.info("삭제된 메일")
                                jsondata = json.dumps({ 'user': user, 'userip': userip, 'uid': uidstr, 'filename': "mailnotfound", 'fcp2filename': "mailnotfound"},sort_keys = False, indent=4, separators=(',',': '))

				jasoninname = outPath + user + "-" + uidstr + "-" + fcp2filename + "-in" + ".json"
                                #jasoninname = outPath + user + "-" + uidstr + "-in" + ".json"
                                with open(jasoninname, 'w') as open_file:
                                        open_file.write(jsondata)
                                        open_file.close()

                                dstjson = cfg.Desthost + ":" + jasoninname
                                arg = """ """.join(["/opt/JionLab/fcp2/bin/fcp2 -f", jasoninname, "-p", cfg.LocalIPPort, dstjson, "-P", "/opt/JionLab/caengine/script/relay"])
                                #dstjson = "CBIN2:" + jasoninname
                                #arg = """ """.join(["/opt/JionLab/fcp2/bin/fcp2 -f", jasoninname, "-p 10.0.0.124:7776", dstjson, "-P", "/opt/JionLab/caengine/script/relay"])
                                obj = Popen(arg, shell=True, stdin=None, stdout=None, stderr=None, close_fds=True)
                                obj.wait()
                                os.remove(jasoninname)
	# hjkim 20170326 메일 첨부파일 수신 끝

def decrypt(passphrase):
        tmp = passphrase.decode('base64').split('\t')
        print tmp[0]
        return tmp[0], tmp[1]

        m=md5.new()
        m.update(key)
        k = triple_des(m.digest(), ECB, padmode=PAD_PKCS5)
        result = k.decrypt(passphrase.decode('base64'))
        return result

def encrypt(id, pw):
        return (id + '\t' + pw).encode('base64')

        m=md5.new()
        m.update(key)
        k = triple_des(m.digest(), ECB, padmode=PAD_PKCS5)
        d = k.encrypt(data)
        d = d.encode('base64')
        print d

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
        def __init__(self, daemonName = 'amail', isTest = False):
                self.LoadConfig(daemonName)

		self.isTest = isTest
		self.logger = Log(self.cfg.Log +'/' + daemonName + '.log', isDebug = True, isConsoleOut = isTest)

		#self.logger.info("Start Receive")
		#self.ReceiveAttachment()
		#self.logger.info('End Receive')

        def LoadConfig(self, daemonName):
                etcpath = path.dirname(path.dirname(path.abspath(__file__))) + "/etc/"
                cfgName = etcpath + daemonName + ".conf"
		print cfgName
                cfg = caengineconfig.Info(cfgName)

                self.cfg = cfg.Receive

	def Open(self, server, user, asynctasks):  # id, pw):
		while not asynctasks.empty():
			task = asynctasks.get()
			self.logger.info('Worker got task')
			gevent.sleep(0)
	                id, pw = decrypt(user)
        	        self.mail = RecvMailAttachment(self.cfg, self.logger, server, id, pw)
                	self.id = id
		self.logger.info('Quitting time!')
                return self.mail.mail != None

        def Close(self):
                self.mail = None
                self.logger.info('Recv Stop')

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
                cfgName = etcpath + "amaild.conf"
                print cfgName
                cfg = caengineconfig.Info(cfgName).Receive

		mail = RecvMailAttachment(cfg, None, "", "", "")
		mail.id = 'test'

		sys.exit(0)

        pw = encrypt(sys.argv[1], sys.argv[2])
        id, pw2 = decrypt(pw)
        print pw, id, pw2

