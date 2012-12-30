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

"""Tests for the store contract and common facilities."""

from functools import partial

from testtools.matchers import raises

from cr_cache.store import local, memory, read_locked, write_locked
from cr_cache.tests import TestCase

def memory_factory():
    backend = {}
    return partial(memory.Store, backend)

# what implementations do we need to test?
store_implementations = [
    ('Local', {'store_factory_factory': lambda:local.Store}),
    ('Memory', {'store_factory_factory': memory_factory}),
    ]


class TestStoreContract(TestCase):

    scenarios = store_implementations

    def make_store(self):
        if not getattr(self, 'store_factory', None):
            self.store_factory = self.store_factory_factory()
        return self.store_factory()

    def test_put(self):
        s = self.make_store()
        with write_locked(s):
            s['foo'] = 'bar'

    def test_get(self):
        s = self.make_store()
        s2 = self.make_store()
        with write_locked(s):
            s['foo'] = 'bar'
        with read_locked(s):
            self.assertEqual('bar', s['foo'])
        # The change is immediately visible to other store instances.
        with read_locked(s2):
            self.assertEqual('bar', s2['foo'])

    def test_get_missing(self):
        s = self.make_store()
        with read_locked(s):
            self.assertThat(lambda:s['bar'], raises(KeyError))

    def test_delete(self):
        s = self.make_store()
        s2 = self.make_store()
        with write_locked(s):
            s['foo'] = 'bar'
        with write_locked(s):
            del s['foo']
        with read_locked(s):
            self.assertThat(lambda:s['foo'], raises(KeyError))
        # The change is immediately visible to other store instances.
        with read_locked(s2):
            self.assertThat(lambda:s2['foo'], raises(KeyError))

    def test_lock_read_exist(self):
        s = self.make_store()
        s.lock_read()
        s.unlock()

    def test_lock_read_reentrant(self):
        s = self.make_store()
        with write_locked(s):
            s['f'] = 't'
        s.lock_read()
        try:
            try:
                s.lock_read()
                s['f']
            finally:
                s.unlock()
            s['f']
        finally:
            s.unlock()

    def test_lock_write_exist(self):
        s = self.make_store()
        s.lock_write()
        s.unlock()

    def test_lock_write_reentrant(self):
        s = self.make_store()
        s.lock_write()
        try:
            try:
                s.lock_write()
                s['f'] = 't'
            finally:
                s.unlock()
            s['f'] = 't'
        finally:
            s.unlock()

    def test_unlock_exist(self):
        s = self.make_store()
        s.lock_read()
        s.unlock()


class TestDecorators(TestCase):

    def test_read_locked(self):
        s = memory.Store({})
        self.assertEqual('u', s._lock)
        with read_locked(s):
            self.assertEqual('r', s._lock)
        self.assertEqual('u', s._lock)

    def test_write_locked(self):
        s = memory.Store({})
        self.assertEqual('u', s._lock)
        with write_locked(s):
            self.assertEqual('w', s._lock)
        self.assertEqual('u', s._lock)
