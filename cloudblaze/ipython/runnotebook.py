import IPython.frontend.html.notebook.notebookapp as notebookapp
import IPython.frontend.html.notebook.kernelmanager as kernelmanager
from IPython.zmq.kernelmanager import KernelManager
import blazekernel
from tornado import httpserver
import tornado
import uuid
import os

class BlazeKernelManager(kernelmanager.MappingKernelManager):
    
    def _start_kernel(self, **kwargs):
        ## FROM MultiKernelManager
        kernel_id = unicode(uuid.uuid4())
        # use base KernelManager for each Kernel
        km = KernelManager(
            connection_file=os.path.join(
                self.connection_dir, "kernel-%s.json" % kernel_id),
            config=self.config,
        )
        km.start_kernel(launcher=blazekernel.cloud_blaze_launcher
                        , **kwargs)
        self._kernels[kernel_id] = km
        return kernel_id

    def start_kernel(self, notebook_id=None):
        #FROM MappingKernelManager
        """Start a kernel for a notebok an return its kernel_id.

        Parameters
        ----------
        notebook_id : uuid
            The uuid of the notebook to associate the new kernel with. If this
            is not None, this kernel will be persistent whenever the notebook
            requests a kernel.
        """
        kernel_id = self.kernel_for_notebook(notebook_id)
        if kernel_id is None:
            kwargs = dict()
            kwargs['extra_arguments'] = self.kernel_argv
            kernel_id = self._start_kernel(**kwargs)
            self.set_kernel_for_notebook(notebook_id, kernel_id)
            self.log.info("Kernel started: %s" % kernel_id)
            self.log.debug("Kernel args: %r" % kwargs)
        else:
            self.log.info("Using existing kernel: %s" % kernel_id)
        return kernel_id
    
notebookapp.MappingKernelManager = BlazeKernelManager

app = notebookapp.NotebookApp.instance()
app.open_browser = False
def launch_new_instance():
    app.initialize()
    app.start()
    app.web_app.notebook_manager.list_notebooks()
if __name__ == "__main__":
    launch_new_instance()
    
