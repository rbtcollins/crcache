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

import ConfigParser
import os.path

from testtools.matchers import raises

from cr_cache import cache
from cr_cache.source import local, model, pool
from cr_cache.store import memory, read_locked
from cr_cache.tests import TestCase

class TestCache(TestCase):

    def test_construct(self):
        # Cache objects need a name, store, source.
        source = model.Source(None, None)
        store = memory.Store({})
        c = cache.Cache("foo", store, source)
        # They have optional reserve and maximum watermarks.
        c = cache.Cache("foo", store, source, reserve=2, maximum=4)
        # Which can be supplied separately.
        c = cache.Cache("foo", store, source, reserve=2)
        c = cache.Cache("foo", store, source, maximum=4)
        # If a source has children, then
        c = cache.Cache("c", store, source, reserve=2, maximum=4)
        config = ConfigParser.ConfigParser()
        config.set("DEFAULT", "sources", "c")
        children = {'c': c}
        p = pool.Source(config, children.__getitem__)
        # maximum is clamped to sum() child maximums.
        self.assertEqual(4, cache.Cache("bar", store, p, maximum=10).maximum)
        # Except when any child is unlimited
        c2 = cache.Cache("c2", store, source)
        children['c2'] = c2
        config.set("DEFAULT", "sources", "c,c2")
        p = pool.Source(config, children.__getitem__)
        self.assertEqual(10, cache.Cache("bar", store, p, maximum=10).maximum)

    def test_maximum_capped_by_source_maximum(self):
        config = ConfigParser.ConfigParser()
        source = local.Source(config, None)
        store = memory.Store({})
        # Unlimited case.
        c = cache.Cache("foo", store, source)
        self.assertEqual(1, c.maximum)
        # Too-high a limit case.
        c = cache.Cache("foo", store, source, maximum=2)
        self.assertEqual(1, c.maximum)
        # A lower limit wins though.

    def test_fill_reserve(self):
        source = model.Source(None, None)
        c = cache.Cache("foo", memory.Store({}), source, reserve=3)
        c.provision(1)
        c.fill_reserve()
        self.assertEqual(1, c.in_use())
        self.assertEqual(2, c.cached())
        # Check its all mapped correctly.
        with read_locked(c.store):
            self.assertEqual('0,1,2', c.store['pool/foo'])
            self.assertEqual('0', c.store['allocated/foo'])
            self.assertEqual('foo', c.store['resource/0'])
            self.assertEqual('foo', c.store['resource/1'])
            self.assertEqual('foo', c.store['resource/2'])

    def test_provision_single(self):
        source = model.Source(None, None)
        c = cache.Cache("foo", memory.Store({}), source)
        self.assertEqual(0, c.in_use())
        # One instance should be returned
        self.assertEqual(set(['foo-0']), c.provision(1))
        self.assertEqual(1, c.in_use())
        # The instance should have been mapped in both directions in the store.
        with read_locked(c.store):
            self.assertEqual('0', c.store['pool/foo'])
            self.assertEqual('foo', c.store['resource/0'])

    def test_provision_several(self):
        source = model.Source(None, None)
        c = cache.Cache("foo", memory.Store({}), source)
        # Three instance should be returned
        self.assertEqual(set(['foo-0', 'foo-1', 'foo-2']), c.provision(3))
        self.assertEqual(3, c.in_use())
        # The instances should have been mapped in both directions in the store.
        with read_locked(c.store):
            self.assertEqual('0,1,2', c.store['pool/foo'])
            self.assertEqual('foo', c.store['resource/0'])
            self.assertEqual('foo', c.store['resource/1'])
            self.assertEqual('foo', c.store['resource/2'])

    def test_provision_separate_calls(self):
        source = model.Source(None, None)
        c = cache.Cache("foo", memory.Store({}), source)
        self.assertEqual(set(['foo-0', 'foo-1']), c.provision(2))
        self.assertEqual(2, c.in_use())
        self.assertEqual(set(['foo-2', 'foo-3']), c.provision(2))
        self.assertEqual(4, c.in_use())
        # The instances should have been mapped in both directions in the store.
        with read_locked(c.store):
            self.assertEqual('0,1,2,3', c.store['pool/foo'])
            self.assertEqual('foo', c.store['resource/0'])
            self.assertEqual('foo', c.store['resource/1'])
            self.assertEqual('foo', c.store['resource/2'])
            self.assertEqual('foo', c.store['resource/3'])

    def test_provision_pulls_from_reserve(self):
        source = model.Source(None, None)
        c = cache.Cache("foo", memory.Store({}), source, reserve=2)
        c.discard(c.provision(2))
        self.assertEqual(0, c.in_use())
        self.assertEqual(2, c.cached())
        self.assertEqual(set(['foo-0', 'foo-1', 'foo-2']), c.provision(3))
        self.assertEqual(3, c.in_use())
        self.assertEqual(0, c.cached())
        # The instances should have been mapped in both directions in the store.
        with read_locked(c.store):
            self.assertEqual('0,1,2', c.store['pool/foo'])
            self.assertEqual('foo', c.store['resource/0'])
            self.assertEqual('foo', c.store['resource/1'])
            self.assertEqual('foo', c.store['resource/2'])

    def test_provision_to_cap(self):
        source = model.Source(None, None)
        c = cache.Cache("foo", memory.Store({}), source, maximum=2)
        self.assertEqual(2, c.available())
        c.provision(2)
        self.assertEqual(0, c.available())

    def test_provision_at_cap(self):
        source = model.Source(None, None)
        c = cache.Cache("foo", memory.Store({}), source, maximum=2)
        c.provision(2)
        self.assertThat(lambda: c.provision(1), raises(ValueError))
        # The source was not interrogated for more resources.
        self.assertEqual(['2'], source.provision(1))
        with read_locked(c.store):
            self.assertEqual('0,1', c.store['pool/foo'])
            self.assertThat(lambda:c.store['resource/2'], raises(KeyError))

    def test_provision_beyond_cap(self):
        source = model.Source(None, None)
        c = cache.Cache("foo", memory.Store({}), source, maximum=2)
        self.assertThat(lambda: c.provision(3), raises(ValueError))

    def test_provision_from_cache(self):
        source = model.Source(None, None)
        c = cache.Cache("foo", memory.Store({}), source, reserve=2)
        c.discard(c.provision(2))
        self.assertEqual(set(['foo-0', 'foo-1']), c.provision_from_cache(5))

    def test_discard_single(self):
        source = model.Source(None, None)
        c = cache.Cache("foo", memory.Store({}), source)
        c.provision(2)
        c.discard(['foo-0'])
        self.assertEqual(1, c.in_use())
        self.assertEqual(0, c.cached())
        # The instance should have been unmapped in both directions from the
        # store.
        with read_locked(c.store):
            self.assertEqual('1', c.store['pool/foo'])
            self.assertThat(lambda:c.store['resource/0'], raises(KeyError))

    def test_discard_multiple(self):
        source = model.Source(None, None)
        c = cache.Cache("foo", memory.Store({}), source)
        c.provision(4)
        c.discard(['foo-0', 'foo-2'])
        self.assertEqual(2, c.in_use())
        self.assertEqual(0, c.cached())
        self.assertEqual(
            [('provision', 4), ('discard', ['0', '2'])], source._calls)
        # The instances should have been unmapped in both directions from the
        # store.
        with read_locked(c.store):
            self.assertEqual('1,3', c.store['pool/foo'])
            self.assertThat(lambda:c.store['resource/0'], raises(KeyError))
            self.assertThat(lambda:c.store['resource/2'], raises(KeyError))

    def test_discard_keeps_reserve_level(self):
        source = model.Source(None, None)
        c = cache.Cache("foo", memory.Store({}), source, reserve=1)
        c.discard(c.provision(2))
        self.assertEqual(0, c.in_use())
        self.assertEqual(1, c.cached())
        self.assertEqual(
            [('provision', 2), ('discard', ['1'])], source._calls)
        # The instance should have been unmapped in both directions from the
        # store.
        with read_locked(c.store):
            self.assertEqual('0', c.store['pool/foo'])
            self.assertThat(lambda:c.store['resource/1'], raises(KeyError))
            self.assertEqual('foo', c.store['resource/0'])

    def test_discard_increases_available(self):
        source = model.Source(None, None)
        c = cache.Cache("foo", memory.Store({}), source, reserve=1, maximum=4)
        self.assertEqual(4, c.available())
        c.discard(c.provision(2))
        self.assertEqual(4, c.available())

    def test_discard_force_ignores_reserve(self):
        source = model.Source(None, None)
        c = cache.Cache("foo", memory.Store({}), source, reserve=1)
        c.discard(c.provision(2), force=True)
        self.assertEqual(
            [('provision', 2), ('discard', ['0', '1'])], source._calls)
        # The instance should have been unmapped in both directions from the
        # store.
        with read_locked(c.store):
            self.assertEqual('', c.store['pool/foo'])
            self.assertThat(lambda:c.store['resource/0'], raises(KeyError))
            self.assertThat(lambda:c.store['resource/1'], raises(KeyError))
