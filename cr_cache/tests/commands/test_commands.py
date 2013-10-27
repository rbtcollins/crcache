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

"""Tests for the commands command."""

from cr_cache.commands import commands
from cr_cache.ui.model import UI
from cr_cache.tests import TestCase


class TestCommandCommands(TestCase):

    def get_test_ui_and_cmd(self):
        ui = UI()
        cmd = commands.commands(ui)
        ui.set_command(cmd)
        return ui, cmd

    def test_shows_a_table_of_commands(self):
        ui, cmd = self.get_test_ui_and_cmd()
        cmd.execute()
        self.assertEqual(1, len(ui.outputs))
        self.assertEqual('table', ui.outputs[0][0])
        self.assertEqual(('command', 'description'), ui.outputs[0][1][0])
        command_names = [row[0] for row in ui.outputs[0][1]]
        summaries = [row[1] for row in ui.outputs[0][1]]
        self.assertTrue('acquire' in command_names)
        self.assertTrue(
            'Release one or more resources.' in summaries)
