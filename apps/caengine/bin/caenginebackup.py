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

srcFolder = cfg.rootPath + '/Backup'
dstFolder = cfg.rootPath + '/BACKUP'

def CreateDirectory(directory):
	if not os.path.exists(directory):
		os.makedirs(directory)

def RemoveFile(file):
	if os.path.exists(file):
		os.remove(file);
	
def MoveFile(srcpath, dstpath, file):
	if os.path.exists(srcpath + '/' + file):
		CreateDirectory(dstpath)
	RemoveFile(dstpath + '/' + file);
	shutil.move(srcpath + '/' + file, dstpath + '/' + file)

# 기존에 프로세스가 있으면 재 실행 방지
# process 확인
# Get Current Process List
a = os.popen('ps aux | grep caenginebackup.py').read()
b = a.split('\n')

# Check Overrun
isOverrun = 0
for eachB in b:
        #print eachB
        idx = eachB.find('/caenginebackup.py')
        if (idx > 0):
                isOverrun += 1

# print isOverrun
if (isOverrun > 1):
        #print('Overrun')
        sys.exit()


############################################################################
# 원본 파일 백업
############################################################################
folderlist = os.listdir(srcFolder)
for folder in folderlist:
	newFolder = srcFolder + '/' + folder
	if not os.path.isdir(newFolder):
		continue
	print newFolder
	
	filelist = os.listdir(newFolder)
	for file in filelist:
		if not os.path.isfile(newFolder + '/' + file):
			continue
		print file
		MoveFile(newFolder, dstFolder + '/' + folder, file)
