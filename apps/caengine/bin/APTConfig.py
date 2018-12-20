#! /usr/bin/python
# coding: utf-8
#=========================================================================================
# Initial
#=========================================================================================
import ConfigParser

#-----------------------------------------------------------------------------------------
# Data Handling
class Data():
	def __init__(self, conf):
		self.Path = conf.get("Data", "Path")
		self.Sleep = conf.getfloat("Data", "Sleep") / 1000

#-----------------------------------------------------------------------------------------
# Log Handling
class Log():
	def __init__(self, conf):
		self.Path = conf.get("Log", "Path")
		self.Level = conf.get("Log", "Level")
		self.Console = (conf.get("Log", "Console").upper() == 'YES')

#-----------------------------------------------------------------------------------------
# File Inspection Option
class FileInspection():
	def __init__(self, conf):
		self.Vaccine = (conf.get("Inspection", "Vaccine").upper() == 'YES')
		self.APT = (conf.get("Inspection", "APT").upper() == 'YES')
		self.SEED256 = (conf.get("Inspection", "SEED256").upper() == 'YES')
		self.AVscript = conf.get("Inspection", "AV")
		self.SEEDscript = conf.get("Inspection", "SEED")
		self.MaxThread = conf.getint("Inspection", "MAX")

class APT():
	def __init__(self, conf):
		self.Path = conf.get("APT", "Path")
		self.ScanPath = self.Path + '/' + conf.get("APT", "ScanPath")
		self.SuccessPath = self.Path + '/' + conf.get("APT", "SuccessPath")
		self.MalPath = self.Path + '/' + conf.get("APT", "MalPath")
		self.UnknownPath = self.Path + '/' + conf.get("APT", "UnknownPath")
		self.UnknownIsSuccess = (conf.get("APT", "UnknownIsSuccess").upper() == 'YES')
		self.Timeout = conf.getfloat("APT", "Timeout")

#-----------------------------------------------------------------------------------------
# Configuration Information
class Info():
	def __init__(self, configFile = ''):
		self.__Load__(configFile)

	def __Load__(self, configFile= ''):
		conf = ConfigParser.RawConfigParser()
		conf.read(configFile)

		self.Data = Data(conf)
		self.Log = Log(conf)
		self.FileInspection = FileInspection(conf)
		self.APT = APT(conf)

#-----------------------------------------------------------------------------------------
# Test Process
if __name__ == "__main__":
	cfg = Info("../etc/caengine2d.conf")
	print cfg.Data.Path
	print cfg.Data.Sleep
	print cfg.Log.Path
	print cfg.Log.Level
	print cfg.Log.Console
	print cfg.APT.ScanPath
	print cfg.APT.SuccessPath
	print cfg.APT.MalPath
	print cfg.FileInspection.AVscript
	print cfg.FileInspection.MaxThread
