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

		print("I'm in init")
		if ClientManager._instance is None:

			# client
			ClientManager._instance = self
			self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
			self.connected = False

			# lock
			self.lock = Lock()
			self.lock.acquire()

			# packeges
			self.sent_packages = []
			self.current_packages = []

			# selection
			self.selection = ""
			self.selection_file_name = ""

	
	# Definition:
	# It's defined the host, the port and starts a connection thread.
	# 
	def startclient(self):
		self.host = "127.0.0.1"
		self.port = 4123
		self.is_alive_counter = 0

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
			print("")
			print("SENDED MESSAGE: ", msg)
			print("")
			self.socket.send(msg)
			self.is_alive_counter += 1

	# Definition:
	# This method is responsible for catch response messages from the server.
	#	
	#  ha az egész üzenet space karakterekből áll akkor droppoljuk
	#  ha az uzenet elejét kapjuk meg, akkor eltároljuk, incoming-ba
	# különben felbontjuk new line karakterenként, de előtte hozzáfűzzük az incoming-ot
		# és külön külön a részekre ráhívjuk a 
		# message = json.loads(data.decode("utf-8")) (try-catch-ben)
		# mert egyszerre több üzenet is jöhet 
	def receive(self):

		incoming = b''
		list_of_data = []

		while True:
			data = self.socket.recv(1024)		
			if data == b'\n':
				continue
			else:
				incoming += data
				
			list_of_data = incoming.splitlines()
			incoming = b''

			for i in list_of_data:
				print(i)
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

	# Definition:
	# With this method the client notifies the server that it's still up and running.
	#
	def keep_alive(self):
		message = b'{"tag":"KeepAlive","contents":[]}'
		self.send_message(message)

	def keep_alive_server(self, server):
		
		while True:

			if self.is_alive_counter > 10:
				#server.run()
				print("THE SERVER STARTED")
				self.is_alive_counter = 0
			else: 
				time.sleep(1)
				self.keep_alive()
				#self.is_alive_counter += 1


	def keep_alive_server_runner(self, server):
		thread = Thread(target = self.keep_alive_server, args=(server))
		thread.start()

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
	def refresh_packages(self):

		self.current_packages = sublime.active_window().folders()
		# nagyobb vagy nagyobb egyenlő legyen a vizsgálat?
		if len(self.current_packages) >= len(self.sent_packages):

			# http://stackoverflow.com/questions/6486450/python-compute-list-difference
			self.difference = list(set(self.current_packages) - set(self.sent_packages))

			str_message = '{"tag":"AddPackages","addedPathes":['

			flag = True

			for i in self.difference:
				if flag:
					flag = False

				else:
					str_message += ','

				str_message += i

			str_message += ']}'

			byte_message = str.encode(str_message)
			self.send_message(byte_message)

			# Ez így oké, vagy használjam a list.append()-et? remove-nál (list.remove()) hasonlóképp?
			self.sent_packages = self.current_packages

		elif len(self.current_packages) < len(self.sent_packages):

			self.difference = list(set(self.sent_packages) - set(self.current_packages))

			str_message = '{"tag":"RemovePackages","removedPathes":['

			for i in self.difference:
				i = str(i).replace('\\','\\\\')
				# itt még meg kell oldani, hogy vesszővel írja ki
				str_message += i + ' '

			str_message += ']}'
			byte_message = str.encode(str_message)
			self.send_message(byte_message)

			self.sent_packages = self.current_packages
			print(self.sent_packages)

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
		print("Selected range: ", self.selection)

	def perform_refactoring(self, edit, refactoring_type, details):
		# Egyenlőre annyit csinál, hogy elküldi a kijelölést, a file abs útját
		# és egy beégetett "rename" refaktor type-ot
		self.edit = edit
		self.get_selection()
		path = str(self.selection_file_name).replace('\\','\\\\')

		details_array = []
		details_array.append(details)

		data = {}
		data['tag'] = 'PerformRefactoring'
		data['refactoring'] = refactoring_type
		data['modulePath'] = path
		data['editorSelection'] = self.selection
		data['details'] = details_array
		str_message = json.dumps(data)

		# str_message = '{"tag":"PerformRefactoring","refactoring":"' + refactoring_type + '","modulePath":"' + path + '","editorSelection":"' + self.selection + '","details":['+ details +']}'
		# http://stackoverflow.com/questions/23110383/how-to-dynamically-build-a-json-object-with-python
		# json objectumot csinálni, hogy ne kelljen szövegekkel bajlódni, így kéne megvalósítani
		byte_message = str.encode(str_message)
		self.send_message(byte_message)

	# Definition:
	# If the user press the button represents stop client, the tool send a message
	# about this.
	#
	def stop(self,edit):
		self.edit = edit
		message = b'{"tag":"Stop","contents":[]}'
		self.send_message(message)
		self.socket.close()

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

		if action_tpye == "saved":
			str_message = '{"tag":"ReLoad","changedModules":['	
			str_message += path	+ '], "removedModules":[]}'
			byte_message = str.encode(str_message)
			self.send_message(byte_message)

		elif action_tpye == "removed":
			str_message = '{"tag":"ReLoad","changedModules":[], "removedModules":['		
			str_message += path + ']}'
			byte_message = str.encode(str_message)
			self.send_message(byte_message)

# static method 
def get_client_manager():

	if ClientManager._instance is None:
		ClientManager._instance = ClientManager()

	return ClientManager._instance