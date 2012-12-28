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

from inspect import getdoc

from testtools.matchers import Contains

from cr_cache.commands import help
from cr_cache.ui.model import UI
from cr_cache.tests import TestCase


class TestCommand(TestCase):

    def get_test_ui_and_cmd(self,args=()):
        ui = UI(args=args)
        cmd = help.help(ui)
        ui.set_command(cmd)
        return ui, cmd

    def test_shows_rest_of__doc__(self):
        ui, cmd = self.get_test_ui_and_cmd(args=['help'])
        cmd.execute()
        expected_doc = getdoc(help.help)
        self.assertThat(ui.outputs[-1][1], Contains(expected_doc))

    def test_shows_cmd_arguments(self):
        ui, cmd = self.get_test_ui_and_cmd(args=['help'])
        cmd.execute()
        self.assertThat(ui.outputs[-1][1], Contains("command"))

    def test_shows_cmd_options(self):
        return
        ui, cmd = self.get_test_ui_and_cmd(args=['help'])
        cmd.execute()
        self.assertThat(ui.outputs[-1][1], Contains("--partial"))

    def test_shows_general_help_with_no_args(self):
        ui, cmd = self.get_test_ui_and_cmd()
        self.assertEqual(0, cmd.execute())
        self.assertEqual(1, len(ui.outputs))
        self.assertEqual('rest', ui.outputs[0][0])
