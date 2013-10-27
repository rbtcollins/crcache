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

import doctest
from io import StringIO
import os
import sys
from textwrap import dedent

from fixtures import EnvironmentVariable
from testtools.matchers import (
    DocTestMatches,
    MatchesException,
    )

from cr_cache import arguments
from cr_cache import commands
from cr_cache.commands import help
from cr_cache.ui import cli
from cr_cache.tests import TestCase


def get_test_ui_and_cmd(options=(), args=()):
    stdout = StringIO()
    stdin = StringIO()
    stderr = StringIO()
    argv = list(args)
    for option, value in options:
        # only bool handled so far
        if value:
            argv.append('--%s' % option)
    ui = cli.UI(argv, stdin, stdout, stderr)
    cmd = help.help(ui)
    ui.set_command(cmd)
    return ui, cmd


class TestCLIUI(TestCase):

    def setUp(self):
        super(TestCLIUI, self).setUp()
        self.useFixture(EnvironmentVariable('CRCACHE_PDB'))

    def test_construct(self):
        stdout = StringIO()
        stdin = StringIO()
        stderr = StringIO()
        cli.UI([], stdin, stdout, stderr)

    def test_stream_comes_from_stdin(self):
        stdout = StringIO()
        stdin = StringIO(u'foo\n')
        stderr = StringIO()
        ui = cli.UI([], stdin, stdout, stderr)
        cmd = commands.Command(ui)
        cmd.input_streams = ['input']
        ui.set_command(cmd)
        results = []
        for stream in ui.iter_streams('input'):
            results.append(stream.read())
        self.assertEqual(['foo\n'], results)

    def test_dash_d_sets_here_option(self):
        stdout = StringIO()
        stdin = StringIO(u'foo\n')
        stderr = StringIO()
        ui = cli.UI(['-d', '/nowhere/'], stdin, stdout, stderr)
        cmd = commands.Command(ui)
        ui.set_command(cmd)
        self.assertEqual('/nowhere/', ui.here)

    def test_outputs_error_string(self):
        try:
            raise Exception('fooo')
        except Exception:
            err_tuple = sys.exc_info()
        expected = str(err_tuple[1]) + '\n'
        stdout = StringIO()
        stdin = StringIO()
        stderr = StringIO()
        ui = cli.UI([], stdin, stdout, stderr)
        ui.output_error(err_tuple)
        self.assertThat(stderr.getvalue(), DocTestMatches(expected))

    def test_error_enters_pdb_when_CRCACHE_PDB_set(self):
        os.environ['CRCACHE_PDB'] = '1'
        try:
            raise Exception('fooo')
        except Exception:
            err_tuple = sys.exc_info()
        expected = dedent("""\
              File "...test_cli.py", line ..., in ...pdb_when_CRCACHE_PDB_set
                raise Exception('fooo')
            <BLANKLINE>
            fooo
            """)
        stdout = StringIO()
        stdin = StringIO(u'c\n')
        stderr = StringIO()
        ui = cli.UI([], stdin, stdout, stderr)
        ui.output_error(err_tuple)
        self.assertThat(stderr.getvalue(),
            DocTestMatches(expected, doctest.ELLIPSIS))

    def test_outputs_rest_to_stdout(self):
        ui, cmd = get_test_ui_and_cmd()
        ui.output_rest(u'topic\n=====\n')
        self.assertEqual('topic\n=====\n', ui._stdout.getvalue())

    def test_outputs_stream_to_stdout(self):
        ui, cmd = get_test_ui_and_cmd()
        stream = StringIO(u"Foo \n bar")
        ui.output_stream(stream)
        self.assertEqual("Foo \n bar", ui._stdout.getvalue())

    def test_outputs_tables_to_stdout(self):
        ui, cmd = get_test_ui_and_cmd()
        ui.output_table([('foo', 1), ('b', 'quux')])
        self.assertEqual('foo  1\n---  ----\nb    quux\n',
            ui._stdout.getvalue())

    def test_outputs_values_to_stdout(self):
        ui, cmd = get_test_ui_and_cmd()
        ui.output_values([('foo', 1), ('bar', 'quux')])
        self.assertEqual('foo=1, bar=quux\n', ui._stdout.getvalue())

    def test_parse_error_goes_to_stderr(self):
        stdout = StringIO()
        stdin = StringIO()
        stderr = StringIO()
        ui = cli.UI(['one'], stdin, stdout, stderr)
        cmd = commands.Command(ui)
        cmd.args = [arguments.command.CommandArgument('foo')]
        ui.set_command(cmd)
        self.assertEqual("Could not find command 'one'.\n", stderr.getvalue())

    def test_parse_excess_goes_to_stderr(self):
        stdout = StringIO()
        stdin = StringIO()
        stderr = StringIO()
        ui = cli.UI(['one'], stdin, stdout, stderr)
        cmd = commands.Command(ui)
        ui.set_command(cmd)
        self.assertEqual("Unexpected arguments: ['one']\n", stderr.getvalue())

    def test_parse_options_after_double_dash_are_arguments(self):
        stdout = StringIO()
        stdin = StringIO()
        stderr = StringIO()
        ui = cli.UI(['one', '--', '--two', 'three'], stdin, stdout, stderr)
        cmd = commands.Command(ui)
        cmd.args = [arguments.string.StringArgument('myargs', max=None),
            arguments.doubledash.DoubledashArgument(),
            arguments.string.StringArgument('subargs', max=None)]
        ui.set_command(cmd)
        self.assertEqual({
            'doubledash': ['--'],
            'myargs': ['one'],
            'subargs': ['--two', 'three']},
            ui.arguments)

    def test_double_dash_passed_to_arguments(self):
        class CaptureArg(arguments.AbstractArgument):
            def _parse_one(self, arg):
                return arg
        stdout = StringIO()
        stdin = StringIO()
        stderr = StringIO()
        ui = cli.UI(['one', '--', '--two', 'three'], stdin, stdout, stderr)
        cmd = commands.Command(ui)
        cmd.args = [CaptureArg('args', max=None)]
        ui.set_command(cmd)
        self.assertEqual({'args':['one', '--', '--two', 'three']}, ui.arguments)

    def test_run_option_disabled(self):
        self.skip('no commands with options yet.')
        ui, cmd = get_test_ui_and_cmd(options=[('someopt', True)])
        self.assertEqual(True, ui.options.someopt)

    def test_dash_dash_help_shows_help(self):
        stdout = StringIO()
        stdin = StringIO()
        stderr = StringIO()
        ui = cli.UI(['--help'], stdin, stdout, stderr)
        cmd = commands.Command(ui)
        cmd.args = [arguments.string.StringArgument('foo')]
        cmd.name = "bar"
        # By definition SystemExit is not caught by 'except Exception'.
        try:
            ui.set_command(cmd)
        except SystemExit:
            exc_info = sys.exc_info()
            self.assertThat(exc_info, MatchesException(SystemExit(0)))
        else:
            self.fail('ui.set_command did not raise')
        self.assertThat(stdout.getvalue(),
            DocTestMatches("""Usage: ....py bar [options] foo
...
A command that can be run...
...
  -d HERE, --here=HERE...
...""", doctest.ELLIPSIS))
