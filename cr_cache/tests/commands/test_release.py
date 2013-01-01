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

from cr_cache.commands import release
from cr_cache.config import Config
from cr_cache.ui.model import UI
from cr_cache.tests import TestCase
from cr_cache.tests.test_config import SourceConfigFixture


class TestCommand(TestCase):

    def get_test_ui_and_cmd(self,args=(), options=()):
        ui = UI(args=args, options=options)
        cmd = release.release(ui)
        ui.set_command(cmd)
        return ui, cmd

    def test_release_known(self):
        self.useFixture(SourceConfigFixture('model', 'model'))
        conf = Config()
        source = conf.get_source('model')
        resources = list(source.provision(2))
        ui, cmd = self.get_test_ui_and_cmd(args=resources)
        result = cmd.execute()
        self.assertEqual([], ui.outputs)
        self.assertEqual(0, result)
