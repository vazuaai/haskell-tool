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
import time

from .server.ServerManager import ServerManager
from .server.ServerManager import get_server_manager

from .client.ClientManager import ClientManager
from .client.ClientManager import get_client_manager

class ServerControllerCommand(sublime_plugin.TextCommand):

	def __init__(self,view):
		super(ServerControllerCommand,self).__init__(view)
		self.server = get_server_manager()
		self.client = get_client_manager()

	def run(self,edit):

		self.server.run()
		self.client.startclient()
		self.client.init_client(edit)
		#time.sleep(3)
		#self.client.keep_alive_server(self.server)

		#self.client.keep_alive()
		#self.add_packages()
		#remove_packages()
		#perform_refactoring()
		#self.stop()
		#self.disconnect()
		#self.reload()

		#self.client.send_message(msg)

	
