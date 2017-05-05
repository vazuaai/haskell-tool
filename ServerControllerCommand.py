import sublime_plugin

from .server.ServerManager import get_a_new_server_manager
from .server.ServerManager import get_server_manager

from .client.ClientManager import get_a_new_client_manager
from .client.ClientManager import get_client_manager

class ServerControllerCommand(sublime_plugin.TextCommand):

	def __init__(self,view):
		super(ServerControllerCommand,self).__init__(view)
		self.server = get_server_manager()
		self.client = get_client_manager()

	def run(self, edit):
		if(self.client.is_client_closable):
			print("Client is closable!")
			del self.server
			del self.client
			self.server = get_a_new_server_manager()
			self.client = get_a_new_client_manager()
		print("S: ", self.server)
		print("C: ", self.client)
		self.client.init_config_file()
		self.client.startclient()
		self.server.run()

