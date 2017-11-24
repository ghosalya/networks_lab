import os, hashlib, random
from socket import *
from threading import Thread, Semaphore

from filepart import ZyloadFilepart


FILEPART_MAXSIZE = 1024
FILEHOST_PORT = 7171
DEFAULT_LOOKUP_TRY = 5

class Zyloader:
	'''
	Zyload file uploader/downloader
	'''

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
		return uri+str(idd)

	#=====
	#  File loading
	#=====	

	def request_part(self, zyload_file, part_id):
		uri = zyload_file.file_uri
		request = ZyloadRequest(self, zyload_file, part_id)

		if uri not in self.zyload_files:
			self.zyload_files[uri] = zyload_file

		request.start()
		return request

	#====
	#   saving
	#====

	def upload_local_file(self, fileobject, filename):
		# since server is yet to be here,
		# we split files and store as value
		filedata = fileobject.read()
		ips = self.server.bootstrappableNeighbors()

		strings = []
		file_uri = hashlib.md5(filedata.encode()).hexdigest()
		# length = len(filedata)/len(ips)
		length = FILEPART_MAXSIZE
		print('IPS found: {}'.format(ips))

		while len(filedata) > 0:
			strings.append(filedata[0:length])
			filedata = filedata[length:]

		for i in range(len(strings)):
			key = Zyloader._get_fp_key(file_uri, str(i))

			chosen_machine = random.choice(ips)

			# self.server.set(key, strings[i]).addCallback(self.printSet, file_uri, i)
			self.save_remote_filepart(file_uri, str(i), strings[i], chosen_machine[0])
			self.server.set(key, chosen_machine[0])\
					   .addCallback(self.printSet, file_uri, i, chosen_machine[0])
			# 
			# -- store on all machine
		with open(filename + '.zylo', 'w') as zylo:
			zylo.write(file_uri +'\n'+str(len(strings)))
			zylo.close()

	def printSet(self, result, file_uri, part_id, target):
		print "{};{} - set {} in {}"\
			  .format(file_uri, part_id, result, target)

	def save_remote_filepart(self, file_uri, part_id, data, host):
		s = socket(AF_INET, SOCK_STREAM)
		print host, 7171
		s.connect((host, 7171)) #TCP port

		# 1. send indicator packet

		indi_packet = "[file-sending][{}][{}]".format(file_uri, part_id)

		while True:	
			s.sendall(indi_packet)
			response = s.recv(1024)
			if response == "[mode_corrupted]":
				continue
			elif response == "[mode_accepted:{}]".format(indi_packet):
				break

		# 2. start sending
		
		datta = list(data + "[end]")
		current_packet = datta[:FILEPART_MAXSIZE]
		del datta[:FILEPART_MAXSIZE]

		while True:
			s.sendall(''.join(current_packet))
			response = s.recv(1024)
			if response == "accepted":
				current_packet = datta[:FILEPART_MAXSIZE]
				del datta[:FILEPART_MAXSIZE]
			elif response == "accepted[end]":
				s.close()
				break

	def save_local_filepart(self, file_uri, part_id, data):
		# 
		filepath = os.path.join(self.drive_path, 
								file_uri, part_id + '.zyl')
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

class ReqStatus(Enum):
	IDLE = "IDLE"
	SUCCESS = "SUCCESS"
	REQUESTING = "REQUESTING kademlia key"
	LOADING = "LOADING stream/file"
	RETRYING = "RETRYING request"
	FAILED = "FAILED"

class ZyloadRequest(Thread):

	DEFAULT_LOOKUP_TRY = 5

	#Request Status

	def __init__(self, loader, zyload_file, part_id):
		super(ZyloadRequest,self).__init__()
		self.zyload_file = zyload_file
		self.loader = loader
		self.file_uri = zyload_file.file_uri
		self.part_id = part_id
		self.server = self.loader.server

		self.lookup_tries = ZyloadRequest.DEFAULT_LOOKUP_TRY
		self.lookup_result = []
		self.stream = None
		self.status = ReqStatus.IDLE
		self.semaphore = Semaphore(0)

	def is_local(self):
		filepath = os.path.join(self.loader.drive_path, 
								self.file_uri, str(self.part_id) + '.zyl')
		return os.path.exists(filepath)

	def _get_fp_key(self):
		return self.loader._get_fp_key(self.file_uri, self.part_id)

	def run(self):
		self.lookup()

	def lookup(self):
		'''
		filepart address is in (file_uri, part_id)
		'''
		# print "starting request {}...".format(self._get_fp_key())
		if self.is_local():
			self.stream = ZyloadFilepart\
						  .from_local((self.file_uri,self.part_id),
						  			   self.load_local_filestream())
			self.status = ReqStatus.SUCCESS
			self.zyload_file.recv_part(self.part_id, self.stream)
		else:
			self.lookup_tries = DEFAULT_LOOKUP_TRY
			key = self._get_fp_key()
			self.status = ReqStatus.REQUESTING
			print "requesting {}...".format(self._get_fp_key())
			self.server.get(key).addCallback(self.lookupDone)
			# self.semaphore.acquire()

	def lookup_retry(self):
		'''
		filepart address is in (file_uri, part_id)
		'''
		print "retrying request {}...".format(self._get_fp_key())
		self.status = ReqStatus.RETRYING
		key = self._get_fp_key()
		self.server.get(key).addCallback(self.lookupDone)	

	def lookupDone(self, result):
		print "lookup done!!"
		if result is None:
			# we try a few times 
			self.lookup_tries -= 1
			if self.lookup_tries > 0:
				self.lookup_retry()
			else:
				#not found
				self.status = ReqStatus.FAILED
				print "                     REQUEST {} FAILED".format(self._get_fp_key())
				self.semaphore.release()
		else:
			# found a few IP
			self.lookup_result = result[:]
			self.status = ReqStatus.LOADING
			print "request {} loading...".format(self._get_fp_key())
			self.get_remote_filestream()


	def get_remote_filestream(self):
		if len(self.lookup_result) > 0:
			ip = self.lookup_result.pop()
			try:
				self.stream = self.connect_filepart_host(ip)

				#temporary hack - save locally
				data = self.stream.recv(1024)

				filedir = os.path.join('.zytemp', self.file_uri)
				if not os.path.exists(filedir):
					os.makedirs(filedir)

				filepath = os.path.join('.zytemp', self.file_uri, str(self.part_id)+".zyl")
				f = open(filepath, 'w+')
				f.write(data)
				f.close()

				f.open(filepath, 'r')

				self.status = ReqStatus.SUCCESS
				print "request {} success!".format(self._get_fp_key())
				self.zyload_file.recv_part(self.part_id,
										   ZyloadFilepart.from_local((self.file_uri, self.part_id),
										   							 f))
				self.semaphore.release()
				# self.zyload_file.recv_part(self.part_id,
				# 						   ZyloadFilepart.from_socket((self.file_uri,
				# 						   	                           self.part_id),
				# 						                              self.stream))
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
								self.file_uri, str(self.part_id) + '.zyl')
		return open(filepath, 'rb')

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