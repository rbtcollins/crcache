#!/usr/bin/env python
#
# Copyright (c) 2013 crcache contributors
# 
# Licensed under either the Apache License, Version 2.0 or the BSD 3-clause
# license at the users choice. A copy of both licenses are available in the
# project source as Apache-2.0 and BSD. You may not use this file except in
# compliance with one of these two licences.
# 
# Unless required by applicable law or agreed to in writing, software
# distributed under these licenses is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.  See the
# license you chose for the specific language governing permissions and
# limitations under that license.

import email
import os.path
from setuptools import setup

import extras
testtools = extras.try_import('testtools')

import cr_cache


def get_version_from_pkg_info():
    """Get the version from PKG-INFO file if we can."""
    pkg_info_path = os.path.join(os.path.dirname(__file__), 'PKG-INFO')
    try:
        pkg_info_file = open(pkg_info_path, 'r')
    except (IOError, OSError):
        return None
    try:
        pkg_info = email.message_from_file(pkg_info_file)
    except email.MessageError:
        return None
    return pkg_info.get('Version', None)


def get_version():
    """Return the version of crcache that we are building."""
    version = '.'.join(
        str(component) for component in cr_cache.__version__[0:3])
    phase = cr_cache.__version__[3]
    if phase == 'final':
        return version
    pkg_info_version = get_version_from_pkg_info()
    if pkg_info_version:
        return pkg_info_version
    if phase == 'alpha':
        # No idea what the next version will be
        return 'next'
    else:
        # Preserve the version number but give it a -next suffix.
        return version + '-next'


description = open(os.path.join(os.path.dirname(__file__), 'README.rst'), 'rt').read()


cmdclass = {}

if testtools is not None:
    cmdclass['test'] = testtools.TestCommand


setup(name='crcache',
      author='Robert Collins',
      author_email='robertc@robertcollins.net',
      url='https://github.com/rbtcollins/crcache',
      description='An API for obtaining and reusing computing resources.',
      long_description=description,
      keywords="testing compute cache",
      classifiers = [
          'Development Status :: 3 - Alpha',
          'Intended Audience :: Developers',
          'License :: OSI Approved :: BSD License',
          'License :: OSI Approved :: Apache Software License',
          'Operating System :: OS Independent',
          'Programming Language :: Python',
          'Programming Language :: Python :: 3',
          'Topic :: System :: Distributed Computing',
          ],
      scripts=['crcache'],
      version=get_version(),
      packages=[
        'cr_cache',
        'cr_cache.arguments',
        'cr_cache.commands',
        'cr_cache.store',
        'cr_cache.ui',
        'cr_cache.tests',
        'cr_cache.tests.arguments',
        'cr_cache.tests.commands',
        'cr_cache.tests.store',
        'cr_cache.tests.ui',
        ],
      install_requires=[
        'extras',
        'six',
        ],
      setup_requires=[
        'extras',
      ],
      tests_require=[
        'discover',
        'fixtures',
        'testresources',
        'testscenarios',
        'testtools',
      ],
      extras_require = dict(
        test=[
            ]
        ),
      cmdclass=cmdclass,
      )
