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

"""Am object based UI for cr_cache."""

from io import StringIO
import optparse

from cr_cache import ui


class UI(ui.AbstractUI):
    """A object based UI.
    
    This is useful for reusing the Command objects that provide a simplified
    interaction model with the domain logic from python. It is used for
    testing cr_cache commands.
    """

    def __init__(self, input_streams=None, options=(), args=(),
        here='memory:', proc_outputs=(), proc_results=()):
        """Create a model UI.

        :param input_streams: A list of stream name, (file or bytes) tuples to
            be used as the available input streams for this ui.
        :param options: Options to explicitly set values for.
        :param args: The argument values to give the UI.
        :param here: Set the here value for the UI.
        :param proc_outputs: byte strings to be returned in the stdout from
            created processes.
        :param proc_results: numeric exit code to be set in each created
            process.
        """
        self.input_streams = {}
        if input_streams:
            for stream_type, stream_value in input_streams:
                self.input_streams.setdefault(stream_type, []).append(
                    stream_value)
        self.here = here
        self.unparsed_opts = options
        self.outputs = []
        # Could take parsed args, but for now this is easier.
        self.unparsed_args = args
        self.proc_outputs = list(proc_outputs)
        self.proc_results = list(proc_results)

    def _check_cmd(self):
        options = list(self.unparsed_opts)
        self.options = optparse.Values()
        seen_options = set()
        for option, value in options:
            setattr(self.options, option, value)
            seen_options.add(option)
        if not 'quiet' in seen_options:
            setattr(self.options, 'quiet', False)
        for option in self.cmd.options:
            if not option.dest in seen_options:
                setattr(self.options, option.dest, option.default)
        args = list(self.unparsed_args)
        parsed_args = {}
        failed = False
        for arg in self.cmd.args:
            try:
                parsed_args[arg.name] = arg.parse(args)
            except ValueError:
                failed = True
                break
        self.arguments = parsed_args
        return args == [] and not failed

    def _iter_streams(self, stream_type):
        streams = self.input_streams.pop(stream_type, [])
        for stream_value in streams:
            if getattr(stream_value, 'read', None):
                yield stream_value
            else:
                yield StringIO(stream_value)

    def output_error(self, error_tuple):
        self.outputs.append(('error', error_tuple))

    def output_rest(self, rest_string):
        self.outputs.append(('rest', rest_string))

    def output_stream(self, stream):
        self.outputs.append(('stream', stream.read()))

    def output_table(self, table):
        self.outputs.append(('table', table))

    def output_values(self, values):
        self.outputs.append(('values', values))
