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

#load a directory full of hdf5 files
def init_dir(datadir, disco=None):
    # datadir will have redis.db, redis.log, and a data directory,
    # as well as a blaze.config
    config_path = os.path.join(datadir, 'blaze.config')
    if not os.path.exists(config_path):
        base_config = os.path.join(os.path.abspath(os.path.dirname(__file__)),
                                   'default_config.yaml')
        with open(base_config) as f:
            config = f.read()
        config = config % {'datapath' : datadir}
        yamlconfig =yaml.load(config, Loader=orderedyaml.OrderedDictYAMLLoader)
        if disco is not None:
            yamlconfig['disco'] = collections.OrderedDict([('type', 'disco'),
                                                           ('connection', disco)])

        with open(config_path, 'w+') as f:
            f.write(yaml.dump(yamlconfig))

            

import os.path
import argparse

def main():
    parser = argparse.ArgumentParser(description='Start blaze')
    parser.add_argument('datapath', nargs="?")
    parser.add_argument(
        '-s', '--server-name',
        help='name of server',
        default='myserver'
    )
    parser.add_argument(
        '-fa', '--front-address',
        help='specify the adress which communicates with the outside world',
        default='tcp://127.0.0.1:5555'
    )
    parser.add_argument(
        '-ba', '--back-address',
        help='specify the internal address for communicating with workers',
        default='tcp://127.0.0.1:5556'
    )
    parser.add_argument(
        '-n', '--namespace',
        help='namespace of node, nodes can see all nodes within this namespace',
        default='main'
    )
    
    parser.add_argument(
        '-d', '--disco',
        help='disco host:port',
        default=None
    )
    
    parser.add_argument('-nr', '--no-redis', action='store_true')
    parser.add_argument('-rh', '--redis-host', default='localhost')
    parser.add_argument('-rp', '--redis-port', default=6379)
    parser.add_argument('-sc', '--skip-config', action='store_true')
    parser.add_argument('-rc', '--rebuild-config', action='store_true')    
    args = parser.parse_args()
    print args
    servername = args.server_name
    if args.datapath is None:
        datapath = os.path.abspath(os.path.dirname(blaze.server.tests.__file__))
        datapath = os.path.join(datapath, 'data')
    else:
        datapath = os.path.abspath(args.datapath)
    print 'datapath', datapath
    if not args.no_redis:
        assert args.redis_host == 'localhost', 'cannot start redis on another host'
        proc = redisutils.RedisProcess(
            args.redis_port,
            datapath,
            data_file=os.path.join(datapath, 'redis.db'),
            log_file=os.path.join(datapath, 'redis.log'))
    time.sleep(0.1)
    init_dir(datapath, disco=args.disco)
    data = yaml.load(open(os.path.join(datapath, 'blaze.config')).read(),
                          Loader=orderedyaml.OrderedDictYAMLLoader)
    namespace = args.namespace
    config = blazeconfig.BlazeConfig(servername, host=args.redis_host,
                                     port=args.redis_port, sourceconfig=data)
    frontaddr = args.front_address
    backaddr = args.back_address
    node = blazenode.BlazeNode(backaddr, servername, config)
    node.start()
    b = blazebroker.BlazeBroker(frontaddr, backaddr, config)
    b.start()
    maincontroller.prepare_app(frontaddr, rhost=args.redis_host,
                           rport=args.redis_port)
    maincontroller.start_app()
    
if __name__ == "__main__":
    main()
    
