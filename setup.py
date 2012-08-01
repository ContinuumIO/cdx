import os
import sys

from setuptools import Command, setup, find_packages
__version__ = (0, 0, 1)

package_data_dirs = []
for dirname, _, files in os.walk('cdx/static'):
    dirname = os.path.relpath(dirname, 'cdx')
    for f in files:
        package_data_dirs.append(os.path.join(dirname, f))
        
for dirname, _, files in os.walk('cdx/templates'):
    dirname = os.path.relpath(dirname, 'cdx')
    for f in files:
        package_data_dirs.append(os.path.join(dirname, f))
setup(
    name = 'cdx',
    version = '.'.join([str(x) for x in __version__]),
    packages = find_packages(),
    package_data = {'cdx' : package_data_dirs},
    scripts = ["cdx/scripts/runcdx"],
    author = 'Continuum Analytics',
    author_email = '',
    url = '',
    description = 'CDX',
    zip_safe=False,
    #long_description=open('docs/README').read(),
    #install_requires = ['pyzmq>=2.1.0', 'gevent'],
    license = 'New BSD',
)
