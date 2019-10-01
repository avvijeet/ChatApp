# Python program to implement server side of chat room. 
import socket 
import select 
import sys 
from thread import *
from cryptography.fernet import Fernet

import dbConnector

file = open('chat_key.key', 'rb')
key = file.read() # The key will be type bytes
file.close()
fernet = Fernet(key)

"""The first argument AF_INET is the address domain of the 
socket. This is used when we have an Internet Domain with 
any two hosts The second argument is the type of socket. 
SOCK_STREAM means that data or characters are read in 
a continuous flow."""
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1) 

# checks whether sufficient arguments have been provided 
# if len(sys.argv) != 3: 
# 	print "Correct usage: script, IP address, port number"
# 	exit() 

# takes the first argument from command prompt as IP address 
# IP_address = str(sys.argv[1]) 
IP_address = "127.0.0.1" 

# takes second argument from command prompt as port number 
# Port = int(sys.argv[2]) 
Port = 8000

""" 
binds the server to an entered IP address and at the 
specified port number. 
The client must be aware of these parameters 
"""
server.bind((IP_address, Port)) 

""" 
listens for 100 active connections. This number can be 
increased as per convenience. 
"""
server.listen(10) 

list_of_clients = [] 

def printPreviousChats(chatroom_name, conn):
	chat_room = dbConnector.db[chatroom_name]

	# print("\n\nMessages for chatroom " + str(chatroom_name))
	for chat in chat_room.find():
		# print("> " + chat["message"].split("\n")[0])
		message = fernet.encrypt(str("<{}> ".format(chat["name"]) + chat["message"].split("\n")[0]))
		conn.send(message)

def clientthread(conn, addr, c_name, room_name): 

	# sends a message to the client whose user object is conn 
	conn.send(fernet.encrypt("Welcome to this chatroom!")) 
	chat_room = dbConnector.db[room_name]

	printPreviousChats(room_name, conn)

	while True: 
			try:
				message = conn.recv(2048*10) 
				if message:
					message = fernet.decrypt(message)

					"""prints the message and address of the 
					user who just sent the message on the server 
					terminal"""
					print "<" + c_name + "> " + message

					chat_room.insert_one({
						"name": str(c_name),
						"message": str(message)
					})

					# Calls broadcast function to send message to all 
					message = fernet.encrypt("<" + c_name + "> " + message)
					broadcast(message, conn) 

				else: 
					"""message may have no content if the connection 
					is broken, in this case we remove the connection"""
					remove(conn) 

			except: 
				continue

"""Using the below function, we broadcast the message to all 
clients who's object is not the same as the one sending 
the message """
def broadcast(message, connection): 
	for clients in list_of_clients: 
		if clients!=connection: 
			try: 
				clients.send(message) 
			except: 
				clients.close() 

				# if the link is broken, we remove the client 
				remove(clients) 

"""The following function simply removes the object 
from the list that was created at the beginning of 
the program"""
def remove(connection): 
	if connection in list_of_clients: 
		list_of_clients.remove(connection) 

while True: 

	"""Accepts a connection request and stores two parameters, 
	conn which is a socket object for that user, and addr 
	which contains the IP address of the client that just 
	connected"""
	conn, addr = server.accept() 
	message = conn.recv(2048*10)
	[room, username] = fernet.decrypt(message).split(":")
	print("User {} trying to connect to room {}".format(username, room))

	"""Maintains a list of clients for ease of broadcasting 
	a message to all available people in the chatroom"""
	list_of_clients.append(conn) 

	# prints the address of the user that just connected 
	print addr[0] + " connected"

	# creates and individual thread for every user 
	# that connects 
	start_new_thread(clientthread,(conn, addr, username, room))	 

conn.close() 
server.close() 
