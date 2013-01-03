import time
import unittest
import mock
import websocket
import gevent

import cdx.wsmanager as wsmanager
import test_utils
from cdx.app import app
from cdx import start
import cdx.models.docs as docs
import test_utils

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
        
ws_address = "ws://localhost:5006/cdx/sub"
class TestSubscribeWebSocket(test_utils.CDXServerTestCase):
    def setUp(self):
        super(TestSubscribeWebSocket, self).setUp()
        doc2 = docs.new_doc(app, "defaultdoc2",
                            'main', rw_users=["defaultuser"],
                            apikey='nokey')
    def test_basic_subscribe(self):
        ph = start.app.ph
        sock = websocket.WebSocket()
        connect(sock, ws_address, 'cdxplot:defaultdoc', 'nokey')
        app.wsmanager.send('cdxplot:defaultdoc', 'hello!')
        msg = sock.recv()
        assert msg == 'cdxplot:defaultdoc:hello!'
        sock2 = websocket.WebSocket()
        connect(sock2, ws_address, 'cdxplot:defaultdoc', 'nokey')
        sock3 = websocket.WebSocket()
        connect(sock3, ws_address, 'cdxplot:defaultdoc2', 'nokey')
        app.wsmanager.send('cdxplot:defaultdoc', 'hello2!')        
        app.wsmanager.send('cdxplot:defaultdoc2', 'hello3!')
        msg = sock.recv()
        assert msg == 'cdxplot:defaultdoc:hello2!'
        msg = sock2.recv()
        assert msg == 'cdxplot:defaultdoc:hello2!'
        msg = sock3.recv()
        assert msg == 'cdxplot:defaultdoc2:hello3!'
        
def connect(sock, addr, topic, auth):
    ph = start.app.ph
    sock.io_sock.settimeout(1.0)
    sock.connect(addr)
    msgobj = dict(msgtype='subscribe',
                  topic=topic,
                  auth=auth
                  )
    sock.send(ph.serialize_msg(msgobj))
    msg = sock.recv()
    msgobj = ph.deserialize_msg(msg)
    assert msgobj['status'][:2] == ['subscribesuccess', topic]
