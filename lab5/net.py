#!/usr/bin/env python
# Lab 6 network script
# Based on original BGP exercise
# Nils, SUTD, 2015

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

        # Add external AS and switches
        serverOne = self.addHost( 'extH1', ip='8.8.8.2/24')
        serverTwo = self.addHost( 'extH2', ip='8.8.8.8/24' )
        extGW = self.addHost( 'extGW', ip='8.8.8.1/24' )
        extSwitch = self.addSwitch( 'extS1' )
        self.addLink( serverOne, extSwitch )
        self.addLink( serverTwo, extSwitch )
        self.addLink( extGW, extSwitch )

        # Add internal hosts and switches
        serverOne = self.addHost( 'srv1' )
        serverTwo = self.addHost( 'srv2' )
        intGW = self.addHost( 'intGW' )
        desktops = [self.addHost( 'h%d'%i ) for i in range(5)]
        leftSwitch = self.addSwitch( 's1' )
        rightSwitch = self.addSwitch( 's2' )

        # Add links
        self.addLink( serverOne, leftSwitch )
        self.addLink( serverTwo, leftSwitch )
        self.addLink( leftSwitch, rightSwitch )
        self.addLink( intGW, rightSwitch )
        for i in range(len(desktops)):
            self.addLink( rightSwitch, 'h%d'%i)
        self.addLink( intGW, extGW )
        return

def log(s, col="green"):
    print T.colored(s, col)

def enableNAT(net,hostn):
    # this assumes that internal interface is eth0, external interface is eth1, and the network is 10.0.0.0/24
    host = net.getNodeByName(hostn)
    host.cmd("iptables -A FORWARD -o %s-eth1 -i %s-eth0 -s 10.0.0.0/24 -m conntrack --ctstate NEW -j ACCEPT"%(hostn,hostn))
    host.cmd("iptables -A FORWARD -m conntrack --ctstate ESTABLISHED,RELATED -j ACCEPT")
    host.cmd("iptables -t nat -F POSTROUTING")
    host.cmd("iptables -t nat -A POSTROUTING -o %s-eth1 -j MASQUERADE"%hostn)


    
def startWebserver(net, hostname, text="Default web server"):
    host = net.getNodeByName(hostname)
    return host.popen("python webserver.py --text '%s'" % text, shell=True)

def main():
    os.system("rm -f /tmp/R*.log /tmp/R*.pid logs/*")
    os.system("mn -c >/dev/null 2>&1")
    os.system('pgrep -f webserver.py | xargs kill -9')
    os.system("killall -9 dnsmasq")
    #os.system("service isc-dhcpd-server stop")

    net = Mininet(topo=myTopo(), controller = OVSController, autoSetMacs=True)
    net.start()

    # Set default routes for ext hosts
    for h in ['extH1','extH2']:
        host = net.getNodeByName(h)
        host.cmd("route add default gw 8.8.8.1")
    
    # Let extGW drop all private network packets. Not entirely what would really happen, but close enough
    host = net.getNodeByName('extGW')
    host.cmd("iptables -I FORWARD -s 10.0.0.0/24 -j DROP")
        
    # Enable forwarding for the routers
    routes={'intGW':'2.2.2.1','extGW':'2.2.2.2'}
    firstIP={'intGW':'10.0.0.1','extGW':'8.8.8.1'}
    secondIP={'intGW':'2.2.2.2','extGW':'2.2.2.1'}
    for h in ['intGW','extGW']:
        host = net.getNodeByName(h)
        host.cmd("sysctl -w net.ipv4.ip_forward=1")
        host.cmd("ifconfig %s-eth0 %s netmask 255.255.255.0"%(h,firstIP[h]))
        host.cmd("ifconfig %s-eth1 %s netmask 255.255.255.0"%(h,secondIP[h]))
        host.cmd("route add default gw %s"%routes[h])

    # enable NAT'ing on intGW
    enableNAT(net,'intGW')
    
    log("Configured the routers")

    # start the dns server on 8.8.8.8
    host = net.getNodeByName('extH2')
    host.cmd("dnsmasq -C ./extH2DHCP.conf")
    log("Done with dnsmask")
    # start the dhcp on srv1
    # This is also broken because dnsmasq takes ages for the authorative answer
    host = net.getNodeByName('srv1')
    host.cmd("dnsmasq -C ./srv1DHCP.conf")
    host.cmd("route add default gw 10.0.0.1")
    #host.cmd("service isc-dhcp-server stop")
    #host.cmd("service isc-dhcp-server start")
    log("Done with isc-dhcp-server start")
    # configure server 2
    host = net.getNodeByName('srv2')
    host.cmd("route add default gw 10.0.0.1")
    log("added the route")    
    #log("Requesting configuration by DHCP, this can take a while")
    # Set default routes for int hosts, or do this via DHCP?
    for i in range(5):
        host = net.getNodeByName('h%d'%i)
        host.cmd("dhclient -r h%d-eth0"%i)
        host.cmd("dhclient h%d-eth0"%i)
        #host.cmd("route add default gw 10.0.0.1")
        log("Received IP for h%d"%i)
        
    log("Starting web servers", 'yellow')
    startWebserver(net, 'extH1', "Nils 50.012 Networks web server")
    #startTerminal(net, 'h3-1')

    CLI(net)
    net.stop()
    os.system("killall -9 dnsmasq")
    os.system('pgrep -f webserver.py | xargs kill -9')


if __name__ == "__main__":
    main()
