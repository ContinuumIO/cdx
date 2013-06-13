from bokeh.session import PlotServerSession
from objects import CDX


class CDXSession(PlotServerSession):
    def load_doc(self, docid):
        super(CDXSession, self).load_doc(docid)
        cdx = self.load_type('CDX')
        if len(cdx):
            cdx = cdx[0]
        else:
            cdx = CDX()
            import pdb;pdb.set_trace()
            self.add(cdx)
            self.store_obj(cdx)
        self.cdx = cdx
        if not cdx.namespace:
            pass
        
        
        
