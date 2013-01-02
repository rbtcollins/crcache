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

"""Tests for UI support logic and the UI contract."""

from cStringIO import StringIO
import optparse
import sys

from cr_cache import arguments, commands
from cr_cache.commands import help
from cr_cache.tests import TestCase
from cr_cache.ui import cli, model


def cli_ui_factory(input_streams=None, options=(), args=()):
    if input_streams and len(input_streams) > 1:
        # TODO: turn additional streams into argv and simulated files, or
        # something - however, may need to be cli specific tests at that
        # point.
        raise NotImplementedError(cli_ui_factory)
    stdout = StringIO()
    if input_streams:
        stdin = StringIO(input_streams[0][1])
    else:
        stdin = StringIO()
    stderr = StringIO()
    argv = list(args)
    for option, value in options:
        # only bool handled so far
        if value:
            argv.append('--%s' % option)
    return cli.UI(argv, stdin, stdout, stderr)


# what ui implementations do we need to test?
ui_implementations = [
    ('CLIUI', {'ui_factory': cli_ui_factory}),
    ('ModelUI', {'ui_factory': model.UI}),
    ]


class TestUIContract(TestCase):

    scenarios = ui_implementations

    def get_test_ui(self):
        ui = self.ui_factory()
        cmd = commands.Command(ui)
        ui.set_command(cmd)
        return ui

    def test_factory_noargs(self):
        self.ui_factory()

    def test_factory_input_stream_args(self):
        self.ui_factory([('input', 'value')])

    def test_here(self):
        ui = self.get_test_ui()
        self.assertNotEqual(None, ui.here)

    def test_output_error(self):
        try:
            raise Exception('fooo')
        except Exception:
            err_tuple = sys.exc_info()
        ui = self.get_test_ui()
        ui.output_error(err_tuple)

    def test_output_rest(self):
        # output some ReST - used for help and docs.
        ui = self.get_test_ui()
        ui.output_rest('')

    def test_output_stream(self):
        # a stream of bytes can be output.
        ui = self.get_test_ui()
        ui.output_stream(StringIO())

    def test_output_table(self):
        # output_table shows a table.
        ui = self.get_test_ui()
        ui.output_table([('col1', 'col2'), ('row1c1','row1c2')])

    def test_output_values(self):
        # output_values can be called and takes a list of things to output.
        ui = self.get_test_ui()
        ui.output_values([('foo', 1), ('bar', 'quux')])

    def test_set_command(self):
        # All ui objects can be given their command.
        ui = self.ui_factory()
        cmd = commands.Command(ui)
        self.assertEqual(True, ui.set_command(cmd))

    def test_set_command_checks_args_unwanted_arg(self):
        ui = self.ui_factory(args=['foo'])
        cmd = commands.Command(ui)
        self.assertEqual(False, ui.set_command(cmd))

    def test_set_command_checks_args_missing_arg(self):
        ui = self.ui_factory()
        cmd = commands.Command(ui)
        cmd.args = [arguments.command.CommandArgument('foo')]
        self.assertEqual(False, ui.set_command(cmd))

    def test_set_command_checks_args_invalid_arg(self):
        ui = self.ui_factory(args=['a'])
        cmd = commands.Command(ui)
        cmd.args = [arguments.command.CommandArgument('foo')]
        self.assertEqual(False, ui.set_command(cmd))

    def test_args_are_exposed_at_arguments(self):
        ui = self.ui_factory(args=['help'])
        cmd = commands.Command(ui)
        cmd.args = [arguments.command.CommandArgument('foo')]
        self.assertEqual(True, ui.set_command(cmd))
        self.assertEqual({'foo':[help.help]}, ui.arguments)

    def test_set_command_with_no_name_works(self):
        # Degrade gracefully if the name attribute has not been set.
        ui = self.ui_factory()
        cmd = commands.Command(ui)
        self.assertEqual(True, ui.set_command(cmd))

    def test_options_at_options(self):
        ui = self.get_test_ui()
        self.assertEqual(False, ui.options.quiet)

    def test_options_when_set_at_options(self):
        ui = self.ui_factory(options=[('quiet', True)])
        cmd = commands.Command(ui)
        ui.set_command(cmd)
        self.assertEqual(True, ui.options.quiet)

    def test_options_on_command_picked_up(self):
        ui = self.ui_factory(options=[('demo', True)])
        cmd = commands.Command(ui)
        cmd.options = [optparse.Option("--demo", action="store_true",
            default=False, help="Do something.")]
        ui.set_command(cmd)
        self.assertEqual(True, ui.options.demo)
        # And when not given the default works.
        ui = self.ui_factory()
        cmd = commands.Command(ui)
        cmd.options = [optparse.Option("--demo", action="store_true",
            default=False, help="Do something.")]
        ui.set_command(cmd)
        self.assertEqual(False, ui.options.demo)
