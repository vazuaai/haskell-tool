import sublime
import sublime_plugin

from .client.ClientManager import ClientManager
from .client.ClientManager import get_client_manager
    
class UntoggleCommand(sublime_plugin.WindowCommand):

    def run(self, paths=[]):
        get_client_manager().refresh_packages(paths, "untoggle")
        print("UNTOGGLE_COMMAND: ", paths)