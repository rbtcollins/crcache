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

from cr_cache import cache
from cr_cache.store import memory, read_locked
from cr_cache.tests import TestCase

class TestCache(TestCase):

    def test_construct(self):
        # Cache objects need a name, a provision callback, a discard callback
        # and a store.
        c = cache.Cache("foo", None, None, None)

    def test_provision_single(self):
        provide = lambda count:[str(c) for c in range(count)]
        c = cache.Cache("foo", provide, None, memory.Store({}))
        # One instance should be returned
        self.assertEqual(['0'], c.provision(1))
        # The instance should have been mapped in both directions in the store.
        with read_locked(c.store):
            self.assertEqual('0', c.store['pool/foo'])
            self.assertEqual('foo', c.store['resource/0'])

    def test_provision_several(self):
        provide = lambda count:[str(c) for c in range(count)]
        c = cache.Cache("foo", provide, None, memory.Store({}))
        # Three instance should be returned
        self.assertEqual(['0', '1', '2'], c.provision(3))
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
        self.assertEqual(['0', '1'], c.provision(2))
        self.assertEqual(['2', '3'], c.provision(2))
        # The instances should have been mapped in both directions in the store.
        with read_locked(c.store):
            self.assertEqual('2,3,0,1', c.store['pool/foo'])
            self.assertEqual('foo', c.store['resource/0'])
            self.assertEqual('foo', c.store['resource/1'])
            self.assertEqual('foo', c.store['resource/2'])
            self.assertEqual('foo', c.store['resource/3'])

