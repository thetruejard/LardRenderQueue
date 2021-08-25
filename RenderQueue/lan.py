
import socket
import threading
import shlex
from pathlib import Path
import os

import __main__ as M
import taskfile


'''
lan
When working over LAN, the script can run in one of 3 states:
1. Client: the user sends and receives blend files and output files by connecting to a server
2. Server: the script receives tasks from a Client, renders them, and then returns the result
3. Slave: the script shares a task list with a Server and helps it render
If the current script instance is running as a server, a thread is created to monitor connections

--- A Client/Slave -> Server connection goes as follows:
1. C/S -> Server: Send a header with basic version/state info
2. Server -> C/S: Send a response either accepting or refusing the connection
--- If accepted, execution depends on whether a Client or Slave is involved
--- Client:
3. C -> Server: Send the request to the server, as well as a header defining all supplementary files (if any)
4. Server -> C: Send a response either accepting or refusing the request and supplementary files
5. C -> Server: If supplementary files are needed, send them
--- Slave:
# TODO
---
6. All sockets are closed
'''



class LANState:
	NONE = 'n'
	CLIENT = 'c'
	SERVER = 's'
	SLAVE = 'l'

current_LAN_state = LANState.NONE
current_LAN_ip_port = (None, None)

current_socket = None


# Basic communication definitions
class Comm:
	# The maximum number of bytes to accept at one time. Must be larger than the max Header size (see below)
	BUFFER_LENGTH = 4096

	ACCEPT = 'accept'
	REFUSE = 'refuse'
	DELIMITER = '&'
	FILE = 'file'
	SUCCESS = 'success'
	FAILURE = 'failure'


class RequestType:
	# Just establish a connection between a Client/Slave and a Server
	ESTABLISH = 'est'
	# Send a task request to be queued on the server
	ADD_TASK = 'addtask'
	# Ask the server for the next task from its queue
	NEXT_TASK = 'nexttask'




# The header, i.e. the first thing sent from a client or slave to a server
class Header:
	def __init__(self):
		self.version = M.version
		self.LANState = LANState.NONE
		# TODO: Password, if appropriate
	
	def __str__(self):
		return f'"{self.version}" "{self.LANState}"'

	# If parsing fails, returns None
	def parse(string):
		try:
			tokens = shlex.split(string)
			tmp = Header()
			tmp.version = tokens[0]
			tmp.LANState = tokens[1]
		except IndexError:
			return None
		return tmp

	# Creates a header from the current script state. Don't forget to convert to a string, if appropriate
	def create_header():
		tmp = Header()
		tmp.LANState = current_LAN_state
		return tmp






server_thread = None
server_continue = True
def server_thread_func():
	global current_LAN_state
	global current_LAN_ip_port
	global current_socket
	global server_thread
	current_socket.listen()
	current_socket.settimeout(1.0)
	while server_continue:
		try:
			connection, address = current_socket.accept()
		except socket.timeout:
			continue
		print(f'Connected to {address}')
		
		# Wait for a header
		header = receive_string(connection)
		if header is None:
			print('Connection failed')
			continue
		header = Header.parse(header)
		if header.version != M.version:
			# Wrong version, refuse the connection
			send_data(connection, Comm.REFUSE)
			continue
		send_data(connection, Comm.ACCEPT)
		print(f'Connection accepted from instance of type "{header.LANState}"')

	# Clean up
	current_socket.close()
	current_socket = None



def make_client(ip, port):
	global current_LAN_state
	global current_LAN_ip_port
	global current_socket
	global server_thread
	if current_LAN_state != LANState.NONE:
		print(M.get_col('RED') + "The script is already in an LAN-enabled state. Run 'disconnect' first\n" +
		M.get_col('RESET'))
		return
	current_socket = socket.socket()
	try:
		current_socket.connect((ip, port))
	except:
		print('failed to connect')
		current_socket = None
		return
	print(f'Connected to {ip} on port {port}')
	current_LAN_state = LANState.CLIENT
	# Send header
	send_data(current_socket, str(Header.create_header()))
	# Get response
	response = receive_string(current_socket)
	if response is None:
		print('Connection lost')
		current_socket = None
		current_LAN_state = LANState.NONE
		return
	tokens = str(response).split(Comm.DELIMITER)
	if tokens[0] != Comm.ACCEPT:
		print('Connection refused')
		current_socket = None
		current_LAN_state = LANState.NONE
		return

	# TODO
	current_socket.close()


def make_server(port=None):
	global current_LAN_state
	global current_LAN_ip_port
	global current_socket
	global server_thread
	global server_continue
	if current_LAN_state == LANState.SERVER:
		print(M.get_col('CYAN') + "This script has already launched a server")
		print(f"IPv4: {socket.gethostbyname(socket.gethostname())}")
		print(f"Port: {current_LAN_ip_port[1]}\n" + M.get_col('RESET'))
		return
	elif current_LAN_state != LANState.NONE:
		print(M.get_col('RED') + "The script is already in an LAN-enabled state. Run 'disconnect' first\n" +
		M.get_col('RESET'))
		return
	if port is None:
		port = 0
	current_socket = socket.socket()
	# Using "0.0.0.0" allows this computer to be accessible via all its names across all networks
	current_LAN_ip_port = ("0.0.0.0", port)
	current_socket.bind(current_LAN_ip_port)
	# If we passed 0 for the port, the OS will have changed it
	current_LAN_ip_port = current_socket.getsockname()
	current_LAN_state = LANState.SERVER
	server_continue = True
	server_thread = threading.Thread(target=server_thread_func)
	server_thread.start()
	print(M.get_col('CYAN') + "Server launched, now accepting connections")
	print(f"IPv4: {socket.gethostbyname(socket.gethostname())}")
	print(f"Port: {current_LAN_ip_port[1]}\n" + M.get_col('RESET'))
	pass

def make_slave(ip, port):
	global current_LAN_state
	global current_LAN_ip_port
	global current_socket
	global server_thread
	if current_LAN_state != LANState.NONE:
		print(M.get_col('RED') + "The script is already in an LAN-enabled state. Run 'disconnect' first\n" +
		M.get_col('RESET'))
		return
	pass

def disconnect():
	global current_LAN_state
	global current_LAN_ip_port
	global current_socket
	global server_thread
	global server_continue
	server_continue = False
	if current_LAN_state == LANState.SERVER:
		server_thread.join()
	current_LAN_state = LANState.NONE
	current_LAN_ip_port = (None, None)
	print("Disconnected")
	pass


# Interpret the next data from the socket as message. If not message or failure, returns False. If message, returns True
def await_msg(socket : socket.socket, message):
	received = receive_string(socket)
	return received is not None and received == message



# Send the given string or data over the given socket
def send_data(socket : socket.socket, data):
	if type(data) is str:
		data = data.encode()
	socket.sendall(data)

# Receives and returns at most the given amount of data from the socket
# If no data could be received, returns None
def receive_data(socket : socket.socket, max_amount=Comm.BUFFER_LENGTH):
	try:
		return socket.recv(max_amount)
	except:
		return None
def receive_string(socket : socket.socket, max_amount=Comm.BUFFER_LENGTH):
	r = receive_data(socket, max_amount)
	return r.decode() if r is not None else r


# Returns whether the file was successfully sent
def send_file(socket : socket.socket, file : Path):
	with open(file, 'rb') as f:
		file = file.absolute()
		size = os.path.getsize(file)
		send_data(socket, f'{Comm.FILE}{Comm.DELIMITER}{size}')
		if not await_msg(socket, Comm.ACCEPT):
			return False
		while True:
			data = f.read(Comm.BUFFER_LENGTH)
			if data is None or data == '' or data == b'':
				break
			send_data(socket, data)
	return await_msg(socket, Comm.SUCCESS)


# Returns whether the file was successfully received
def receive_file(socket : socket.socket, destination : Path):
	meta = receive_string(socket)
	if meta is None:
		return False
	splitmeta = meta.split()
	if len(splitmeta) != 2 or splitmeta[0] != 'FILE':
		return False
	try:
		size = int(splitmeta[1])
	except:
		print("couldn't get size")
		send_data(socket, Comm.REFUSE)
		return False
	# Confirm this is a reasonable size (10 GBish ?)
	if size > 10000000000 or size <= 0:
		print('invalid size')
		send_data(socket, Comm.REFUSE)
		return False
	send_data(socket, Comm.ACCEPT)
	amt = 0;
	with open(destination, 'wb') as f:
		while True:
			data = receive_data(socket)
			if data is None:
				send_data(socket, Comm.FAILURE)
				return False
			amt += len(data)
			f.write(data)
			if amt == size:
				break
	send_data(socket, Comm.SUCCESS)
	return True




# Only call if the current LAN state is CLIENT
def client_send_task(task : taskfile.Task):
	pass