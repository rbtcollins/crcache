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

"""Grab instances from a source."""

import optparse

from cr_cache.arguments import number
from cr_cache.commands import Command
from cr_cache import config

class acquire(Command):
    """Obtain one or more resources from a source for use.
    
    Each resource will be reserved for exclusive use until
    released by crcache release.
    """

    args = [number.IntegerArgument('resource_count', min=0)]
    options = [
        optparse.Option(
            "--source", "-s", help="What source to acquire from.",
            default="local"),
        ]

    def run(self):
        conf = config.Config()
        source = conf.get_source(self.ui.options.source)
        resource_count = 1
        if len(self.ui.arguments['resource_count']):
            resource_count = self.ui.arguments['resource_count'][0]
        resources = source.provision(resource_count)
        self.ui.output_rest(" ".join(sorted(resources)))
        return 0
