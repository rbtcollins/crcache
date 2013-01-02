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

"""Tests and test support for the crcache config system."""

import os.path

from fixtures import Fixture
from testtools.matchers import Is, IsInstance

from cr_cache import config
from cr_cache.source import model
from cr_cache.tests import TestCase


class SourceConfigFixture(Fixture):
    """Sets up a source configuration."""

    def __init__(self, name, type, reserve=None, sources=None):
        """Create a SourceConfigFixture.

        :param name: The name for the source to configure.
        :param type: The type to give the source.
        :param reserve: Configure a reserve.
        :param sources: Configure sources.
        """
        super(SourceConfigFixture, self).__init__()
        self._type = type
        self._name = name
        self._reserve = reserve
        self._sources = sources

    def setUp(self):
        super(SourceConfigFixture, self).setUp()
        homedir_config = os.path.join(os.environ['HOME'], '.config', 'crcache')
        source_dir = os.path.join(homedir_config, 'sources', self._name)
        os.makedirs(source_dir)
        with open(os.path.join(source_dir, 'source.conf'), 'wt') as f:
            f.write("[DEFAULT]\ntype=model\n")
            if self._reserve is not None:
                f.write('reserve=%s\n' % self._reserve)
            if self._sources is not None:
                f.write('sources=%s\n' % self._sources)


class TestConfig(TestCase):

    def test_search_path(self):
        homedir_config = os.path.join(self.homedir, '.config', 'crcache')
        cwd_config = os.path.join(os.getcwd(), '.crcache')
        expected_path = [homedir_config, cwd_config]
        self.assertEqual(expected_path, config.default_path())

    def test_finds_source_in_home(self):
        root = config.default_path()[0]
        os.makedirs(os.path.join(root, 'sources', 'foo'))
        self.assertEqual(set(['foo']), config.sources([root]))

    def test_source_dirs_missing_paths(self):
        config.source_dirs(config.default_path())

    def test_source_dirs(self):
        root1 = os.path.join(self.homedir, 'conf1')
        root2 = os.path.join(self.homedir, 'conf2')
        os.makedirs(os.path.join(root1, 'sources', 'foo'))
        os.makedirs(os.path.join(root2, 'sources', 'foo'))
        os.makedirs(os.path.join(root2, 'sources', 'bar'))
        # config.source_dirs finds the first dir for foo, and the bar in the
        # second dir.
        self.assertEqual({'foo': os.path.join(root1, 'sources', 'foo'), 
            'bar': os.path.join(root2, 'sources', 'bar')},
            config.source_dirs([root1, root2]))

    def test_get_source_local_implicit(self):
        # There is always a local source, even if its not configured
        # explicitly.
        c = config.Config()
        s = c.get_source('local')
        self.assertThat(c.get_source('local'), Is(s))

    def test_get_source_local_explicit(self):
        # Its possible to replace the definition of local.
        self.useFixture(SourceConfigFixture('local', 'model'))
        c = config.Config()
        s = c.get_source('local')
        self.assertThat(s.source, IsInstance(model.Source))

    def test_get_source_defaults(self):
        c = config.Config()
        s = c.get_source('local')
        self.assertEqual(0, s.reserve)

    def test_get_source_reserve_in_ini_passed_to_cache(self):
        self.useFixture(SourceConfigFixture('model', 'model', reserve=1))
        c = config.Config()
        s = c.get_source('model')
        self.assertEqual(1, s.reserve)
