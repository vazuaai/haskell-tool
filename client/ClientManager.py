#!/usr/bin/python27  

from __future__ import with_statement
import sublime
import sublime_plugin
import os
import sys
import socket 
import time 
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

			# selection
			self.selection = ""
			self.selection_file_name = ""

			#config
			self.config = {}
			self.config_packages = []
			self.config_file_path = "C:\\Users\\Zoli\\AppData\\Roaming\\Sublime Text 3\\Packages\\haskell-tool\\client\\config"
	
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
				self.connected = True
				break
			except Exception as e:
				time.sleep(0.1)

		thread = Thread(target = self.receive, args=())
		thread.start()
		print("Receive thread started.")

		

	# Definition:
	# It's send a message to the server, if the lock released.
	#
	# @msg the message that we want to send
	#
	def send_message(self, msg):

		with self.lock:

			if msg != b'\n' and msg != b'':
				print("")
				print("SENDED MESSAGE: ", msg)
				print("")
				self.socket.send(msg)
				self.is_alive_counter += 1
			else: 
				print("This message is a ", msg, " we can't send that!")


	# Definition:
	# This method is responsible for catch response messages from the server.
	def receive(self):

		incoming = b''
		list_of_data = []

		while True:

			data = self.socket.recv(1024)	
			if data == b'\n' and data == b'':
				print("This message is a ", data, " we can't send that!")
				continue 
			else:
				incoming += data
				
			list_of_data = incoming.splitlines()

			for i in list_of_data:
				print("")
				print("RECEIVED MESSAGE: ",i)
				print("")
				message = json.loads(i.decode("utf-8"))
				self.is_alive_counter -= 1

				if message.get("tag") == "ErrorMassage":
					error_msg = "Error received: ", message.get("errorMsg")
					sublime.error_message(error_msg)

				else :
					print("Még nem kezeljük ezt a hibát: ", message)
					msg_dialog = "The received message is: " + str(message)
					sublime.message_dialog(msg_dialog)


	# Definition:
	# This method intended to make some steps that necessary for
	# the client, like asks for the opened folders in the project.
	#
	def init_client(self, edit):
		# itt már rögtön elküldjük a szervernek a megnyitott mappákat?
		self.sent_packages = sublime.active_window().folders()
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

			else: 
				time.sleep(1)
				self.keep_alive()


	def keep_alive_server_runner(self, server):
		thread = Thread(target = self.keep_alive_server, args=(server))
		thread.start()


	# with this method we can change the servers path in config
	# TODO: its only changes, but what we could do when the config file doesent contain the path
	#	we should create a flag like: [SERVER_PATH]:
	def set_servers_path(self, path):
		
		self.server_path = path
		self.config['server_path'] = self.server_path
		self.set_config_file()


	def set_toggled_packages(self, package):

		self.config_packages.append(package)
		self.config['packages'] = self.config_packages
		self.set_config_file()

	def remove_untoggled_packages(self, package):

		self.config_packages.remove(package)
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
		config_json = json.loads(config_str)
		value = config_json.get("server_path")

		if( value != None ):
			self.server_path = value

		config_file.close()

	def init_packages_from_config_file(self):
		config_file = open(self.config_file_path, 'r')
		config_str = config_file.read()
		config_json = json.loads(config_str)
		value = config_json.get("packages")

		if( value != None ):
			self.config_packages = value
			
		config_file.close()

	def init_config_file(self):

		try:
			self.init_servers_path_from_config_file()
			self.init_packages_from_config_file()

		except:
			print("Unexpected error while servers path initialization!")
			raise

	# Definition:
	# If the user add a new package to the project or remove one from it
	# the tool cathes these post events. They handled in HaskellToolPlugin.py, 
	# exactly in the on_post_window_command() method. This method triggered 
	# refresh_packages() that check the differencies between the sent_packages
	# and the current_packages. Depending on the event was a remove or add, the
	# client notifies the server.
	#
	# TODO: ide is kell majd az edit!!!
	#
	def refresh_packages(self, paths, command):

		data = {}
		for i in paths:
			i.replace('\\','\\\\')
		
		if(command == "toggle"):	
			data['tag'] = 'AddPackages'
			data['addedPathes'] = paths
			self.set_toggled_packages(paths)

		elif (command == "untoggle"):
			data['tag'] = 'RemovePackages'
			data['removedPathes'] = paths
			self.remove_untoggled_packages(paths)
		
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
		details_array.append(details)

		data = {}
		data['tag'] = 'PerformRefactoring'
		data['refactoring'] = refactoring_type
		data['modulePath'] = path
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

		path = str(path).replace('\\','\\\\')
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

# static method 
def get_client_manager():

	if ClientManager._instance is None:
		ClientManager._instance = ClientManager()

	return ClientManager._instance