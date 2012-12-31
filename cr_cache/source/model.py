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

from cr_cache import source

class Source(source.AbstractSource):
    """An in-memory testing source."""

    def _init(self):
        self._generator = count()

    def provision(self, count):
        return [str(x) for x in islice(self._generator, count)]

    def discard(self, instances):
        return None
