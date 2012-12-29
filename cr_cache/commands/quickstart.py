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

"""Get a quickstart on crcache."""

from cr_cache.commands import Command

class quickstart(Command):
    """Introductory documentation for cr_cache."""

    def run(self):
        # This gets written to README.rst by Makefile.
        help = """Overview
++++++++

crcache - Compute resource cache - is a command line tool for obtaining and
reusing computing resources. This is a horribly abstract description and an
elevator pitch is really really needed.

crcache lets you write programs that need to scale to multiple machines without
tying yourself to one particular provisioning system. For instance, running
tests locally, in lxc containers or in a compute cloud can be done with one
crcache call, and the user can tell crcache where (and how) to obtain the
compute resource to run the test in. A simple configuration system and command
line API make it easy to reconfigure at will.

A sample transcript to whet your appetite::

    $ crcache -p demo available
    45
    $ crcache -p demo status
    15 allocated
    45 in pool
    2 provisioners active
    $ crcache -p demo acquire -n 2
    I1234 I5678
    $ crcache -p demo release I5678
    $ crcache -p demo run I1234 -- echo "foo"
    foo
    $ crcache -p demo release I1234
    $ crcache -p demo run I1234
    Resource I1234 is currently in the pool.
    Exit code 1
    $

Here you can see me working with a pool of compute resources called demo. Demo
is tracked locally and backed onto as many backends as I care to write.

Differences to "Cloud" APIs
+++++++++++++++++++++++++++

crcache differs to cloud APIs (both cloud specific and vendor neutral) in a few
key ways:

* It focuses on running simple commands within each resources, which gives a
  simple programming model.

* Programs that layer on it do not need to know about the whole cloud computing
  model, instead that is a matter for configuration by the user.

* It manages state locally, rather than in a remote cloud. This is a key 
  feature for the caching functionality, which is used to achieve low latency
  execution of commands.

Installation
++++++++++++

Pip is the easiest way to install crcache::

    $ pip install crcache

Requirements
++++++++++++

crcache is intended to be widely portable. It should run (and if it doesn't,
its a bug) on any platform as long as you have:

* Python 2.6+ or 3.2+.

Some of the provider plugins for cr_cache may be less portable. When a provider
depends on things outside the standard library (or newer than the version range
above), it is placed in a separate tree, so that its installation is optional.

Developing crcache
++++++++++++++++++

Releases
========

To do a release:

1. Update crcache/__init__.py to the new version.

2. Commit, make a signed tag.

3. Run `./setup.py sdist upload -s`.

4. Push the tag and trunk.

Hacking
=======

(See also doc/DESIGN.rst).

The primary repository is https://github.com/rbtcollins/crcache. Please branch
from there and use pull requests to submit changes. Bug tracking is the github
bug tracker.

Coding style
============

Pep8. Be liberal with pylint. Pragmatism over purity.

Test everything that can be sensibly tested.

Tests
=====

Can be run either with `./setup.py test` (which should install the needed
dependencies) or `testr run` (if you have installed testrepository). If for
some reason `setup.py test` does not install dependencies, they can be found
by looking in ``setup.py``.

Copyright
=========

Contributions need to be dual licensed (see COPYING), but no copyright
assignment or grants are needed.
"""
        self.ui.output_rest(help)
        return 0
