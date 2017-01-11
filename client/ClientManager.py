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
		folderlist = sublime.active_window().folders()

		print("\nThe opened folders on the sidebar: " )

		for i in folderlist:
			add_package(self, i)
			#print(i)

	#def add_package(self, path):
	#	print(path)

	def set_event_listeners(self):
		on_modified()

	def keep_alive(self):
		message = b'{"tag":"KeepAlive","contents":[]}'
		self.send_message(message)

	def refresh_packages(self):
		## kommenteket gyártani
		# Csak azokat a packageket küldje el amiket még nem küldött el,
		# le kell tárolni a már elküldött listákat, az initben kapottakat is ugyanabba
		# az egész lényege hogy szinkronban legyen a szerver és kliens
		# ha olyan event jön ami kiváltja ezt a függvényt akkor attól függően h lett új vagy töröltek packaget, kell küldeni a refresh vagy remove packages üzenetet
		# Boldizsár emailje tartalmazza hogy hogy kell packaget belerakni a projektbe annak a post eventjét kell elkapni
		# init fv beolvassa a mappákat | ha jött új mappa (Project/Add package..) akkor annak post eventjét elkapom, lekérem az összes foldert összehasonlítom az inittel és elküldöm az új mappa nevét | törlésnél ugyanígy | az alap mappa lista amihez hasonlítok mindig frissül!!!
		# fontos a \ legyen \\ mindenhol
		folders = sublime.active_window().folders()
		str_message = '{"tag":"AddPackages","addedPathes":['

		for i in folders:
			str_message += i + ','

		str_message += ']}'
		byte_message = str.encode(str_message)
		self.send_message(byte_message)

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

	def stop(self):
		# ha megnyomtuk a stopot
		message = b'{"tag":"Stop","contents":[]}'
		self.client.please_send(message)

	def reload(self):
		# ha valaki save-et nyom
		# ha valaki töröl akkor is csak akkor removedModules
		message = b'{"tag":"ReLoad","changedModules":[<pathes>], "removedModules":[<pathes>]}'
		self.send_message(message)