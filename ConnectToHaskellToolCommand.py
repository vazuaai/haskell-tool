#!/usr/bin/python35

import sublime
import sublime_plugin
import os
import socket
from threading import Thread
import subprocess                                     
import time
import errno 
import json

from .client.ClientManager import ClientManager
from .client.ClientManager import get_client_manager

class ConnectToHaskellToolCommand(sublime_plugin.TextCommand):

	def __init__(self,view):
		super(ConnectToHaskellToolCommand,self).__init__(view)
		self.client = get_client_manager()

	def run(self,edit):

		#self.client.startclient()
		host = "127.0.0.1"
		port = 4123
		socket2 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		connection = socket2.connect((host, port))
		socket2.send(b'valami')
		data = socket2.recv(1024)		
		message = json.loads(data.decode("utf-8"))
		print(message)


	
