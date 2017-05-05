from __future__ import with_statement
from threading import Thread
from threading import Lock

import sublime
import os
import socket 
import time    
import json 

class ClientManager:

	_instance = None

	def __init__(self):
		# server
		self.server_path = ""
		self.is_server_alive = False
		self.server_init_error = False
		
		# client
		ClientManager._instance = self
		self.host = "127.0.0.1"
		self.port = 4123

		# lock
		self.lock = Lock()
		self.lock.acquire()

		# packeges
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
		self.sb_event_msg_type = ""
		self.sb_event_msg = ""
		self.is_sb_event_active = False;
		sublime.active_window().active_view().set_status('serverStatus', ''.join([self.sb_connection,'disconnected from server']))

		self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.is_client_closable = False

	def startclient(self):
		thread = Thread(target = self.connect, args=())
		thread.start()
		print("INFO: Connect thread started.")


	def connect(self):
		isConnected = False
		while True:
			
			try:
				self.socket.connect((self.host, self.port))
				self.lock.release()
				isConnected = True
				break

			except Exception as e:
				time.sleep(0.1)
				self.status_thread_runner(self.sb_error, "can't make a connection with server")
				print("Receive threads exception: ",e)
				break
			
		self.is_server_alive = True	
		thread = Thread(target = self.receive, args=())
		thread.start()
		print("INFO: Receive thread started.")
		
		sublime.active_window().active_view().set_status('serverStatus', ''.join([self.sb_connection,'connected to server']))
		sublime.active_window().run_command("toggle", {"paths": self.config_packages})
					

	def receive(self):
		list_of_data = []

		while True:
			try:
				data = self.socket.recv(1024)
				#self.is_server_alive = True		
				del list_of_data[:]

				if data == b'\n' or data == b'':
					continue 
				else:
					list_of_data.append(data)
				
				for i in list_of_data:
					message = json.loads(i.decode("utf-8"))
					print("RECEIVED MESSAGE: ", message)

					if message.get("tag") == "ErrorMessage":
						sublime.message_dialog(message.get("errorMsg"))
						self.status_thread_runner(self.sb_error, message.get("errorMsg"))

					elif message.get("tag") == "LoadedModules":
							
						if(message.get("loadedModules") != []):
							self.set_toggled_packages()
							self.status_thread_runner(self.sb_info, 'modules loaded')

					else :
						self.status_thread_runner(self.sb_info, "a message handled, for further info please read the log")
						print("Handled message: ", message)

			except Exception:
				self.is_server_alive = False
				sublime.active_window().active_view().set_status('serverStatus', ''.join([self.sb_connection,'disconnected from server']))
				self.status_thread_runner(self.sb_error, 'connection with server unexpectedly closed')
				self.stop_client_but_server()
				break


	def send_message(self, msg):
		try:
			with self.lock:
				if msg != b'\n' and msg != b'':
					self.socket.send(msg)
					print("SENDED MESSAGE: ", msg)

		except ConnectionResetError:
			self.is_server_alive = False
			self.status_thread_runner(self.sb_error, 'connection with server unexpectedly closed')
			self.stop_client_but_server()			

	def set_servers_path(self, path):
		if(path != ""):
			self.server_path = path
			self.config['server_path'] = self.server_path
			self.set_config_file()
		else:
			sublime.message_dialog("Empty path value is not valid.")


	def set_toggled_packages(self):
		for i in self.sent_package_paths:
			if(not(i in self.config_packages)):
				self.config_packages.append(i)
		
		self.config['packages'] = self.config_packages
		self.set_config_file()


	def remove_untoggled_packages(self, package):
		is_sendable = True
		for item in package:
			try:
				self.config_packages.remove(item)
			except ValueError as ve:
				is_sendable = False
				sublime.message_dialog("This file was not toggled before!")
			
		if(is_sendable):
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
		else:
			self.server_init_error = True
			sublime.message_dialog("The servers path is not given yet! Please give it below.")
			sublime.active_window().run_command("set_server_path")
		
		config_file.close()


	def init_packages_from_config_file(self):
		config_file = open(self.config_file_path, 'r')
		config_str = config_file.read()
		try:
			config_json = json.loads(config_str)
			value = config_json.get("packages")
			if( (value != None) and (len(value) != 0)):
				self.config_packages = value
			else: 
				self.status_thread_runner(self.sb_error, "there isn't any packages to initialize")
		except ValueError:
			self.status_thread_runner(self.sb_error, "there isn't any packages to initialize")
		
		config_file.close()
		

	def init_config_file(self):
		try:
			self.init_servers_path_from_config_file()
			self.init_packages_from_config_file()
		except Exception as exc:
			self.status_thread_runner(self.sb_error, "unexpected error while config file initialization")
			print("Exception thrown at config file initialization: ", exc)


	def encode_and_send(self, data):
		str_message = json.dumps(data)
		byte_message = str.encode(str_message)
		self.send_message(byte_message)


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
				is_sendable = True
				data['tag'] = 'RemovePackages'
				data['removedPathes'] = paths
				self.remove_untoggled_packages(paths)
			
			if is_sendable:
				self.encode_and_send(data)


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

		if(self.is_server_alive):
			
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
			self.encode_and_send(data)

		else:
			sublime.message_dialog("You need to start haskell tool first!")
			

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
		self.encode_and_send(data)


	def show_status(self, msg_type, msg):
		self.set_status_bar()
		time.sleep(5)
		self.erase_status_bar()
		
	def set_status_bar(self):
		sublime.active_window().active_view().set_status(self.sb_event_msg_type, self.sb_event_msg)
		self.is_sb_event_active = True

	def erase_status_bar(self):
		sublime.active_window().active_view().erase_status(self.sb_event_msg_type)
		self.is_sb_event_active = False

	def status_thread_runner(self, msg_type, msg):
		self.sb_event_msg_type = msg_type
		self.sb_event_msg = ''.join([ msg_type, msg])

		thread = Thread(target = self.show_status, args=(msg_type, msg))
		thread.start()

	def stop_client(self):
		if(self.is_server_alive):	
			data = {}
			contents_array = []
			data['tag'] = 'Stop'
			data['contents'] = contents_array
			self.encode_and_send(data)
			self.close_socket()
			self.kill_server()
			self.erase_status_bar()
			self.is_client_closable = True
		else:
			sublime.message_dialog("You need to start the tool before you want to stop!")

	def stop_client_but_server(self):
		data = {}
		contents_array = []
		data['tag'] = 'Stop'
		data['contents'] = contents_array
		self.encode_and_send(data)
		self.close_socket()
		self.erase_status_bar()
		self.is_client_closable = True

	def close_socket(self):
		print("SOCKET BEFORE CLOSE: ",self.socket)
		self.socket.close()
		

	def kill_server(self):
		self.is_server_alive = False
		kill_command = 'TASKKILL /F /IM ' + self.server_path
		os.system(kill_command)

def get_client_manager():
	if ClientManager._instance is None:
		ClientManager._instance = ClientManager()
	return ClientManager._instance

def get_a_new_client_manager():
	ClientManager._instance = ClientManager()
	return ClientManager._instance