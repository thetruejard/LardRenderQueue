
import os
import sys

import bgdthread as bgd
import msgqueue as msgq
import taskfile

'''
__main__.py
Starts and stop the background thread and handles user input
Relays messages to the MsgQueue based on user input
'''


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
	if args.find(' ') >= 0:
		invalid_args('help')
		return
	elif args=='':
		# print_header_info is defined below, but is guaranteed to be defined before this function is called
		print_header_info()
	else:
		cmdname = command_aliases.get(args, None)
		cmd = commands.get(cmdname, None) if cmdname != None else None
		if cmd != None:
			print(Color.YELLOW + "=========================")
			print_command_info(cmdname, cmd)
			print(Color.YELLOW + "=========================\n")
		else:
			print(Color.RED + f"Unrecognized command '{args}'")
			print("Type 'help' for a list of available commands")

@command('<filepath>', ['r'],
'''Adds the specified blend file to the queue for rendering
<filepath> may be quoted but does not have to be, even if it includes spaces''')
def render(args):
	args = args.strip('"')
	Tasks.create_task(taskfile.TaskType.RENDER_ANIMATION, args)
	bgd_thread.notify_thread()


@command('<filepath>', ['b'], 'Adds the specified blend file to the queue for baking all physics dynamics')
def bake(args):
	bgd_thread.notify_thread()

@command('', ['rl'], 'Lists all blend files currently queued for rendering')
def renderlist(args):
	if args != '':
		invalid_args('renderlist')
		return

@command('', ['q', 'exit'], 'Ends the background thread and quits the script')
def quit(args=''):
	if args != '':
		invalid_args('quit')
		return
	global done
	done = True
	msgq.add_message(msgq.MessageType.QUIT)

@command('', ['cls'], 'Clears the console')
def clear(args):
	if args != '':
		invalid_args('clear')
		return
	os.system('cls' if os.name == 'nt' else 'clear')
	print(Color.YELLOW + "=========================\n\n")

@command('[index]', [],
'''Skips the current task and re-inserts it in the queue either at the end or at [index].
Specify 0 for [index] to re-insert the current tasks at the beginning of the queue.''')
def skip(args):
	if args == '':
		index = -1
	else:
		try:
			index = int(args)
		except ValueError:
			invalid_args('skip')
			return



# Start

def print_command_info(name, cmd : Command):
	print(Color.RESET + "\t", name, cmd.params)
	splittooltip = cmd.tooltip.splitlines()
	for line in splittooltip:
		print(Color.CYAN + "\t\t-", line)
	if len(cmd.aliases) < 1:
		print(Color.BLUE + "\t\tNo aliases")
	else:
		print(Color.BLUE + "\t\tAliases: ", str(cmd.aliases)[1:-1])

def print_header_info():
	print(Color.YELLOW + "=== Lard Render Queue ===")
	print("A queue designed for rendering and baking Blender projects")
	print("Commands:")
	for name, cmd in commands.items():
		print_command_info(name, cmd)
	print(Color.YELLOW + "=========================\n\n")
print_header_info()


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
			cmd.func('' if len(splitline) < 2 else splitline[1].strip())
		else:
			print(Color.RED + f"Unknown command '{cmdalias}'")
			print("Type 'help' for a list of available commands")
	except EOFError:
		print(Color.RED + "Error parsing command")
		

bgd_thread.join()
print(Color.YELLOW + "\nScript execution has stopped" + Color.RESET)