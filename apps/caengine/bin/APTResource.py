#! /usr/bin/python
# coding: utf-8
import time
import datetime
import psutil
import logging
import logging.handlers
from multiprocessing import Process, Pipe
from threading import Thread
import multiprocessing

import signal

class Monitor():
	def __init__(self, logfile, netifs = [], disks = [], processes = []):
		self.parent_conn, child_conn = Pipe()
		self.prc = Thread(target=self.ThreadProcess, args=(child_conn, ))
		self.logger = logging.getLogger('resource')
		self.logger.setLevel(logging.INFO)
		self.netifs = netifs
		self.disks = disks
		self.processes = processes
		
		# create formatter
		formatter = logging.Formatter('%(asctime)s.%(msecs)03d %(levelname)s %(message)s', '%m/%d/%Y %H:%M:%S')
		#formatter = logging.Formatter('%(message)s')

		# File Handler
		hdlr = logging.handlers.TimedRotatingFileHandler(logfile, 'd', 1)
		hdlr.setFormatter(formatter)
		hdlr.setLevel(logging.INFO)
		self.logger.addHandler(hdlr) 

	def Start(self):
		self.logger.info('Start Resource Monitor')
		self.logger.info('cpu% memfree mem% disk disk_free disk% [netif net_sent net_recv] [proc count]')
		self.prc.start()
		
	def Stop(self):
		self.parent_conn.send([True])
		self.parent_conn.close()
		self.prc.join()
		self.logger.info('Stop Resource Monitor')

	def ThreadProcess(self, conn):
		while (True):
			self.GetInform()
			isStop = False
			if conn.poll():
				isStop = conn.recv()
				if isStop:
					break;
		
	def GetInform(self):
		# CPU, Memory, Disk, Network, 절대치, %
		msgs = []
		cpu = psutil.cpu_percent(interval=1)
		#d = datetime.datetime.now()
		#msgs.append(d.strftime('%m/%d/%Y %H:%M:%S.%f'))
		msgs.append(str(cpu))

		mem = psutil.virtual_memory()
		msgs.append(str(mem.free))
		msgs.append(str(mem.percent))

		for eachdisk in self.disks:
			tmp = psutil.disk_usage(eachdisk)
			msgs.append(eachdisk)
			msgs.append(str(tmp.free))
			msgs.append(str(tmp.percent))

		netinfo = psutil.net_io_counters(pernic=True)
		for netif in self.netifs:
			net = netinfo[netif]
			msgs.append(netif)
			msgs.append(str(net.bytes_sent))
			msgs.append(str(net.bytes_recv))
		
		cntProcess = {}
		for proc in self.processes:
			cntProcess[proc] = 0

		pids = psutil.pids()
		for pid in pids:
			#print p
			try:
				p = psutil.Process(pid)
				if p.status != psutil.STATUS_ZOMBIE:
					if p.name() in self.processes:
						cntProcess[p.name()] += 1
			except psutil.NoSuchProcess:
				#print 'Error', pid
				a = 1

		for proc in self.processes:
			msgs.append(proc)
			msgs.append(str(cntProcess[proc]))

		self.logger.info(' '.join(msgs))

if __name__ == "__main__":
	disks = [ '/' , '/Volumes/Parallels']
	netifs = ['en0', 'en1']
	processes = ['sockd', 'fcp2d', 'caengined']
	m = Monitor('../../Test/Log/resource.log', netifs, disks, processes)
	m.Start()
	time.sleep(10)
	print '---------------'
	m.Stop()
	print '---------------'
	time.sleep(10)
	print '---------------'

