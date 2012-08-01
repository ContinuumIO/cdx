import time
import unittest
import mock
import websocket
import gevent

import cdx.wsmanager as wsmanager
import arrayserver.server.tests.test_utils as test_utils
from cdx.app import app
import cdx.controllers.maincontroller as maincontroller


class WSmanagerTestCase(unittest.TestCase):
    def test_some_topics(self):
        manager = wsmanager.WebSocketManager()
        s1 = mock.Mock()
        s2 = mock.Mock()
        manager.subscribe_socket(s1, '1', clientid='11')
        manager.subscribe_socket(s2, '1', clientid='12')
        manager.send('1', 'hello')
        assert s1.send.call_count == 1
        assert s2.send.call_count == 1
        manager.remove_clientid('11')
        manager.send('1', 'hello')
        assert s2.send.call_count == 2
        assert s1.send.call_count == 1
        
frontaddr = "tcp://127.0.0.1:6000"
ws_address = "ws://localhost:5000/sub"
class TestSubscribeWebSocket(unittest.TestCase):
    def setUp(self):
        maincontroller.prepare_app(frontaddr)        
        self.servert = gevent.spawn(maincontroller.start_app)

    def tearDown(self):
        time.sleep(1.0)
        maincontroller.shutdown_app()
        self.servert.kill()
        
    def test_basic_subscribe(self):
        ph = maincontroller.app.ph
        test_utils.wait_until(lambda : maincontroller.http_server.started)
        sock = websocket.WebSocket()
        connect(sock, ws_address, 'mytopic')
        app.wsmanager.send('mytopic', 'hello!')
        msg = sock.recv()
        assert msg == 'hello!'
        sock2 = websocket.WebSocket()
        connect(sock2, ws_address, 'mytopic')
        sock3 = websocket.WebSocket()
        connect(sock3, ws_address, 'anothertopic')
        app.wsmanager.send('mytopic', 'hello2!')        
        app.wsmanager.send('anothertopic', 'hello3!')
        msg = sock.recv()
        assert msg == 'hello2!'
        msg = sock2.recv()
        assert msg == 'hello2!'
        msg = sock3.recv()
        assert msg == 'hello3!'
        
def connect(sock, addr, topic):
    ph = maincontroller.app.ph    
    sock.io_sock.settimeout(1.0)
    sock.connect(addr)
    msgobj = dict(msgtype='subscribe',
                  topic=topic)
    sock.send(ph.serialize_msg(msgobj))
    msg = sock.recv()
    msgobj = ph.deserialize_msg(msg)
    assert msgobj['status'][:2] == ['subscribesuccess', topic]
