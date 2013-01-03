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

"""Report status about the system."""

from cr_cache.arguments import string
from cr_cache.commands import Command
from cr_cache import config

class status(Command):
    """Get help on a command."""

    args = [string.StringArgument('(re)sources', min=0, max=None)]

    def run(self):
        conf = config.Config()
        table = [('source', 'cached', 'in-use', 'max')]
        sources = config.sources(config.default_path())
        if 'local' not in sources:
            sources.add('local')
        if self.ui.arguments['(re)sources']:
            query = sorted(self.ui.arguments['(re)sources'])
            check = set(query).__contains__
        else:
            check = lambda x:True
        for source_name in sorted(sources):
            if not check(source_name):
                continue
            source = conf.get_source(source_name)
            cached = str(source.cached())
            in_use = str(source.in_use())
            table.append((source.name, cached, in_use, str(source.maximum)))
        self.ui.output_table(table)
        return 0
