#!/usr/bin/python27

import sublime
import sublime_plugin
import os
import socket               # Socket modul importálása
from threading import Thread
import subprocess                                     
import time

class ServerManager:

	def run(self):
		
		thread = Thread(target = startserver, args=())
		thread.start()
		print("Server thread started.")

def startserver():
	subprocess.call('"C:\\Users\\Zoli\\AppData\\Roaming\\Sublime Text 3\\Packages\\haskell-tool\\ht-daemon.exe"', shell=False)

