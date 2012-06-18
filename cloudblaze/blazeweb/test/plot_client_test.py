import time
import unittest
import mock
import websocket
import gevent
import requests

import blaze.server.tests.test_utils as test_utils
from cloudblaze.blazeweb.app import app
import cloudblaze.blazeweb.start as start
import cloudblaze.continuumweb.bbmodel as bbmodel
import cloudblaze.continuumweb.plot as plot

frontaddr = "tcp://127.0.0.1:6000"
class TestPlotClient(unittest.TestCase):
    def setUp(self):
        start.prepare_app(frontaddr, timeout=0.1)        
        self.servert = gevent.spawn(start.start_app)

    def tearDown(self):
        start.shutdown_app()
        self.servert.kill()
        time.sleep(1.0)

    # def test_fetch_populates(self):
    #     test_utils.wait_until(lambda : start.http_server.started)
    #     requests.get('http://localhost:5000/interactive/mydoc')
    #     client = plot.PlotClient("mydoc", "http://localhost:5000/bb/")
    #     assert client.ic is not None

