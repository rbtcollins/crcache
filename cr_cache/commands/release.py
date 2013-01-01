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

"""Return instances that are no longer needed."""

from cr_cache.arguments import string
from cr_cache.commands import Command
from cr_cache import config

class release(Command):
    """Release one or more resources.
    
    If the resource is from a caching source, it may get cached for later use,
    unless -f is supplied, which will force it to be discarded.

    If any of the resources are unknown the command will fail without taking
    any action.
    """

    args = [string.StringArgument('resources', max=None)]

    def run(self):
        discard_map = {}
        for resource in self.ui.arguments['resources']:
            name, _ = resource.split('-', 1)
            discard_map.setdefault(name, []).append(resource)
        conf = config.Config()
        for source_name, resources in discard_map.items():
            conf.get_source(source_name).discard(resources)
        return 0
