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

"""Tests for the acquire command."""

from cr_cache.commands import acquire
from cr_cache.config import Config
from cr_cache.ui.model import UI
from cr_cache.tests import TestCase
from cr_cache.tests.test_config import SourceConfigFixture


class TestCommand(TestCase):

    def get_test_ui_and_cmd(self,args=(), options=()):
        ui = UI(args=args, options=options)
        cmd = acquire.acquire(ui)
        ui.set_command(cmd)
        return ui, cmd

    def test_acquires_defaults(self):
        ui, cmd = self.get_test_ui_and_cmd()
        self.useFixture(SourceConfigFixture('local', 'model'))
        cmd.execute()
        self.assertEqual([('rest', 'local-0')], ui.outputs)

    def test_acquire_count(self):
        ui, cmd = self.get_test_ui_and_cmd(args=['2'])
        self.useFixture(SourceConfigFixture('local', 'model'))
        cmd.execute()
        self.assertEqual([('rest', 'local-0 local-1')], ui.outputs)

    def test_acquires_source(self):
        ui, cmd = self.get_test_ui_and_cmd(options=[('source', 'model')])
        self.useFixture(SourceConfigFixture('model', 'model'))
        cmd.execute()
        self.assertEqual([('rest', 'model-0')], ui.outputs)
