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

"""Locally defined and obtained computing resource."""

import os
import signal
import subprocess

from cr_cache import source

class Source(source.AbstractSource):
    """Provides a map onto the local machine.
    
    No special configuration.

    Can only provide one resource.
    """

    def _init(self):
        self.maximum = 1

    def discard(self, resources):
        pass

    def provision(self, count):
        if count > 1:
            raise source.TooManyInstances()
        return ['local'] * count

    def _clear_SIGPIPE(self):
        """Clear SIGPIPE : child processes expect the default handler."""
        signal.signal(signal.SIGPIPE, signal.SIG_DFL)

    def subprocess_Popen(self, resource, command, *args, **kwargs):
        if resource != 'local':
            raise source.UnknownInstance("No such resource %r." % resource)
        if os.name == "posix":
            # GZ 2010-12-04: Should perhaps check for existing preexec_fn and
            #                combine so both will get called.
            kwargs['preexec_fn'] = self._clear_SIGPIPE
        if not command:
            # Run a shell for the user.
            command = [os.environ['SHELL']]
        return subprocess.Popen(command, *args, **kwargs)
