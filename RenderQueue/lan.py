
import socket
import threading

import __main__
import taskfile


'''
lan
When working over LAN, the script can run in one of 3 states:
1. Client: the user sends and receives blend files and output files by connecting to a server
2. Server: the script receives tasks from a Client, renders them, and then returns the result
3. Slave: the script shares a task list with a Server and helps it render
If the current script instance is running as a server, a thread is created to monitor connections
'''



class LANState:
	NONE = None
	CLIENT = 'c'
	SERVER = 's'
	SLAVE = 'l'

current_LAN_state = LANState.NONE
current_LAN_ip_port = (None, None)

current_socket = None


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
		pass
	# Clean up
	current_socket.close()
	current_socket = None



def make_client(ip, port):
	global current_LAN_state
	global current_LAN_ip_port
	global current_socket
	global server_thread
	if current_LAN_state != LANState.NONE:
		print(__main__.get_color('RED') + "The script is already in an LAN-enabled state. Run 'disconnect' first\n" +
		__main__.get_color('RESET'))
		return
	current_socket = socket.socket()
	try:
		current_socket.connect((ip, port))
	except:
		print('failed to connect')
		current_socket = None
		return
	print(f'Connected to {ip} on port {port}')
	# TODO
	current_socket.close()



def make_server(port=None):
	global current_LAN_state
	global current_LAN_ip_port
	global current_socket
	global server_thread
	global server_continue
	if current_LAN_state != LANState.NONE:
		print(__main__.get_color('RED') + "The script is already in an LAN-enabled state. Run 'disconnect' first\n" +
		__main__.get_color('RESET'))
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
	print(__main__.get_color('CYAN') + "Server launched, now accepting connections")
	print(f"IPv4: {socket.gethostname()}")
	print(f"Port: {current_LAN_ip_port[1]}\n" + __main__.get_color('RESET'))
	pass

def make_slave(ip, port):
	global current_LAN_state
	global current_LAN_ip_port
	global current_socket
	global server_thread
	if current_LAN_state != LANState.NONE:
		print(__main__.get_color('RED') + "The script is already in an LAN-enabled state. Run 'disconnect' first\n" +
		__main__.get_color('RESET'))
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



# Only call if the current LAN state is CLIENT
def client_send_task(task : taskfile.Task):
	pass