
import threading

'''
Tasks
Handles all types of tasks, interfacing with file(s) to track queued bakes and renders
'''

# The name of the file in which tasks are stored. The current working directory is used
# If this is changed, the .gitignore file must be updated too (see bottom of .gitignore)
tasklist_filename = 'tasklist.dat'
# Each task in the taskfile is one line of text followed by a newline



class TaskType:
	RENDER_ANIMATION = 'ra'
	RENDER_STILL = 'rs'
	BAKE = 'b'


class Task:
	def __init__(self, type, args : str):
		self.type = type
		self.args = args

	def __str__(self):
		return self.type + ' ' + self.args


disk_mutex = threading.RLock()

# Locks the task list on disk
# This is a recursive operation, i.e. it can be locked multiple times (and must be unlocked multiple times)
def lock_disk():
	disk_mutex.acquire()
def unlock_disk():
	disk_mutex.release()

# Returns the number of tasks that are currently queued
def num_tasks():
	lock_disk()
	count = 0
	try:
		with open(tasklist_filename, 'r') as f:
			count = f.read().count('\n')
	except:
		pass
	unlock_disk()
	return count

# Reads the taskfile and returns a list of Task objects
def read_tasks() -> list:
	lock_disk()
	tasks = []
	try:
		with open(tasklist_filename, 'r') as f:
			lines = f.readlines()
		for line in lines:
			split = line.split(sep=' ', maxsplit=1)
			tasks.append(Task(split[0], split[1]))
	except:
		pass
	unlock_disk()
	return tasks

# Writes a list of Task objects to the taskfile, overwriting the list currently in the file
def write_tasks(tasks : list):
	lock_disk()
	with open(tasklist_filename, 'w') as f:
		for task in tasks:
			f.write(str(task))
	unlock_disk()


# idx is the index at which to insert the task into the queue. If out of range (default = -1), adds to end
def create_task(type, args, idx=-1):
	task = Task(type, args)
	lock_disk()
	current_list = read_tasks()
	if idx < 0 or idx >= len(current_list):
		current_list.append(task)
	else:
		current_list.insert(idx, task)
	write_tasks(current_list)
	unlock_disk()


def next_task():
	return None
