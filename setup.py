import os
import sys

from setuptools import Command, setup, find_packages

try:
    import nose
except ImportError:
    nose = None

class TestCommand(Command):
    """Custom distutils command to run the test suite."""

    user_options = []

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        if nose is None:
            print ("nose unavailable, skipping tests.")
        else:
            return nose.core.TestProgram(argv=["", '-vvs', os.path.join(self._zmq_dir, 'tests')])

__version__ = (0, 0, 1)

package_data_dirs = []
for dirname, _, files in os.walk('cloudblaze/blazeweb/static'):
    dirname = os.path.relpath(dirname, 'cloudblaze')
    for f in files:
        package_data_dirs.append(os.path.join(dirname, f))
        
for dirname, _, files in os.walk('cloudblaze/blazeweb/templates'):
    dirname = os.path.relpath(dirname, 'cloudblaze')
    for f in files:
        package_data_dirs.append(os.path.join(dirname, f))
setup(
    name = 'cloudblaze',
    version = '.'.join([str(x) for x in __version__]),
    packages = find_packages(),
    package_data = {'cloudblaze' : package_data_dirs},
    scripts = ["cloudblaze/blazeweb/scripts/runcdx.py"],
    author = 'Continuum Analytics',
    author_email = '',
    url = '',
    description = 'cloudblaze',
    #long_description=open('docs/README').read(),
    #install_requires = ['pyzmq>=2.1.0', 'gevent'],
    license = 'New BSD',
)
