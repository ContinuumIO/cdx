import os
import sys
import subprocess
from os.path import join, dirname

from launch_process import ManagedProcess

def start_ipython(pidfilename, port, work_dir):
    python = sys.executable
    script = join(dirname(__file__), 'singlecell', 'singlecell.py')
    cmd = [python, script, str(port), work_dir]
    mproc = ManagedProcess(cmd, 'ipython', pidfilename,
        stdout=sys.stdout, stderr=sys.stderr, stdin=sys.stdin)
    return mproc
