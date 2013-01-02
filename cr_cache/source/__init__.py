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

"""The basic interface for getting hold of compute resources.

Interesting modules:
local : sources local compute resources.
model : for testing.
"""

class AbstractSource(object):
    """Defines the contract for a source.
    
    :attr config: The ConfigParser object containing the configuration of the
        source.
    :attr get_source: The configured callback to obtain other sources.
    :attr children: Cache child objects, used for status and introspection.
        May only be read from, not mutated.
    :attr maximum: Exported maximum instance count for this source. Defaults to
        0 - unlimited.
    """

    def __init__(self, config, get_source):
        """Create an AbstractSource.

        :param config: A ConfigParser config containing the configuration for
            the source.
        :param get_source: A callback to get a new source (used when sources
            layer).
        """
        self.config = config
        self.get_source = get_source
        self.children = []
        self.maximum = 0
        self._init()

    def _init(self):
        """Stub child classes can override for initialisation."""

    def provision(self, count):
        """Provision one or more instances.
        
        :raises TooManyInstances: if the call would exceed the source's maximum
            available resource count. This should not be raised until
            self.maximum instances have been issued.
        """
        raise NotImplementedError(self.provision)

    def discard(self, instances):
        """Discard one or more instances."""
        raise NotImplementedError(self.discard)

    def subprocess_Popen(self, instance, *args, **kwargs):
        """Call an external process via the source.
        
        The behaviour of this call should match that of subprocess.Popen with
        one exception - SIGPIPE should be defaulted automatically.
        """
        raise NotImplementedError(self.subprocess_Popen)


def find_source_type(name):
    modname = "cr_cache.source.%s" % name
    return __import__(modname, globals(), locals(), ['Source']).Source


class TooManyInstances(Exception):
    """Too many instances have been pulled (or would be pulled)."""


class UnknownInstance(ValueError):
    """An unknown resource was requested/supplied."""
