from __future__ import print_function
from IPython.zmq.session import Session
from IPython.utils.traitlets import Instance, Dict
from IPython.zmq.ipkernel import Kernel
from IPython.zmq.ipkernel import IPKernelApp
import IPython.zmq.entry_point as entry_point
import simplejson
import numpy as np
import pandas
import notifications
#import npcframe

    
class CloudBlazeKernelMixin(object):
    def __init__(self, *args, **kwargs):
        self.parent = None
        super(CloudBlazeKernelMixin, self).__init__(*args, **kwargs)
        notify_d = notifications.NotificationDict(self.shell.user_ns)
        notify_d.set_notifier = self.namespace_notification
        self.shell.user_ns  = notify_d
        self.shell.Completer.namespace = notify_d
        self.shell.Completer.global_namespace = notify_d
        
    def namespace_notification(self, key, val):
        if self.parent is None:
            return
        if isinstance(val, pandas.DataFrame) or \
               isinstance(val, notifications.DataFrame):
            notifications.pub_object(key, val)
            val.varname = key
            
    def get_namespace_data(self):
        local_varnames = self.shell.magic_who_ls()
        local_vars = [self.shell.user_ns[x] for x in local_varnames]
        local_types = [type(x).__name__ for x in local_vars]
        return [(x, y) for x,y in zip(local_varnames, local_types)]
    
    def execute_request(self, ident, parent):
        #store most recent parent here.... hack.. how should we store this?
        #the issue is we need it to send out pub messages
        self.parent = parent
        super(CloudBlazeKernelMixin, self).execute_request(ident, parent)
        self.session.send(self.iopub_socket,
                          u'namespace',
                          {u'variables': self.get_namespace_data()},
                          parent=parent)
        
    def namespace_request(self, ident, parent):
        reply_msg = self.session.send(self.shell_socket, u'namespace',
                                      {u'variables': self.get_namespace_data()},
                                      parent, ident=ident)
        
    def object_request(self, ident, parent):
        if 'varname' in parent['content']:
            msgobj = notifications.get_variable_message(
                parent['content']['varname'], user_ns = self.shell.user_ns)
        else:
            msgobj = {'error' : 'no variable specified'}
        reply_msg = self.session.send(self.shell_socket, u'object',
                                      msgobj,
                                      parent, ident=ident)

class CloudBlazeKernel(CloudBlazeKernelMixin, Kernel):
    def __init__(self, **kwargs):
        super(CloudBlazeKernel, self).__init__(**kwargs)
        new_msg_types = ['namespace_request', 'object_request']
        for msg_type in new_msg_types:
            self.handlers[msg_type] = getattr(self, msg_type)
        self.log.warning('CLOUD BLAZE KERNEL!')


        
class CloudBlazeKernelApp(IPKernelApp):
    #cut and paste from ipython project, with my own kernel class instead of
    #theirs... should refactor.
    def init_kernel(self):
        kernel = CloudBlazeKernel(config=self.config, session=self.session,
                                  shell_socket=self.shell_socket,
                                  iopub_socket=self.iopub_socket,
                                  stdin_socket=self.stdin_socket,
                                  log=self.log,
                                  profile_dir=self.profile_dir,
                                  )
        self.kernel = kernel
        kernel.record_ports(self.ports)
        shell = kernel.shell
        if self.pylab:
            try:
                gui, backend = pylabtools.find_gui_and_backend(self.pylab)
                shell.enable_pylab(gui, import_all=self.pylab_import_all)
            except Exception:
                self.log.error("Pylab initialization failed", exc_info=True)
                # print exception straight to stdout, because normally 
                # _showtraceback associates the reply with an execution, 
                # which means frontends will never draw it, as this exception 
                # is not associated with any execute request.
                
                # replace pyerr-sending traceback with stdout
                _showtraceback = shell._showtraceback
                def print_tb(etype, evalue, stb):
                    print ("Error initializing pylab, pylab mode will not "
                           "be active", file=io.stderr)
                    print (shell.InteractiveTB.stb2text(stb), file=io.stdout)
                shell._showtraceback = print_tb
                
                # send the traceback over stdout
                shell.showtraceback(tb_offset=0)
                
                # restore proper _showtraceback method
                shell._showtraceback = _showtraceback
    
def cloud_blaze_launcher(*args, **kwargs):
    entry_point.base_launch_kernel(
        'from cloudblaze.ipython.blazekernel import main; main()',
        *args, **kwargs)

def main():
    """Run an IPKernel as an application"""
    app = CloudBlazeKernelApp.instance()
    app.initialize()
    app.start()
