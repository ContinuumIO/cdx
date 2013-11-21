import os
import sys
import subprocess
from os.path import join, dirname

from launch_process import ManagedProcess

def start_redis(pidfilename, port, data_dir, data_file='redis.db', save=True):
    base_config = os.path.join(os.path.dirname(__file__), 'redis.conf')
    with open(base_config) as f:
        redisconf = f.read()
    savestr = ''
    if save: savestr = 'save 10 1'
    redisconf = redisconf % {'port' : port,
                             'dbdir' : data_dir,
                             'dbfile' : data_file,
                             'save' : savestr}
    mproc = ManagedProcess(['redis-server', '-'], 'redis',
        pidfilename, stdout=sys.stdout, stderr=sys.stderr)
    mproc.proc.stdin.write(redisconf)
    mproc.proc.stdin.close()
    return mproc

def start_ipython(pidfilename, port, work_dir):
    python = sys.executable
    script = join(dirname(__file__), 'singlecell', 'singlecell.py')
    cmd = [python, script, str(port), work_dir]
    mproc = ManagedProcess(cmd, 'ipython', pidfilename,
        stdout=sys.stdout, stderr=sys.stderr, stdin=sys.stdin)
    return mproc
