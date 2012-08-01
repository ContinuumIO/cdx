import time
from gevent_zeromq import zmq

def wait_until(func, timeout=1.0, interval=0.01):
    st = time.time()
    while True:
        if func():
            return True
        if (time.time() - st) > interval:
            return False
        time.sleep(interval)

def recv_timeout(socket, timeout):
	poll = zmq.Poller()
	poll.register(socket, zmq.POLLIN)
	socks = dict(poll.poll(timeout=timeout))
	if socks.get(socket, None) == zmq.POLLIN:
		return socket.recv_multipart()
	else:
		return None
	
