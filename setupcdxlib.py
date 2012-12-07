import sys
if sys.argv[1] == 'develop':
    import setuptools
from distutils.core import setup
__version__ = (0, 0, 1)

packages = ["cdxlib"]
setup(
    name = 'cdxlib',
    version = '.'.join([str(x) for x in __version__]),
    author = 'Continuum Analytics',
    packages = packages,
    author_email = '',
    url = '',
    description = 'CDX library',
    zip_safe=False,
    license = 'New BSD',
)
