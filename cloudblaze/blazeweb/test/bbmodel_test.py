import time
import unittest
import mock
import websocket
import gevent

import blaze.server.tests.test_utils as test_utils
import blaze.server.redisutils as redisutils
from cloudblaze.blazeweb.app import app
import cloudblaze.blazeweb.start as start
import cloudblaze.continuumweb.bbmodel as bbmodel

frontaddr = "tcp://127.0.0.1:6000"

class TestBBModel(unittest.TestCase):
    def setUp(self):
        start.prepare_app(frontaddr, timeout=0.1)        
        self.servert = gevent.spawn(start.start_app)
        self.client = bbmodel.ContinuumModelsClient(
            "mydoc", "http://localhost:5000/bb/", app.ph)
        self.client2 = bbmodel.ContinuumModelsClient(
            "mydoc2", "http://localhost:5000/bb/", app.ph)
        self.redisproc = redisutils.RedisProcess(6379, '/tmp', save=False)
        time.sleep(0.1)
        
    def tearDown(self):
        start.shutdown_app()
        self.servert.kill()
        self.redisproc.close()        
        time.sleep(1.0)

        
    def test_create(self):
        test_utils.wait_until(lambda : start.http_server.started)
        client = self.client
        client.create('Test', dict(testval=1, id='foo'))
        test_utils.wait_until(lambda : app.collections.get('Test', 'foo'))
        assert app.collections.get('Test', 'foo').get('testval') == 1
        assert client.fetch('Test', 'foo').get('testval') == 1

    def test_update(self):
        test_utils.wait_until(lambda : start.http_server.started)
        client = self.client        
        client.create('Test', dict(testval=1, id='foo'))
        client.update('Test', dict(id='foo', testval=2))
        test_utils.wait_until(
            lambda : app.collections.get('Test', 'foo').get('testval') == 2
            )
        assert app.collections.get('Test', 'foo').get('testval') == 2
        assert client.get('Test', 'foo').get('testval') == 2
        
    def test_fetch_type(self):
        test_utils.wait_until(lambda : start.http_server.started)
        client = self.client
        client.create('Test', dict(testval=1, id='foo'))
        client.create('Test2', dict(testval=1, id='foo2'))
        models = client.fetch(typename='Test')
        assert len(models) == 1 and models[0].get('id') == 'foo'
        
    def test_fetch_docid(self):
        test_utils.wait_until(lambda : start.http_server.started)
        client = self.client
        client2 = self.client2
        client.create('Test', dict(testval=1, id='foo'))
        client.create('Test2', dict(testval=1, id='foo2'))
        client2.create('Test', dict(testval=1, id='foo3'))
        client2.create('Test2', dict(testval=1, id='foo4'))
        assert client.get('Test', 'foo').get('testval') == 1
        assert client.get('Test', 'foo3') is None
        assert client2.get('Test2', 'foo2') is None
        assert client2.get('Test', 'foo3').get('testval') == 1
        
    def test_delete(self):
        test_utils.wait_until(lambda : start.http_server.started)
        client = self.client                
        client.create('Test', dict(testval=1, id='foo'))
        client.create('Test', dict(testval=1, id='foo2'))
        client.delete('Test', 'foo')
        assert client.get('Test', 'foo') is None
        assert client.get('Test', 'foo2') is not None
        
