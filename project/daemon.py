# Server Code - running daemon

from socket import *

from zy_util import get_filepart_path
from zy_packet import ZyloadPacket

CONFIG_FILE = "zyload.conf"
config = {}

def load_config():
	config = {}
	with open(CONFIG_FILE, "r") as cf:
		for line in cf:
			k, v = line.strip('\n').split('=')
			config[k] = v


class ZyloadDaemon:

	_daemon = None

	def __init__(port, drive_path=".zyload"):
		'''
		port: the port that Daemon lives on
		drive_path: local file path where zyload files are stored
		'''
		self.port = port
		self.drive_path = drive_path
		self.filetable = {}
		ZyloadDaemon._daemon = self

	@static
	def get_daemon():
		if ZyloadDaemon._daemon is None:
			return ZyloadDaemon(load_config['port'] or 5555)
		else:
			return _daemon

	def store_file_part(self, file_uri, part_id, data):
		'''
		storing file part to drive
		'''
		dat = data.decode("utf-8", "ignore")
		filepath = get_filepart_path(file_uri, part_id)
		with open(filepath, "wb") as f:
			f.write(dat)

	def load_file_part(self, file_uri, part_id):
		'''
		loading file part from drive
		'''
		filepath = get_filepart_path(file_uri, part_id)
		with open(filepath, "rb") as f:
			data = f.read()
		return data

	def initiate_socket():
		self.socket = socket(AF_INET, SOCK_DGRAM)
		self.socket.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
		self.socket.setsockopt(SOL_SOCKET, SO_BROADCAST, 1)
		self.socket.bind(('', self.port))

	def main(self):
		self.initiate_socket()

		while True:
			#listen to request
			message, address = self.socket.recvfrom(8192)
			print "message:{}\n   address:{}"\
				  .format(message, address)





if __name__ == '__main__':
	load_config()
	daemon = ZyloadDaemon.get_daemon()
	daemon.main()







