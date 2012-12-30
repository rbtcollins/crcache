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

"""Tests for the crcache resource cache."""

import os.path

from testtools.matchers import raises

from cr_cache import cache
from cr_cache.store import memory, read_locked
from cr_cache.tests import TestCase

class TestCache(TestCase):

    def test_construct(self):
        # Cache objects need a name, a provision callback, a discard callback
        # a store, an optional reserve watermark, an optional maximum
        # watermark.
        c = cache.Cache("foo", None, None, None)
        c = cache.Cache("foo", None, None, None, reserve=1)
        c = cache.Cache("foo", None, None, None, maximum=1)

    def test_fill_reserve(self):
        gen = iter(range(10))
        def provide(count):
            result = []
            for _ in range(count):
                result.append(str(gen.next()))
            return result
        c = cache.Cache("foo", provide, None, memory.Store({}), reserve=3)
        c.provision(1)
        c.fill_reserve()
        # Check its all mapped correctly.
        with read_locked(c.store):
            self.assertEqual('0,1,2', c.store['pool/foo'])
            self.assertEqual('0', c.store['allocated/foo'])
            self.assertEqual('foo', c.store['resource/0'])
            self.assertEqual('foo', c.store['resource/1'])
            self.assertEqual('foo', c.store['resource/2'])

    def test_provision_single(self):
        provide = lambda count:[str(c) for c in range(count)]
        c = cache.Cache("foo", provide, None, memory.Store({}))
        # One instance should be returned
        self.assertEqual(set(['foo-0']), c.provision(1))
        # The instance should have been mapped in both directions in the store.
        with read_locked(c.store):
            self.assertEqual('0', c.store['pool/foo'])
            self.assertEqual('foo', c.store['resource/0'])

    def test_provision_several(self):
        provide = lambda count:[str(c) for c in range(count)]
        c = cache.Cache("foo", provide, None, memory.Store({}))
        # Three instance should be returned
        self.assertEqual(set(['foo-0', 'foo-1', 'foo-2']), c.provision(3))
        # The instances should have been mapped in both directions in the store.
        with read_locked(c.store):
            self.assertEqual('0,1,2', c.store['pool/foo'])
            self.assertEqual('foo', c.store['resource/0'])
            self.assertEqual('foo', c.store['resource/1'])
            self.assertEqual('foo', c.store['resource/2'])

    def test_provision_separate_calls(self):
        gen = iter(range(10))
        def provide(count):
            result = []
            for _ in range(count):
                result.append(str(gen.next()))
            return result
        c = cache.Cache("foo", provide, None, memory.Store({}))
        self.assertEqual(set(['foo-0', 'foo-1']), c.provision(2))
        self.assertEqual(set(['foo-2', 'foo-3']), c.provision(2))
        # The instances should have been mapped in both directions in the store.
        with read_locked(c.store):
            self.assertEqual('0,1,2,3', c.store['pool/foo'])
            self.assertEqual('foo', c.store['resource/0'])
            self.assertEqual('foo', c.store['resource/1'])
            self.assertEqual('foo', c.store['resource/2'])
            self.assertEqual('foo', c.store['resource/3'])

    def test_provision_pulls_from_reserve(self):
        gen = iter(range(3))
        def provide(count):
            result = []
            for _ in range(count):
                result.append(str(gen.next()))
            return result
        discard = lambda instances:None
        c = cache.Cache("foo", provide, discard, memory.Store({}), 2)
        c.discard(c.provision(2))
        self.assertEqual(set(['foo-0', 'foo-1', 'foo-2']), c.provision(3))
        # The instances should have been mapped in both directions in the store.
        with read_locked(c.store):
            self.assertEqual('0,1,2', c.store['pool/foo'])
            self.assertEqual('foo', c.store['resource/0'])
            self.assertEqual('foo', c.store['resource/1'])
            self.assertEqual('foo', c.store['resource/2'])

    def test_provision_to_cap(self):
        provide = lambda count:[str(c) for c in range(count)]
        c = cache.Cache("foo", provide, None, memory.Store({}), maximum=2)
        c.provision(2)

    def test_provision_at_cap(self):
        gen = iter(range(3))
        def provide(count):
            result = []
            for _ in range(count):
                result.append(str(gen.next()))
            return result
        c = cache.Cache("foo", provide, None, memory.Store({}), maximum=2)
        c.provision(2)
        self.assertThat(lambda: c.provision(1), raises(ValueError))
        with read_locked(c.store):
            self.assertEqual('0,1', c.store['pool/foo'])
            self.assertThat(lambda:c.store['resource/2'], raises(KeyError))

    def test_provision_beyond_cap(self):
        provide = lambda count:[str(c) for c in range(count)]
        c = cache.Cache("foo", provide, None, memory.Store({}), maximum=2)
        self.assertThat(lambda: c.provision(3), raises(ValueError))

    def test_discard_single(self):
        provide = lambda count:[str(c) for c in range(count)]
        discard = lambda instances:None
        c = cache.Cache("foo", provide, discard, memory.Store({}))
        c.provision(2)
        c.discard(['foo-0'])
        # The instance should have been unmapped in both directions from the
        # store.
        with read_locked(c.store):
            self.assertEqual('1', c.store['pool/foo'])
            self.assertThat(lambda:c.store['resource/0'], raises(KeyError))

    def test_discard_multiple(self):
        provide = lambda count:[str(c) for c in range(count)]
        calls = []
        discard = lambda instances:calls.append(instances)
        c = cache.Cache("foo", provide, discard, memory.Store({}))
        c.provision(4)
        c.discard(['foo-0', 'foo-2'])
        self.assertEqual([['0', '2']], calls)
        # The instances should have been unmapped in both directions from the
        # store.
        with read_locked(c.store):
            self.assertEqual('1,3', c.store['pool/foo'])
            self.assertThat(lambda:c.store['resource/0'], raises(KeyError))
            self.assertThat(lambda:c.store['resource/2'], raises(KeyError))

    def test_discard_keeps_reserve_level(self):
        provide = lambda count:[str(c) for c in range(count)]
        calls = []
        discard = lambda instances:calls.append(instances)
        c = cache.Cache("foo", provide, discard, memory.Store({}), reserve=1)
        c.discard(c.provision(2))
        self.assertEqual([['1']], calls)
        # The instance should have been unmapped in both directions from the
        # store.
        with read_locked(c.store):
            self.assertEqual('0', c.store['pool/foo'])
            self.assertThat(lambda:c.store['resource/1'], raises(KeyError))
            self.assertEqual('foo', c.store['resource/0'])

