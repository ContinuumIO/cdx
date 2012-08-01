import requests
import arrayserver.protocol as protocol
import urlparse

class CDXClient(object):
    def __init__(self, url, ph=None):
        if ph is None:
            self.ph = protocol.ProtocolHelper()
        self.cdxinfo(url)
        self.get_clients()
        self.load_clients()
        
    def cdxinfo(self, url):
        parsed = urlparse.urlsplit(url)
        path = parsed.path
        #hack
        docid = path.split("/")[2]
        newpath = "/cdxinfo/" + docid    
        parsed = urlparse.SplitResult(parsed.scheme,
                                      parsed.netloc, newpath, '', '')
        data = self.ph.deserialize_web(requests.get(parsed.geturl()).content)
        parsed = urlparse.SplitResult(parsed.scheme,
                                      parsed.netloc, "/bb/", '', '')
        self.backboneurl = parsed.geturl()
        self.docid = data['docid']
        self.arrayserveraddress = data['arrayserveraddress']
        
    def get_clients(self):
        import cdx.plot as plot
        self.p = plot.PlotClient(self.docid, self.backboneurl)
        import arrayserver.server.rpc.client as arrayserverclient
        self.bc = arrayserverclient.ArrayServerClient(self.arrayserveraddress)
        self.bc.connect()
        import arrayserver.array_proxy.array_proxy as array_proxy
        array_proxy.client = self.bc
        
    def load_clients(self):
        import arrayserver.array_proxy.npproxy as npp
        ipython = get_ipython()
        ipython.user_ns['bc'] = self.bc
        ipython.user_ns['p'] = self.p
        ipython.user_ns['npp'] = npp

        
    
