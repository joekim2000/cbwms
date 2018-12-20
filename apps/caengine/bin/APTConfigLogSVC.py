#! /usr/bin/python
# coding: utf-8
#=========================================================================================
# import python module
#=========================================================================================
from os import sys, path
import os
import logging
import logging.handlers

class Log():
	def __init__(self, cfg):
		self.cfg = cfg
		self.logger = logging.getLogger('caengine2d')
		if (self.cfg.Log.Level == 'DEBUG'):
			loglevel = logging.DEBUG
		else:
			loglevel = logging.INFO

		self.logger.setLevel(loglevel)

		# create formatter
		formatter = logging.Formatter('%(asctime)s.%(msecs)03d %(levelname)s %(message)s', '%m/%d/%Y %H:%M:%S')
		#formatter = logging.Formatter('%(message)s')

		# create console handler and set level to debug
		if (self.cfg.Log.Console):
			ch = logging.StreamHandler()
			ch.setLevel(loglevel)
			ch.setFormatter(formatter)
			self.logger.addHandler(ch)

		# File Handler
		hdlr = logging.handlers.TimedRotatingFileHandler(self.cfg.Log.Path + '/caengine2d.log', 'd', 1)
		hdlr.setFormatter(formatter)
		hdlr.setLevel(loglevel)
		self.logger.addHandler(hdlr) 

	#=====================================================================================
	# Logger Function
	def info(self, header, message):
		self.logger.info('[' + header + '] ' + message)

	def debug(self, header, message):
		self.logger.debug('[' + header + '] ' + message)

	def error(self, header, message):
		self.logger.error('[' + header + '] ' + message)

	def warning(self, header, message):
		self.logger.warning('[' + header + '] ' + message)

