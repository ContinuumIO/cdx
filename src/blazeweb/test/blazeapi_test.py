import gevent
import gevent.monkey
gevent.monkey.patch_all()
import gevent_zeromq
gevent_zeromq.monkey_patch()
import zmq

import unittest
import continuumweb.webzmqproxy as webzmqproxy
import continuumweb.test.test_utils as test_utils

import threading

import requests
import blazeweb.start as start
import urllib
import time
import simplejson

reqrep = "inproc://#4"
baseurl = "http://localhost:5000/data/"

class BlazeApiTestCase(unittest.TestCase):
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
        self.ctx = zmq.Context()
        repsocket = self.ctx.socket(zmq.REP)
        repsocket.bind(reqrep)
        self.echot = threading.Thread(target=self.echo, args = (repsocket,))
        self.echot.start()
        start.prepare_app(reqrep, self.ctx)
        self.servert = gevent.spawn(start.start_app)
        time.sleep(0.5)
        # self.servert = threading.Thread(target=start.start_app)
        # self.servert.start()

    def tearDown(self):
        self.kill = True
        start.shutdown_app()
        self.servert.kill()
        #self.ctx.term()

    def test_get(self):
        s = requests.session()
        result = s.get(
            baseurl + "datasets/mydata?" + urllib.urlencode({'message' : 'hello'}),
            timeout = 1.0
            )
        result = simplejson.loads(result.content)
        assert result['path'] == "datasets/mydata"
        assert result['message'] == 'hello'

    def test_patch(self):
        s = requests.session()
        result = s.patch(
            baseurl + "datasets/mydata",
            timeout = 10.0,
            data = {'message' : 'hello'}
            )
        result = simplejson.loads(result.content)
        assert result['path'] == "datasets/mydata"
        assert result['message'] == 'hello'

    def test_delete(self):
        s = requests.session()
        result = s.delete(
            baseurl + "datasets/mydata",
            timeout = 10.0,
            )
        result = simplejson.loads(result.content)
        assert result['path'] == "datasets/mydata"

    def test_create(self):
        s = requests.session()
        result = s.post(
            baseurl + "datasets/mydata",
            timeout = 10.0,
            data = {'message' : 'hello'}            
            )
        result = simplejson.loads(result.content)
        assert result['path'] == "datasets/mydata"
        assert result['message'] == 'hello'
