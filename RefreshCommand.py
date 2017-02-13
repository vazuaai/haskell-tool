import sublime
import sublime_plugin

from .client.ClientManager import ClientManager
from .client.ClientManager import get_client_manager
    
class RefreshCommand(sublime_plugin.WindowCommand):

    def run(self, paths=[]):
        get_client_manager().refresh_packages()
        print("TOGGLE_COMMAND: ", paths)