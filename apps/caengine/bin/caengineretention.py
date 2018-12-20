#! /usr/bin/python
# coding: utf-8
#=========================================================================================
# import python module
#=========================================================================================
import os
import shutil
import sys
import time
import datetime
import caengineconf
############################################################################
# 원본 파일 백업
############################################################################
# CronTab에서 실행
# 파일을 순서대로 Move 한다.
cfg = caengineconf.config('', __name__ == "__main__")

def RemoveFile(file):
	if os.path.exists(file):
		os.remove(file);
		
# 지정한 폴더의 날짜가 retentionday 보다 크면 삭제
def ManageFolder(dstpath, retentiondays):
	print "TimeOut Files: " + dstpath
	d=datetime.datetime.now()
	folderlist = os.listdir(dstpath)
	for folder in folderlist:
		newFolder = dstpath + '/' + folder
		if os.path.isfile(newFolder):
			# last modified
			ftime = datetime.datetime.fromtimestamp(os.path.getmtime(newFolder))
			df = d - ftime
			#print newFolder,'\t', d,'\t', ftime,'\t', df.days, '\t', df.days > retentiondays
			if df.days > retentiondays:
				print 'Remove ===> ' + newFolder + '\t', df.days, retentiondays
				RemoveFile(newFolder);
		else: # folder
			ManageFolder(newFolder, retentiondays)

# 지정한 폴더의 날짜가 retentionday 보다 크면 삭제
def ManageFolder2(dstpath, retentiondays, specialfolder, retentiondays2):
	print "TimeOut Files: " + dstpath
	d=datetime.datetime.now()
	folderlist = os.listdir(dstpath)
	for folder in folderlist:
		newFolder = dstpath + '/' + folder
		if os.path.isfile(newFolder):
			# last modified
			ftime = datetime.datetime.fromtimestamp(os.path.getmtime(newFolder))
			df = d - ftime
			if df.days > retentiondays:
				print 'Remove2 ===> ' + newFolder + '\t', df.days, retentiondays
				RemoveFile(newFolder);
		else: # folder
			if folder == specialfolder:
				ManageFolder(newFolder, retentiondays2)
			else:
				ManageFolder2(newFolder, retentiondays, specialfolder, retentiondays2)

############################################################################
# 백업 파일 관리, 지정된 기간 지난 파일 삭제
# du -b -s /DATA/BACKUP
############################################################################
filename = cfg.rootPath + '/INF/retention.dat'
if not os.path.exists(filename):
	sys.exit(1)
	
File = open(filename)
conf = File.read(-1)
File.close
conf2 = conf.split('\n')
print conf2
retention_backup = int(conf2[0])	# LOG, BACKUP은 동일하게
retention_log = int(conf2[1])	# caengine의 log
retention_file = int(conf2[2])		# 승인 신청 파일 유지 기간
retention_person = int(conf2[3])	# 개인별 승인 및 신청 로그 유지
ManageFolder(cfg.rootPath + '/BACKUP', retention_backup) 
ManageFolder(cfg.rootPath + '/LOG', retention_log)
ManageFolder('/var/log/JionLab/caengine', retention_log)
ManageFolder2(cfg.rootPath + '/GET', retention_file, 'Log', retention_person)	#  GET안에 파일과 GET/ID/LOG 폴더를 구분.
ManageFolder(cfg.rootPath + '/PUT', retention_file)	#  GET안에 파일과 GET/ID/LOG 폴더를 구분.
