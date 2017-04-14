#!/usr/bin/python27  

from __future__ import with_statement
import sublime
import sublime_plugin
import os
import sys
import socket 
import time 
import datetime
import errno      
import json 
import re
from threading import Thread
from threading import Lock

# Definition: 
# This class represents the client that commuicate with server.
#
class ClientManager:

	_instance = None

	# Definition:
	# This method is the constructor of the client.
	#
	def __init__(self):

		if ClientManager._instance is None:

			# server
			self.server_path = ""
			self.is_server_alive = False
			self.server_init_error = False
			
			# client
			ClientManager._instance = self
			self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
			self.connected = False
			self.is_alive_counter = 0

			# lock
			self.lock = Lock()
			self.lock.acquire()

			# packeges
			self.sent_packages = []
			self.current_packages = []
			self.sent_package_paths = ""

			# selection
			self.selection = ""
			self.selection_file_name = ""

			#config
			self.config = {}
			self.config_packages = []
			self.config_file_path = os.path.dirname(__file__) + "\\config"

			#status bar
			self.sb_connection = "Connection: "
			self.sb_info = "Info: "
			self.sb_error = "Error message: "
			sublime.active_window().active_view().set_status('serverStatus', ''.join([self.sb_connection,'disconnected from server']))

	# Definition:
	# It's defined the host, the port and starts a connection thread.
	# 
	def startclient(self):
		self.host = "127.0.0.1"
		self.port = 4123

		thread = Thread(target = self.connect, args=())
		thread.start()
		print("Connect thread started.")

	# Definition:
	# 
	# This methods task is connecting to the server and start a thread with receive() method.
	# After connection the lock released and the tool can send messages after that.
	#
	def connect(self):
		
		while True:

			try:
				self.connection = self.socket.connect((self.host, self.port))
				self.lock.release()
				break

			except Exception as e:
				self.status_thread_runner(self.sb_error, "can't make a connection with server")
				print("Receive threads exception: ",e)
				time.sleep(0.1)

		thread = Thread(target = self.receive, args=())
		thread.start()

		print("Receive thread started.")

		self.connected = True
		self.is_server_alive = True
		sublime.active_window().active_view().set_status('serverStatus', ''.join([self.sb_connection,'connected to server']))
		sublime.active_window().run_command("toggle", {"paths": self.config_packages})

	# Definition:
	# This method is responsible for catch response messages from the server.
	def receive(self):

		incoming = b''
		list_of_data = []

		while True:
			
			try:
				data = self.socket.recv(1024)
				self.is_server_alive = True		
				del list_of_data[:]

				if data == b'\n' or data == b'':
					continue 
				else:
					list_of_data.append(data)
				
				for i in list_of_data:
					
					message = json.loads(i.decode("utf-8"))
					self.is_alive_counter -= 1
					print("RECEIVED MESSAGE: ", message)

					if message.get("tag") == "ErrorMessage":
						self.status_thread_runner(self.sb_error, message.get("errorMsg"))
						
					elif message.get("tag") == "LoadedModules":
						self.status_thread_runner(self.sb_info, 'modules loaded')
						
						if(message.get("loadedModules") != []):
							self.set_toggled_packages()

					else :
						self.status_thread_runner(self.sb_info, "received message")
						
			except ConnectionResetError:
				self.is_server_alive = False
				self.status_thread_runner(self.sb_error, 'connection with server unexpectedly closed')
				break

	# Definition:
	# It's send a message to the server, if the lock released.
	#
	# @msg the message that we want to send
	#
	def send_message(self, msg):

		try:

			with self.lock:

				if msg != b'\n' and msg != b'':
					self.socket.send(msg)
					self.is_alive_counter += 1
					print("SENDED MESSAGE: ", msg)

		except ConnectionResetError:
			self.is_server_alive = False
			self.status_thread_runner(self.sb_error, 'connection with server unexpectedly closed')
			
	# Definition:
	# This method intended to make some steps that necessary for
	# the client, like asks for the opened folders in the project.
	#
	def init_client(self, edit):
		self.edit = edit
		self.init_config_file()
		

	# Definition:
	# With this method the client notifies the server that it's still up and running.
	#
	def keep_alive(self):
		data = {}
		contents_array = []
		
		data['tag'] = 'KeepAlive'
		data['contents'] = contents_array

		str_message = json.dumps(data)
		byte_message = str.encode(str_message)
		self.send_message(byte_message)

	def keep_alive_server(self, server):
		
		while True:

			if self.is_alive_counter > 10:
				server.run()
				self.is_alive_counter = 0
				self.is_server_alive = True

			else: 
				time.sleep(1)
				self.keep_alive()
				self.is_server_alive = False


	def keep_alive_server_runner(self, server):
		thread = Thread(target = self.keep_alive_server, args=(server))
		thread.start()


	# with this method we can change the servers path in config
	def set_servers_path(self, path):

		self.server_path = path
		self.config['server_path'] = self.server_path
		self.set_config_file()


	def set_toggled_packages(self):

		for i in self.sent_package_paths:
			if(not(i in self.config_packages)):
				self.config_packages.append(i)
		
		self.config['packages'] = self.config_packages
		self.set_config_file()


	def remove_untoggled_packages(self, package):

		for item in package:
			print("UT: ", item)
			self.config_packages.remove(item)
			
		self.config['packages'] = self.config_packages
		self.set_config_file()


	def set_config_file(self):
		
		open(self.config_file_path,'w').close
		self.config['server_path'] = self.server_path
		self.config['packages'] = self.config_packages
		config_str = json.dumps(self.config)

		with open(self.config_file_path, 'w') as config_file:
			config_file.write(config_str)
		config_file.close()


	def init_servers_path_from_config_file(self):

		config_file = open(self.config_file_path, 'r')
		config_str = config_file.read()
		try:
			config_json = json.loads(config_str)
			value = config_json.get("server_path")

			if( value != None ):
				self.server_path = value

		except ValueError:
			self.server_init_error = True
			sublime.message_dialog("The the servers path is not given yet! Please give it below.")
			sublime.active_window().run_command("set_server_path")
			config_file.close()


	def init_packages_from_config_file(self):
		
		config_file = open(self.config_file_path, 'r')
		config_str = config_file.read()
		try:
			config_json = json.loads(config_str)
			value = config_json.get("packages")
			
			if( value != None ):
				self.config_packages = value

		except ValueError:
			self.status_thread_runner(self.sb_error, "there isn't any packages to initialize")
			config_file.close()
		

	def init_config_file(self):

		try:
			self.init_servers_path_from_config_file()
			self.init_packages_from_config_file()
			
		except:
			self.status_thread_runner(self.sb_error, "unexpected error while servers path initialization")
			raise

	# Definition:
	# If the user add a new package to the project or remove one from it
	# the tool cathes these post events. They handled in HaskellToolPlugin.py, 
	# exactly in the on_post_window_command() method. This method triggered 
	# refresh_packages() that check the differencies between the sent_packages
	# and the current_packages. Depending on the event was a remove or add, the
	# client notifies the server.
	#
	#
	def refresh_packages(self, paths, command):

		if(self.is_server_alive == True):
			
			data = {}
			is_sendable = False
			if((command == "toggle")):
				is_sendable = True	
				data['tag'] = 'AddPackages'
				data['addedPathes'] = paths
				self.sent_package_paths = paths

			elif (command == "untoggle"):
				print("In remove")
				is_sendable = True
				data['tag'] = 'RemovePackages'
				data['removedPathes'] = paths
				self.remove_untoggled_packages(paths)
			
			if is_sendable:
				str_message = json.dumps(data)
				byte_message = str.encode(str_message)
				self.send_message(byte_message)


	# Definition:
	# 
	def get_selection(self):

		view = sublime.active_window().active_view()

		row_begin, col_begin = view.rowcol(view.sel()[0].begin())
		row_end, col_end = view.rowcol(view.sel()[0].end())

		row_begin += 1
		col_begin += 1
		row_end += 1
		col_end += 1

		self.selection = str(row_begin) + ":" + str(col_begin) + "-" + str(row_end) + ":" + str(col_end)
		self.selection_file_name = view.file_name()


	def perform_refactoring(self, edit, refactoring_type, details):

		self.edit = edit
		self.get_selection()
		path = str(self.selection_file_name)
		details_array = []
		if details != None:
			details_array.append(details)

		data = {}
		data['tag'] = 'PerformRefactoring'
		data['refactoring'] = refactoring_type
		data['modulePath'] = path

		if(refactoring_type == "OrganizeImports" or refactoring_type == "GenerateExports"):
			data['editorSelection'] = ""
		else:
			data['editorSelection'] = self.selection
			
		data['details'] = details_array
		str_message = json.dumps(data)

		byte_message = str.encode(str_message)
		self.send_message(byte_message)

	# Definition:
	# If the user press the button represents stop client, the tool send a message
	# about this.
	#
	def stop(self,edit):

		data = {}
		contents_array = []
		
		data['tag'] = 'Stop'
		data['contents'] = contents_array

		str_message = json.dumps(data)
		byte_message = str.encode(str_message)
		self.send_message(byte_message)

	# Definition:
	# If the user modifies (save or delete file) a file, the tool catches the post 
	# event and send a message to the server depending on the type of action.
	#
	# @path is the absolute path of the file which modified 
	# @action_type can be "saved" or "removed"
	# 
	# The triggers of the reload() method is in the HaskellToolPlugin.py
	# The exact methods that listen the events and trigger the reload() are 
	# on_post_save() and on_close(self, view).
	#
	# Comment: kell majd itt az edit a paraméter listába erre még visszatérünk
	#
	def reload(self, path, action_tpye):

		changed_modules_array = []
		removed_modules_array = []
		data = {}

		if action_tpye == "saved":
			changed_modules_array.append(path)

		elif action_tpye == "removed":
			removed_modules_array.append(path)

		data['tag'] = 'ReLoad'
		data['changedModules'] = changed_modules_array
		data['removedModules'] = removed_modules_array
		str_message = json.dumps(data)
		byte_message = str.encode(str_message)
		self.send_message(byte_message)

	#TODO: definition
	def show_status(self, msg_type, msg):
		sublime.active_window().active_view().set_status(msg_type, ''.join([ msg_type, msg]))
		time.sleep(5)
		sublime.active_window().active_view().erase_status(msg_type)
		
	def status_thread_runner(self, msg_type, msg):
		thread = Thread(target = self.show_status, args=(msg_type, msg))
		thread.start()

# static method 
def get_client_manager():

	if ClientManager._instance is None:
		ClientManager._instance = ClientManager()

	return ClientManager._instance