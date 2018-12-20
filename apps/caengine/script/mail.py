#! /usr/bin/python
# coding: utf-8
#================================================================

import logging
import logging.handlers
from maillib import SendMail
import maillib
import sys
import glob
import os
import datetime
import shutil

class Mail():
        def __init__(self, isTest = False):
		'''
                loglevel = logging.DEBUG
                self.logger = logging.getLogger('caengine-mail')
                self.logger.setLevel(loglevel)
                self.isTest = isTest

                formatter = logging.Formatter('%(asctime)s %(message)s')

                if (isTest):
                        ch = logging.StreamHandler()
                        ch.setLevel(loglevel)
                        ch.setFormatter(formatter)
                        self.logger.addHandler(ch)

                hdlr = logging.handlers.TimedRotatingFileHandler('/var/log/JionLab/caengine/mail.log', 'D', 1)
                hdlr.setFormatter(formatter)
                hdlr.setLevel(loglevel)
                self.logger.addHandler(hdlr)
                '''
                self.logger = Log('/var/log/JionLab/caengine/mail.log', '%Y-%m-%d %H:%M:%S,%f')
		print self.logger

        def Put(self, uid):
                maillib.RootPath = '/home/DATA/MAIL'
                mail =  maillib.SendMail('127.0.0.1', '', '')
		mail.SetFilter([], [])
                #mail.SetFilter(['jinwoowa','hckim','sykwon','hsjeon','sjun.kim','gyunam.kim',
                #                'yelii','sjan','jw.kim','jhhan','20200963','korea','skyblue12',
                #                'ymchoi','jyw','hoyoungAn','yujeong','epum','onewant','hansung','pgkim'],
                #                [])

		uidlist = []
		if uid == '':
			files = sorted(glob.glob(maillib.RootPath + '/*.json'))
			for each in files:
				uidlist.append(os.path.basename(each)[:-5])
			# print files
		else:
			uidlist = [uid]
		print uidlist
		for UID in uidlist:
			self.logger.info('Send ' + str(UID) + ' Start')
			result, msg = mail.Run(str(UID), self.logger)
			self.logger.info('Send ' + str(UID) + ' ' + result + ' ' + msg)

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

if __name__ == "__main__":
        if len(sys.argv) == 2:
                uid = sys.argv[1]
        else:
                uid = ''
        mail = Mail()
        #mail.Put(uid)
        mail.Put('')

