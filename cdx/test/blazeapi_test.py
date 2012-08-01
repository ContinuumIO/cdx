import gevent
import gevent.monkey
gevent.monkey.patch_all()
import gevent_zeromq
gevent_zeromq.monkey_patch()
import zmq

import urllib
import unittest
import simplejson
import numpy as np
import logging
import time
import os
import shelve
import requests

import cdx.webzmqproxy as webzmqproxy
import cdx.test.test_utils as test_utils
import arrayserver.server.arrayserverbroker as arrayserverbroker
import arrayserver.server.arrayservernode as arrayservernode
import arrayserver.server.arrayserverconfig as arrayserverconfig
import arrayserver.server.redisutils as redisutils
import cdx.controllers.maincontroller as maincontroller

logging.basicConfig(level=logging.DEBUG)
log = logging.getLogger(__name__)
logging.debug("starting")

backaddr = "inproc://#1"
frontaddr = "inproc://#2"
addr = "inproc://#3"
baseurl = "http://localhost:5000/"


class ArrayserverApiTestCase(unittest.TestCase):
    def setUp(self):
        self.servername = 'testserver'
        self.redisproc = redisutils.RedisProcess(9000, '/tmp', save=False)
        time.sleep(0.1)
        self.config = arrayserverconfig.ArrayserverConfig(self.servername, port=9000)
        testroot = os.path.abspath(os.path.dirname(__file__))
        hdfpath = os.path.join(testroot, 'gold.hdf5')
        arrayserverconfig.generate_config_hdf5(self.servername, '/hugodata',
                                         hdfpath, self.config)
        broker = arrayserverbroker.ArrayserverBroker(frontaddr, backaddr, self.config)
        broker.start()
        self.broker = broker
        rpcserver = arrayservernode.ArrayserverNode(backaddr, self.servername, self.config)
        rpcserver.start()
        self.rpcserver = rpcserver
        test_utils.wait_until(lambda : len(broker.nodes) > 0)
        maincontroller.prepare_app(frontaddr)
        self.servert = gevent.spawn(maincontroller.start_app)
        time.sleep(0.5)
        
    def tearDown(self):
        if hasattr(self, 'rpcserver'):
            self.rpcserver.kill = True
        if hasattr(self, 'broker'):
            self.broker.kill = True
        if hasattr(self, 'rpcserver'):
            test_utils.wait_until(lambda : self.rpcserver.socket.closed)
            print 'rpcserver closed!'
        if hasattr(self, 'broker'):
            def done():
                return self.broker.frontend.closed and self.broker.backend.closed
            test_utils.wait_until(done)
            print 'broker closed!'            
        #we need this to wait for sockets to close, really annoying
        maincontroller.shutdown_app()
        self.redisproc.close()
        self.servert.kill()
        time.sleep(1.0)
        
    def test_get(self):
        s = requests.session()
        result = s.get(
            baseurl + "data/hugodata/20100217/names",
            timeout = 1.0
            )
        result = simplejson.loads(result.content)
        assert result['data'] == [["GDX"], ["GLD"], ["USO"]]

        s = requests.session()
        result = s.get(
            baseurl + "data/hugodata/20100217",
            timeout = 1.0
            )
        result = simplejson.loads(result.content)
        assert 'names' in result['children']
        print result

    def test_summary(self):
        s = requests.session()
        result = s.get(
            baseurl + "summary/hugodata/20100217/prices",
            timeout = 1.0
            )
        response = simplejson.loads(result.content)
        summary = response['summary']
        columnsummary = response['colsummary']
        assert summary['shape'] == [1561, 3]
        assert summary['colnames'] == [0, 1, 2]
        assert '0' in columnsummary
        assert '2' in columnsummary
        assert columnsummary['1']['mean'] == 64.07833333333333

    def test_bulk_summary(self):
        s = requests.session()
        paths = ["/hugodata/20100217/names", "/hugodata/20100217/prices"]
        #paths = ["/hugodata/20100217/prices"]        
        paths = simplejson.dumps(paths)
        args = urllib.urlencode({'paths' : paths})
        print baseurl + "bulksummary/?" + args
        result = s.get(
            baseurl + "bulksummary?" + args,
            timeout = 1.0
            )
        responses = simplejson.loads(result.content)
        for idx, response in enumerate(responses):
            if idx == 0 :
                continue
            summary = response['summary']
            columnsummary = response['colsummary']
            assert summary['shape'] == [1561, 3]
            assert summary['colnames'] == [0, 1, 2]
            assert '0' in columnsummary
            assert '2' in columnsummary
            assert columnsummary['1']['mean'] == 64.07833333333333


    
        

if __name__ == "__main__":
    unittest.main()
