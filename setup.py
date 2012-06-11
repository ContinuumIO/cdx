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

setup(
    name = 'cloudblaze',
    version = '.'.join([str(x) for x in __version__]),
    packages = find_packages(),
    entry_points = {
        'console_scripts': [
        ],
    },
    author = 'Continuum Analytics',
    author_email = '',
    url = '',
    description = 'cloudblaze',
    #long_description=open('docs/README').read(),
    #install_requires = ['pyzmq>=2.1.0', 'gevent'],
    license = 'New BSD',
)
