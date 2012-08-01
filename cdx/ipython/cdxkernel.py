from __future__ import print_function
from IPython.zmq.session import Session
from IPython.utils.traitlets import Instance, Dict
from IPython.zmq.ipkernel import Kernel
from IPython.zmq.ipkernel import IPKernelApp
from zmq.eventloop.zmqstream import ZMQStream
import arrayserver.array_proxy.arrayserver_array_proxy as arrayserver_array_proxy
import arrayserver.array_proxy.array_proxy as array_proxy
import IPython.zmq.entry_point as entry_point
import numpy as np
import notifications
import uuid

def save_temp_numpy(client, arr):
    url  = "/tmp/" + str(uuid.uuid4())
    client.rpc('store', urls=[url], data=[arr])
    return url

class CDXKernelMixin(object):
    def __init__(self, *args, **kwargs):
        self.parent = None
        super(CDXKernelMixin, self).__init__(*args, **kwargs)
        notify_d = notifications.NotificationDict(self.shell.user_ns)
        notify_d.set_notifier = self.namespace_notification
        self.shell.user_ns  = notify_d
        self.shell.Completer.namespace = notify_d
        self.shell.Completer.global_namespace = notify_d
        self.changed = set()
        self.npurls = {}
        
    def namespace_notification(self, key, val):
        self.changed.add(key)
        
    def process_changed(self):
        for varname in self.changed:
            value = self.shell.user_ns[varname]
            if isinstance(value, array_proxy.ArrayNode):
                value.save_temp()
            if isinstance(value, np.ndarray):
                print ('BC', 'bc' in self.shell.user_ns)
                if 'bc' in self.shell.user_ns:
                    newurl = save_temp_numpy(self.shell.user_ns['bc'], value)
                    self.npurls[id(value)] = newurl
        self.session.send(self.iopub_socket,
                          u'namespace',
                          {'variables': self.get_namespace_data(),
                           'newvars' : list(self.changed)})
        self.changed.clear()
        
    def get_namespace_data(self):
        local_varnames = self.shell.magics_manager.magics['line']['who_ls']()
        local_varnames.append("_")        
        self.log.warning("%s", local_varnames)
        variables = []
        local_vars = [self.shell.user_ns[x] for x in local_varnames]
        for var, varname in zip(local_vars, local_varnames):
            local_type = type(var).__name__
            display_val = repr(var)
            if len(display_val) > 100:
                display_val = display_val[:100] + "..."
            varinfo = {'name' : varname,
                       'type' : local_type,
                       'value' : display_val}
            if isinstance(var, (array_proxy.BaseArrayNode)):
                varinfo['url'] = var.url
            elif isinstance(var, (np.ndarray)):
                varinfo['url'] = self.npurls.get(id(var))
            variables.append(varinfo)
        return variables

    def execute_request(self, stream, ident, parent):
        #store most recent parent here.... hack.. how should we store this?
        #the issue is we need it to send out pub messages
        self.parent = parent
        super(CDXKernelMixin, self).execute_request(stream, ident, parent)
        local_varnames = self.shell.magics_manager.magics['line']['who_ls']()
        self.process_changed()
        
    def namespace_request(self, stream, ident, parent):
        reply_msg = self.session.send(stream, u'namespace',
                                      {u'variables': self.get_namespace_data()},
                                      parent, ident=ident)

    def object_request(self, stream, ident, parent):
        if 'varname' in parent['content']:
            msgobj = notifications.get_variable_message(
                parent['content']['varname'], user_ns = self.shell.user_ns)
        else:
            msgobj = {'error' : 'no variable specified'}
        reply_msg = self.session.send(stream, u'object',
                                      msgobj,
                                      parent, ident=ident)

class CDXKernel(CDXKernelMixin, Kernel):
    def __init__(self, **kwargs):
        super(CDXKernel, self).__init__(**kwargs)
        new_msg_types = ['namespace_request', 'object_request']
        for msg_type in new_msg_types:
            self.shell_handlers[msg_type] = getattr(self, msg_type)
        self.log.warning('CDX KERNEL!')



class CDXKernelApp(IPKernelApp):
    #cut and paste from ipython project, with my own kernel class instead of
    #theirs... should refactor.

    def init_kernel(self):
        shell_stream = ZMQStream(self.shell_socket)

        kernel = CDXKernel(config=self.config, session=self.session,
                                shell_streams=[shell_stream],
                                iopub_socket=self.iopub_socket,
                                stdin_socket=self.stdin_socket,
                                log=self.log,
                                profile_dir=self.profile_dir,
        )
        self.kernel = kernel
        kernel.record_ports(self.ports)
        shell = kernel.shell

def CDX_launcher(*args, **kwargs):
    entry_point.base_launch_kernel(
        'from cdx.ipython.cdxkernel import main; main()',
        *args, **kwargs)

def main():
    """Run an IPKernel as an application"""
    app = CDXKernelApp.instance()
    app.initialize()
    app.start()
