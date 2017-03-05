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

from .client.ClientManager import ClientManager
from .client.ClientManager import get_client_manager

class SetServerPathCommand(sublime_plugin.TextCommand):

	def run(self,edit):
		self.edit = edit
		sublime.active_window().show_input_panel("Please type here the server's path: ", "C:\\Users\\Zoli\\AppData\\Roaming\\Sublime Text 3\\Packages\\haskell-tool\\ht-daemon.exe", self.on_done, None, None)	

	def on_done(self, text):
		get_client_manager().server_path = text