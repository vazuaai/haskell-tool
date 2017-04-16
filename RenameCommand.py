import sublime
import sublime_plugin
from .client.ClientManager import get_client_manager

class RenameCommand(sublime_plugin.TextCommand):

	def run(self,edit):
		self.edit = edit
		sublime.active_window().show_input_panel("Type here: ", "", self.on_done, None, None)
		

	def on_done(self, text):
		get_client_manager().perform_refactoring(self.edit, "RenameDefinition", text)