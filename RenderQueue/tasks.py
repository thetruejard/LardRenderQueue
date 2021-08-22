
from pathlib import Path
import subprocess

import taskfile


'''
tasks
Runs tasks of all types. Also has some utilities to validate files and task arguments
'''



brender_path = Path(__file__).parent.joinpath('brender.py').absolute()

blender_path = "blender"



def is_valid_file(file : Path):
	file = Path(file)
	return file.exists() and file.is_file()

def is_valid_blend(file : Path):
	file = Path(file)
	return is_valid_file(file) and file.suffix == '.blend'



def launch_blender(filename, script, extra_args):
	if not is_valid_blend(filename):
		# TODO: raise a warning and fail the task
		print('some warning 2')
		return None
	try:
		return subprocess.Popen(
			f'{blender_path} -b "{filename}" -P "{script}" -- {extra_args}',
			creationflags=subprocess.CREATE_NEW_CONSOLE)
	except OSError:
		# TODO: blender not found warning
		print("blender not found warning")
		return None



# Launches a task and returns a subprocess.Popen object. Assign this to BgdThread.subp
# If the task failed to launch, returns None
def run_task(task : taskfile.Task):
	if task.type == taskfile.TaskType.RENDER_ANIMATION:
		return render_animation(task.args)
	elif task.type == taskfile.TaskType.RENDER_STILL:
		return render_still(task.args)
	elif task.type == taskfile.TaskType.BAKE:
		return bake(task.args)
	else:
		# TODO: Log a warning of some kind
		print('some warning 1')
		return None

def render_animation(args):
	splitargs = args.split(' ')
	filename = splitargs[0]
	# Arg 0: whether to render an animation (if false, then this is a still image)
	return launch_blender(filename, brender_path, '1')
	

def render_still(args):
	splitargs = args.split(' ')
	filename = splitargs[0]
	# Arg 0: whether to render an animation (if false, then this is a still image)
	return launch_blender(filename, brender_path, '0')


def bake(args):
	pass