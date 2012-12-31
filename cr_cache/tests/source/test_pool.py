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

import ConfigParser

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
        sources['a'] = cache.Cache(
            'a', store, backend.provision, lambda x:None, reserve=1)
        sources['b'] = cache.Cache(
            'b', store, backend.provision, lambda x:None, reserve=1)
        sources['a'].fill_reserve()
        sources['b'].fill_reserve()
        source = pool.Source(config, sources.__getitem__)
        # If we ask for 3 instances, we should get the cached one from each
        # source and then one arbitrary extra one.
        resources = source.provision(3)
        self.assertThat(set(resources), MatchesAny(
            Equals(set(['a-0', 'b-1', 'a-2'])),
            Equals(set(['a-0', 'b-1', 'b-2']))))
