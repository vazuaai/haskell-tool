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

from .ServerManager import ServerManager
from .ClientManager import ClientManager
from .FoldersCommand import FoldersCommand

class ServerControllerCommand(sublime_plugin.ApplicationCommand):

	def __init__(self):
		self.server = ServerManager()
		self.client = ClientManager()
		self.folder_listing = FoldersCommand

	def run(self):

		# Start server
		self.server.run()

		# Put folder to a list that are listed in the sidebar
		#folders = self.folder_listing.run(self)

		#msg = b'{"tag":"KeepAlive","contents":[]}'
		#start_folders_msg = bytes('\n'.join(map(str, folders)), 'utf-8')

		# Start client
		self.client.run()

