

class ZyloadPacket:
	REQUEST = "REQUEST"
	RESPONSE = "RESPONSE"

	def __init__(self, message):
		msg_bytes = bytearray()
		msg_bytes.extend(message)

		self.port = msg_bytes[0:2]
		self.file_uri = msg_bytes[2:4]
		self.part_id = msg_bytes[4:6]

		length = int.from_bytes(msg_bytes[6:8])
		if length == 0:
			self.mode = ZyloadPacket.REQUEST
		else:
			self.mode = ZyloadPacket.RESPONSE
			self.length = length
			self.data = msg_bytes[6:]


