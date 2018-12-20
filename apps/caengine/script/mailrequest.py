#!/usr/bin/python
# -*- coding: utf-8 -*-
import os, sys
import glob, os
reload(sys)
sys.setdefaultencoding('utf-8')

sys.path.append("/opt/JionLab/caengine/bin")
import caengineconf

# hjkim 20170416 async 처리
import gevent
from gevent import monkey; monkey.patch_all()
from time import sleep

import datetime
import json
from bottle import Bottle, get, request, route, run, static_file, template
from json import dumps
from subprocess import Popen

reload(sys)
sys.setdefaultencoding('utf8')

#=========================================================================================
# 스크립트 설정
#=========================================================================================
cfg = caengineconf.config('', __name__ == "__main__")

linebreak = '\t\n'
div = '\t'

# 임시 백업 폴더로 이동
# 별개 프로그램이 최종 백업 폴더로 파일 이동 시킴
backupPath = cfg.rootPath + '/Backup/MailBack'
infPath = cfg.rootPath + '/MAIL/INF/'
putPath = cfg.rootPath + '/MAIL/PUT/'
getPath = cfg.rootPath + '/MAIL/GET/'
logPath = cfg.rootPath + '/LOG/MAIL/'
destHost = 'CBOUT2'

class RequestAttachment:
	def __init__(self):
		__FileLocation__ = os.path.abspath(__file__)
		__CurrentPath__, __msgfile__ = os.path.split(__FileLocation__)
		self.etcPath = __CurrentPath__[:-3] + "etc/"
		confname = self.etcPath + "caengined.conf"

@route('/<name:path>')
def run(name):
	data = name.split('-=-')
	print data
	splitdata = data[0].split('-')

	userip = request.environ.get('REMOTE_ADDR')

	userNid = data[0]
	filename = data[1]
	user = splitdata[0]
	uid = splitdata[1]

	dt = datetime.datetime.now()
	format = '%m%d%Y-%H%M%S%f'

	fcp2filename = ''.join( [dt.strftime(format),"-",splitdata[0],"-",splitdata[1]])
	jsondata = json.dumps({ 'user': user, 'userip': userip, 'uid': uid, 'filename': filename, 'fcp2filename': fcp2filename},sort_keys = False, indent=4, separators=(',',': '))

	outPathFile = putPath + userNid + '-' + fcp2filename + "-out" + ".json"
	inPathFile = getPath + user + '/' + userNid + '-' + fcp2filename + "-in" + ".json"
	outPath = putPath + user
	inPath = getPath + user

	CreateDirectory(outPath)

	# 외부망으로 보내자
	if not os.path.isfile(outPathFile) :
		with open(outPathFile, 'wb') as fp:
			fp.write(jsondata)
			fp.close()
		# hjkim 20170416 이전에 수신한 파일들을 삭제
		for the_file in os.listdir(inPath):
			file_path = os.path.join(inPath, the_file)
			try:
				if os.path.isfile(file_path):
					os.unlink(file_path)
			except Exception as e:
				print(e)

		dstfile = destHost+ ':' + outPathFile
		arg = """ """.join(["/opt/JionLab/fcp2/bin/fcp2 -f", outPathFile, "-p 10.211.55.126:7776", dstfile, "-P", "/opt/JionLab/caengine/script/relay"])
		obj = Popen(arg, shell=True, stdin=None, stdout=None, stderr=None, close_fds=True)
		obj.wait()
		# fcp2 외부망 전송 문제 없을때 풀것
		os.remove(outPathFile)

	# hjkim 20170416 내부망으로 넘어왔으면 PC 사용자에게 보내자 시작
	print inPathFile
	escapeCount = 0
	while True:
		if escapeCount == 1200:
			rtnfilename  = "mailnotreached"
			break
		if(os.path.exists(inPathFile)):
			rtnfilename = RentoOrgFile(inPathFile, inPath)
			break
		gevent.sleep(1)
		escapeCount =  escapeCount + 1

	userPath = inPath + '/'
	
	if rtnfilename  == "mailnotfound":
		return template('메일 서버의 메일이 삭제 되어{{filename}}을(를) 다운로드 할 수 없습니다.', filename=data[1])
	elif rtnfilename  == "mailnotreached":
		return template('메일서버 접속에 시간을 초과하여  {{filename}}을(를) 다운로드 할 수 없습니다. 잠시후 다시 다운로드 하십시오.', filename=data[1])
	else:
		return static_file(rtnfilename, root= userPath, download=rtnfilename)
	# hjkim 20170416 내부망으로 넘어왔으면 PC 사용자에게 보내자 끝

def RentoOrgFile(inPathFile, inPath):
	getfname = os.path.basename(inPathFile)

	with open(inPathFile, 'r') as f:
		getdata = f.read()
		f.close()
	attachinfo = JsonToInfo(getdata)

	userip = ''.join(listJsonToText(attachinfo['userip']))
	getfilename = ''.join(listJsonToText(attachinfo['filename']))
	fcp2filename = ''.join(listJsonToText(attachinfo['fcp2filename']))
	uidstr = ''.join(listJsonToText(attachinfo['uid']))
	user = ''.join(listJsonToText(attachinfo['user']))

	if getfilename != "mailnotfound":
		# hjkim 20170414 Local PC 에서는 euc-kr로 읽어야 해서
		getfilename = getfilename.decode('utf-8').encode('euc-kr')
		srcFile = inPath + '/' + fcp2filename
		dstFile = inPath + '/' + getfilename
		os.rename(srcFile, dstFile)

	return getfilename

def JsonToInfo(jsontext):
	j = json.loads(jsontext)
	return j

def listJsonToText(list):
	result = []
	if (list != None) and (len(list) != 0):
		for each in list:
			if type(each) == type([]):
				tmp = listJsonToText(each)
				for each2 in tmp:
					result.append(each2)
			else:
				result.append(each.encode('utf-8'))
	if len(result) == 0:
		result = [u'없음']
	return result

def CreateDirectory(directory):
	if not os.path.exists(directory):
		os.makedirs(directory)
