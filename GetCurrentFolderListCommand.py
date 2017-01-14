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

class GetCurrentFolderListCommand(sublime_plugin.ApplicationCommand):

	def run(self):
		ClientManager._instance.current_packages = sublime.active_window().folders()
		print("Current folder list:",ClientManager._instance.current_packages)