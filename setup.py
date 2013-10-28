# needs to be tested
import sys
if len(sys.argv)>1 and sys.argv[1] == 'develop':
    # Only import setuptools if we have to
    import setuptools
else:
    import shutil
    shutil.copy("hembuild/application.js",
                "cdx/static/js/application.js")
    shutil.copy("hembuild/application.css",
                "cdx/static/css/application.css")

from distutils.core import setup
import os
import sys
__version__ = (0, 0, 1)
package_data = []
for dirname, _, files in os.walk('cdx/static', followlinks=True):
    dirname = os.path.relpath(dirname, 'cdx')
    for f in files:
        package_data.append(os.path.join(dirname, f))

for dirname, _, files in os.walk('cdx/templates', followlinks=True):
    dirname = os.path.relpath(dirname, 'cdx')
    for f in files:
        package_data.append(os.path.join(dirname, f))

for dirname, _, files in os.walk('cdx/singlecell/static',
                                 followlinks=True):
    dirname = os.path.relpath(dirname, 'cdx')
    for f in files:
        package_data.append(os.path.join(dirname, f))

for dirname, _, files in os.walk('cdx/singlecell/templates',
                                 followlinks=True):
    dirname = os.path.relpath(dirname, 'cdx')
    for f in files:
        package_data.append(os.path.join(dirname, f))
package_data.append('redis.conf')

setup(
    name = 'cdx',
    version = '.'.join([str(x) for x in __version__]),
    packages = ['cdx', 'cdx.remotedata', 'cdx.singlecell'],
    scripts=['cdxlocal.py'],
    package_data = {'cdx' : package_data},
    author = 'Continuum Analytics',
    author_email = 'info@continuum.io',
    url = 'http://github.com/ContinuumIO/cdx',
    description = 'data analysis',
    zip_safe=False,
    license = 'New BSD',
)
