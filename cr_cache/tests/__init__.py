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

"""Tests for crcache.

Tests are structed in a pattern matching the unit under test.

e.g. tests for cr_cache.commands.* are in cr_cache.tests.commands.test_*, and
the tests for cr_cache.commands itself are in cr_cache.tests.test___init__.
"""

import unittest

from fixtures import TempHomeDir
import testresources
from testscenarios import generate_scenarios
import testtools


class TestCase(testtools.TestCase, testresources.ResourcedTestCase):
    """Make all tests have resource support."""

    def setUp(self):
        super(TestCase, self).setUp()
        # Avoid any tests accidentally mutating ~.
        self.homedir = self.useFixture(TempHomeDir()).path


def test_suite():
    """Test suite thunk, manually defined for Python 2.6."""
    test_mods = [
        'config',
    ]
    test_names = ['cr_cache.tests.test_' + name for name in test_mods]
    test_pkgs = [
        'arguments',
        'commands',
        'source',
        'store',
        'ui',
    ]
    test_names.extend(
        ['cr_cache.tests.%s.test_suite' % name for name in test_pkgs])
    loader = unittest.TestLoader()
    result = loader.loadTestsFromNames(test_names)
    result = generate_scenarios(result)
    result = testresources.OptimisingTestSuite(result)
    return result
