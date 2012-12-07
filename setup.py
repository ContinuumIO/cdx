import sys
if sys.argv[1] == 'develop':
    import setuptools
from distutils.core import setup
import os
import sys
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
    packages = ['cdx', 'cdx.models', 'cdx.views', 'cdx.test'],
    package_data = {'cdx' : package_data_dirs},
    author = 'Continuum Analytics',
    author_email = '',
    url = '',
    description = 'CDX',
    zip_safe=False,
    #long_description=open('docs/README').read(),
    #install_requires = ['pyzmq>=2.1.0', 'gevent'],
    license = 'New BSD',
)
