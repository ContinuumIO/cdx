import gevent
import gevent.monkey
gevent.monkey.patch_all()
from gevent_zeromq import zmq
import unittest
import test_utils as test_utils

import webzmqproxy
import threading
pubsub = "inproc://#1"
reqrep = "inproc://#2"
pushpull = "inproc://#3"

class ProxyTestCase(unittest.TestCase):
	def echo(self, socket):
		while True:
			m = socket.recv_multipart()
			print 'echo received', m
			socket.send_multipart(m)
			
	def test_proxy(self):
		ctx = zmq.Context()
		repsocket = ctx.socket(zmq.REP)
		repsocket.bind(reqrep)
		proxy = webzmqproxy.Proxy(reqrep, pushpull, pubsub, ctx=ctx)
		proxy.start()
		t = threading.Thread(target=self.echo, args = (repsocket,))
		t.start()

		push = ctx.socket(zmq.PUSH)
		sub = ctx.socket(zmq.SUB)
		sub.setsockopt(zmq.SUBSCRIBE,'')
		push.connect(pushpull)
		sub.connect(pubsub)
		push.send('hello')
		result = test_utils.recv_timeout(sub, 10000)
		print result
		assert result == ['hello']

		
