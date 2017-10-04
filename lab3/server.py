#!/usr/bin/python2

"""
Networks Lab 3: UDP Socket Programming

Server code.

Gede Ria Ghosalya - 1001841
"""

from socket import *

if __name__ == "__main__":

    sock = socket(AF_INET, SOCK_DGRAM)
    sock.bind(('localhost', 5555))
    print("Server Running")

    #format: 	{     (addrs)     : (    message   ,  latest_id)  }
    data_from = {('localhost',777): ("message storing format", 35)}

    while True:
        data, addrs = sock.recvfrom(4096)
        if addrs not in data_from:
        	data_from[addrs] = ''        	
        	print("Getting data from {}:{}"\
        			.format(addrs[0], addrs[1]))
        packet_id = int(data[:8])
        print(packet_id)
        pure_data = data[8:]
        print(pure_data)
        currently_received = data_from[addrs][0]
        latest_id = data_from[addrs][1]
        expected_id = (int(latest_id) +1) % 256
        if packet_id != 1:
        	if packet_id != 0:
        		print("WARNING: Missing Datagram (ID {} expected, got ID {})")

        data_from[addrs] = (currently_received+pure_data, packet_id)




