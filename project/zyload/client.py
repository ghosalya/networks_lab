
import os, sys
import subprocess

from twisted.internet import reactor
from twisted.python import log
from kademlia.network import Server

# import daemon

CONFIG_FILE = "zyload.conf"



class ZyloadClient:
	def __init__(self, ip, port):
		self.server = None
		self.ip = ip
		self.port = port
		self.load_config()
		self.initiate_kademlia(ip, 8468)

	def load_config(self):
		self.config = {}
		if os.path.exists(CONFIG_FILE):
			with open(CONFIG_FILE, "r") as cf:
				for line in cf:
					if '=' in line:
						k, v = line.strip('\n').split('=')
						self.config[k] = v

	def initiate_kademlia(self, ip, port):
		'''
		create a kademlia.Server to listen to the network
		'''
		log.startLogging(sys.stdout)
		self.server = self.server or Server()
		self.server.listen(self.port)
		self.server.bootstrap([(ip, port)])\
				   .addCallback(self.CLI, self.server)
		reactor.run()

	def get_key(self, key):
		print "getting {}".format(key)
		self.server.get(key).addCallback(self.CLI, self.server)

	def set_key(self, key, value):
		print "setting {},{}".format(key, value)
		self.server.set(key, value)\
			.addCallback(self.CLI, self.server)

	def CLI(self, result, server):
		print result
		user_input = raw_input(">>")
		user_input = user_input.strip('\n')\
							   .split(' ')

		if "get" == user_input[0]:
			print self.get_key(user_input[1])
		elif "set" == user_input[0]:
			self.set_key(user_input[1], user_input[2])


if __name__ == '__main__':
	zlc = ZyloadClient('10.0.0.105', 5552)