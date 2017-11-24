'''
Server for TCP connections - filepart transfer
'''
import os.path
from threading import Thread
from socket import *

def get_local_ip():
	import commands
	return commands.getoutput("/sbin/ifconfig")\
				   .split("\n")[1]\
				   .split()[1][5:]

class Zyserver:
	'''
	handles file transfer via tcp
	'''
	def __init__(self, port=7171):
		self.listening = False
		self.port = port
		self.socket = socket(AF_INET, SOCK_STREAM)
		# self.socket.bind((gethostname(), port))
		self.socket.bind((get_local_ip(), port))


	def listen(self):
		self.listening = True
		self.socket.listen(5) #max 5 connection
		while self.listening:
			clientsocket, address = self.socket.accept()
			zycon = Zyconnection(self, clientsocket)
			# zycon.run()
			zycon.start()


class Zyconnection(Thread):
	def __init__(self, zyserver, clientsocket):
		super(Zyconnection,self).__init__()
		self.zyserver = zyserver
		self.clientsocket = clientsocket

	def run(self):
		# 1. wait for indicator packet
		# that indicates whether the request is 
		# asking for a filepart, or sending one

		request = None

		while request is None:
			try:
				req = self.clientsocket.recv(1024)
				if not req: break
				print "Request: {}".format(req)
				# format is [mode][fileuri][part]
				if "[filepart-request]" in req\
					or "[file-sending]" in req: 
					request = req
				else:
					#should re-request
					self.clientsocket.sendall("[mode_corrupted]")

			except error:
				print "Error occured"
				return

		# 2. send acknowledgement
		# for requester to start sending data
		# and check if correct

		self.clientsocket.sendall("[mode_accepted:{}]".format(request))

		# 3. handles remaning data
		req_param = request.split(']')
		req_param = [s.strip('[') for s in req_param]

		if "filepart-request" == req_param[0]:
			self.handle_request(req_param[1], req_param[2])
		elif "file-sending" == req_param[0]:
			self.handle_receive(req_param[1], req_param[2])

	def handle_request(self, file_uri, part_id):
		transferring = True
		filepath = os.path.join('.zyload', file_uri, part_id+".zyl")
		exists = os.path.exists(filepath)

		if not exists:
			self.clientsocket.sendall("[error][file-not-found]")
			self.clientsocket.close() # not sure if want to close here
			return

		f = open(filepath, 'r')
		try:
			data = f.reads()
			self.clientsocket.sendall(current_packet)
			self.clientsocket.recv(1024)
			#if anything is received, close socket
			self.clientsocket.close()
		except:
			return

		'''
		#transfer with ack
		current_packet = f.read(1024)

		while transferring:
			try:
				self.clientsocket.sendall(current_packet)
				ack = self.clientsocket.recv(256) #dk the length
				if ack == "received":
					current_packet = f.read(1024)
					transferring = len(current_packet ) > 0
				#otherwise resend
			except:
				print "Error bro"
				break

		f.close()
		self.clientsocket.close()
		'''

	def handle_receive(self, file_uri, part_id):
		# right now it overrides existing

		filedir = os.path.join('.zyload', file_uri)
		if not os.path.exists(filedir):
			os.makedirs(filedir)

		filepath = os.path.join('.zyload', file_uri, part_id+".zyl")
		f = open(filepath, 'w+')

		accepting = True

		while accepting:
			accepted_data = self.clientsocket.recv(1024)
			if '[end]' in accepted_data:
				accepting = False
				accepted_data.strip('[end]')
				f.write(accepted_data)
				self.clientsocket.sendall("accepted[end]")
			else:
				f.write(accepted_data)
				self.clientsocket.sendall("accepted")


		f.close()
		self.clientsocket.close()
		

if __name__ == '__main__':
	zs = Zyserver()
	zs.listen()