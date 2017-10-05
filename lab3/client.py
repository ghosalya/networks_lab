#!/usr/bin/python2

"""
Networks Lab 3: UDP Socket Programming

Client code.

Gede Ria Ghosalya - 1001841
"""

from socket import *
from time import sleep
from datetime import datetime
import argparse, struct
from threading import Thread

from barrier import Barrier


if __name__=="__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument('-r', type=float, dest='rate',
        help='Packet rate in Mbps (eg; -r 1.5 is 1.5 Mbps)')
    parser.add_argument('-m', type=str, dest='message',
        help='Message to send', default='This is the message from the client')
    parser.add_argument('-f', type=str, dest='filename',
        help="Read the content of a file to use as message")

    args = parser.parse_args()
    i = 0
    
    if args.rate == None:
        print("USAGE:")
        print("python2 client.py -r 3.0:")
    else:
        sock = socket(AF_INET, SOCK_DGRAM)
        # server_address = ('localhost', 5555)
        server_address = ('10.0.0.2', 5555)
        packet_len = (args.rate * 1000000/8)
        if(packet_len < 10):
            print("WARNING: rate must be more than 10 Bps ({} Bps given)".format(packet_len))
            packet_len = 10
        print("Client rate is {} Mbps ({} Bps).".format(args.rate, packet_len))
        seg_maxlen = int(packet_len - 8) / 100 #max length of data per packet
        
        if args.filename is None:
            message = args.message
        else:
            message = open(args.filename, 'r').read()

        msg_byte = bytes(message)

    timed_barrier = Barrier(2)
    # cyclic barrier that takes 2 Thread
    # 1 thread is for timer (waits every 1 sec)
    # the other thread to process datagram

    def timer_thread_gen(timed_barrier):
        def timer_thread():
            reloop = True
            while reloop:
                sleep(0.01)
                reloop = timed_barrier.wait()
        return timer_thread

    def datagram_processing_thread(msg_byte, server_address):
        data_id = 0
        packets = 0
        total_byte = 0
        running = True
    	while len(msg_byte) > 0:
            msg_len = len(msg_byte)
            packet_cut = min(msg_len,seg_maxlen)
            pax_data = msg_byte[:packet_cut]
            msg_byte = msg_byte[packet_cut:]
                
            seg_id = struct.pack('q', data_id)
            total_pax = seg_id + pax_data
            sent = sock.sendto(total_pax, server_address)
            packets += 1
            total_byte += sent

            #in case of segment id overflow
            if data_id+1 >= 256:
                data_id = 0
            else:
                data_id += 1

            running = timed_barrier.wait()
        return packets, total_byte


    timer = Thread(target=timer_thread_gen(timed_barrier))
    # sender = Thread(target=datagram_processing_thread)
    

    try:
        starttime = datetime.now()
        timer.start()
        pax, total = datagram_processing_thread(msg_byte, server_address)
        endtime = datetime.now()
        timed_barrier.stop()
        # sender.start()

        deltatime = endtime - starttime
        duration = deltatime.seconds + 10**(-6)*deltatime.microseconds
        actual_speed = total/duration
        percentage = 100*actual_speed/packet_len
        overhead = total - len(msg_byte)
        print("\nUDP Report")
        print("Client rate is {} Mbps ({} Bps).".format(args.rate, packet_len))
        print("Message size: {} Bytes".format(len(msg_byte)))
        print("  in {} packets ({} total bytes sent, {} Bytes overhead)"\
                .format(pax, total, overhead))
        print("Duration: {}".format(duration))
        print("Rate: {:.2f} Bps ({:.2f}%)".format(actual_speed, percentage))

    except KeyboardInterrupt:
        timed_barrier.stop()





            