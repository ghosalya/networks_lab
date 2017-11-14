# File format
.zylo

 0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5  
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
|             Hex URI           |
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
|             Part ID           |
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
|              Data             |
|              ....             |
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+


# User Story
+ Download & store-distribute
+ Open & lazyly load

# Protocol
ZFSP = Zyload File Sharing Protocol

- request file part from the network (all)
	: source port, file URI, part A, part B 
- send file part to a machine (single)
    : destination port, file URI, part A, part B, data


 0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1 2 
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
|   PORT: source/destination    |             File URI            |
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
|             Part ID           |              length             |
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+




IMPORTANT: lenght == 0 is read as request 