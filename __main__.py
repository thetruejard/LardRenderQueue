
import os
import sys
import atexit
import shlex
import time

import bgdthread as bgd
import msgqueue as msgq
import taskfile
import lan


'''
__main__
Starts and stop the background thread and handles user input
Relays messages to the MsgQueue based on user input
'''

# For parsing reasons, the version name cannot include quotes or other special characters
version = 'dev'



# As a general (empirical) rule of thumb, debuggers on Windows do not support ANSI codes
# This line will guess whether or not we are running in a debugger
# @source: https://stackoverflow.com/questions/38634988/check-if-program-runs-in-debug-mode?rq=1
use_colored_text = not hasattr(sys, 'gettrace') or sys.gettrace() is None

# Define ANSI color codes, if appropriate
if use_colored_text:
	class Color:
		BLACK = '\033[30m'
		RED = '\033[31m'
		GREEN = '\033[32m'
		YELLOW = '\033[33m'
		BLUE = '\033[34m'
		MAGENTA = '\033[35m'
		CYAN = '\033[36m'
		RESET = '\033[0m'	
	# At least one system() call is needed to enable color on Windows
	os.system("")
else:
	print("Colored text has been disabled for this session")
	class Color:
		BLACK = ''
		RED = ''
		GREEN = ''
		YELLOW = ''
		BLUE = ''
		MAGENTA = ''
		CYAN = ''
		RESET = ''
def get_col(color):
	return eval(f'Color.{color}')



# When func() is called, only the parameters are passed in; the name of the command is not
class Command:
	def __init__(self, func, params, aliases, tooltip):
		self.func = func
		self.params = params
		self.aliases = aliases[:]
		self.tooltip = tooltip
commands = {}
command_aliases = {}
def add_command(name, func, params, aliases, tooltip):
	commands[name] = Command(func, params, aliases, tooltip)
	command_aliases[name] = name
	for a in aliases:
		command_aliases[a] = name
def command(params, aliases, tooltip):
	def helper(c):
		add_command(c.__name__, c, params, aliases, tooltip)
		return c
	return helper

def invalid_args(command):
	cmd = commands[command]
	print(Color.RED + "Usage:", command, cmd.params)
	print(f"Type 'help' or 'help {command}' for more information")



# Define some variables here so they can be accessed by certain commands
done = False
bgd_thread = bgd.BgdThread()


# Define all commands

@command('[command]', ['h'],
'''Prints usage information about commands
If [command] is not specified, all available commands are printed''')
def help(args):
	if args is None:
		# print_header_info is defined below, but is guaranteed to be defined before this function is called
		print_header_info()
	elif len(args) > 1:
		invalid_args('help')
		return
	else:
		cmdname = command_aliases.get(args, None)
		cmd = commands.get(cmdname, None) if cmdname != None else None
		if cmd != None:
			print(Color.YELLOW + "=========================")
			print_command_info(cmdname, cmd)
			print(Color.YELLOW + "=========================\n")
		else:
			print(Color.RED + f"Unrecognized command '{args[0]}'")
			print("Type 'help' for a list of available commands")

@command('<filepath>', ['r'],
'''Adds the specified blend file to the queue for rendering as an animation
If <filepath> includes whitespace, it must be quoted''')
def render(args):
	if args is None or len(args) != 1:
		invalid_args('render')
		return
	taskfile.create_task(taskfile.TaskType.RENDER_ANIMATION, args)
	bgd_thread.notify_thread()

@command('<filepath>', ['s'],
'''Adds the specified blend file to the queue for rendering as a still image
If <filepath> includes whitespace, it must be quoted''')
def still(args):
	if args is None or len(args) != 1:
		invalid_args('still')
		return
	taskfile.create_task(taskfile.TaskType.RENDER_STILL, args)
	bgd_thread.notify_thread()



@command('<filepath>', ['b'], 'Adds the specified blend file to the queue for baking all physics dynamics')
def bake(args):
	bgd_thread.notify_thread()

@command('', [], 'Prints the current state information of the script and all tasks')
def status(args):
	if args is not None:
		invalid_args('status')
		return
	current = taskfile.get_current_task()
	tasks = taskfile.read_tasks()
	completed = taskfile.read_completed()
	failed = taskfile.read_failed()
	# TODO: completed and failed tasks
	if current is not None:
		# Correct the time, since it has changed since the task started running
		current.time += time.perf_counter() - bgd_thread.start_time
		print(Color.YELLOW + "===== Current Task =====")
		print(current.desc())
	print('')
	if len(tasks) == 0:
		print(Color.CYAN + "===== Tasks Queued =====\nThere are no tasks currently queued" + Color.RESET)
	else:
		print(Color.CYAN + "===== Tasks Queued =====")
		for i in range(0, len(tasks)):
			print(str(i + 1) + ". " + tasks[i].desc())
	print('')
	if len(completed) > 0:
		print(Color.GREEN + "===== Tasks Completed =====")
		for i in range(0, len(completed)):
			print(str(i + 1) + ". " + completed[i].desc())
	print('')
	if len(failed) > 0:
		print(Color.MAGENTA + "===== Tasks Failed =====")
		for i in range(0, len(failed)):
			print(str(i + 1) + ". " + failed[i].desc())
	print('\n' + Color.RESET)


@command('[completed/failed/queued/c/f/q]', [],
'''Clears the specified list(s) of tasks. This cannot be undone
Multiple can be specified at a time (ex: 'clear c f')
If no list is specified, the lists of completed and failed tasks are cleared''')
def clear(args):
	has_args = args is not None
	valid = ['completed', 'c', 'failed', 'f', 'queued', 'q']
	if has_args and any(term not in valid for term in args):
		invalid_args('clear')
		return
	if not has_args or 'completed' in args or 'c' in args:
		taskfile.clear_completed()
	if not has_args or 'failed' in args or 'f' in args:
		taskfile.clear_failed()
	if has_args and ('queued' in args or 'q' in args):
		taskfile.clear_tasks()


@command('<IPv4> <port>', [],
'''Connects as a client to a server at IPv4 over port
Run 'server' on the server to retrieve these values''')
def client(args):
	if args is None or len(args) != 2:
		invalid_args('client')
		return
	try:
		ip, port = args[0], int(args[1])
	except:
		invalid_args('client')
		return
	lan.make_client(ip, port)

@command('[port]', [],
'''Establishes this script instance as a server that other instances can connect to
If no port is specified, the script will let the OS select a port
If this instance is already a server, the current ip and port are retrieved''')
def server(args):
	if args is not None:
		if len(args) > 1:
			invalid_args('server')
			return
		try:
			port = int(args[0])
		except:
			invalid_args('server')
			return
	else:
		port = None
	lan.make_server(port)

@command('<IPv4> <port>', [],
'''Connects as a worker to a server at IPv4 over port
Run 'server' on the server to retrieve these values''')
def worker(args):
	if args is None or len(args) != 2:
		invalid_args('worker')
		return
	try:
		ip, port = args[0], int(args[1])
	except:
		invalid_args('worker')
		return
	lan.make_worker(ip, port)

@command('', [], 'Disconnects the current LAN state (client/server/worker), if any')
def disconnect(args):
	if args is not None:
		invalid_args('disconnect')
		return
	lan.disconnect()


@command('', ['q', 'exit'], 'Ends the background thread and quits the script')
def quit(args=None):
	if args is not None:
		invalid_args('quit')
		return
	global done
	done = True
	msgq.add_message(msgq.MessageType.QUIT)
atexit.register(quit)

@command('', [], 'Clears the console')
def cls(args):
	if args is not None:
		invalid_args('cls')
		return
	os.system('cls' if os.name == 'nt' else 'clear')
	print(Color.YELLOW + "=========================\n\n")

@command('[index]', [],
'''Skips the current task and re-inserts it in the queue either at the end or at [index].
Specify 0 for [index] to re-insert the current tasks at the beginning of the queue.''')
def skip(args):
	if args is None:
		index = -1
	else:
		try:
			index = int(args[0])
		except ValueError:
			invalid_args('skip')
			return


def print_command_info(name, cmd : Command):
	print(Color.RESET + "\t", name, cmd.params)
	splittooltip = cmd.tooltip.splitlines()
	for line in splittooltip:
		print(Color.CYAN + "\t\t-", line)
	if len(cmd.aliases) >= 1:
		print(Color.BLUE + "\t\tAliases: ", str(cmd.aliases)[1:-1])

def print_header_info():
	print(Color.YELLOW + "=== Lard Render Queue ===")
	print("A queue designed for rendering and baking Blender projects")
	print("Commands:")
	for name, cmd in commands.items():
		print_command_info(name, cmd)
	print(Color.YELLOW + "=========================\n\n")


if __name__ == '__main__':
	print_header_info()

	headless = (len(sys.argv) > 1 and sys.argv[1] == '--headless')

	if not headless:
		bgd_thread.start()

	# done is defined above and set to True in quit()
	while not done:
		print(Color.RESET + "> ", end='')
		try:
			line = input().strip()
			splitline = line.split(' ', 1)
			if splitline[0] == '':
				continue
			cmdalias = splitline[0].strip()
			cmdname = command_aliases.get(cmdalias, None)
			cmd = commands.get(cmdname, None) if cmdname != None else None
			if cmd != None:
				try:
					args = None if len(splitline) < 2 else shlex.split(splitline[1].strip())
				except ValueError:
					raise EOFError() # shlex error: just pass to bottom
				cmd.func(args)
			else:
				print(Color.RED + f"Unknown command '{cmdalias}'")
				print("Type 'help' for a list of available commands")
		except EOFError:
			print(Color.RED + "Error parsing command")

	if not headless:
		bgd_thread.join()
	print(Color.YELLOW + "\nScript execution has stopped" + Color.RESET)