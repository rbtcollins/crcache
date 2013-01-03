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

"""Run a command on a resource."""

from cr_cache.arguments import doubledash, string
from cr_cache.commands import Command
from cr_cache import config

class run(Command):
    """Run a command on a resource.
    
    If the resource is from a caching source, it may get cached for later use,
    unless -f is supplied, which will force it to be discarded.

    If any of the resources are unknown the command will fail without taking
    any action.
    """

    args = [
        string.StringArgument('resource'),
        string.StringArgument('command', min=0),
        string.StringArgument('args', min=0, max=None),
        doubledash.DoubledashArgument(),
        string.StringArgument('moreargs', min=0, max=None),
        ]

    def run(self):
        resource = self.ui.arguments['resource'][0]
        name, remainder = resource.split('-', 1)
        conf = config.Config()
        source = conf.get_source(name).source
        command = (self.ui.arguments['command'] + self.ui.arguments['args'] +
            self.ui.arguments['moreargs'])
        proc = source.subprocess_Popen(remainder, command)
        proc.communicate()
        return proc.returncode
