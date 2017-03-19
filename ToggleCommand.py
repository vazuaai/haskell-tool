import sublime
import sublime_plugin
import os

from .client.ClientManager import ClientManager
from .client.ClientManager import get_client_manager

class ToggleCommand(sublime_plugin.WindowCommand):

	def run(self, paths=[]):

		# több foldert is kaphat a togglecommand
		self.files = []

		for folder in paths:
			print("ROOTDIR: ", folder)
			self.files.append(folder)
			for subdir, dirs, files in os.walk(folder):
				for file in files:
					print("SUBDIRS, FILES: ", os.path.join(subdir, file))
					self.files.append(os.path.join(os.path.join(subdir, file)))
					
		get_client_manager().refresh_packages(self.files, "toggle")
