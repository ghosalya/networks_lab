import os
from socket import *

from filepart import ZyloadFilepart

class Zyloader:
	'''
	Zyload file uploader/downloader
	'''
	FILEPART_MAXSIZE = 1024
	
	FILEHOST_PORT = 5555

	def __init__(self, server=None, drive_path='.zyload'):
		self.drive_path = drive_path
		self.server = server
		self.zyload_files = {} #fileuri-zyloadfile pair
		self.requests = {} #fileadress-zyloadrequest pair


	@staticmethod
	def _get_fp_key(uri, idd):
		'''
		get filepart key by combining uri and id,
		used in kamedlia tables
		'''
		return uri+idd

	#=====
	#  File loading
	#=====	

	def request_part(self, zyload_file, part_id):
		uri = zyload_file.file_uri
		request = ZyloadRequest(self, zyload_file)

		if uri not in self.zyload_files:
			self.zyload_files[uri] = zyload_file

		filepart_address = (uri, part_id)
		self.lookup(filepart_address)

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
		#1. listen to request from network

		#1b. open up socketServer for each 
		pass


from enum import Enum

class ZyloadRequest:

	DEFAULT_LOOKUP_TRY = 5

	#Request Status

	class ReqStatus(Enum):
		IDLE = "IDLE"
		SUCCESS = "SUCCESS"
		REQUESTING = "REQUESTING kademlia key"
		LOADING = "LOADING stream/file"
		RETRYING = "RETRYING request"
		FAILED = "FAILED"

	def __init__(self, loader, zyload_file):
		self.zyload_file = zyload_file
		self.loader = loader
		self.file_uri = zyload_file.file_uri
		self.part_id = zyload_file.part_id
		self.server = self.loader.server

		self.lookup_tries = ZyloadRequest.DEFAULT_LOOKUP_TRY
		self.lookup_result = []
		self.stream = None
		self.status = ReqStatus.IDLE

	def is_local(self):
		filepath = os.path.join(self.loader.drive_path, 
								self.file_uri, self.part_id + '.zyl')
		return os.path.exists(filepath)

	def _get_fp_key(self):
		return self.loader._get_fp_key(self.file_uri, self.part_id)

	def lookup(self):
		'''
		filepart address is in (file_uri, part_id)
		'''
		if self.is_local():
			self.stream = ZyloadFilepart\
						  .from_local(self.load_local_filepart())
			self.status = ReqStatus.SUCCESS
			self.zyload_file.recv_part(self.part_id,
									   ZyloadFilepart.from_local((self.file_uri,
									   							  self.part_id),
									   							 self.stream))
		else:
			self.current_lookup = (file_uri, part_id)
			self.lookup_tries = DEFAULT_LOOKUP_TRY
			key = self._get_fp_key()
			self.status = ReqStatus.REQUESTING
			self.server.get(key).addCallback(self.lookupDone)

	def lookup_retry(self):
		'''
		filepart address is in (file_uri, part_id)
		'''
		self.status = ReqStatus.RETRYING
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
				self.status = ReqStatus.FAILED
		else:
			# found a few IP
			self.lookup_result = result[:]
			self.status = ReqStatus.LOADING

	def get_remote_filestream(self):
		if len(self.lookup_result) > 0:
			ip = self.lookup_result.pop()
			try:
				self.stream = self.connect_filepart_host(ip)
				self.status = ReqStatus.SUCCESS
				self.zyload_file.recv_part(self.part_id,
										   ZyloadFilepart.from_socket((self.file_uri,
										   	                           self.part_id),
										                              self.stream))
			except:
				self.get_remote_filestream()
		else:
			self.status = ReqStatus.FAILED

	def load_local_filestream(self):
		'''
		args:
		- file_uri: 16bit file URI
		- part_id: file part identifier
		- data: bytearray to write
		'''
		filepath = os.path.join(self.loader.drive_path, 
								self.file_uri, self.part_id + '.zyl')
		return open(filepath. 'rb')

	def connect_filepart_host(self, ip):
		'''
		Once lookup is done and we know where the filepart is,
		use TCP connection to make a TCP stream that can be
		treated as a file stream
		'''
		host_address = (ip, Zyloader.FILEHOST_PORT)
		sock = socket(AF_INET, SOCK_STREAM)
		sock.connect(host_address)
		return sock