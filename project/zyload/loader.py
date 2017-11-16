import os
from socket import *

from filepart import ZyloadFilepart

class Zyloader:
	'''
	Zyload file uploader/downloader
	'''
	FILEPART_MAXSIZE = 1024
	DEFAULT_LOOKUP_TRY = 5
	FILEHOST_PORT = 5555

	def __init__(self, server=None, drive_path='.zyload'):
		self.drive_path = drive_path
		self.server = server

		self.zyload_files = {} #fileuri-zyloadfile pair

		self.current_lookup = (None, None)
		self.lookup_tries = {}
		self.lookup_result = {} #list of ip with that filepart

		self.tcp_connections = {} #IP-socket pair
		self.streams = {} #fileaddress-ZyloadFilepart pair

	@staticmethod
	def _get_fp_key(uri, idd):
		'''
		get filepart key by combining uri and id,
		used in kamedlia tables
		'''
		return uri+idd

	def is_local(self, file_uri, part_id):
		filepath = os.path.join(self.drive_path, file_uri, part_id + '.zylo')
		return os.path.exists(filepath)

	#=====
	#  File loading
	#=====

	def lookup(self, filepart_address):
		'''
		filepart address is in (file_uri, part_id)
		'''
		if is_local(*filepart_address):
			self.stream[filepart_address] = ZyloadFilepart.from_local()
		else:
			self.current_lookup = (file_uri, part_id)
			self.lookup_tries = DEFAULT_LOOKUP_TRY
			key = self._get_fp_key(file_uri, part_id)
			self.server.get(key).addCallback(self.lookupDone)

	def lookup_retry(self):
		'''
		filepart address is in (file_uri, part_id)
		'''
		key = self._get_fp_key(*self.current_lookup)
		self.server.get(key).addCallback(self.lookupDone)	

	def lookupDone(self, result):
		if result is None:
			# we try a few times 
			self.lookup_tries -= 1
			if self.lookup_tries > 0:
				self.lookup_retry()
			else:
				#not found
				self.current_lookup = (None, None)
		else:
			# found a few IP
			self.lookup_result = result[:]
			self.current_lookup = (None, None)

	def connect_filepart_host(self, ip):
		'''
		Once lookup is done and we know where the filepart is,
		use TCP connection to make a TCP stream that can be
		treated as a file stream
		'''
		host_address = (ip, FILEHOST_PORT)
		if ip in self.tcp_connections:
			sock = self.tcp_connections[ip]
		else:
			sock = socket(AF_INET, SOCK_STREAM)
			self.tcp_connections[ip] = sock
		sock.connect(host_address)

	def load_local_filepart(self, file_uri, part_id):
		'''
		args:
		- file_uri: 16bit file URI
		- part_id: file part identifier
		- data: bytearray to write
		'''
		filepath = os.path.join(self.drive_path, file_uri, part_id + '.zyl')
		return open(filepath. 'rb')

	def request_part(self, zyload_file, part_id):
		uri = zyload_file.file_uri

		if uri not in self.zyload_files:
			self.zyload_files[uri] = zyload_file

		filepart_address = (uri, part_id)
		self.lookup(filepart_address)
		# self.lookup_queue.append(filepart_address)

	def return_request(self, file_uri, part_id, filepart):
		self.zyload_files[file_uri].recv_part(part_id, filepart)


	#====
	#   saving
	#====

	def save_remote_filepart(self, file_uri, part_id, data):
		#should introduce file hashes to prevent merging problem
		pass

	def save_local_filepart(self, file_uri, part_id, data):
		'''
		args:
		- file_uri: 16bit file URI
		- part_id: file part identifier
		- data: bytearray to write
		'''
		filepath = os.path.join(self.drive_path, file_uri, part_id + '.zyl')
		with opem(filepath, 'wb') as f:
			f.write(data)

	#====
	#   Daemon services
	#====
	

	def main(self):
		#1. send ZyloadFile part requests to network

		#1b. return any response to corresponding Zyfile

		#2. listen to request from network

		#2b. open up socketServer for each 
		pass