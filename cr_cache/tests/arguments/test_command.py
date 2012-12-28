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

"""Tests for the command argument."""

from testtools.matchers import raises

from cr_cache.arguments import command
from cr_cache.commands import help
from cr_cache.tests import TestCase


class TestArgument(TestCase):

    def test_looks_up_command(self):
        arg = command.CommandArgument('name')
        result = arg.parse(['help'])
        self.assertEqual([help.help], result)

    def test_no_command(self):
        arg = command.CommandArgument('name')
        self.assertThat(lambda: arg.parse(['one']),
            raises(ValueError("Could not find command 'one'.")))

