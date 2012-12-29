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

"""Tests for the crcache config system."""

import os.path

from cr_cache import config
from cr_cache.tests import TestCase

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
