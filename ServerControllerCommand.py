import sublime_plugin

from .server.ServerManager import get_server_manager
from .client.ClientManager import get_client_manager

class ServerControllerCommand(sublime_plugin.TextCommand):

	def __init__(self,view):
		super(ServerControllerCommand,self).__init__(view)
		self.server = get_server_manager()
		self.client = get_client_manager()

	def run(self, edit):
		self.client.init_config_file()
		self.server.run()
		self.client.startclient()
	
