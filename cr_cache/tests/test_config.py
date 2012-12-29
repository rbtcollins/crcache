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
