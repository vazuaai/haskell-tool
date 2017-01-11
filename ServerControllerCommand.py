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
from .client.ClientManager import ClientManager
from .FoldersCommand import FoldersCommand



class ServerControllerCommand(sublime_plugin.ApplicationCommand):

	def __init__(self):
		self.server = ServerManager()
		self.client = ClientManager()
		self.folder_listing = FoldersCommand

	def run(self):

		self.server.run()

		self.client.startclient()

		#self.client.init_client()
		self.client.keep_alive()
		#self.add_packages()
		#remove_packages()
		#perform_refactoring()
		#self.stop()
		#self.disconnect()
		#self.reload()

		#self.client.send_message(msg)

	
