import uuid

import gevent
import gevent.monkey
gevent.monkey.patch_all()
import gevent_zeromq
gevent_zeromq.monkey_patch()
import zmq

import arrayserver.server.tests
import arrayserver.server.redisutils as redisutils
import arrayserver.server.arrayserverconfig as arrayserverconfig
import arrayserver.server.arrayserverconfig.orderedyaml as orderedyaml
import arrayserver.server.arrayservernode as arrayservernode
import arrayserver.server.arrayserverbroker as arrayserverbroker
import arrayserver.server.scripts.run as run

import time
import redis
import sys
import socket
import yaml
import os
import logging
import posixpath as arrayserverpath
import cdx.controllers.maincontroller as maincontroller
import collections
log = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG)
import os.path
import argparse

def main():
    parser = run.argparser()
    args = parser.parse_args()
    run.write_pid(args.datapath, 'CDX')    
    redisproc, broker, node = run.start_arrayserver(args)
    maincontroller.prepare_app(args.front_address, rhost=args.redis_host,
                               rport=args.redis_port)
    try:
        maincontroller.start_app()
    except socket.error as e:
        log.error('port unavailable, is CDX already running?')
        log.error('shutting it all down')
        broker.kill = True
        node.kill = True
        maincontroller.shutdown_app()

if __name__ == "__main__":
    main()
    
