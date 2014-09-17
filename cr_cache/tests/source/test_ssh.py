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

"""Tests for the crcache.source.ssh module."""

from testtools.matchers import Equals, MatchesAny, raises

from cr_cache import cache
from cr_cache.source import ssh
from cr_cache.store import memory
from cr_cache.tests import TestCase

class TestSSHSource(TestCase):

    def test_basics(self):
        config = {}
        store = memory.Store({})
        sources = {}
        # Needs a ssh_host configured.
        self.assertThat(
            lambda: ssh.Source(config, sources.__getitem__),
            raises(KeyError))
        config['ssh_host'] = 'localhost'
        source = ssh.Source(config, sources.__getitem__)
        resources = source.provision(1)
        source.discard(resources)
        self.assertEqual(['localhost'], resources)
        self.assertEqual(1, source.maximum)
