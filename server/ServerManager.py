#!/usr/bin/python27

import sublime
import subprocess
from threading import Thread
from ..client.ClientManager import get_client_manager

class ServerManager:

	_instance = None

	def run(self,path):	
		self.server_path = path	
		thread = Thread(target = self.startserver, args=())
		thread.start()
		print("INFO: Server thread started.")


	def startserver(self):
		try:
			server_path = get_client_manager().server_path
			subprocess.call([server_path, '4123', 'True'])

		except OSError:
			if (get_client_manager().server_init_error == False):
				sublime.message_dialog("The the servers path not valid! Please give below the servers path.")
				sublime.active_window().run_command("set_server_path")


def get_server_manager():
	if ServerManager._instance is None:
		ServerManager._instance = ServerManager()
		
	return ServerManager._instance