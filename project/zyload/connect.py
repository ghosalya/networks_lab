'''
Server for TCP connections - filepart transfer
'''
import os.path
from threading import Thread
from socket import *

class Zyserver:
	'''
	handles file transfer via tcp
	'''
	def __init__(self, port=7171):
		self.listening = False
		self.port = port
		self.socket = socket(AF_INET, SOCK_STREAM)
		self.socket.bind((gethostname(), port))


	def listen(self):
		self.listening = True
		self.socket.listen(5) #max 5 connection
		while self.listening:
			clientsocket, address = self.socket.accept()
			zycon = Zyconnection(self, clientsocket)
			zycon.run()


class Zyconnection(Thread):
	def __init__(self, zyserver, clientsocket):
		self.zyserver = zyserver
		self.clientsocket = clientsocket

	def run(self):
		# 1. wait for indicator packet
		# that indicates whether the request is 
		# asking for a filepart, or sending one

		request = None

		while request is None:
			try:
				req = self.clientsocket.recv()
				if not req: break
				print "Request type: {}".format(req)
				# format is [mode][fileuri][part]
				if "[filepart-request]" in req 
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
		req_param = request.strip('[').split(']')

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

	def handle_receive(self, file_uri, part_id):
		# right now it overrides existing

		filepath = os.path.join('.zyload', file_uri, part_id+".zyl")
		f = open(filepath, 'w')

		accepting = True

		while accepting:
			try:
				accepted_data = self.clientsocket.recv(1024)
				if '[end]' in accepted_data:
					accepting = False
					accepted_data.strip('[end]')
				f.write(accepted_data)
			except:
				print "Error bro"
				break

		f.close()
		self.clientsocket.close()
		