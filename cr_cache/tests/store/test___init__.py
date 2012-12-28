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

from cr_cache.store import local, memory
from cr_cache.tests import TestCase


# what implementations do we need to test?
store_implementations = [
    ('Local', {'store_factory': local.Store}),
    ('Memory', {'store_factory': memory.Store}),
    ]


class TestStoreContract(TestCase):

    scenarios = store_implementations

    def test_construct(self):
        self.store_factory()
