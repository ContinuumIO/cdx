import unittest
import blazeweb.wsmanager as wsmanager
import mock

class WsmanagerTestCase(unittest.TestCase):
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
        
        
