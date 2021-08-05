
import threading
import subprocess

import MsgQueue as msgq
import Tasks

'''
BgdThread
Handles the background thread that receives and processes messages from MsgQueue
Also handles the creation of subprocesses that run renders and bakes

The "Background Thread" is actually made up of 2 threads:
1. The thread that handles and responds to messages from other threads
2. The thread that waits for the subprocess to finish and then sends a MessageType.COMPLETE message
'''


class BgdThread(threading.Thread):
	def __init__(self):
		threading.Thread.__init__(self)
		self.setName('BgdThread')
		self.cv = threading.Condition()
		self.done = False
		# When subp is None, a new task is allowed to begin
		self.subp = None
		self.last_exit_code = 0
		self.waiting_thread = None

	# The function used by the waiting thread
	def wait_func(self):
		self.last_exit_code = self.subp.wait()
		msgq.add_message(msgq.MessageType.COMPLETE if self.last_exit_code == 0 else msgq.MessageType.FAILED)

	# The main background thread function. Must be named 'run'
	def run(self):
		# done is set to true in killThread
		while not self.done:
			# If subp is None, we're allowed to start a new task
			if self.subp is None:
				task = Tasks.next_task()
				if task is not None:
					self.launch_task(task)
			nextMsg = msgq.next_message()
			if nextMsg != None:
				if nextMsg == msgq.MessageType.QUIT:
					self.quit()
				elif nextMsg == msgq.MessageType.SKIP:
					self.skip()
				elif nextMsg == msgq.MessageType.COMPLETE:
					self.complete()
				elif nextMsg == msgq.MessageType.FAILED:
					self.failed()
			else:
				# There was no message
				self.cv.acquire()
				self.cv.wait()
				self.cv.release()


	def launch_task(self, task):
		return # TODO
		self.waiting_thread = threading.Thread(target = wait_func, args = (self))
		
				
	# Call this to tell the thread to check for newly added messages or tasks
	def notify_thread(self):
		self.cv.acquire()
		self.cv.notify_all()
		self.cv.release()

	def end_subprocess(self):
		if self.subp is not None:
			# We have to kill, not terminate; Blender will not stop a render with normal termination
			subp.kill()
			# TODO: Based on some parameter, either mark this as incomplete or return to task list
		if self.waiting_thread is not None:
			self.waiting_thread.join()
			self.waiting_thread = None


	def quit(self):
		self.done = True
		# End the subprocess if necessary
		self.end_subprocess()

	def skip(self):
		self.end_subprocess()

	def complete(self):
		self.subp = None

	def failed(self):
		self.subp = None

