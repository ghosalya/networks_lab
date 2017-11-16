# File format
.zylo -> Zyloader File Representation
.zyl -> Zyloader part file

# Usage

0. Install python dependencies

    $ pip install -r requirements.txt

1. Run kademlia server in one shell window (ideally this will be daemon/autolaunched)

    ./zserver.sh

2. 


# Structure

a) client.py
  
  User-facing script to interact with the network. 
  + can add files to network (ideally download from internet)
  + can read file from network
  + can lookup and set kademlia key-value pair

b) filepart.py

  Contains `ZyloadFile` class that ideally behaves like a normal file object.
  Opens from a `.zylo` file.

  Also contains `ZyloadFilepart`, a representation of the filepart for the access.
  Opens from a `.zyl` file.

c) loader.py

  Contains `Zyloader` class, which is a background service that the client code can interact with in order to reach the network. 

  It also has `ZyloadRequest` class that does asynchronous requesting of the file.
  + lookup() search within the kademlia as to where the file part lives
  + load_local_filestream() and get_remote_filestream() that get the filestream
  + will pass a proper filepart to its corresponding file.

d) zserver.sh and server.tac.py

  server for kademlia DHT network
  


# User Story
+ Download & store-distribute
+ Open & lazyly load




# Issues

possible proble:
- network node is down, file part unavailable
	- how to know no filepart vs corrupted file
:: sol - have 2 identical filepart in network
	- when one is down, new node is given a copy
	- problem: conflicting file
		- set timestamp? use latest?
	- problem: saving
		-filepart 

- congestion:
	- save part as temporary local copy, and refer to that?


- normal split? hash split?

