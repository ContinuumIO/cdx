import IPython.frontend.html.notebook.notebookapp as notebookapp
from tornado import httpserver
import tornado
app = notebookapp.NotebookApp.instance()
app.open_browser = False
def launch_new_instance():
    app.initialize()
    app.start()
    app.web_app.notebook_manager.list_notebooks()
if __name__ == "__main__":
    launch_new_instance()
    
