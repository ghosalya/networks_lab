# File format
.zylo -> Zyloader File Representation
.zyl -> Zyloader part file

# Usage

0. Install python dependencies

    $ pip install -r requirements.txt

1. Run kademlia server in one shell window (ideally this will be daemon/autolaunched)

    ./zserver.sh

2. 


# User Story
+ Download & store-distribute

    1) download bit-by-bit
    2) 

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

