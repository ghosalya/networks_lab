# Zyload

by Gede Ria Ghosalya (1001841)
for 50.012 Networks project

## File format
.zylo -> Zyloader File Representation
.zyl -> Zyloader part file

## Usage

### Testing

For the sake of test, we added a mininet script that simulates 3 machines (h0, h1, h2) that runs the necessary servers. 

1. adding file

+ in mininet open `xterm` for h1. 
+ `cd` into the folder `h1` (where the server are running from). 
+ run `client.sh`

0. Install python dependencies

    $ pip install -r requirements.txt

1. Run kademlia server in one shell window (ideally this will be daemon/autolaunched)

    $ ./zserver.sh

2. Run client.py

    $ python client.py

3. 2 commands that can be tested:
  a) add_file `filename` adds the content of file to the network.
     It will create a `filename.zylo` file
  b) read `filename.zylo` prints the content of the file stored in network.


## Structure

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



## User Story

+ Open & lazyly load
  1) client.py will load a `.zylo` file as a ZyloadFile object
  2) as we call ZyloadFile.read(), the file will request from the available Zyloader
  3) Zyloader will create a new ZyloadRequest for each part of the file that is read
  4) multiple ZyloadRequest objects looking up and loading file parts
  5) lookup returns a ZyloadFilepart that is fed into ZyloadFile
  6) ZyloadFile reads from relevant part and returns it to client code



## Issues

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

