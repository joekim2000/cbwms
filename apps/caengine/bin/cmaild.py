#!/usr/bin/python
# coding: utf-8
import gevent
from gevent.queue import Queue
from gevent import monkey; monkey.patch_all()
from gevent import Greenlet
import sys, os, time, atexit
import signal
import datetime
import cmail
daemonName = 'cmaild'
pidName = '/var/run/JionLab/caengine/' + daemonName + '.pid'
errName = '/var/log/JionLab/caengine/' + daemonName + '.err'
logName = '/var/log/JionLab/caengine/' + daemonName + '.log'

asynctasks = Queue()

class Daemon:
	"""
	A generic daemon class.

	Usage: subclass the Daemon class and override the run() method
	"""
	def __init__(self, pidfile, stdin='/dev/null', stdout='/dev/null', stderr='/dev/null'):
		self.stdin = stdin
		self.stdout = stdout
		self.stderr = stderr
		self.pidfile = pidfile

	def daemonize(self):
		"""
		do the UNIX double-fork magic, see Stevens' "Advanced
		Programming in the UNIX Environment" for details (ISBN 0201563177)
		http://www.erlenstar.demon.co.uk/unix/faq_2.html#SEC16
		"""

		try:
			pid = os.fork()
			if pid > 0:
				# exit first parent
				sys.exit(0)
		except OSError, e:
			sys.stderr.write("fork #1 failed: %d (%s)\n" % (e.errno, e.strerror))
			sys.exit(1)
				
		# decouple from parent environment
		os.chdir("/")
		os.setsid()
		os.umask(0)

		# do second fork
		try:
			pid = os.fork()
			if pid > 0:
				# exit from second parent
				sys.exit(0)
		except OSError, e:
			sys.stderr.write("fork #2 failed: %d (%s)\n" % (e.errno, e.strerror))
			sys.exit(1)
        
		# redirect standard file descriptors
		sys.stdout.flush()
		sys.stderr.flush()
		si = file(self.stdin, 'r')
		so = file(self.stdout, 'a+')
		se = file(self.stderr, 'a+', 0)

		os.dup2(si.fileno(), sys.stdin.fileno())
		os.dup2(so.fileno(), sys.stdout.fileno())
		os.dup2(se.fileno(), sys.stderr.fileno())

		# write pidfile
		atexit.register(self.delpid)
		pid = str(os.getpid())
		file(self.pidfile,'w+').write("%s\n" % pid)
       
	def delpid(self):
		os.remove(self.pidfile)

	def boss(self):
		for i in xrange(1,25):
			asynctasks.put_nowait(i)

	def start(self):
		"""
		Start the daemon
		"""
		# Check for a pidfile to see if the daemon already runs
		try:                
			pf = file(self.pidfile,'r')
			pid = int(pf.read().strip())
			pf.close()
		except IOError:
			pid = None
		if pid:
			message = "pidfile %s already exist. Daemon already running?\n"
			sys.stderr.write(message % self.pidfile)
			sys.exit(1)

		# Start the daemon
		print "start"
		self.daemonize()
		self.run()
 
	def stop(self):
		"""
		Stop the daemon
		"""
		# Get the pid from the pidfile
		try:
			pf = file(self.pidfile,'r')
			pid = int(pf.read().strip())
			pf.close()
		except IOError:
			pid = None

		if not pid:
			message = "pidfile %s does not exist. Daemon not running?\n"
			sys.stderr.write(message % self.pidfile)
			return # not an error in a restart

		# Try killing the daemon process       
		try:
			while 1:
				os.kill(pid, signal.SIGTERM)
				time.sleep(0.1)
		except OSError, err:
			err = str(err)
			if err.find("No such process") > 0:
				if os.path.exists(self.pidfile):
					os.remove(self.pidfile)
			else:
				print str(err)
				sys.exit(1)
 
	def restart(self, n):
		"""
		Restart the daemon
		"""
		self.stop()
		self.start()
 
	def run(self):
		"""
		You should override this method when you subclass Daemon. It will be called after the process has been
		daemonized by start() or restart().
		"""
		signal.signal(signal.SIGTERM, self.StopProcess)
                self.mail = cmail.Mail(daemonName)

		self.isStop = False

		while (not self.isStop):
			gevent.spawn(self.boss).join()
			for user in self.mail.cfg.Users:
				gevent.joinall([
					gevent.spawn(self.mail.Open, user[0],user[1],asynctasks),
				])

			if (self.isStop):
				break
			time.sleep(1)
			self.mail.Close()

	def fetch(self, pid):
		print pid
		for user in self.mail.cfg.Users:
			self.mail.Open(user[0], user[1])

	def StopProcess(self, signum, frame):
		self.mail.Stop()
		self.isStop = True

def Test(userno, arg=''):
	print 'Test'

#=====================================================================================
# FileBridge Message Daemon Start
#=====================================================================================
if __name__ == "__main__":
	if (len(sys.argv) == 2) and ('start' == sys.argv[1]) and os.path.exists(errName):
		os.remove(errName)

	daemon = Daemon(pidName, '/dev/null', '/dev/null', stderr=errName)
	if len(sys.argv) == 2:
		if 'start' == sys.argv[1]:
			print "Start cmaild"
			daemon.start()
		elif 'stop' == sys.argv[1]:
			print "Stop cmaild"
			daemon.stop()
		elif 'restart' == sys.argv[1]:
			daemon.restart()
		elif 'ver' == sys.argv[1]:
			print "v1.0.180206"
		else:
			print "Unknown command"
			sys.exit(2)
		sys.exit(0)
	elif len(sys.argv) == 3:
		Test(int(sys.argv[1]), sys.argv[2])
	else:
		print "usage: %s start|stop|restart" % sys.argv[0]
		sys.exit(2)
