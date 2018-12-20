#! /usr/bin/python
# coding: utf-8
#=========================================================================================
# Initial
#=========================================================================================
import ConfigParser

#-----------------------------------------------------------------------------------------
# Log Handling
class Receive():
	def __init__(self, conf):
		self.Width = conf.getint('Receive', 'Width')
		self.Quality = conf.getint('Receive', 'Quality')
		self.UseSSL = (conf.get("Receive", "UseSSL").upper() == 'YES')
		self.Root = conf.get('Receive', 'Root')
		self.LocalIPPort = conf.get('Receive', 'LocalIPPort')
		self.Desthost = conf.get('Receive', 'Desthost')
		self.Outbound = conf.get('Receive', 'Outbound')
		self.Log = conf.get('Receive', 'Log')
		self.RemoveBeforeDays = conf.getint('Receive', 'RemoveBeforeDays')

		cnt = conf.getint('Receive', 'UserCount')
		self.Users =[]
		for i in range(1, cnt+1):
			tmp = conf.get('Receive', 'User' + str(i))
			self.Users.append(tmp.split(' '))


#-----------------------------------------------------------------------------------------
# Configuration Information
class Info():
	def __init__(self, configFile = ''):
		self.__Load__(configFile)

	def __Load__(self, configFile= ''):
		conf = ConfigParser.RawConfigParser()
		conf.read(configFile)

		self.Receive = Receive(conf)


#-----------------------------------------------------------------------------------------
# Test Process
if __name__ == "__main__":
	cfg = Info("../etc/mail.conf")
	print cfg.Receive.Quality
	print cfg.Receive.Width
	print cfg.Receive.UseSSL
	print cfg.Receive.Root
	print cfg.Receive.Outbound
	print cfg.Receive.RemoveBeforeDays
	print cfg.Receive.Users
