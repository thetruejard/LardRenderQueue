
import queue

import BgdThread
import __main__

'''
MsgQueue
The Message Queue communicates actions from the main thread and waiting thread to the background thread
This is for things like canceling/skipping tasks and finishing tasks but NOT starting tasks
I.e., these messages are only relevant within one runtime; these messages do not persist across instances
'''


class MessageType:
	SKIP = 's'
	QUIT = 'q'
	COMPLETE = 'c'
	FAILED = 'f'



msg_queue = queue.Queue()



# Adds a message of the specified MessageType
def add_message(type):
	msg_queue.put(type)
	__main__.bgd_thread.notify_thread()



# Gets the next message from the queue if there is one, otherwise returns None
def next_message():
	try:
		return msg_queue.get_nowait()
	except queue.Empty:
		return None