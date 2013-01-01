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

"""Tests for the help command."""

from cr_cache.commands import status
from cr_cache.ui.model import UI
from cr_cache.tests import TestCase
from cr_cache.tests.test_config import SourceConfigFixture


class TestCommand(TestCase):

    def get_test_ui_and_cmd(self,args=()):
        ui = UI(args=args)
        cmd = status.status(ui)
        ui.set_command(cmd)
        return ui, cmd

    def test_shows_all_sources_status(self):
        ui, cmd = self.get_test_ui_and_cmd()
        self.useFixture(SourceConfigFixture('model', 'model'))
        cmd.execute()
        self.assertEqual(
            [('table', [
                ('source', 'cached', 'in-use', 'max'),
                ('local', '0', '0', '1'),
                ('model', '0', '0', '0'),
                ]),
            ], ui.outputs)
