import sublime
import sublime_plugin
import os

from .client.ClientManager import ClientManager
from .client.ClientManager import get_client_manager

class ToggleCommand(sublime_plugin.WindowCommand):

	def run(self, paths=[]):

		for item in paths:

			if(os.path.isdir(item) != True):
				sublime.message_dialog("You can toggle only directories!")

			else:
				get_client_manager().refresh_packages(paths, "toggle")