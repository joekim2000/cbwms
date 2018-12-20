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
import caengineconfig
import random

import sys
reload(sys)  # Reload does the trick!
sys.setdefaultencoding('UTF8')

class RecvMail():
	def __init__(self, cfg, logger, server, id, pw, box = 'inbox'):
		self.cfg = cfg
		self.logger = logger
		try:
			if (self.cfg.UseSSL):
				self.mail = imaplib.IMAP4_SSL(server)
			else:
				self.mail = imaplib.IMAP4(server)
			self.logger.debug('Try Log In: ' + id)
			self.mail.login(id, pw)
			self.mail.list()
			self.mail.select(box)
			self.id = id
		except:
			exc_type, exc_value, exc_traceback = sys.exc_info()
			lines = traceback.format_exception(exc_type, exc_value, exc_traceback)
			msg = ','.join(lines)
			self.error(msg)
			self.mail = None

	def __del__(self):
		print  'Close Mail'
		if (self.mail == None):
			return []

		self.mail.close()
		self.mail.logout()

	def info(self, msg):
		if (self.logger == None):
			print datetime.datetime.now().strftime('%m/%d/%y %H:%M:%S.%f'), 'info', msg
		else:
			self.logger.info(msg)

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

	def MoveTrash(self, uidlist, trashfolder = 'Trash'):
		cnt = 0
		for uid in uidlist:
			self.mail.uid('COPY', str(uid), trashfolder)
			self.mail.uid('STORE', str(uid), '+FLAGS', '(\\DELETED)')
			cnt = cnt + 1
			if (cnt > 8): # 한번에 8개씩만 삭제
				break
	def Search(self, query):
		if (self.mail == None):
			return []
		esult, data = self.mail.uid('search', None, query)
		if data[0] == None:
			self.debug(result + ', Search Not Found')
			return None
		return data

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
			for each in tmp:
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
						enc = self.getEncodeName(s, None)
						if s != '':
							s = s.decode(enc).encode('utf-8')
				except:
					exc_type, exc_value, exc_traceback = sys.exc_info()
					lines = traceback.format_exception(exc_type, exc_value, exc_traceback)
					msg = ','.join(lines)
					s = self.DecodeText(each[0]).strip()
					s = '문자열 변환 불가'
					print 'error', msg
				result.append(s)
			return result

        def EachMailAddress(self, text):
		print '1', text
                tmp = self.GetDecodeText(text)
                result = (' '.join(tmp)).strip()
		print '2', result

                sp = result.find('"')
                if sp >= 0:
                        ep = result.find('"', sp + 1)
                        if (ep > sp):
                                result = result.replace('"', '')
                                tmp = self.GetDecodeText(result)
                                result = (' '.join(tmp)).strip()
                return result

        def GetMailNameAndAddress(self, text):
                if text == None:
                        return []

                result = []
                eachAddress = text.split(',')
                for each in eachAddress:
                        #tmp = each.replace('\r', '')
                        #addr = tmp.split('\n')
                        #tmp = ''
                        #for each2 in addr:
                        #        tmp = tmp + self.EachMailAddress(addr)
			#tmp = self.EachMailAddress(tmp)
                        #tmp = tmp.replace('\r\n', ' ')
			#tmp = tmp.replace('\r', ' ')
			#tmp = tmp.replace('\n', ' ')
			#tmp = tmp.replace('\t', '')
			#idx = tmp.find('<')
			#if idx > 0:
			#	if tmp[idx-1] != ' ':
			#		tmp = tmp[:idx] + ' ' + tmp[idx:]
                        result.append(self.EachMailAddress(each))
                return result

	def LineParse(self, text):
		tmp = email.Header.decode_header(text)
		codeset = ''
		result = ''
		#print 'Parse Data: ',tmp[0][0], ',', tmp[0][1]
		codeset = tmp[0][1]
		if (codeset == None) or (codeset == 'None'):
			codeset = self.getEncodeName(tmp[0][0], None)
		result = tmp[0][0]
		if (codeset == 'ks_c_5601-1987') or (codeset == 'euc-kr'):
                	codeset = 'cp949'
		#print 'result', codeset, result
		return codeset, result

	def DataToString(self, text):
		if (text == None):
                        return ''
		print '=================================================================='
                print text
                text = text.replace('\r','')
                data = text.split('\n')
                print data
                result = ''
		pCode = ''
		oldData = ''
                for each in data:
 			cset, strdata = self.LineParse(each)
			print cset, ',', strdata
			if (pCode != cset):
				if (oldData != ''):
					result = result + oldData.decode(pCode).encode('utf-8')
					oldData = ''
			pCode = cset
			oldData = oldData + strdata
		if (oldData != ''):
			result = result + oldData.decode(pCode).encode('utf-8')
		return result

        def DataToString_160121(self, text):
                if (text == None):
                        return ''
                print '=================================================================='
                print text
		text = text.replace('\r','')
		data = text.split('\n')
		print data
		result = ''
		result2 = ''
		for each in data:
			result = result + ''.join(self.GetDecodeText(each))
			result2 = result2 + ''.join(self.GetDecodeTextN(each))

		print result2.encode('utf-8')

		return result

        def DataToString_org(self, text):
                if (text == None):
                        return ''
		print '=================================================================='
		print text
		s1 = text.find('=?')
		s2 = text.find('?Q?')
		if (s1 >=0) and (s2 <0):
			s2 = text.find('?q?')
		if (s1 >=0) and (s2 >= s1) and (s2 <= (s1 + 10)):
			print 'Q coding'
			return ''.join(self.GetDecodeText(text))

                data = text.split('?=')
                #print data
                s = ''
                result = ''
                for each in data:
                        if (each == None)  or (each == ''):
                                continue
                        if (each.find('=?') >= 0) and ((each.find('?B?') > 0) or (each.find('?b?') > 0)):   # base64
                                result = result + each + '?='
                        elif (each.find('=?') >= 0) and (each.find('?Q?') > 0): # Q coding
                                print '>> QQQ'
				print each
                                idx = each.find('?Q?')
                                ss = each[idx+3:]
                                idx = 0
                                while True:
                                        idx = ss.find('=', idx)
                                        if (idx < 0):
                                                break
                                        bs = ss[idx+1:idx+3]
                                        hd = bs.decode('hex')
                                        ss = ss[:idx] + hd + ss[idx+3:]
                                        idx = idx + 1
                                        print ss
                                result = ss
                        else:
                                print '--->> add space <<---'
                                result = result + ' ' + each

                result = ''.join(self.GetDecodeText(result))
                result = result.replace('\r\n','')
                return result

	def FindBcc(self, recvs):
		if recvs == None:
			return []
                result = []
                for tmp in recvs:
                        si = tmp.find('for ')
                        if si >= 0:
                                si = tmp.find('<', si)
                                ei = tmp.find('>', si)
                                if (si < 0) or (ei < 0):
                                        continue
                                msg = tmp[si+1:ei]
                                msg = msg.replace('<','')
                                msg = msg.replace('>','')
                                if not (msg in result):
                                        result.append(msg)
                return result

        def IDExist(self, id, idlist):
                result = False
                for each in idlist:
                        tmp = each.lower()
                        if tmp.find(id) >= 0:
                                result = True
                                break
                return result

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
			result.append(name + '<' + tmp[1] + '>')
		print result
		return result

	# 160129. Exxchange Option
        def FindRecipient(self, text):
                data = text.split('\r\n')
                result = ''
                for tmp in data:
                        data2 = tmp.split(' ')
                        if (data2[0] == 'Recipient:'):
                                result = data2[1].strip()
                                break
                return result
		#return ''

        def GetInfo(self, text):
		with open(self.emlfile, 'w') as f:
			f.write(text)

                msg = email.message_from_string(text)
                result = {}
               
                result["Date"] = ''.join(self.GetDecodeText(msg['Date']))
                result["Subject"] = ''.join(self.GetDecodeText(msg['Subject']))
                result["ID"] = ''.join(self.GetDecodeText(msg['message-id']))

		result["From"] = self.GetMailAddress(msg, 'From')
		result["To"] = self.GetMailAddress(msg, 'To')
		result["Cc"] = self.GetMailAddress(msg, 'Cc')

                if result["From"] == None:
                        result["From"] = []
                if result["To"] == None:
                        result["To"] = []
                if result["Cc"] == None:
                        result["Cc"] = []

		
                # BCC Process
		#print '\n\n-----------------------------------------------------------------------------------'	
		#print text
		#print '-----------------------------------------------------------------------------------\n\n'	
                recvx = msg.get_all('Received')
                bcclist = self.FindBcc(recvx)
                # To,CC에 있으면 제외
                result['Bcc'] = []
                for eachbcc in bcclist:
			if eachbcc == None:
				continue
                        isexist = self.IDExist(eachbcc.lower(), result["To"])
                        if isexist:
                                continue
                        isexist = self.IDExist(eachbcc.lower(), result["Cc"])
                        if isexist:
                                continue
                        result['Bcc'].append(eachbcc)

                plain = ''
                html = ''
                plaincharset = ''
                htmlcharset = ''
                files = []
		cids = {}
		self.delfiles = []
                for part in msg.walk():
                        ctype = str(part.get_content_type())
			d = part.get("Content-Type", None)
			cid = part.get("Content-Id", None)
                        attachment = part.get("Content-Disposition", None)
                        if (ctype.find('text/') == 0):
                                data = str(part.get_payload(decode=True))
                                if (ctype.find('/plain') == 4):
                                        plaincharset = part.get("Content-Type", None)
                                        plain = plain + '\n' + data
                                elif (ctype.find('/html') == 4):
                                        htmlcharset  = part.get("Content-Type", None)
                                        html = html + data
			elif (d.find('image/') == 0) and (cid != None):
				cid = cid.replace('<', '')
				cid = cid.replace('>', '')
				fnamex = self.GetFileName(d, 'name')
				cids[cid] = self.id + '-' + self.uid + '-' + fnamex
				print 'Image:', cids[cid]
				self.delfiles.append(self.rpath + cids[cid])
				data = part.get_payload(decode=True)
				with open(self.rpath + cids[cid], 'w') as f:
					f.write(data)
                        elif attachment:
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
                                                        files.append(self.GetDecodeText(fname))
                result['Files'] = files
                result['Plain'] = ''
                result['HTML'] = ''

                if (plain != ''):
                        result['Plain'] = self.ChangeCharSet(plaincharset, plain)

		# 160129, Exchange-Option
		recvm = self.FindRecipient(result['Plain'])
                self.debug('Recipient: ' + recvm)
		rvlist = []
		rvlist.extend(result["To"])
		rvlist.extend(result["Cc"])
		rvlist.extend(result["Bcc"])
                for toMan in rvlist: #result["To"]:
                        if (toMan.find(recvm) <0):
                                result['Bcc'] = [ recvm ]
                                break
		if len(rvlist) == 0:
			result['Bcc'] = [ recvm ]

                self.debug('Bcc: ' + ','.join(result['Bcc']))
                result["ID"] = hashlib.sha224(result["Date"] + '\t'.join(result["From"]) + '\t'.join(result["To"])  + '\t'.join(result["Cc"]) + '\t'.join(result["Bcc"]) + result["Subject"]).hexdigest()
                #self.logger.debug('OrgID = ' + result['ID'])
                if len(result['Bcc']) > 0:
                        result["ID"] = '<BCC>' + result["ID"]
                #print result["ID"]

		#print '------------------------------------------------------------------'
		#print plain
		#print '------------------------------------------------------------------'
		#print html, len(html)
		#print '------------------------------------------------------------------'

                if (html == ''):
			html = self.RemoveJournalInfo(plain)
                        html = html.replace('\r', '')
                        html = html.replace('\n', '<br>')
                        htmlcharset = 'text/html charset=utf-8'
		#print html
                if (html != ''):
			if (htmlcharset == ''):
                        	htmlcharset = 'text/html charset=utf-8'
                        result['HTML'] = self.ChangeCharSetHTML(htmlcharset, html)

                c = re.compile('charset\s?=\s?"*', re.I)
                m = c.search(result['HTML'])
                if (m != None):
                        k = m.span()
                        c = re.compile('[\s;\'"/>]', re.I)
                        m = c.search(result['HTML'], k[1])
                        cs = 'Error'
                        if (m != None):
                                k1 = m.span()
                                cs = result['HTML'][k[1]:k1[0]]
                                result['HTML'] =  result['HTML'][0:k[1]] + 'utf-8' + result['HTML'][k1[0]:]
                #else:
                #        result['HTML'] = '<meta http-equiv="content-type" content="text/html; charset=utf-8"/>\n' + result['HTML']
		# 무조건 추가
		# print result['HTML']
		for cid in cids:
			result['HTML'] = result['HTML'].replace('cid:' + cid, cids[cid])

		result['HTML'] = '<meta http-equiv="content-type" content="text/html; charset=utf-8"/>\n' + result['HTML']
                return result

	def RemoveJournalInfo(self, text):
		data = text.split('\n')
		result = ''
		for each in data:
			if (each.find('Sender:') < 0) and (each.find('Subject:') < 0) and (each.find('Message-Id:') < 0) and (each.find('Recipient:') < 0):
				result = result + each + '\n'
		return result

	def GetFileName(self, text, key):        
		tmp = text.split(';')
		fstr = ''
		for each in tmp:
			each = each.strip()
			if each.find(key) == 0:
				sp = each.find('"')
				if sp < 0:
					sp = each.find('=') + 1
				fname = each[sp:]
				if (fname[0] == '"'):
					fname = fname[1:]
				if (fname[-1] == '"'):
					fname = fname[:-1]
				fstr += fname
		r = self.GetDecodeText(fstr)
		return r[0]

	def ChangeCharSetHTML(self, charTag, text):
		lines = text.split(' ')
		result = ''
		for each in lines:
			ctag = self.getEncodeName(each, None)
			if (ctag == 'utf-8'):
				result += each + ' '
			else:
				result += each.decode(ctag).encode('utf-8') + ' '
		return result

        def ChangeCharSet(self, charTag, text):
		if charTag == None:
			charTag = " "
		codeset = charTag.lower()
		print '>>>>>>>>>>>', codeset
		if (codeset.find('gb2312')>=0):
			return text.decode('gbk').encode('utf-8')

                ctag = self.getEncodeName(text, None)
		print ctag
                if ctag != '':
                        return text.decode(ctag).encode('utf-8')
                else:
			lines = text.split('\n')
			result = ''
			for each in lines:
				ctag = self.getEncodeName(each, None)
				if (ctag != ''):
					result += each.decode(ctag).encode('utf-8') + '\n'
				else:
					result += each + '\n'
			return result

	def GetCharSet(self, text):
		result = ''
		tmp = text.split(';')
		for each in tmp:
			each = each.strip()
			if (each.find('charset') >= 0):
				each2 = each.split('=')
				result = each2[1].strip()
		if (result[0] == '"'):
			result = result[1:]
		if (result[-1] == '"'):
			result = result[:-1]
		return result

	def Fetch(self, uid):
		if (self.mail == None):
			return None
		try:
			result, data = self.mail.uid('fetch', uid, '(BODY[])')
			if (data[0] == None):
				self.debug('Fetch Data None')
				return None
			return self.GetInfo(data[0][1])
		except:
			exc_type, exc_value, exc_traceback = sys.exc_info()
			result = 'Error'
			lines = traceback.format_exception(exc_type, exc_value, exc_traceback)
			msg = ','.join(lines)
			self.error(msg)
		return None
			
	def ErrorMessage(self, uid, html):
		result = '<meta http-equiv="content-type" content="text/html; charset=utf-8"/>'
		return result

        def RemoveTag(self, html):
                s= html
                sp = 0
                ep = 0
                while True:
                        sp = s.find('/*')
                        if (sp < 0):
                                break
                        ep = s.find('*/', sp)
                        s = s[:sp] + s[ep+2:]
                while True:
                        sp = s.find('<script')
                        if (sp < 0):
                                break
                        ep = s.find('script>', sp)
                        s = s[:sp] + s[ep+7:]
                while True:
                        sp = s.find('<style')
                        if (sp < 0):
                                break
                        ep = s.find('style>', sp)
                        s = s[:sp] + s[ep+6:]
                while True:
                        sp = s.find('<')
                        if (sp < 0):
                                break
                        ep = s.find('>', sp)
                        s = s[:sp] + s[ep+1:]
                while (s.find('^M^M') >= 0):
                        s = s.replace('^M^M', '^M')
                while (s.find('\n\n') >= 0):
                        s = s.replace('\n\n', '\n')
                while (s.find('\r\n\r\n') >= 0):
                        s = s.replace('\r\n\r\n', '\r\n')
                s = s.replace('&nbsp', ' ')
                s = s.replace('\r', '')
                s = s.replace('\n', '<br>')

                return s


        # string to hex-string
        def asctohex(self, string_in):
                a = ""
                for x in string_in:
                        a = a + ("0"+((hex(ord(x)))[2:]))[-2:]
                return(a)

        def GetHash(self, filename):
                md5 = hashlib.sha256()
                with open(filename, 'rb') as f:
                        for chunk in iter(lambda: f.read(8192), b''):
                                md5.update(chunk)
                md5s = self.asctohex(md5.digest())
                return md5s

        def cnvImage(self, imgfile):
                args = ['/usr/local/bin/wkhtmltoimage']
                args.extend(['--quality', str(self.cfg.Quality)])
                args.extend(['--width', str(self.cfg.Width)])
                args.extend(['--disable-javascript', '--quiet', '--disable-smart-width'])
                args.extend([self.htmlfile, imgfile])
                p = subprocess.Popen(args, stdout = file(os.devnull, 'w'), stderr = file(os.devnull, 'w'))
                cnt = 0
                retcode = 0
                while True:
                        retcode = p.poll()
                        if (retcode == None):
                                cnt += 1
                                if cnt > 360:   # 360sec, 6 minute
                                        p.kill()
                                        retcode = 1000
                                        break
                                time.sleep(1)
                        else:
                                break
		# 160527
                #DPath = '/home/DATA/BACKUP/.MAIL/EXT/'
		#pp, ff = os.path.split(imgfile)
                #shutil.copy(imgfile, DPath + ff)
                        
                return retcode

        def wkHTML(self, htmltext):
                with open(self.htmlfile, 'w') as f:
                        f.write(htmltext)

                ifile = self.imgfile[:-4]
                retcode1 = self.cnvImage(ifile + ".1.jpg")
                retcode2 = self.cnvImage(ifile + ".2.jpg")
                hash1 = self.GetHash(ifile + ".1.jpg")
                hash2 = self.GetHash(ifile + ".2.jpg")
                #print hash1, retcode1
                #print hash2, retcode2
                #hash1 = hash1 + 'a'
                #hash2 = hash2 + 'b'
                if hash1 != hash2:
                        retcode3 = self.cnvImage(ifile + ".3.jpg")
                        hash3 = self.GetHash(ifile + ".3.jpg")
                        self.delfiles.append(ifile + ".3.jpg")
                        self.info('Hash not matched')
                else:
                        hash3 = hash1
                        retcode3 = hash1
                retcode = retcode1
                if (hash1 == hash3):
                        shutil.move(ifile + ".1.jpg", self.imgfile)
                        self.delfiles.append(ifile + ".2.jpg")
                        retcode = retcode1
                        self.info('1.jpg')
                elif (hash2 == hash3):
                        shutil.move(ifile + ".2.jpg", self.imgfile)
                        self.delfiles.append(ifile + ".1.jpg")
                        retcode = retcode2
                        self.info('2.jpg')
                else:
                        retcode = 1
                        self.info('Hash error.......3')

                return retcode

        def HtmlToImage(self, uid, htmltext):
		self.debug('HTML Rendering')	

		ret = self.wkHTML(htmltext)
		if (ret != 0):
			if (not os.path.exists(self.imgfile)) or (os.path.getsize(self.imgfile) < 10):
			#if (not os.path.exists(self.htmlfile)) or (os.path.getsize(self.htmlfile) < 10):
				self.error('Conversion Fail')
				htmltext = '<meta http-equiv="content-type" content="text/html; charset=utf-8"/>\n' 
				htmltext += '<div  style="font-size:14px;  font-weight:bold; color:#0000ff">\n'
				htmltext += '<p> <br>&nbsp;&nbsp;본문 내용은 아래의 "인터넷PC접속 시스템 바로가기"를 클릭 하신 후<br>'
				htmltext += '<br>&nbsp;&nbsp;인터넷 PC내의 외부메일에 접속하여 확인하시기 바랍니다.<br> </p>\n'
				htmltext += '</div>\n'
				ret = self.wkHTML(htmltext)
			else:
				self.info('Abnormal Conversion')
				ret = 0

		self.debug('HTML Rendering Complete')	

		for each in self.delfiles:
			if os.path.exists(each):
				os.remove(each)

                return ret

        def InfoToJson(self, eml):
                j = json.dumps({'Date': eml['Date'], 'From': eml['From'],
                                'To': eml['To'], 'Cc': eml['Cc'],  'Bcc': eml['Bcc'],
                                'Subject': eml['Subject'], 'Files': eml['Files']},
                                sort_keys = False, indent=4, separators=(',',': '))
                return j

        def JsonToInfo(self, jsontext):
                j = json.loads(jsontext)
                return j

	def getEncodeName(self, msg, encodeSet):
		if encodeSet == None:
			result = ''
			if result == '':
				result = self.getEncodeName(msg, 'utf-8')
			if result == '':
				result = self.getEncodeName(msg, 'euc-kr')
			if result == '':
				result = self.getEncodeName(msg, 'gb18030')
			if result == '':
				result = self.getEncodeName(msg, 'gbk')
			if result == '':
				result = self.getEncodeName(msg, 'cp1252')
			return result
		try:
			s = msg.decode(encodeSet).encode('utf-8')
			return encodeSet
		except:
			return ''
		return result

        def listToString(self, list, separator = ',', emptytext = ''):
                result = emptytext
                if (list != None) and (len(list) != 0):
			rlist = []
			for each in list:
				if type(each) == type([]):
					tmp = self.listToString(each, separator, ' ')
				else:
					tmp = each
				if not (tmp in rlist):
					rlist.append(tmp)
				#print tmp

                        result = separator.join(rlist)
                return result

        def Run(self, uid, isTest = False):
                try:
                        if self.cfg.Root != '':
                                if not os.path.exists(self.cfg.Root + '/TMP'):
                                        os.makedirs(self.cfg.Root + '/TMP')
                        result = 'Success'
                        msg = ''
			
			self.uid = uid
			self.emlfile = self.cfg.Root + '/TMP/' + self.id + '-' + uid + '.tmp'
			self.rpath = self.cfg.Root + '/TMP/' 
                        eml = self.Fetch(int(uid))
			if eml == None:
				return 'Error', 'Mail Not Found: ' + uid

			self.jsonfile = self.cfg.Root + '/TMP/' + self.id + '-' + uid + '.json'
			self.imgfile = self.cfg.Root + '/TMP/' + self.id + '-' + uid + '.jpg'
			self.htmlfile = self.cfg.Root + '/TMP/' + self.id + '-' + uid + '.html'

                        msg = ' '.join(['Recv', self.id + ':' + str(uid),
                                        'I[' + eml['ID'] + ']',
                                        'D[' + eml['Date'] + ']',
                                        'F[' + self.listToString(eml['From']) + ']',
                                        'T[' + self.listToString(eml['To']) + ']',
                                        'C[' + self.listToString(eml['Cc']) + ']',
                                        'B[' + self.listToString(eml['Bcc']) + ']',
                                        'S[' + eml['Subject'] + ']',
                                        'F[' + self.listToString(eml['Files'], ',', '없음') + ']'])
                        self.info(msg)
                        msg = ''

                        if not isTest:
                                db = DB(self.cfg)
                                if db.FindKey(eml['ID']):
					db.Clear()
					os.remove(self.emlfile)
					return 'Etc', '중복메일'
				db.Clear()

                        s = self.InfoToJson(eml)
                        with open(self.jsonfile, 'w') as f:
                                f.write(s)

                        Fail = self.HtmlToImage(uid, eml['HTML'])
                        if Fail:
				self.debug('HTML Rendering Error')
                                result = 'Etc'
                                msg = 'Image Conversion Error'
                                html = self.RemoveTag(eml['HTML'])
                                html = self.ErrorMessage(uid, html)
                                self.HtmlToImage(uid, html)

                        # 160527
                        #DPath = '/home/DATA/BACKUP/.MAIL/EXT/'
                        #shutil.copy(self.jsonfile, DPath + self.id + '-' + uid + '.json')
                        #shutil.copy(self.imgfile,  DPath + self.id + '-' + uid + '.jpg')
                        #shutil.copy(self.htmlfile, DPath + self.id + '-' + uid + '.tmp')
                        #shutil.copy(self.emlfile,  DPath + self.id + '-' + uid + '.html')
			#subprocess.call(['chmod', '755', '/home/DATA/BACKUP/', '-R'])

			if (not isTest):
				shutil.move(self.jsonfile, self.cfg.Outbound + '/' + self.id + '-' + uid + '.json')
				shutil.move(self.imgfile, self.cfg.Outbound + '/' + self.id + '-' + uid + '.jpg')
				os.remove(self.htmlfile)
				os.remove(self.emlfile)
                except:
                        exc_type, exc_value, exc_traceback = sys.exc_info()
                        result = 'Error'
                        lines = traceback.format_exception(exc_type, exc_value, exc_traceback)
                        msg = ','.join(lines)
                return result, msg

class DB:
        def __init__(self, cfg):
                self.conn = sqlite3.connect(cfg.Root + '/mail.db')
                self.conn.text_factory = str
                self.conn.row_factory = sqlite3.Row
                self.CreateTable()
        def __del__(self):
                self.conn.close()

        def CreateTable(self):
                cr = self.conn.cursor()
                cr.execute('''CREATE TABLE IF NOT EXISTS MailID (id VARCHAR(20) PRIMARY KEY, datekey datetime)''')
        def FindKey(self, key):
                d = datetime.datetime.now().strftime('%Y%m%d')
                cr = self.conn.cursor()
                cr.execute('SELECT * FROM MailID WHERE id=\'' + key + '\'')
                row = cr.fetchone()
                result = True
                if row == None:
                        qry = 'INSERT INTO MailID VALUES (\'' + key + '\',\'' + d + '\')'
			try:
	                        cr.execute(qry)
                        	self.conn.commit()
	                        result = False
			except:
				result = True
                return result

        def Clear(self, days = 4):
                d = datetime.datetime.now() + datetime.timedelta(days = -1 * days)
                cr = self.conn.cursor()
                qry = 'Delete From MailID WHERE datekey<\'' + d.strftime('%Y%m%d') + '\''
		try:
	                cr.execute(qry)
                	self.conn.commit()
		except:
			print 'Clear Error'

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
        def __init__(self, daemonName = 'rmail', isTest = False):
                self.LoadConfig(daemonName)

		self.isTest = isTest
		self.logger = Log(self.cfg.Log +'/' + daemonName + '.log', isDebug = True, isConsoleOut = isTest)

		'''
                loglevel = logging.DEBUG
                self.logger = logging.getLogger('caengine-rmail')
                self.logger.setLevel(loglevel)

                formatter = logging.Formatter('%(asctime)s.%(msecs)03d %(levelname)s %(message)s', '%m/%d/%Y %H:%M:%S')

                if (isTest):
                        ch = logging.StreamHandler()
                        ch.setLevel(loglevel)
                        ch.setFormatter(formatter)
                        self.logger.addHandler(ch)

                hdlr = logging.handlers.TimedRotatingFileHandler(self.cfg.Log +'/' + daemonName + '.log', when = 'D', interval = 1)
                hdlr.setFormatter(formatter)
                hdlr.setLevel(loglevel)
                self.logger.addHandler(hdlr)
		'''

		self.logger.info('Recv Start')

        def LoadConfig(self, daemonName):
                etcpath = path.dirname(path.dirname(path.abspath(__file__))) + "/etc/"
                cfgName = etcpath + daemonName + ".conf"
		print cfgName
                cfg = caengineconfig.Info(cfgName)

                self.cfg = cfg.Receive

	def Open(self, server, user):  # id, pw):
                id, pw = decrypt(user)
		self.mail = RecvMail(self.cfg, self.logger, server, id, pw)
		self.id = id
                return self.mail.mail != None

	def Close(self):
		self.mail = None
		self.logger.info('Recv Stop')
		
	
	def DeleteUidList(self, uidlist):
		if self.mail == None:
			self.logger.error('Server Open Failed')
			return
		self.mail.MoveTrash(uidlist)
		
	def GetUidList(self, d = '05-JAN-2016'):
                if self.mail == None:
			self.logger.error('Server Open Failed')
                        return

		qry = '(BEFORE ' + d + ')'
		s = self.mail.Search(qry)
		if (s == None) or (len(s) == 0) or (s[0] == None):
			return []
		uidlist = s[0].split()

		return uidlist
	
	def RemoveOldList(self, sincedays = 30):
                try:
        		d = datetime.datetime.now() + datetime.timedelta(days = -1 * sincedays)
        		sd = d.strftime('%d-%b-%Y')
        		uidlist = self.GetUidList(sd) # date:'04-JAN-2016'
        		if len(uidlist) > 0:
        			self.logger.info('Remove old Mails: ' + ','.join(uidlist))
        			self.DeleteUidList(uidlist)
                except:
			exc_type, exc_value, exc_traceback = sys.exc_info()
                        lines = traceback.format_exception(exc_type, exc_value, exc_traceback)
                        msg = ','.join(lines)
                        self.logger.error(msg)
                        return

        def Get(self, uid = ''):
                if self.mail == None:
			self.logger.error('Server Open Failed')
                        return

		uidfile = self.cfg.Root + '/INF/' + self.id + '.uid'
                if uid == '':
			if os.path.exists(uidfile):
	                        with open(uidfile, 'r') as f:
        	                        uid = f.read(-1)
				uid2 = int(uid) + 1
			else:
				uid2 = 1
                        qry = '(UID ' + str(uid2) + ':*)'
                        try:
                                s = self.mail.Search(qry)
                        except:
                                exc_type, exc_value, exc_traceback = sys.exc_info()
                                result = 'Error'
                                lines = traceback.format_exception(exc_type, exc_value, exc_traceback)
                                msg = ','.join(lines)
                                self.logger.info('Recv ' + self.id + ': Fetch error ' + msg)
                                return
			if (s == None) or (len(s) == 0) or (s[0] == None):
			     return
			
			uidlist = s[0].split()
                else:
			uid2 = 0
                        uidlist = [ uid ]

                self.isStop = False
		count  = 0
                for UID in uidlist:
			if (UID == None):
				break
                        if int(UID) >= uid2:
                                result, msg = self.mail.Run(UID, self.isTest)
                                self.logger.info('Recv ' + self.id + ':' + str(UID) + ' ' + result + ' ' + msg)
				retry = 0
                                while (result == 'Error'):
					wtime = random.randrange(3,20)
	                                self.logger.info('Retry ' + self.id + ':' + str(UID) + ' , ' + str(wtime) + 'sec')
					try:
						time.sleep(wtime)
					except:
						print 'random error'
                                        result, msg = self.mail.Run(UID, self.isTest)
	                                self.logger.info('Recv ' + self.id + ':' + str(UID) + ' ' + result + ' ' + msg)
					retry = retry + 1
					if retry > 1:
						break
				count = count + 1
				if not self.isTest: # Write Last UID
					with open(uidfile, 'w') as f:
        	                        	f.write(UID)
                        if (count > 10): # 10 개만 하고 다음 번에
                                break
                        if self.isStop:
                                break
		return count

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
                cfgName = etcpath + "rmaild.conf"
                print cfgName
                cfg = caengineconfig.Info(cfgName).Receive

		mail = RecvMail(cfg, None, "", "", "")
		mail.id = 'test'

		mail.rpath = cfg.Root + '/TMP/'
		mail.emlfile = cfg.Root + '/TMP/test-1.eml'
		info = mail.GetInfo(eml)
		mail.jsonfile = cfg.Root + '/TMP/test-1.json'
		mail.imgfile = cfg.Root + '/TMP/test-1.jpg'
		mail.htmlfile = cfg.Root + '/TMP/test-1.html'

		mail.HtmlToImage('1', info['HTML'])	

		print '================================================================================'
		print 'Subject:', info['Subject']
		print 'Files:',  info['Files'][0][0]
		sys.exit(0)

        pw = encrypt(sys.argv[1], sys.argv[2])
        id, pw2 = decrypt(pw)
        print pw, id, pw2

