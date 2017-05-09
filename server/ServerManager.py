import sublime
import subprocess

from threading import Thread
from ..client.ClientManager import get_client_manager

class ServerManager:

	_instance = None

	def run(self):	
		thread = Thread(target = self.startserver, args=())
		thread.start()
		print("INFO: SERVER THREAD STARTED.")

	def startserver(self):
		try:
			subprocess.call([get_client_manager().server_path, str(get_client_manager().port), 'True'])

		except OSError:
			if (get_client_manager().server_init_error == False):
				sublime.message_dialog("The the servers path not valid! Please give it below.")
				sublime.active_window().run_command("set_server_path")

def get_server_manager():
	if ServerManager._instance is None:
		ServerManager._instance = ServerManager()
	return ServerManager._instance

def get_a_new_server_manager():
	ServerManager._instance = ServerManager()
	return ServerManager._instance