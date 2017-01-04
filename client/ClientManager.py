#!/usr/bin/python27  

import sublime
import sublime_plugin
import os
import sys
import socket 
import time 
import errno      
import json 
from threading import Thread     

class ClientManager:

	def __init__(self):
		self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

	def run(self):
		thread = Thread(target = self.startclient, args=())
		thread.start()
		print("Client thread started.")

	def send_message(self, msg):
		self.socket.send(msg)

	def startclient(self):
		print("asdsad")
		self.host = "127.0.0.1"
		self.port = 4123
		#msg = b'{"tag":"KeepAlive","contents":[]}'
					
		#s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)	
		self.socket.connect((self.host, self.port))

		#send_message(msg, s)

		#s.send(msg)
		data = self.socket.recv(1024)	
		print(json.loads(data.decode("utf-8")).get("errorMsg"))
							
		#s.close()

		return

	def init_client(self):
		folderlist = sublime.active_window().folders()

		print("\nThe opened folders on the sidebar: " )

		for i in folderlist:
			add_package(self, i)
			#print(i)

	def add_package(self, path):
		print(path)

	def set_event_listeners(self):
		on_modified()
