#!/usr/bin/python27

import sublime
import sublime_plugin
import os
import socket
from threading import Thread
import subprocess
import time

# Definition: 
# This class represents the server, that communicate with client.
#
class ServerManager:

	# Definition:
	# This methods task is to create and start a thread with startserver() method.
	#
	def run(self):		
		thread = Thread(target = self.startserver, args=())
		thread.start()
		print("Server thread started.")

	# Definition:
	# Startserver merthod calls a subprocess that run an exe file that contains the server.
	#
	def startserver(self):
		subprocess.call('"C:\\Users\\Zoli\\AppData\\Roaming\\Sublime Text 3\\Packages\\haskell-tool\\ht-daemon.exe"', shell=False)
