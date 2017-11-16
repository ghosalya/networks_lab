

class ZyloadFile:
	'''
	Behaves like a file object
	'''
	def __init__(self, file_uri, zyloader):
		self.file_uri = file_uri
		self.zyloader = zyloader
		self.loaded_parts = {} #partid-ZyloadFilepart pair

	def set_zyloader(self, zyloader):
		if zyloader != self.zyloader:
			self.zyloader = zyloader
			self.loaded_parts = {}

	def load_part(self, part_id):
		if self.zyloader = None:
			print "ERROR: Zyloader not set"
			return
		self.zyloader.request_part(self, part_id)

	def recv_part(self, part_id, filepart):
		self.loaded_parts[part_id] = filepart

	# "File" implementation

	def close(self):
		for idd, filepart in self.loaded_parts:
			filepart.close()
		self.zyloader = None
		self.loaded_parts = {}

	def read(self, size):
		pass

	def write(self, data):
		pass

	def seek(self, data):
		pass



class ZyloadFilepart:
	
	SOCKET = "SoCkEt"
	LOCAL = "lOcAl"

	def __init__(self, file_uri, part_id):
		self.file_uri = file_uri
		self.part_id = part_id
		self.address = (file_uri, part_id)
		self.type = None
		self.stream = None

	@staticmethod
	def from_socket(self, file_address, socket):
		zfp = ZyloadFilepart(*file_address)
		zfp.type = ZyloadFilepart.SOCKET
		zfp.stream = socket.makefile()
		return zfp

	@staticmethod
	def from_local(self, file_address, filestream):
		zfp = ZyloadFilepart(*file_address)
		zfp.type = ZyloadFilepart.LOCAL
		zfp.stream = filestream
		return zfp

	def read(self):
		return self.stream.read()

	def read(self, size):
		return self.stream.read(char)


