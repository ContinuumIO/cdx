import time
import unittest
import mock
import websocket
import gevent

import blaze.server.tests.test_utils as test_utils
from blazeweb.app import app
import blazeweb.start as start
import continuumweb.bbmodel as bbmodel

frontaddr = "tcp://127.0.0.1:6000"

class TestSubscribeWebSocket(unittest.TestCase):
    def setUp(self):
        start.prepare_app(frontaddr, timeout=0.1)        
        self.servert = gevent.spawn(start.start_app)

    def tearDown(self):
        start.shutdown_app()
        self.servert.kill()
        time.sleep(1.0)

    def test_create(self):
        test_utils.wait_until(lambda : start.http_server.started)
        client = bbmodel.ContinuumModels(
            bbmodel.ContinuumModelsStorage(),
            bbmodel.ContinuumModelsClient(
                "mydoc", "http://localhost:5000/bb/", app.ph))
        client.create('Test', dict(testval=1, id='foo'))
        test_utils.wait_until(lambda : app.collections.get('Test', 'foo'))
        assert app.collections.get('Test', 'foo').get('testval') == 1
        assert client.get('Test', 'foo').get('testval') == 1

    def test_update(self):
        test_utils.wait_until(lambda : start.http_server.started)
        client = bbmodel.ContinuumModels(
            bbmodel.ContinuumModelsStorage(),
            bbmodel.ContinuumModelsClient(
                "mydoc", "http://localhost:5000/bb/", app.ph))
        client.create('Test', dict(testval=1, id='foo'))
        client.update('Test', dict(id='foo', testval=2))
        test_utils.wait_until(
            lambda : app.collections.get('Test', 'foo').get('testval') == 2
            )
        assert app.collections.get('Test', 'foo').get('testval') == 2
        assert client.get('Test', 'foo').get('testval') == 2
        
    def test_fetch_type(self):
        test_utils.wait_until(lambda : start.http_server.started)
        client = bbmodel.ContinuumModels(
            bbmodel.ContinuumModelsStorage(),
            bbmodel.ContinuumModelsClient(
                "mydoc", "http://localhost:5000/bb/", app.ph))
        client.create('Test', dict(testval=1, id='foo'))
        client.create('Test2', dict(testval=1, id='foo2'))
        client = bbmodel.ContinuumModels(
            bbmodel.ContinuumModelsStorage(),
            bbmodel.ContinuumModelsClient(
                "mydoc", "http://localhost:5000/bb/", app.ph))
        assert client.get('Test', 'foo') is None
        client.fetch(typename='Test')
        assert client.get('Test', 'foo').get('testval') == 1
        assert client.get('Test2', 'foo2') is None
        
    def test_fetch_docid(self):
        test_utils.wait_until(lambda : start.http_server.started)
        client = bbmodel.ContinuumModels(
            bbmodel.ContinuumModelsStorage(),
            bbmodel.ContinuumModelsClient(
                "mydoc", "http://localhost:5000/bb/", app.ph))
        client.create('Test', dict(testval=1, id='foo'))
        client.create('Test2', dict(testval=1, id='foo2'))
        client = bbmodel.ContinuumModels(
            bbmodel.ContinuumModelsStorage(),
            bbmodel.ContinuumModelsClient(
                "mydoc2", "http://localhost:5000/bb/", app.ph))
        client.create('Test', dict(testval=1, id='foo3'))
        client.create('Test2', dict(testval=1, id='foo4'))
        client = bbmodel.ContinuumModels(
            bbmodel.ContinuumModelsStorage(),
            bbmodel.ContinuumModelsClient(
                "mydoc", "http://localhost:5000/bb/", app.ph))
        client.fetch()
        assert client.get('Test', 'foo').get('testval') == 1
        assert client.get('Test', 'foo3') is None
        
        client = bbmodel.ContinuumModels(
            bbmodel.ContinuumModelsStorage(),
            bbmodel.ContinuumModelsClient(
                "mydoc2", "http://localhost:5000/bb/", app.ph))
        client.fetch()        
        assert client.get('Test2', 'foo2') is None
        assert client.get('Test', 'foo3').get('testval') == 1
    def test_delete(self):
        test_utils.wait_until(lambda : start.http_server.started)
        client = bbmodel.ContinuumModels(
            bbmodel.ContinuumModelsStorage(),
            bbmodel.ContinuumModelsClient(
                "mydoc", "http://localhost:5000/bb/", app.ph))
        client.create('Test', dict(testval=1, id='foo'))
        client.create('Test', dict(testval=1, id='foo2'))
        client.delete('Test', 'foo')
        assert client.get('Test', 'foo') is None
        assert client.get('Test', 'foo2') is not None
        client = bbmodel.ContinuumModels(
            bbmodel.ContinuumModelsStorage(),
            bbmodel.ContinuumModelsClient(
                "mydoc", "http://localhost:5000/bb/", app.ph))
        client.fetch()
        assert client.get('Test', 'foo') is None
        assert client.get('Test', 'foo2') is not None
        
