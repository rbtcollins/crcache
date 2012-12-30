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

"""The crcache testing data store.

This store uses a simple in-memory dict for storing data.
"""

from cr_cache.store import AbstractStore


class Store(AbstractStore):
    
    def __init__(self, backend):
        self._backend = backend
        self._lock = 'u'
        self._lock_count = 0

    def __getitem__(self, item):
        if self._lock not in 'rw':
            raise AssertionError('not locked')
        return self._backend[item]

    def __setitem__(self, item, value):
        if self._lock not in 'w':
            raise AssertionError('not locked')
        self._backend[item] = value

    def __delitem__(self, item):
        if self._lock not in 'w':
            raise AssertionError('not locked')
        del self._backend[item]

    def unlock(self):
        self._lock_count -= 1
        if not self._lock_count:
            self._lock = 'u'

    def lock_read(self):
        self._lock = 'r'
        self._lock_count += 1

    def lock_write(self):
        self._lock = 'w'
        self._lock_count += 1
