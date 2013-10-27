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

"""A command line UI for cr_cache."""

import io
import os
import sys

from cr_cache import ui
from cr_cache.commands import get_command_parser


class UI(ui.AbstractUI):
    """A command line user interface."""

    def __init__(self, argv, stdin, stdout, stderr):
        """Create a command line UI.

        :param argv: Arguments from the process invocation.
        :param stdin: The stream for stdin.
        :param stdout: The stream for stdout.
        :param stderr: The stream for stderr.
        """
        self._argv = argv
        self._stdin = stdin
        self._stdout = stdout
        self._stderr = stderr

    def _iter_streams(self, stream_type):
        yield self._stdin

    def output_error(self, error_tuple):
        if 'CRCACHE_PDB' in os.environ:
            import traceback
            self._stderr.write(u''.join(traceback.format_tb(error_tuple[2])))
            self._stderr.write(u'\n')
            # This is terrible: it is because on Python2.x pdb writes bytes to
            # its pipes, and the test suite uses io.StringIO that refuse bytes.
            import pdb;
            if sys.version_info[0]==2:
                if isinstance(self._stdout, io.StringIO):
                    write = self._stdout.write
                    def _write(text):
                        return write(text.decode('utf8'))
                    self._stdout.write = _write
            p = pdb.Pdb(stdin=self._stdin, stdout=self._stdout)
            p.reset()
            p.interaction(None, error_tuple[2])
        error_type = str(error_tuple[1])
        # XX: Python2.
        if type(error_type) is bytes:
            error_type = error_type.decode('utf8')
        self._stderr.write(error_type + u'\n')

    def output_rest(self, rest_string):
        self._stdout.write(rest_string)
        if not rest_string.endswith('\n'):
            self._stdout.write(u'\n')

    def output_stream(self, stream):
        contents = stream.read(65536)
        while contents:
            self._stdout.write(contents)
            contents = stream.read(65536)

    def output_table(self, table):
        # stringify
        contents = []
        for row in table:
            new_row = []
            for column in row:
                new_row.append(str(column))
            contents.append(new_row)
        if not contents:
            return
        widths = [0] * len(contents[0])
        for row in contents:
            for idx, column in enumerate(row):
                if widths[idx] < len(column):
                    widths[idx] = len(column)
        # Show a row
        outputs = []
        def show_row(row):
            for idx, column in enumerate(row):
                outputs.append(column)
                if idx == len(row) - 1:
                    outputs.append(u'\n')
                    return
                # spacers for the next column
                outputs.append(u' '*(widths[idx]-len(column)))
                outputs.append(u'  ')
        show_row(contents[0])
        # title spacer
        for idx, width in enumerate(widths):
            outputs.append(u'-'*width)
            if idx == len(widths) - 1:
                outputs.append(u'\n')
                continue
            outputs.append(u'  ')
        for row in contents[1:]:
            show_row(row)
        self._stdout.write(u''.join(outputs))

    def output_values(self, values):
        outputs = []
        for label, value in values:
            outputs.append(u'%s=%s' % (label, value))
        self._stdout.write(u'%s\n' % ', '.join(outputs))

    def _check_cmd(self):
        parser = get_command_parser(self.cmd)
        parser.add_option("-d", "--here", dest="here",
            help="Set the directory or url that a command should run from. "
            "This affects all default path lookups but does not affect paths "
            "supplied to the command.", default=os.getcwd(), type=str)
        parser.add_option("-q", "--quiet", action="store_true", default=False,
            help="Turn off output other than the primary output for a command "
            "and any errors.")
        # yank out --, as optparse makes it silly hard to just preserve it.
        try:
            where_dashdash = self._argv.index('--')
            opt_argv = self._argv[:where_dashdash]
            other_args = self._argv[where_dashdash:]
        except ValueError:
            opt_argv = self._argv
            other_args = []
        if '-h' in opt_argv or '--help' in opt_argv or '-?' in opt_argv:
            self.output_rest(parser.format_help())
            # Fugly, but its what optparse does: we're just overriding the
            # output path.
            raise SystemExit(0)
        options, args = parser.parse_args(opt_argv)
        args += other_args
        self.here = options.here
        self.options = options
        parsed_args = {}
        failed = False
        for arg in self.cmd.args:
            try:
                parsed_args[arg.name] = arg.parse(args)
            except ValueError:
                exc_info = sys.exc_info()
                failed = True
                self._stderr.write(u"%s\n" % str(exc_info[1]))
                break
        if not failed:
            self.arguments = parsed_args
            if args != []:
                self._stderr.write(u"Unexpected arguments: %r\n" % args)
        return not failed and args == []
