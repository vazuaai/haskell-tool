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

	def run(self, msg):

		thread = Thread(target = startclient(msg), args=())
		thread.start()
		print("Client thread started.")

def send_message(msg):
	self.socket.send(msg)

def startclient(msg):

	print("asdsad")

	host = self.socket.gethostname() # A lokál gép nevének lekérése
	port = 4123 # Port foglalása
		#msg = b'{"tag":"KeepAlive","contents":[]}'
				
		#s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)         # Socket object létrehozása		
	self.socket.connect((host, port))

		#send_message(msg, s)

		#s.send(msg)
	data = self.socket.recv(1024)	
	print(json.loads(data.decode("utf-8")).get("errorMsg"))

						
		#s.close()

	return
