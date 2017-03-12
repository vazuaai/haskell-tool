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
		
		self.client.init_client(edit)
		self.server.run(get_client_manager().server_path)
		self.client.startclient()
		
	
