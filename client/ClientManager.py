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
from threading import Thread
from threading import Lock

class ClientManager:

	_instance = None

	def __init__(self):

		print("I'm in init")
		if ClientManager._instance is None:
			ClientManager._instance = self
			self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
			self.is_client_alive = False
			self.lock = Lock()
			self.lock.acquire()
			# packeges
			self.sent_packages = []
			self.current_packages = []

	def connect(self):

		while True:
			try:
				self.connection = self.socket.connect((self.host, self.port))
				self.lock.release()
				break
			except Exception as e:
				time.sleep(0.1)

		thread = Thread(target = self.receive, args=())
		thread.start()
		print("Receive thread started.")

	def send_message(self, msg):
		with self.lock:
			self.socket.send(msg)

	def receive(self):
		while True:
			data = self.socket.recv(1024)		
			message = json.loads(data.decode("utf-8"))

			if message.get("tag") == "ErrorMassage":
				print("Egy error érkezett: ", message.get("errorMsg"))
			else :
				print("Még nem kezeljük ezt a hibát: ", message)

	def startclient(self):

		self.host = "127.0.0.1"
		self.port = 4123

		thread = Thread(target = self.connect, args=())
		thread.start()
		print("Connect thread started.")

	def init_client(self):
		# itt már rögtön elküldjük a szervernek a megnyitott mappákat?
		self.sent_packages = sublime.active_window().folders()

		print(self.sent_packages)

	def set_event_listeners(self):
		on_modified()

	def keep_alive(self):
		message = b'{"tag":"KeepAlive","contents":[]}'
		self.send_message(message)

	def refresh_packages(self):

		self.current_packages = sublime.active_window().folders()
		print("Current packages: ",self.current_packages)
		print("Sent packages: ",self.sent_packages)

		# nagyobb vagy nagyobb egyenlő legyen a vizsgálat?
		if len(self.current_packages) >= len(self.sent_packages):
			# http://stackoverflow.com/questions/6486450/python-compute-list-difference
			self.difference = list(set(self.current_packages) - set(self.sent_packages))
			print("Difference: ", self.difference)

			str_message = '{"tag":"AddPackages","addedPathes":['

			for i in self.difference:
				str_message += i + ','
				str_message += ']}'

			byte_message = str.encode(str_message)
			self.send_message(byte_message)

			# Ez így oké, vagy használjam a list.append()-et? remove-nál hasonlóképp?
			self.sent_packages = self.current_packages

		elif len(self.current_packages) < len(self.sent_packages):

			self.difference = list(set(self.sent_packages) - set(self.current_packages))
			print("Difference: ", self.difference)

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

	def perform_refactoring(self, refactoring_type):
		# a haskell tools főaoldal kint vannak h milyen típusok vannak
		# RenameDefinition src-range new-name
		# Menu / Tools / Haskell Tools / Start / Stop
		#							   / pl. rename
		# <refactor-name> = pl. Rename
		# modulpath: annak a filenek az abs elérése amiben a kijelölés van
		# details: lehetséges adatok a refaktoráláshoz
		message = b'{"tag":"PerformRefactoring","refactoring":<refactor-name>,"modulePath":<selected-module>,"editorSelection":<selected-range>,"details":[<refactoring-specific-data>]}'
		self.send_message(message)

	def stop(self, path):
		# ha megnyomtuk a stopot
		message = b'{"tag":"Stop","contents":[]}'
		self.send_message(message)
		self.socket.close()

	def reload(self, path, action_tpye):
		# ha valaki save-et nyo (just got saved)
		# ha valaki töröl akkor is csak akkor removedModules (modified)

		path = str(path).replace('\\','\\\\')

		if action_tpye == "modified":

			str_message = '{"tag":"ReLoad","changedModules":['	
			str_message += path	+ '], "removedModules":[]}'
			byte_message = str.encode(str_message)
			self.send_message(byte_message)

		elif action_tpye == "removed":
			str_message = '{"tag":"ReLoad","changedModules":[], "removedModules":['		
			str_message += path + ']}'
			byte_message = str.encode(str_message)
			self.send_message(byte_message)