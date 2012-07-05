import numpy as np
import simplejson
import pandas
import weakref
import logging
# log = logging.getLogger(__name__)
# logging.basicConfig(level=logging.DEBUG)
    
class NotificationDict(dict):
    def __init__(self, *args, **kwargs):
        self.get_notifier = None
        self.set_notifier = None
        self.update(*args, **kwargs)
        """
        get_notifier = function that takes key,val as args
        set_notifier = function that takes key,val as args
        """
        
    def __getitem__(self, key):
        val = dict.__getitem__(self, key)
        if self.get_notifier is not None:
            self.get_notifier(key, val)
            
        return val

    def __setitem__(self, key, val):
        dict.__setitem__(self, key, val)        
        if self.set_notifier is not None:
            self.set_notifier(key, val)
        
    def __repr__(self):
        dictrepr = dict.__repr__(self)
        return '%s(%s)' % (type(self).__name__, dictrepr)
    
    def update(self, *args, **kwargs):
        for k, v in dict(*args, **kwargs).iteritems():
            self[k] = v

##pandas hacks for subscription functionality.... ugh
import pandas

class Series(pandas.Series):
    def __setitem__(self, key, value):
        super(Series, self).__setitem__(key, value)
        if hasattr(self, 'varname') and self.referer():
            pub_object(self.varname, self.referer())

class DataFrame(pandas.DataFrame):
    def __getitem__(self, item):
        retval = super(DataFrame, self).__getitem__(item)
        if hasattr(self, 'varname') and isinstance(retval, pandas.Series):
            retval = Series(retval)
            retval.varname = self.varname
            retval.referer = weakref.ref(self)
        return retval
    def _set_item(self, key, value):
        super(DataFrame, self)._set_item(key, value)
        if hasattr(self, 'varname'):
            pub_object(self.varname, self)
    def plot(self, colname):
        x = self.index.tolist()
        y = self[colname].tolist()
        payload = [{'x': xx, 'y' : yy} for (xx, yy) in zip(x, y)]
        plot_data = dict(data=payload,
                         dfname=self.varname,
                         colname=colname)
        data = {'x-application/dfplot' : plot_data};
        publish_display_data('notifications.DataFrame', data)


        
from IPython.core.displaypub import publish_display_data
def pub_object(varname, val):
    payload = get_variable_message(varname, val=val)
    data = {'x-application/object' : payload};
    #what name goes here?
    publish_display_data('ObjectPub', data)


def get_variable_message(varname, val=None, user_ns=None):
    try:
        if val is None:
            val = user_ns[varname]
        json_obj =  json_representation(val)
        json_obj['varname'] = varname;
        #for error handling, we need to know whether we can serialize this
        #object in json before we transmit it... this is inefficient,
        #we need a better way at some point
        simplejson.dumps(json_obj)
        return json_obj
    except TypeError:
        return {'error' : 'cannot convert tojson %s' % varname}
    except KeyError:
        return {'error' : 'unknown variable %s' % varname}


def json_representation(obj):
    returnobj = {}
    if isinstance(obj, np.ndarray):
        if obj.dtype.names is not None:
            returnobj['type'] = 'recarray'
            returnobj['names'] = obj.dtype.names
            returnobj['json'] = {}
            for n in returnobj['names']:
                returnobj['json'][n] = obj[n].tolist()
        else:
            returnobj['type'] = 'array'
            returnobj['json'] = obj.tolist()
    elif isinstance(obj, pandas.DataFrame):
        returnobj['names'] = list(obj);
        returnobj['names'].insert(0, 'Index') 
        returnobj['type'] = 'DataFrame'
        jsonobj = {}
        for col in obj:
            jsonobj[col] = obj[col].values.tolist();
        jsonobj['Index'] = obj.index.tolist();
        returnobj['json'] = jsonobj
    else:
        returnobj['json'] = obj
    return returnobj

