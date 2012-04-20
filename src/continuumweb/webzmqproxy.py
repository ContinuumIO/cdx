import gevent
import gevent.monkey
gevent.monkey.patch_all()
import gevent_zeromq
gevent_zeromq.monkey_patch()
from gevent.queue import Queue

import zmq
import threading
import uuid
import time
import logging
import rpc.protocol as protocol

log = logging.getLogger(__name__)

class ProxyClient(threading.Thread):
    def __init__(self, pushpulladdr, pubsubaddr,
                 timeout=2, ctx=None, protocol_handler=None):
        if protocol_handler is None:
            protocol_handler = protocol.ZMQProtocolHelper()
        self.ph = protocol_handler
        if ctx is None:
            ctx = zmq.Context.instance()
        self.ctx = ctx
        self.pushpulladdr = pushpulladdr
        self.pubsubaddr = pubsubaddr
        self.queues = {}
        self.send_queue = Queue()
        self.timeout = timeout
        super(ProxyClient, self).__init__()
        self.kill = False
        self.uuid = str(uuid.uuid4())
        
    def run_send(self):
        print 'runsend'
        self.push = self.ctx.socket(zmq.PUSH)
        self.push.connect(self.pushpulladdr)
        while not self.kill:
            print 'running send'
            try:
                messages = self.send_queue.get(timeout=self.timeout)
            except:
                continue
            print 'sending', messages
            self.push.send_multipart(messages)
        print 'DONE SENDING!'
        
    def run_recv(self):
        self.sub = self.ctx.socket(zmq.SUB)
        self.sub.setsockopt(zmq.SUBSCRIBE,'')
        self.sub.connect(self.pubsubaddr)
        poller = zmq.Poller()
        poller.register(self.sub, zmq.POLLIN)
        print 'subloop'
        try:
            while not self.kill:
                socks = dict(poller.poll(timeout=1000.0))
                if self.sub in socks:
                    messages = self.sub.recv_multipart()
                    (clientid, msgid,
                     msgobj, dataobjs) = self.ph.unpack_blaze(messages)
                    print 'sub received', messages
                    if msgid in self.queues:
                        self.queues[msgid].put((clientid, msgid,
                                                msgobj, dataobjs))
        except zmq.ZMQError as e:
            log.exception(e)
        finally:
            self.sub.close()
            
    def run(self):
        t = threading.Thread(target=self.run_send)
        t.start()
        self.run_recv()
        t.join()
        
    def request(self, msgobj, dataobjs):
        msgid = str(uuid.uuid4())
        queue = Queue()
        self.queues[msgid] = queue
        messages = self.ph.pack_blaze(self.uuid, msgid, msgobj, dataobjs)
        self.send_queue.put(messages)
        while True:
            (clientid, msgid, msgobj, dataobjs) = self.queues[msgid].get()
            if msgobj.get('msgtype') == 'rpcresponse':
                break
            else:
                log.debug("%s, %s, %s, %s", clientid, msgid, msgobj, dataobjs)
        del self.queues[msgid]
        return (msgobj, dataobjs)
    
class Proxy(threading.Thread):
    def __init__(self, reqrepaddr, pushpulladdr, pubsubaddr, ctx=None):
        if ctx is None:
            ctx = zmq.Context.instance()
        self.ctx = ctx
        self.reqrepaddr = reqrepaddr
        self.pushpulladdr = pushpulladdr
        self.pubsubaddr = pubsubaddr
        self.kill = False
        super(Proxy, self).__init__()
        
    def init_sockets(self):
        self.dealer = self.ctx.socket(zmq.DEALER)
        self.dealer.connect(self.reqrepaddr)

        self.pull = self.ctx.socket(zmq.PULL)
        self.pull.bind(self.pushpulladdr)
        print 'pull bound'
        self.pub = self.ctx.socket(zmq.PUB)
        self.pub.bind(self.pubsubaddr)
        print 'pub bound'

        
    def run(self):
        self.init_sockets()
        poller = zmq.Poller()
        poller.register(self.dealer, zmq.POLLIN)
        poller.register(self.pull, zmq.POLLIN)
        try:
            while not self.kill:
                socks = dict(poller.poll(timeout=1000.0))
                if self.dealer in socks:
                    msg = self.dealer.recv_multipart()
                    payload = msg[msg.index('')+1:]
                    self.pub.send_multipart(payload)
                if self.pull in socks:
                    msg = self.pull.recv_multipart()
                    msg.insert(0, '')
                    self.dealer.send_multipart(msg)
        except zmq.ZMQError as e:
            log.exception(e)
        finally:
            self.dealer.close()
            self.pull.close()
            
            

import rpc.client as client

class ProxyRPCClient(client.BaseRPCClient):
    def __init__(self, proxyclient):
        self.proxyclient = proxyclient
        self.ph = proxyclient.ph
    def reqrep(self, requestobj, dataobjs):
        (responseobj, dataobjs) = self.proxyclient.request(requestobj, dataobjs)
        return (responseobj, dataobjs)
    
