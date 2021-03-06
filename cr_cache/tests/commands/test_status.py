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

"""Tests for the status command."""

from cr_cache.commands import status
from cr_cache.config import Config
from cr_cache.ui.model import UI
from cr_cache.tests import TestCase
from cr_cache.tests.test_config import SourceConfigFixture


class TestCommand(TestCase):

    def get_test_ui_and_cmd(self,args=(), options=()):
        ui = UI(args=args, options=options)
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

    def test_shows_in_use(self):
        ui, cmd = self.get_test_ui_and_cmd()
        self.useFixture(SourceConfigFixture('model', 'model'))
        source = Config().get_source('model')
        self.addCleanup(source.discard, source.provision(1))
        cmd.execute()
        self.assertEqual(
            [('table', [
                ('source', 'cached', 'in-use', 'max'),
                ('local', '0', '0', '1'),
                ('model', '0', '1', '0'),
                ]),
            ], ui.outputs)

    def test_shows_in_use_verbose(self):
        ui, cmd = self.get_test_ui_and_cmd(options=[('verbose', True)])
        self.useFixture(SourceConfigFixture('model', 'model'))
        source = Config().get_source('model')
        self.addCleanup(source.discard, source.provision(1))
        cmd.execute()
        self.assertEqual(
            [('table', [
                ('source', 'cached', 'in-use', 'max'),
                ('local', '0', '0', '1'),
                ('model', '0', '1', '0'),
                ]),
             ('rest', '\n'),
             ('table', [('source', 'instance'), ('model', u'model-0')]),
            ], ui.outputs)

    def test_shows_cached(self):
        ui, cmd = self.get_test_ui_and_cmd()
        self.useFixture(SourceConfigFixture('model', 'model', reserve=1))
        source = Config().get_source('model')
        source.fill_reserve()
        cmd.execute()
        self.assertEqual(
            [('table', [
                ('source', 'cached', 'in-use', 'max'),
                ('local', '0', '0', '1'),
                ('model', '1', '0', '0'),
                ]),
            ], ui.outputs)

    def test_filter_source(self):
        ui, cmd = self.get_test_ui_and_cmd(args=['local'])
        self.useFixture(SourceConfigFixture('model', 'model', reserve=1))
        source = Config().get_source('model')
        source.fill_reserve()
        cmd.execute()
        self.assertEqual(
            [('table', [
                ('source', 'cached', 'in-use', 'max'),
                ('local', '0', '0', '1'),
                ]),
            ], ui.outputs)

    def test_query_field(self):
        ui, cmd = self.get_test_ui_and_cmd(
            args=['local'], options=[('query', 'available')])
        self.useFixture(SourceConfigFixture('model', 'model', reserve=1))
        source = Config().get_source('model')
        source.fill_reserve()
        cmd.execute()
        self.assertEqual([('rest', '1')], ui.outputs)
