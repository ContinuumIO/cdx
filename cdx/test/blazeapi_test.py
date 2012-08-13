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
import arrayserver.server.tests.test_utils as atest_utils
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


class ArrayServerApiTestCase(atest_utils.ArrayServerWithDataTestCase):
    testroot = os.path.abspath(os.path.dirname(__file__))        
    def setUp(self):
        super(ArrayServerApiTestCase, self).setUp()
        maincontroller.prepare_app(frontaddr, timeout=1.0)
        self.servert = gevent.spawn(maincontroller.start_app)
        time.sleep(0.5)
        
    def tearDown(self):
        super(ArrayServerApiTestCase, self).tearDown()
        maincontroller.shutdown_app()
        self.servert.kill()
        time.sleep(1.0)        

        
    def test_get(self):
        s = requests.session()
        result = s.get(
            baseurl + "data/arrayserver/data/random.hdf5/a",
            timeout = 1.0
            )
        result = simplejson.loads(result.content)
        assert result['data'] == self.hdf5data_a.tolist()

        s = requests.session()
        result = s.get(
            baseurl + "data/arrayserver/data/random.hdf5",
            timeout = 1.0
            )
        result = simplejson.loads(result.content)
        assert 'a' in result['children']

    def test_summary(self):
        s = requests.session()
        result = s.get(
            baseurl + 'summary/arrayserver/data/random.hdf5/a',
            timeout = 1.0
            )
        response = simplejson.loads(result.content)
        summary = response['summary']
        columnsummary = response['colsummary']
        assert summary['shape'] == list(self.hdf5data_a.shape)
        assert summary['colnames'] == [0, 1]
        assert '0' in columnsummary
        assert columnsummary['1']['mean'] == 0.43365650027370206

    def test_bulk_summary(self):
        s = requests.session()
        paths = ["/arrayserver/data/random.hdf5/a"]
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
            summary = response['summary']
            columnsummary = response['colsummary']
            assert summary['shape'] == list(self.hdf5data_a.shape)
            assert summary['colnames'] == [0, 1]
            assert '0' in columnsummary
            assert columnsummary['1']['mean'] == 0.43365650027370206


    
        

if __name__ == "__main__":
    unittest.main()
