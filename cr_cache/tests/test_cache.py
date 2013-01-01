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
from cr_cache.source import model
from cr_cache.store import memory, read_locked
from cr_cache.tests import TestCase

class TestCache(TestCase):

    def test_construct(self):
        # Cache objects need a name, store, source.
        source = model.Source(None, None)
        store = memory.Store({})
        c = cache.Cache("foo", store, source, reserve=2, maximum=4)
        # They have optional reserve and maximum watermarks.
        c = cache.Cache(
            "foo", None, provision=lambda x:[], discard=lambda x:None,
            reserve=2, maximum=4)
        # Missing provision or discard callbacks implies a need for children.
        # Neither
        self.assertThat(lambda:cache.Cache("bar", None, children=[]),
            raises(ValueError))
        # Missing discard
        self.assertThat(
            lambda:cache.Cache("bar", None, provision=lambda x:[], children=[]),
            raises(ValueError))
        # Missing provision
        self.assertThat(
            lambda:cache.Cache("bar", None, discard=lambda x:None, children=[]),
            raises(ValueError))
        # provision + discard + children
        self.assertThat(
            lambda:cache.Cache("bar", None, provision=lambda x:[],
            discard=lambda x:None, children=[c]), raises(ValueError))
        cache.Cache("bar", None, children=[c])
        cache.Cache("bar", None, reserve=1, children=[c])
        cache.Cache("foo", None, maximum=1, children=[c])
        # maximum is clamped to sum() child maximums.
        self.assertEqual(4,
            cache.Cache("bar", None, maximum=10, children=[c]).maximum)
        # Except when any child is unlimited
        c2 = cache.Cache(
            "foo", None, provision=lambda x:[], discard=lambda x:None)
        self.assertEqual(10,
            cache.Cache("bar", None, maximum=10, children=[c, c2]).maximum)

    def test_fill_reserve(self):
        gen = iter(range(10))
        def provide(count):
            result = []
            for _ in range(count):
                result.append(str(gen.next()))
            return result
        source = model.Source(None, None)
        c = cache.Cache(
            "foo", memory.Store({}), source, provide, lambda x:None, reserve=3)
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
        source = model.Source(None, None)
        c = cache.Cache("foo", memory.Store({}), source, provide, lambda x:None)
        # One instance should be returned
        self.assertEqual(set(['foo-0']), c.provision(1))
        # The instance should have been mapped in both directions in the store.
        with read_locked(c.store):
            self.assertEqual('0', c.store['pool/foo'])
            self.assertEqual('foo', c.store['resource/0'])

    def test_provision_several(self):
        provide = lambda count:[str(c) for c in range(count)]
        source = model.Source(None, None)
        c = cache.Cache("foo", memory.Store({}), source, provide, lambda x:None)
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
        source = model.Source(None, None)
        c = cache.Cache("foo", memory.Store({}), source, provide, lambda x:None)
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
        source = model.Source(None, None)
        c = cache.Cache("foo", memory.Store({}), source, provide, discard, reserve=2)
        c.discard(c.provision(2))
        self.assertEqual(set(['foo-0', 'foo-1', 'foo-2']), c.provision(3))
        # The instances should have been mapped in both directions in the store.
        with read_locked(c.store):
            self.assertEqual('0,1,2', c.store['pool/foo'])
            self.assertEqual('foo', c.store['resource/0'])
            self.assertEqual('foo', c.store['resource/1'])
            self.assertEqual('foo', c.store['resource/2'])

    def test_provision_prefers_child_cached_instances(self):
        store = memory.Store({})
        provide = lambda count:[str(c) for c in range(count)]
        source = model.Source(None, None)
        c1 = cache.Cache("c1", store, source, provide, lambda x:None, reserve=2)
        c2 = cache.Cache("c2", store, source, provide, lambda x:None, reserve=2)
        c1.fill_reserve()
        c2.fill_reserve()
        c = cache.Cache("foo", store, children=[c1, c2])
        self.assertEqual(
            set(['foo-c1-0', 'foo-c1-1', 'foo-c2-0', 'foo-c2-1']),
            c.provision(4))

    def test_provision_to_cap(self):
        provide = lambda count:[str(c) for c in range(count)]
        source = model.Source(None, None)
        c = cache.Cache(
            "foo", memory.Store({}), source, provide, lambda x:None, maximum=2)
        self.assertEqual(2, c.available())
        c.provision(2)
        self.assertEqual(0, c.available())

    def test_provision_at_cap(self):
        gen = iter(range(3))
        def provide(count):
            result = []
            for _ in range(count):
                result.append(str(gen.next()))
            return result
        source = model.Source(None, None)
        c = cache.Cache(
            "foo", memory.Store({}), source, provide, lambda x:None, maximum=2)
        c.provision(2)
        self.assertThat(lambda: c.provision(1), raises(ValueError))
        with read_locked(c.store):
            self.assertEqual('0,1', c.store['pool/foo'])
            self.assertThat(lambda:c.store['resource/2'], raises(KeyError))

    def test_provision_beyond_cap(self):
        provide = lambda count:[str(c) for c in range(count)]
        source = model.Source(None, None)
        c = cache.Cache(
            "foo", memory.Store({}), source, provide, lambda x:None, maximum=2)
        self.assertThat(lambda: c.provision(3), raises(ValueError))

    def test_provision_from_cache(self):
        provide = lambda count:[str(c) for c in range(count)]
        source = model.Source(None, None)
        c = cache.Cache(
            "foo", memory.Store({}), source, provide, lambda x:None, reserve=2)
        c.discard(c.provision(2))
        self.assertEqual(set(['foo-0', 'foo-1']), c.provision_from_cache(5))

    def test_discard_single(self):
        provide = lambda count:[str(c) for c in range(count)]
        discard = lambda instances:None
        source = model.Source(None, None)
        c = cache.Cache("foo", memory.Store({}), source, provide, discard)
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
        source = model.Source(None, None)
        c = cache.Cache("foo", memory.Store({}), source, provide, discard)
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
        source = model.Source(None, None)
        c = cache.Cache("foo", memory.Store({}), source, provide, discard, reserve=1)
        c.discard(c.provision(2))
        self.assertEqual([['1']], calls)
        # The instance should have been unmapped in both directions from the
        # store.
        with read_locked(c.store):
            self.assertEqual('0', c.store['pool/foo'])
            self.assertThat(lambda:c.store['resource/1'], raises(KeyError))
            self.assertEqual('foo', c.store['resource/0'])

    def test_discard_increases_available(self):
        provide = lambda count:[str(c) for c in range(count)]
        discard = lambda instances:None
        source = model.Source(None, None)
        c = cache.Cache(
            "foo", memory.Store({}), source, provide, discard, reserve=1, maximum=4)
        self.assertEqual(4, c.available())
        c.discard(c.provision(2))
        self.assertEqual(4, c.available())

    def test_discard_returns_to_child_cache(self):
        store = memory.Store({})
        gen = iter(range(4))
        def provide(count):
            result = []
            for _ in range(count):
                result.append(str(gen.next()))
            return result
        source = model.Source(None, None)
        c1 = cache.Cache(
            "c1", store, source, provide, lambda x:None, reserve=1, maximum=2)
        c2 = cache.Cache(
            "c2", store, source, provide, lambda x:None, reserve=1, maximum=2)
        c = cache.Cache("foo", store, children=[c1, c2])
        c.provision(4)
        c.discard(['foo-c1-1', 'foo-c2-2'])
        c.discard(['foo-c1-0', 'foo-c2-3'])
        self.assertEqual(set(['c1-0']), c1.provision(1))
        self.assertEqual(set(['c2-3']), c2.provision(1))

    def test_discard_force_ignores_reserve(self):
        provide = lambda count:[str(c) for c in range(count)]
        calls = []
        discard = lambda instances:calls.append(instances)
        source = model.Source(None, None)
        c = cache.Cache("foo", memory.Store({}), source, provide, discard, reserve=1)
        c.discard(c.provision(2), force=True)
        self.assertEqual([['0', '1']], calls)
        # The instance should have been unmapped in both directions from the
        # store.
        with read_locked(c.store):
            self.assertEqual('', c.store['pool/foo'])
            self.assertThat(lambda:c.store['resource/0'], raises(KeyError))
            self.assertThat(lambda:c.store['resource/1'], raises(KeyError))
