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

from operator import attrgetter, methodcaller
import optparse

from cr_cache.arguments import string
from cr_cache.commands import Command
from cr_cache import config

class status(Command):
    """Show cache status."""

    args = [string.StringArgument('(re)sources', min=0, max=None)]
    options = [
        optparse.Option(
            "--query", default=None,
            help="Query a single field. Returns the sum of that field for all"
                " selected sources.",
            choices=['cached', 'in-use', 'max', 'available']),
        optparse.Option(
            "--verbose", "-v", help="Show more details.",
            default=False, action="store_true"),
        ]

    def run(self):
        conf = config.Config()
        table = [('source', 'cached', 'in-use', 'max')]
        details_table = [('source', 'instance')]
        sources = config.sources(config.default_path())
        if 'local' not in sources:
            sources.add('local')
        if self.ui.arguments['(re)sources']:
            query = sorted(self.ui.arguments['(re)sources'])
            check = set(query).__contains__
        else:
            check = lambda x:True
        sources = [conf.get_source(source_name) for source_name
            in sorted(sources) if check(source_name)]
        def available(source):
            return source.maximum - source.in_use()
        if self.ui.options.query:
            source_map = {
                'cached': methodcaller('cached'),
                'in-ues': methodcaller('in_use'),
                'max': attrgetter('maximum'),
                'available': available
                }
            lookup = source_map[self.ui.options.query]
            result = sum(map(lookup, sources))
            self.ui.output_rest('%d' % result)
            return 0
        for source in sources:
            cached = str(source.cached())
            in_use = str(source.in_use())
            table.append((source.name, cached, in_use, str(source.maximum)))
            if self.ui.options.verbose:
                instances = sorted(source.instances())
                if not instances:
                    continue
                details_table.append((source.name, instances[0]))
                for instance in instances[1:]:
                    details_table.append(('', instance))
        self.ui.output_table(table)
        if self.ui.options.verbose:
            self.ui.output_rest("\n")
            self.ui.output_table(details_table)
        return 0
