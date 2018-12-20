#!/usr/bin/python
# -*- coding: utf-8 -*-
import os, sys
reload(sys)
sys.setdefaultencoding('utf-8')

# hjkim 20170416 async 처리
from gevent import monkey; monkey.patch_all()

from bottle import route, template, run
import json
import mailrequest
import threading

@route('/<filename:path>')

def Run(filename):
	template = mailrequest.run(filename)
	return template

# hjkim 20170416 async 처리
threading.Thread(target=run, kwargs=dict(host='10.211.55.125', port=8780, server='gevent')).start()
#threading.Thread(target=run, kwargs=dict(host='10.129.1.172', port=8780, debug=True)).start()
#run(host='10.129.1.172', port=8780, debug=True)
