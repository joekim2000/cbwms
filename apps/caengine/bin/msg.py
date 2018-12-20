#! /usr/bin/python
# coding: utf-8

import sys
import os
import datetime
import httplib, urllib

class UCWare:
	def __init__(self, addr):
		self.defaultEncoding = "UTF-8"
		self.addr = addr
		self.params = dict()
		self.needed = [ "CMD", "Action", "SystemName", "SystemName_Encode", "SendID", "SendName", "SendName_Encode",
						"Dest_domain", "Dest_gubun", "RecvId", "Subject", "Subject_Encode", "Contents", 
						"Contents_Encode" ]
	
	def setParams(self, name, value):
		self.params[name] = value
		
	def Send(self, sender, sendername, receiver, type, message):
		title = ""
		sendmessage = ""
		if type == "0":
			title ="<자료반출입> 승인신청"
			sendmessage = "자료반출입 승인을 신청합니다.<br><br>사유: " + message
		elif type == "1":
			title = "<자료반출입> 승인완료"
			sendmessage = "자료반출입 승인을 완료 하였습니다.<br><br>사유: " + message
		elif type == "2":
			title = "<자료반출입> 승인신청반려"
			sendmessage = "자료반출입 승인신청을 반려 하였습니다.<br><br>사유: " + message
		elif type == "3":
			title = "<메일반출> 승인오류"
			sendmessage = "메일반출에 실패 하였습니다.<br><br>승인신청을 다시 하십시오.<br><br>동일한 오류가 지속되면 망연계 담당자에게 문의 바랍니다."

		self.sendUCMessage("MSG", "secu", sender, sendername, receiver, title, sendmessage)

	def send(self):
		needed = [ need for need in self.needed if need not in self.params ]
		if len(needed) > 0:				
			return -1
		if self.params["RecvId"] == "":	
			self.params["RecvId"] == "2141002"
		self._sendHttp(self.params, self.addr)
		
	def _sendHttp(self, params, addr):
		params = urllib.urlencode(params)
		print addr
		headers = { "Content-Type":"application/x-www-form-urlencoded",
					"Accept":"text/html, application/xhtml+xml, */*",
					"Accept-Encoding":"gzip, deflate" }
		conn = httplib.HTTPConnection(addr)
		conn.request("POST", "/", params, headers)
		response = conn.getresponse()
		print response.status, response.reason
		data = response.read()
		conn.close()
		
	def sendUCMessage(self, type, sysName, sndID, sndName, rcvID, subject, content):
		self.setParams("CMD", type)
		self.setParams("Action", "ALERT")
		self.setParams("SystemName", sysName)
		self.setParams("SystemName_Encode", "UTF-8")
		self.setParams("SendID", sndID)		
		self.setParams("SendName", sndName)
		self.setParams("SendName_Encode", "UTF-8")
		self.setParams("Dest_domain", "")
		self.setParams("Dest_gubun", "US")
		self.setParams("RecvId", rcvID)
		self.setParams("Subject", subject)
		self.setParams("Subject_Encode", "UTF-8")
		self.setParams("Contents", content.replace("\n", "<br>"))
		self.setParams("Contents_Encode", "UTF-8")

		print "type: " + type
		print "sysName: " + sysName
		print "SendID: " + sndID
		print "SendName: " + sndName
		print "RecvID: " + rcvID
		print "Subject: " + subject
		print "Content: " + content

		self.send()
		
if __name__ == "__main__":
	if len(sys.argv) != 5:
		print "Err"
	else:
		uc = UCWare("xxx.xxx.xxx.xxx:12555") 
		uc.Send(sys.argv[0], sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4])