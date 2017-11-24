# from loader import Zyloader
from threading import Semaphore

FILEPART_MAXSIZE = 1024

class ZyloadFile:
	'''
	Behaves like a file object
	'''
	def __init__(self, file_uri, zyloader, length=1):
		self.file_uri = file_uri
		self.zyloader = zyloader
		self.part_count = length
		self.loaded_parts = {} #partid-ZyloadFilepart pair
		self.semaphore = None

	def set_zyloader(self, zyloader):
		if zyloader != self.zyloader:
			self.zyloader = zyloader
			self.loaded_parts = {}

	def load_part(self, part_id):
		# part_threads = []
		self.semaphore = Semaphore(0)
		if self.zyloader is None:
			print "ERROR: Zyloader not set"
			return
		# for part_id in part_ids:
		# part_threads.append(
		self.zyloader.request_part(self, part_id)
			# )

		# for pt in part_threads:
		self.semaphore.acquire()

	def recv_part(self, part_id, filepart):
		self.loaded_parts[part_id] = filepart
		self.semaphore.release()

	# "File" implementation

	def close(self):
		for idd, filepart in self.loaded_parts:
			filepart.close()
		self.zyloader = None
		self.loaded_parts = {}

	def load_all(self):
		self.load_part(range(self.part_count))

	def cache(self):
		#copy all file part to local
		pass

	def read(self, count=0, start=0):
		# check which filepart is needed
		self.semaphore = Semaphore(0)
		if count == 0 and start == 0:
			return self._read_all()
		else:
			return self._read_some(count, start)
			
	def _read_all(self):
		# self.load_all()
		count_left = self.part_count * FILEPART_MAXSIZE
		current_part = 0

		print "reading.."

		retur = ""

		while count_left > 0:
			self.load_part(current_part)
			if current_part in self.loaded_parts:
				# print "reading part {}".format(current_part)
				part_data = self.loaded_parts[current_part]\
								.read(FILEPART_MAXSIZE)\
								.strip('[end]')
				count_left -= FILEPART_MAXSIZE
				current_part += 1
				retur += part_data

		return retur

	def _read_some(self, count, start):
		filepart_count = (count - start) / FILEPART_MAXSIZE
		if (count-start)%FILEPART_MAXSIZE > 0:
			filepart_count+= 1

		filepart_start = start / FILEPART_MAXSIZE
		if start % FILEPART_MAXSIZE > 0:
			filepart_start += 1

		# self.load_part(range(filepart_start, filepart_count))

		print "reading.."

		current_part = filepart_start
		count_left = count
		retur = ""

		while count_left > 0:
			self.load_part(current_part)
			if current_part in self.loaded_parts:
				read_count = min(count_left, FILEPART_MAXSIZE)
				part_data = self.loaded_parts[current_part]\
								.read(read_count)
				count_left -= read_count
				retur += part_data
				current_part += 1
		return retur

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
	def from_socket(file_address, socket):
		zfp = ZyloadFilepart(*file_address)
		zfp.type = ZyloadFilepart.SOCKET
		zfp.stream = socket.makefile()
		return zfp

	@staticmethod
	def from_local(file_address, filestream):
		zfp = ZyloadFilepart(*file_address)
		zfp.type = ZyloadFilepart.LOCAL
		zfp.stream = filestream
		return zfp

	def read(self):
		return self.stream.read()

	def read(self, size):
		return self.stream.read(size)


