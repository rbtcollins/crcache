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

"""In cr_cache a UI is an interface to a 'user' (which may be a machine).

The cr_cache.ui.cli module contains a command line interface, and the
module cr_cache.ui.model contains a purely object based implementation
which is used for testing cr_cache.

See AbstractUI for details on what UI classes should do and are responsible
for.
"""


class AbstractUI(object):
    """The base class for UI objects, this providers helpers and the interface.

    A UI object is responsible for brokering interactions with a particular
    user environment (e.g. the command line). These interactions can take
    several forms:
     - reading bulk data
     - gathering data
     - emitting progress or activity data - hints as to the programs execution.
     - providing notices about actions taken
     - showing the result of some query (including errors)
    All of these things are done in a structured fashion. See the methods
    iter_streams, query_user, progress, notice and result.

    UI objects are generally expected to be used once, with a fresh one
    created for each command executed.

    :ivar cmd: The command that is running using this UI object.
    :ivar here: The location that command is being run in. This may be a local
        path or a URL. This is only guaranteed to be set after set_command is
        called, as some UI's need to do option processing to determine its
        value.
    :ivar options: The parsed options for this ui, containing both global and
        command specific options.
    :ivar arguments: The parsed arguments for this ui. Set Command.args to
        define the accepted arguments for a command.
    """

    def _check_cmd(self):
        """Check that cmd is valid. This method is meant to be overridden.
        
        :return: True if the cmd is valid - if options and args match up with
            the ones supplied to the UI, and so on.
        """

    def iter_streams(self, stream_type):
        """Iterate over all the streams of type stream_type.

        Implementors of UI should implement _iter_streams which is called after
        argument checking is performed.

        :param stream_type: A simple string such as 'input' which matches
            one of the stream types defined for the cmd object this UI is
            being used with.
        :return: A generator of stream objects. stream objects have a read
            method and a close method which behave as for file objects.
        """
        for stream_spec in self.cmd.input_streams:
            if '*' in stream_spec or '?' in stream_spec or '+' in stream_spec:
                found = stream_type == stream_spec[:-1]
            else:
                found = stream_type == stream_spec
            if found:
                return self._iter_streams(stream_type)
        raise KeyError(stream_type)

    def _iter_streams(self, stream_type):
        """Helper for iter_streams which subclasses should implement."""
        raise NotImplementedError(self._iter_streams)

    def output_error(self, error_tuple):
        """Show an error to the user.

        This is typically used only by Command.execute when run raises an
        exception.

        :param error_tuple: An error tuple obtained from sys.exc_info().
        """
        raise NotImplementedError(self.output_error)

    def output_rest(self, rest_string):
        """Show rest_string - a ReST document.

        This is typically used as the entire output for command help or
        documentation.
        
        :param rest_string: A ReST source to display.
        """
        raise NotImplementedError(self.output_rest)

    def output_stream(self, stream):
        """Show a byte stream to the user.

        This is not currently typed, but in future a MIME type may be
        permitted.

        :param stream: A file like object that can be read from. The UI will
        not close the file.
        """
        raise NotImplementedError(self.output_stream)

    def output_table(self, table):
        """Show a table to the user.

        :param table: an iterable of rows. The first row is used for column
            headings, and every row needs the same number of cells.
            e.g. output_table([('name', 'age'), ('robert', 1234)])
        """
        raise NotImplementedError(self.output_table)

    def output_values(self, values):
        """Show values to the user.

        :param values: An iterable of (label, value).
        """
        raise NotImplementedError(self.output_values)

    def set_command(self, cmd):
        """Inform the UI what command it is running.

        This is used to gather command line arguments, or prepare dialogs and
        otherwise ensure that the information the command has declared it needs
        will be available. The default implementation simply sets self.cmd to
        cmd and hands off to self._check_cmd().
        
        :param cmd: A cr_cache.commands.Command.
        """
        self.cmd = cmd
        return self._check_cmd()

    def subprocess_Popen(self, *args, **kwargs):
        """Call an external process from the UI's context.
        
        The behaviour of this call should match the Popen process on any given
        platform, except that the UI can take care of any wrapping or
        manipulation needed to fit into its environment.
        """
        # This might not be the right place.
        raise NotImplementedError(self.subprocess_Popen)
