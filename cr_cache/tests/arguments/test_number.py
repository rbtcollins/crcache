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

"""Tests for the number argument types."""

from testtools.matchers import raises

from cr_cache.arguments import number
from cr_cache.tests import TestCase


class TestArgument(TestCase):

    def test_parses_as_int(self):
        arg = number.IntegerArgument('name')
        result = arg.parse(['1'])
        self.assertEqual([1], result)

    def test_rejects_non_int(self):
        arg = number.IntegerArgument('name')
        self.assertThat(lambda: arg.parse(['1.0']), raises(ValueError))
