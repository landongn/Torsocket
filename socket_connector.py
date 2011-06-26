#!/usr/local/bin/python2.7

import tornado.ioloop
import tornado.httpclient
import socket
import tornado.iostream
import re
import commands
import pymongo
import tornado.web
import cjson
import subprocess
import sys
import shlex
		
class TornadoSocketClient(object):
	def __init__(self, nick, ioloop = None):
		##identify the connection
		self.nick = nick
		
		self.ip = '192.168.1.1'
		self.port = 8000
		
		##set up the IOLoop to use, or create a new one. 
		self.io_loop = ioloop or tornado.ioloop.IOLoop.instance()
		
		##handlers are objects that perform actions from the socket. It's the internal conduit to the rest
		## of the system.  They should be defined below. 
		self.handlers = {}
		
		##modules are objects that perform client side actions when received by the socket message. 
		self.modules = []
		
	def start(self):
		s = socket.socket(socket.AF_INET, socket.SOCK_STREAM, 0) ##the magic that connects up the ioLoop to the socket
		s.connect((self.ip, self.port))
		self.stream = tornado.iostream.IOStream(s)
		self.readLine(self.parseLine)
		self.stream.set_close_callback(self.terminate_connection)

	def terminate_connection(self):
		"""useful if you want to do stuff when the connection drops. """
		pass
		
	def readLine(self, callback):
		"""define your terminator, and the callback"""
		self.stream.read_until("\0", callback)
		
	def write(self, msg):
		"""write a message to the stream, along with the terminator"""
		self.stream.write("%s\0" % msg)
		
	def parseLine(self, data):
		"""parse line from the socket and process. 
		Be sure to call self.readLine(self.parseLine) after you process this line."""
		data = data.strip()
		m = data ##cleanup 
		self.write(data)
		self.readLine(self.parseLine)

	def load(self, module):
		try:
			m = module(self)
			self.modules.append(m)
		except Exception, err:
			print "Error loading module"
			print err
		
	def ExecuteCommand(self, client, cmd):
		
		if not client in self.handlers.keys():
			self.handlers[client] = {}
			
		if not cmd in self.handlers[client].keys():
			self.handlers[client][cmd] = []
			
		if cmd in self.handlers[client]:
			for cb in self.handlers['commands'][cmd]:
				cb(channel, cmd)
		
	def addCommand(self, command, callback):
		if command not in self.handlers['commands']:
			self.handlers['commands'][command] = []
		self.handlers['commands'][command].append(callback)
		
class CmdModule():
	def __init__(self, connection):
		self.connection = connection
		
		

a = tornado.ioloop.IOLoop.instance()
c = TornadoSocketClient('meeps', a)
#c.load(CmdModule)
c.start()
a.start()
