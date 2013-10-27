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
        help = """CRCache
+++++++

Copyright (c) 2013 crcache contributors

Licensed under either the Apache License, Version 2.0 or the BSD 3-clause
license at the users choice. A copy of both licenses are available in the
project source as Apache-2.0 and BSD. You may not use this file except in
compliance with one of these two licences.

Unless required by applicable law or agreed to in writing, software
distributed under these licenses is distributed on an "AS IS" BASIS, WITHOUT
WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.  See the
license you chose for the specific language governing permissions and
limitations under that license.

Overview
++++++++

crcache - Compute resource cache - is a command line tool that abstracts out
obtaining, using and reusing computing resources. This permits separation of
project concerns (such as 'run dpkg-buildpackage') from environmental concerns
(such as using a Debian wheezy chroot to run the command in).

crcache lets you write programs that need to scale to multiple machines without
tying yourself to one particular provisioning system. For instance, running
tests locally, in lxc containers or in a compute cloud can be done with one
crcache call, and the user can tell crcache where (and how) to obtain the
compute resource to run the test in. A simple configuration system and command
line API make it easy to reconfigure at will.

The default configuration will run commands locally with no container or any
other isolation::

    $ crcache acquire
    local
    $ crcache run local echo foo
    foo
    $ crcache release local

See the manual on https://crcache.readthedocs.org/ or in the docs/ subdirectory
of the source tree for configuration details.

Differences to "Cloud" APIs
+++++++++++++++++++++++++++

crcache differs to cloud APIs (both cloud specific and vendor neutral) in a few
key ways:

* It focuses on running simple commands within each resources, which gives a
  simple programming model.

* Programs that layer on it do not need to know about the whole cloud computing
  model, instead that is a matter for configuration by the user.

* It manages state locally, allowing mix-and-match across many clouds and/or
  local facilities such as chroots and containers.

Installation
++++++++++++

Pip is the easiest way to install crcache::

    $ pip install crcache

Requirements
++++++++++++

crcache is intended to be widely portable. It should run (and if it doesn't,
its a bug) on any platform as long as you have:

* Python 2.6+ or 3.2+.

* The 'extras' Python module.

* The 'six' Python module.

Some of the provider plugins for cr_cache may be less portable. When a provider
depends on things outside the standard library (or newer than the version range
above), it is placed in a separate tree, so that its installation is optional.

"""
        self.ui.output_rest(help)
        return 0
