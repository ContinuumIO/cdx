import gevent
import gevent.monkey
gevent.monkey.patch_all()
from gevent_zeromq import zmq
import threading

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
		
	
