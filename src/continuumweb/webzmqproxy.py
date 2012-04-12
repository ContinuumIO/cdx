import gevent
import gevent.monkey
gevent.monkey.patch_all()
from gevent_zeromq import zmq
from gevent.queue import Queue

import threading
import uuid
import time


class ProxyClient(threading.Thread):
	def __init__(self, pushpulladdr, pubsubaddr, timeout=0.5, ctx=None):
		if ctx is None:
			ctx = zmq.Context()
		self.ctx = ctx
		self.pushpulladdr = pushpulladdr
		self.pubsubaddr = pubsubaddr
		self.queues = {}
		self.send_queue = Queue()
		self.timeout = timeout
		super(ProxyClient, self).__init__()
		
	def run_send(self):
		print 'runsend'
		self.push = self.ctx.socket(zmq.PUSH)
		self.push.connect(self.pushpulladdr)
		counter = 0.
		while True:
			print 'runing send'
			try:
				messages = self.send_queue.get(timeout=self.timeout)
			except:
				counter += 1
				if counter < 20:
					continue
				else:
					break
			print 'sending', messages
			self.push.send_multipart(messages)
	
	def run_recv(self):
		self.sub = self.ctx.socket(zmq.SUB)
		self.sub.setsockopt(zmq.SUBSCRIBE,'')
		self.sub.connect(self.pubsubaddr)
		print 'subloop'
		while True:
			messages = self.sub.recv_multipart()
			print 'sub received', messages
			ident = messages[-1]
			messages = messages[:-1]
			if ident in self.queues:
				self.queues[ident].put(messages)
			
	def run(self):
		t = threading.Thread(target=self.run_send)
		t.start()
		self.run_recv()
		t.join()
		
	def request(self, messages):
		ident = str(uuid.uuid4())
		queue = Queue()
		self.queues[ident] = queue
		messages.append(ident)
		self.send_queue.put(messages)
		returnval = self.queues[ident].get()
		del self.queues[ident]
		return returnval
	
class Proxy(threading.Thread):
	def __init__(self, reqrepaddr, pushpulladdr, pubsubaddr, ctx=None):
		if ctx is None:
			ctx = zmq.Context()
		self.dealer = ctx.socket(zmq.DEALER)
		self.dealer.connect(reqrepaddr)

		self.pull = ctx.socket(zmq.PULL)
		self.pull.bind(pushpulladdr)

		self.pub = ctx.socket(zmq.PUB)
		self.pub.bind(pubsubaddr)
		super(Proxy, self).__init__()
		
	def run(self):
		poller = zmq.Poller()
		poller.register(self.dealer, zmq.POLLIN)
		poller.register(self.pull, zmq.POLLIN)

		while True:
			socks = dict(poller.poll())
			if self.dealer in socks:
				msg = self.dealer.recv_multipart()
				payload = msg[msg.index('')+1:]
				self.pub.send_multipart(payload)
			if self.pull in socks:
				msg = self.pull.recv_multipart()
				msg.insert(0, '')
				self.dealer.send_multipart(msg)
		
	
