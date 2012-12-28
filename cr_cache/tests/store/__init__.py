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

"""Tests for crcache.store."""

import unittest

def test_suite():
    """Test suite thunk, manually defined for Python 2.6."""
    test_mods = [
        '__init__',
        'local',
    ]
    test_names = ['cr_cache.tests.store.test_' + name for name in test_mods]
    loader = unittest.TestLoader()
    return loader.loadTestsFromNames(test_names)
