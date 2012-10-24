import os
import sys

from setuptools import Command, setup, find_packages
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
