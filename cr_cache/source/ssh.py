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

"""Provide access to an existing machine over ssh."""

from cr_cache import source
import cr_cache.source.local

class Source(source.AbstractSource):
    """Access to a resource via ssh.
    
    Configured via ssh_host=hostname in the config.
    """

    def _init(self):
        self.maximum = 1
        self.hostname = self.config['ssh_host']

    def provision(self, count):
        if count > 1:
            raise source.TooManyInstances()
        return [self.hostname] * count

    def discard(self, instances):
        if instances != [self.hostname]:
            raise source.UnknownInstance(instances)

    def subprocess_Popen(self, resource, *args, **kwargs):
        if resource != self.hostname:
            raise source.UnknownInstance("No such resource %r." % resource)
        # Perhaps should use a master connection to reduce latency on
        # subsequent commands.
        backend = source.local.Source(None, None)
        command = ['ssh', '-t', self.hostname] + args[0]
        args = (command,) + args[1:]
        return backend.subprocess_Popen('local', *args, **kwargs)
