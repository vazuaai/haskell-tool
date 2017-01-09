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
		self.is_client_alive = False
		self.can_client_send = True
		self.message = ''

	def run(self):
		thread = Thread(target = self.startclient, args=())
		thread.start()
		print("Client thread started.")
		self.is_client_alive = True

	def send_message(self, msg):
		self.socket.send(msg)

	def please_send(self, msg):

		self.can_client_send = True
		self.message = msg

	def startclient(self):

		self.host = "127.0.0.1"
		self.port = 4123

		self.socket.connect((self.host, self.port))

		
		while True:

			#print("In start can send:", self.can_client_send)	
			if self.can_client_send == True:
				self.send_message(self.message)
				data = self.socket.recv(1024)	
				print(json.loads(data.decode("utf-8")).get("errorMsg"))
				self.can_client_send = False


		#msg = b'{"tag":"KeepAlive","contents":[]}'
		#self.send_message(msg)

		#data = self.socket.recv(1024)	
		#print(json.loads(data.decode("utf-8")).get("errorMsg"))

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
