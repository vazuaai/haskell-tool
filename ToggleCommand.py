import sublime
import sublime_plugin
import os

from .client.ClientManager import get_client_manager

class ToggleCommand(sublime_plugin.WindowCommand):

	def run(self, paths=[]):

		is_sendable = False

		for item in paths:
			if(os.path.isdir(item) != True):
				sublime.message_dialog("You can toggle only directories!")
			else:
				is_sendable = True

		if (is_sendable == True):
			get_client_manager().refresh_packages(paths, "toggle")