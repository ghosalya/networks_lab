
class UDPHeader:
    def __init__(self, lenn):
        self.list = [0 for i in range(lenn)]

    def increment(self, index, value=1):
    	if value < 0:
    		self.decrement(index, -1*value)
        cur = self.list[index]
        self.list[index] = (cur+value) % 256
        overflow = (cur+value) // 256
        if overflow > 0 and index!=0:
        	self.increment(index-1, overflow)

    def decrement(self, index, value=1):
    	if value < 0:
    		self.decrement(index, -1*value)
        cur = self.list[index]
        self.list[index] = (cur-value) % 256
        overflow = (cur+value) / 256
        if overflow > 0 and index != 0:
        	self.decrement(index-1, overflow)

    def get_bytearray(self):
    	return bytearray(self.list)

 	def set_bytearray(self, bytearr):
 		newlist = [int(i) for i in bytearr]


        