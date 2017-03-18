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

class FloatOutCommand(sublime_plugin.TextCommand):

	def run(self,edit):
		print("FloatOut")
		# self.edit = edit
		# sublime.active_window().show_input_panel("Type here: ", "", self.on_done, None, None)
		

	def on_done(self, text):
		get_client_manager().perform_refactoring(self.edit, "FloatOut", text)