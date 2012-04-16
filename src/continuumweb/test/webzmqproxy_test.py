import gevent
import gevent.monkey
gevent.monkey.patch_all()
import gevent_zeromq
gevent_zeromq.monkey_patch()

import zmq
import unittest
import test_utils as test_utils

import continuumweb.webzmqproxy as webzmqproxy
import threading
import logging
log = logging.getLogger(__name__)
pubsub = "inproc://#1"
reqrep = "inproc://#2"
pushpull = "inproc://#3"

class ProxyTestCase(unittest.TestCase):
    def echo(self, socket):
        poller = zmq.Poller()
        poller.register(socket, zmq.POLLIN)
        try:
            while not self.kill:
                socks = dict(poller.poll(timeout=1000.0))
                if socket in socks:
                    m = socket.recv_multipart()
                    print 'echo received', m
                    socket.send_multipart(m)
        except zmq.ZMQError as e:
            log.exception(e)
        finally:
            print 'echo shutting down'
            socket.close()
            
    def setUp(self):
        self.kill = False
        
    def tearDown(self):
        self.kill = True
        if hasattr(self, 'proxy'):
            print 'setting kill, proxy'
            self.proxy.kill = True
        if hasattr(self, 'client'):
            print 'setting kill, client'
            self.client.kill = True
            
    def test_proxy(self):
        ctx = zmq.Context()
        repsocket = ctx.socket(zmq.REP)
        repsocket.bind(reqrep)
        t = threading.Thread(target=self.echo, args = (repsocket,))
        t.start()
        proxy = webzmqproxy.Proxy(reqrep, pushpull, pubsub, ctx=ctx)
        proxy.start()
        self.proxy = proxy
        push = ctx.socket(zmq.PUSH)
        sub = ctx.socket(zmq.SUB)
        sub.setsockopt(zmq.SUBSCRIBE,'')
        push.connect(pushpull)
        sub.connect(pubsub)
        push.send('hello')
        result = test_utils.recv_timeout(sub, 10000)
        print result
        assert result == ['hello']
        
    def test_proxy_client(self):
        ctx = zmq.Context()
        repsocket = ctx.socket(zmq.REP)
        repsocket.bind(reqrep)
        t = threading.Thread(target=self.echo, args = (repsocket,))
        t.start()
        proxy = webzmqproxy.Proxy(reqrep, pushpull, pubsub, ctx=ctx)
        proxy.start()
        self.proxy = proxy
        client = webzmqproxy.ProxyClient(pushpull, pubsub, ctx=ctx)
        client.start()
        self.client = client
        result = client.request(['hello'])
        assert result == ['hello']


if __name__ == "__main__":
    unittest.main()
