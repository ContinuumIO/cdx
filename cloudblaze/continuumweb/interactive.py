import requests
import blaze.protocol as protocol
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
        self.blazeaddress = data['blazeaddress']
        
    def get_clients(self):
        import cloudblaze.continuumweb.plot as plot
        self.p = plot.PlotClient(self.docid, self.backboneurl)
        import blaze.server.rpc.client as blazeclient
        self.bc = blazeclient.BlazeClient(self.blazeaddress)
        self.bc.connect()
        import blaze.array_proxy.array_proxy as array_proxy
        array_proxy.client = self.bc
        
    def load_clients(self):
        import blaze.array_proxy.npproxy as npp
        ipython = get_ipython()
        ipython.user_ns['bc'] = self.bc
        ipython.user_ns['p'] = self.p
        ipython.user_ns['npp'] = npp

        
    
