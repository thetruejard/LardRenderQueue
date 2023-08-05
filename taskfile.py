
import threading
import pathlib
import json
from datetime import timedelta
import os

'''
taskfile
Handles all types of tasks, interfacing with file(s) to track queued bakes and renders

There are 2 files that this module interfaces with:
1. taskfile.dat: Stores the list of tasks that need to be completed
2. currenttask.dat: Stores information about the task that is currently running
	- This task is NOT also stored in the taskfile
3. completed.dat: Stores the list of all tasks that have been completed
4. failed.dat: Stores the list of all tasks that have failed
'''

# The name of the file in which tasks are stored. The current working directory is used
# If this is changed, the .gitignore file must be updated too (see bottom of .gitignore)
tasklist_filename = 'tasks/tasklist.txt'
# Each task in the taskfile is one line of text followed by a newline

# The name of the file in which info about the current task is stored. The cwd is used
currenttask_filename = 'tasks/currenttask.txt'

# The name of the file in which the list of completed tasks is stored. The cwd is used
completed_filename = 'tasks/completed.txt'

# The name of the file in which the list of failed tasks is stored. The cwd is used
failed_filename = 'tasks/failed.txt'


class TaskType:
	RENDER_ANIMATION = 'ra'
	RENDER_STILL = 'rs'
	BAKE = 'b'
	def get_name(type):
		if type == TaskType.RENDER_ANIMATION:
			return 'Render Animation'
		elif type == TaskType.RENDER_STILL:
			return 'Render Still'
		elif type == TaskType.BAKE:
			return 'Bake Dynamics'


class Task:
	def __init__(self, type, args : str, time : float = 0):
		self.type = type
		self.args = args
		self.time = time
	
	def time_str(self):
		return str(timedelta(seconds=round(self.time)))

	def __str__(self):
		return f'{self.type} {self.time} ' + json.dumps(self.args)

	def desc(self):
		return f'{TaskType.get_name(self.type)}' + \
			f'\n\t- Elapsed: {self.time_str()}' + \
			f'\n\t- File: {self.args[0]}'

	def parse(line):
		if line[-1] == '\n':
			line = line[:-1]
		split = line.split(sep=' ', maxsplit=2)
		return Task(split[0], json.loads(split[2]), float(split[1]))

class CompletedTask(Task):
	def __init__(self, task):
		super().__init__(task.type, task.args, task.time)

class FailedTask(Task):
	# TODO: add more args (such as time until fail, etc.)
	def __init__(self, task, exit_code):
		super().__init__(task.type, task.args, task.time)
		self.exit_code = exit_code

	def __str__(self):
		return f'{self.exit_code} ' + super().__str__()

	def desc(self):
		return super().desc() + f'\n\t- Exit code: {self.exit_code}'

	def parse(line):
		split = line.split(sep=' ', maxsplit=1)
		task = Task.parse(split[1])
		return FailedTask(task, int(split[0]))


disk_mutex = threading.RLock()

# Locks the task list on disk
# This is a recursive operation, i.e. it can be locked multiple times (and must be unlocked multiple times)
def lock_disk():
	disk_mutex.acquire()
def unlock_disk():
	disk_mutex.release()

# Utility: writes the given list of elements to the given file using str() and newlines
def write_list(filename, elements : list):
	lock_disk()
	with open(filename, 'w') as f:
		for e in elements:
			f.write(str(e) + '\n')
	unlock_disk()

# Utility: returns a list of type from the given file using type.parse() separated by newlines
# If num is positive, only reads the first num elements
def read_list(filename, type, num=-1) -> list:
	elements = []
	if os.path.exists(filename):
		lock_disk()
		try:
			with open(filename, 'r') as f:
				lines = f.readlines()
			if len(lines) > num > 0:
				lines = lines[:num]
			for line in lines:
				elements.append(type.parse(line))
		except Exception as e:
			print(f'Exception while loading task list "{filename}": {e}')
		unlock_disk()
	return elements


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
	return read_list(tasklist_filename, Task)

# Writes a list of Task objects to the taskfile, overwriting the list currently in the file
def write_tasks(tasks : list):
	write_list(tasklist_filename, tasks)


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
	current = get_current_task()
	if current is not None:
		unlock_disk()
		return current
	tasks = read_tasks()
	if len(tasks) == 0:
		unlock_disk()
		return None
	next = tasks[0]
	tasks = tasks[1:]
	write_tasks(tasks)
	unlock_disk()
	return next

# Clears the queue of all tasks. Does not affect the current task
def clear_tasks():
	lock_disk()
	path = pathlib.Path(tasklist_filename)
	if path.exists():
		path.unlink()
	unlock_disk()


def clear_current_task():
	lock_disk()
	path = pathlib.Path(currenttask_filename)
	if path.exists():
		path.unlink()
	unlock_disk()
		

# Returns a Task object defining the current task, or None if none
def get_current_task():
	lock_disk()
	path = pathlib.Path(currenttask_filename)
	if not path.exists():
		unlock_disk()
		return None
	with open(currenttask_filename, 'r') as f:
		lines = f.readlines()
		for line in lines:
			# TODO: parse other lines if necessary. For now just returns the first one
			unlock_disk()
			return Task.parse(line)
	unlock_disk()


def make_task_current(task : Task):
	lock_disk()
	clear_current_task()
	with open(currenttask_filename, 'w') as f:
		f.write(str(task))
	unlock_disk()



# Writes the given list of CompletedTasks to disk
def write_completed(tasks : list):
	write_list(completed_filename, tasks)

# Reads the first num completed tasks. If num is negative, returns all completed tasks
def read_completed(num=-1) -> list:
	return read_list(completed_filename, CompletedTask, num)

# Adds the given task to the list of completed tasks
def add_completed(task : CompletedTask):
	lock_disk()
	tasks = read_completed()
	tasks.insert(0, task)
	write_completed(tasks)
	unlock_disk()

# Clears the list of completed tasks. If keep is positive, clears all except the most recent keep tasks
def clear_completed(keep=-1):
	if keep > 0:
		lock_disk()
		tasks = read_completed()
		tasks = tasks[keep - 1:]
		write_completed(tasks)
		unlock_disk()
	else:
		lock_disk()
		path = pathlib.Path(completed_filename)
		if path.exists():
			path.unlink()
		unlock_disk()



# Writes the given list of FailedTasks to disk
def write_failed(tasks : list):
	write_list(failed_filename, tasks)

# Reads the first num failed tasks. If num is negative, returns all failed tasks
def read_failed(num=-1) -> list:
	return read_list(failed_filename, FailedTask, num)

# Adds the given task to the list of failed tasks
def add_failed(task : FailedTask):
	lock_disk()
	tasks = read_failed()
	tasks.insert(0, task)
	write_failed(tasks)
	unlock_disk()

# Clears the list of failed tasks. If keep is positive, clears all except the most recent keep tasks
def clear_failed(keep=-1):
	if keep > 0:
		lock_disk()
		tasks = read_failed()
		tasks = tasks[keep - 1:]
		write_failed(tasks)
		unlock_disk()
	else:
		lock_disk()
		path = pathlib.Path(failed_filename)
		if path.exists():
			path.unlink()
		unlock_disk()
