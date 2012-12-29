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

"""Tests for the crcache.source interface."""

import ConfigParser

from cr_cache.source import local, model
from cr_cache.tests import TestCase

source_implementations = []
source_implementations.append(('model', {'source_type': model.Source}))


class TestConfigConstruction(TestCase):

    scenarios = source_implementations

    def test_construct_with_path(self):
        config = ConfigParser.ConfigParser()
        self.source_type(config)
