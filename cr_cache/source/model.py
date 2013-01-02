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

"""In-memory testing 'computing' resource."""

from itertools import count, islice
from StringIO import StringIO

from cr_cache import source

class ProcessModel(object):
    """A subprocess.Popen test double."""

    def __init__(self, ui):
        self.ui = ui
        self.returncode = 0
        self.stdin = StringIO()
        self.stdout = StringIO()

    def communicate(self):
        self.ui._calls.append(('communicate',))
        return self.stdout.getvalue(), ''

    def wait(self):
        return self.returncode


class Source(source.AbstractSource):
    """An in-memory testing source.
    
    All commands run through it output 'foo\n'.
    """

    def _init(self):
        self._generator = count()
        self._calls = []

    def provision(self, count):
        self._calls.append(('provision', count))
        return [str(x) for x in islice(self._generator, count)]

    def discard(self, instances):
        self._calls.append(('discard', instances))
        return None

    def subprocess_Popen(self, resource, *args, **kwargs):
        try:
            int(resource)
        except ValueError:
            raise source.UnknownInstance(resource)
        # Really not an output - outputs should be renamed to events.
        self._calls.append(('popen', args, kwargs))
        result = ProcessModel(self)
        result.stdout = StringIO('foo\n')
        return result
