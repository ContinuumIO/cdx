import subprocess
import os
from launch_process import ManagedProcess

def start_redis(pidfilename, port, data_dir, data_file='redis.db', save=True):
    base_config = os.path.join(os.path.dirname(__file__), 'redis.conf')
    log_file = open(os.path.join(data_dir, log_file), 'w+')
    with open(base_config) as f:
        redisconf = f.read()
    savestr = ''
    if save: savestr = 'save 10 1'
    redisconf = redisconf % {'port' : port,
                             'dbdir' : data_dir,
                             'dbfile' : data_file,
                             'save' : savestr}
    mproc = ManagedProcess(['redis-server', '-'], 'redis', pidfilename)
    mproc.proc.stdin.write(redisconf)
    mproc.proc.stdin.close()
    return mproc

                     

