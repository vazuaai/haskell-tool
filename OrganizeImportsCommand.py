#!/usr/bin/python35
import sublime_plugin

from .client.ClientManager import ClientManager
from .client.ClientManager import get_client_manager

class OrganizeImportsCommand(sublime_plugin.TextCommand):

	def run(self,edit):
		get_client_manager().perform_refactoring(edit, "OrganizeImports", None)
