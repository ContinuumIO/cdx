import uuid

import gevent
import gevent.monkey
gevent.monkey.patch_all()
import gevent_zeromq
gevent_zeromq.monkey_patch()
import zmq

import blaze.server.tests
import blaze.server.redisutils as redisutils
import blaze.server.blazeconfig as blazeconfig
import blaze.server.blazeconfig.orderedyaml as orderedyaml
import blaze.server.blazenode as blazenode
import blaze.server.blazebroker as blazebroker
import blaze.server.scripts.run as run

import time
import redis
import sys
import yaml
import os
import logging
import posixpath as blazepath
import cloudblaze.blazeweb.controllers.maincontroller as maincontroller
import collections

log = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG)
import os.path
import argparse

def main():
    parser = run.argparser()
    args = parser.parse_args()
    run.write_pid(args.datapath, 'CDX')    
    redisproc, broker, node = run.start_blaze(args)
    maincontroller.prepare_app(args.front_address, rhost=args.redis_host,
                               rport=args.redis_port)
    maincontroller.start_app()
    
if __name__ == "__main__":
    main()
    
