import sublime
import sublime_plugin
from .client.ClientManager import get_client_manager

class RenameCommand(sublime_plugin.TextCommand):

	def run(self,edit):
		self.edit = edit
		if(get_client_manager().is_server_alive == True):
			sublime.active_window().show_input_panel("New name: ", "", self.on_done, None, None)
		else: 
			sublime.message_dialog("You need to start haskell tool first!")

	def on_done(self, text):
		get_client_manager().perform_refactoring(self.edit, "RenameDefinition", text)