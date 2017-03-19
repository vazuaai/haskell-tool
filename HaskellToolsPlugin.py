#!/usr/bin/python27 

import sublime
import sublime_plugin
import time 

from .client.ClientManager import ClientManager
from .client.ClientManager import get_client_manager

class HaskellToolsPlugin(sublime_plugin.EventListener):

    def on_load(self, view):
        print(view.file_name(), "just got loaded")

    def on_pre_save(self, view):
        print(view.file_name(), "is about to be saved")

    def on_post_save(self, view):
        print(view.file_name(), "just got saved")
        if ClientManager._instance.connected is True:
            ClientManager._instance.reload(view.file_name(), "saved")

    def on_new(self, view):
        print("new file")

    def on_modified(self, view):
        print(view.file_name(), "modified")

    def on_activated(self, view):
        print(view.file_name(), "is now the active view")
        print(get_client_manager().is_server_alive)
        if(get_client_manager().is_server_alive == True):
            view.set_status('serverStatus', "Connected to server " )
        else:
            view.set_status('serverStatus', "Disconnected from server " )


    def on_close(self, view):
        print(view.file_name(), "is no more")
        # if ClientManager._instance.connected is True:
        #     ClientManager._instance.reload(view.file_name(), "removed")

    def on_clone(self, view):
        print(view.file_name(), "just got cloned")

    def on_window_command(self, view, command_name, args):
        print(command_name, "window_command")

    def on_post_window_command(self, window, command_name, args):
        print(command_name, "window_command")       
        
        if command_name == "remove_folder":
            ClientManager._instance.refresh_packages(args, command_name)

    def on_view_command(self, view, command_name, args):
        print(command_name)