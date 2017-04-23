import sublime
import sublime_plugin
from .client.ClientManager import get_client_manager

class SetServerPathCommand(sublime_plugin.WindowCommand):

	def run(self):
		sublime.active_window().show_input_panel("Please type here the server's path: ", "" ,self.on_done, None, None)	

	def on_done(self, text):
		get_client_manager().set_servers_path(text)