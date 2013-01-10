import sys
import os
if sys.argv[1] == 'develop':
    import setuptools
from distutils.core import setup
__version__ = (0, 0, 1)

packages = ["cdxlib"]
package_data_dirs = []
for dirname, _, files in os.walk('cdxlib/static'):
    dirname = os.path.relpath(dirname, 'cdx')
    for f in files:
        package_data_dirs.append(os.path.join(dirname, f))
        
for dirname, _, files in os.walk('cdxlib/templates'):
    dirname = os.path.relpath(dirname, 'cdx')
    for f in files:
        package_data_dirs.append(os.path.join(dirname, f))

setup(
    name = 'cdxlib',
    version = '.'.join([str(x) for x in __version__]),
    author = 'Continuum Analytics',
    packages = packages,
    package_data = {'cdx' : package_data_dirs},    
    author_email = '',
    url = '',
    description = 'CDX library',
    zip_safe=False,
    license = 'New BSD',
)
