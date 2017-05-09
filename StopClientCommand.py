import sublime_plugin

from .client.ClientManager import ClientManager
from .client.ClientManager import get_client_manager

class StopClientCommand(sublime_plugin.WindowCommand):

	def run(self):
		get_client_manager().stop_client()