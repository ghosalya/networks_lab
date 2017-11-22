#!/usr/bin/env python

from mininet.topo import Topo
from mininet.net import Mininet
from mininet.log import lg, info, setLogLevel
from mininet.cli import CLI
from mininet.node import Switch, OVSKernelSwitch
from mininet.node import OVSController
from argparse import ArgumentParser

import sys
import os
import termcolor as T
import time

setLogLevel('info')

parser = ArgumentParser("Configure simple network in Mininet.")
parser.add_argument('--sleep', default=3, type=int)
args = parser.parse_args()

class myTopo( Topo ):
    "Simple topology example."

    def __init__( self ):
        "Create custom topo."

        # Initialize topology
        Topo.__init__( self )

        desktops = [self.addHost( 'h%d'%i ) for i in range(3)]
        # leftSwitch = self.addSwitch( 's1' )
        # rightSwitch = self.addSwitch( 's2' )
        comswitch = self.addSwitch('s0')

        # Add links
        for i in range(len(desktops)):
            self.addLink( comswitch, 'h%d'%i)
        return

def log(s, col="green"):
    print T.colored(s, col)

def main():
    os.system("rm -f /tmp/R*.log /tmp/R*.pid logs/*")
    os.system("mn -c >/dev/null 2>&1")
    os.system("killall -9 dnsmasq")

    net = Mininet(topo=myTopo(), controller = OVSController, autoSetMacs=True)
    net.start()
        
    log("Configured the routers")

    for i in range(3):
        host = net.getNodeByName('h%d'%i)
        host.cmd("cd h%d && twistd -noy ../zyload/server.tac.py & python ../zyload/connect.py"%i)
        #host.cmd("route add default gw 10.0.0.1")
        log("Kademlia server started for h%d"%i)

    CLI(net)
    net.stop()
    os.system("killall -9 dnsmasq")

if __name__ == "__main__":
    main()
