import json
import os
import signal
import subprocess
import sys

class ManagedProcess(object):
    def __init__(self, args, name, pidfilename,
                 stdout=None, stdin=None, stderr=None,
                 kill_old=True):
        self.name = name
        self.pidfilename = pidfilename
        data = self.read_pidfile()
        pid = data.get(name)
        if pid and kill_old:
            try:
                os.kill(pid, signal.SIGINT)
            except OSError:
                #this is ok, just means process is not running
                pass
        elif pid and not kill_old:
            raise Exception, "proces %s is running on PID %s" % (name, pid)
        if stdout is None: stdout = subprocess.PIPE
        if stderr is None: stderr = subprocess.PIPE
        if stdin is None: stdin = subprocess.PIPE
        self.proc = subprocess.Popen(args,
                                     stdout=stdout,
                                     stderr=stderr,
                                     stdin=stdin)
        self.add_to_pidfile()
        self.closed = False
        
    def read_pidfile(self):
        if os.path.exists(self.pidfilename):
            with open(self.pidfilename, "r") as f:
                data = json.load(f)
        else:
            data = {}
        return data
    
    def add_to_pidfile(self):
        data = self.read_pidfile()
        data[self.name] = self.proc.pid
        with open(self.pidfilename, "w+") as f:
            json.dump(data, f)
            
    def remove_from_pidfile(self):
        data = self.read_pidfile()
        if self.name in data:
            del data[self.name]
        with open(self.pidfilename, "w+") as f:
            json.dump(data, f)
        
        
    def close(self):
        if not self.closed:
            self.proc.kill()
            self.proc.communicate()
            self.remove_from_pidfile()
