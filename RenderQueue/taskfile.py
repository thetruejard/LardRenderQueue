
import threading
import pathlib

'''
taskfile
Handles all types of tasks, interfacing with file(s) to track queued bakes and renders

There are 2 files that this module interfaces with:
1. taskfile.dat: Stores the list of tasks that need to be completed
2. currenttask.dat: Stores information about the task that is currently running
	- This task is NOT also stored in the taskfile
'''

# The name of the file in which tasks are stored. The current working directory is used
# If this is changed, the .gitignore file must be updated too (see bottom of .gitignore)
tasklist_filename = 'tasklist.dat'
# Each task in the taskfile is one line of text followed by a newline

# The name of the file in which info about the current task is stored. The cwd is used
currenttask_filename = 'currenttask.dat'


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

	def parse(line):
		if line[-1] == '\n':
			line = line[:-1]
		split = line.split(sep=' ', maxsplit=1)
		return Task(split[0], split[1])


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
			tasks.append(Task.parse(line))
	except:
		pass
	unlock_disk()
	return tasks

# Writes a list of Task objects to the taskfile, overwriting the list currently in the file
def write_tasks(tasks : list):
	lock_disk()
	with open(tasklist_filename, 'w') as f:
		for task in tasks:
			f.write(str(task) + '\n')
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


# Make sure to call clear_current_task() first is appropriate
# If a current task exists, returns that one. Otherwise, retrieves the next one from a list
def next_task():
	lock_disk()
	if pathlib.Path(currenttask_filename).exists():
		with open(currenttask_filename, 'r') as f:
			lines = f.readlines()
		for line in lines:
			# TODO: parse other lines if necessary. For now just returns the first one
			unlock_disk()
			return Task.parse(line)
	tasks = read_tasks()
	if len(tasks) == 0:
		unlock_disk()
		return None
	next = tasks[0]
	tasks = tasks[1:]
	write_tasks(tasks);
	unlock_disk()
	return next


def clear_current_task():
	lock_disk()
	path = pathlib.Path(currenttask_filename)
	if path.exists():
		path.unlink()
	unlock_disk()
		


def make_task_current(task : Task):
	lock_disk()
	clear_current_task()
	with open(currenttask_filename, 'w') as f:
		f.write(str(task))
	unlock_disk()