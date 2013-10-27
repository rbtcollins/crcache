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

"""Tests for the crcache.source.pool module."""

import extras

ConfigParser = extras.try_imports(['ConfigParser', 'configparser'])

from testtools.matchers import Equals, MatchesAny

from cr_cache import cache
from cr_cache.source import model, pool
from cr_cache.store import memory
from cr_cache.tests import TestCase

class TestPoolSource(TestCase):

    def test_simple_construction(self):
        config = ConfigParser.ConfigParser()
        config.set('DEFAULT', 'sources', 'a,b')
        store = memory.Store({})
        backend = model.Source(None, None)
        sources = {}
        sources['a'] = cache.Cache('a', store, backend, reserve=1)
        sources['b'] = cache.Cache('b', store, backend, reserve=1)
        sources['a'].fill_reserve()
        sources['b'].fill_reserve()
        source = pool.Source(config, sources.__getitem__)
        # If we ask for 3 instances, we should get the cached one from each
        # source and then one arbitrary extra one.
        resources = source.provision(3)
        self.assertThat(set(resources), MatchesAny(
            Equals(set(['a-0', 'b-1', 'a-2'])),
            Equals(set(['a-0', 'b-1', 'b-2']))))

    def test_discard_returns_to_child_cache(self):
        config = ConfigParser.ConfigParser()
        config.set('DEFAULT', 'sources', 'a,b')
        store = memory.Store({})
        backend = model.Source(None, None)
        sources = {}
        sources['a'] = cache.Cache('a', store, backend, reserve=1, maximum=2)
        sources['b'] = cache.Cache('b', store, backend, reserve=1, maximum=2)
        sources['a'].fill_reserve()
        sources['b'].fill_reserve()
        source = pool.Source(config, sources.__getitem__)
        source.provision(4)
        source.discard(['a-0', 'b-3'])
        source.discard(['a-2', 'b-1'])
        # The first returned entries get discarded (above reserve), the next
        # two are kept in the reserve.
        self.assertEqual(set(['a-2']), sources['a'].provision(1))
        self.assertEqual(set(['b-1']), sources['b'].provision(1))

    def test_sums_component_maximums(self):
        config = ConfigParser.ConfigParser()
        config.set('DEFAULT', 'sources', 'a,b')
        store = memory.Store({})
        backend = model.Source(None, None)
        sources = {}
        sources['a'] = cache.Cache('a', store, backend, maximum=1)
        sources['b'] = cache.Cache('b', store, backend, maximum=2)
        source = pool.Source(config, sources.__getitem__)
        self.assertEqual(3, source.maximum)
