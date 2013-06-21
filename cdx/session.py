from bokeh.session import PlotServerSession, PlotList
from objects import CDX, Namespace


class CDXSession(PlotServerSession):
    def load_doc(self, docid):
        super(CDXSession, self).load_doc(docid)
        cdx = self.load_type('CDX')
        if len(cdx):
            cdx = cdx[0]
        else:
            cdx = CDX()
            self.add(cdx)
            self.store_obj(cdx)
        self.cdx = cdx
        self.plotcontext.children.append(cdx)
        self.plotcontext._dirty = True
        if not cdx.namespace:
            ns = Namespace()
            self.add(ns)
            cdx.namespace = ns
            self.store_obj(ns)
            self.store_obj(cdx)
            
        if not cdx.plotcontext:
            cdx.plotcontext = self.plotcontext
            self.store_obj(cdx)

        if not cdx.plotlist:
            cdx.plotlist = PlotList()
            self.add(cdx.plotlist)
            self.store_objs([cdx, cdx.plotlist])
        
