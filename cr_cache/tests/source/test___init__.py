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
from StringIO import StringIO

from testtools.matchers import raises

from cr_cache.cache import Cache
from cr_cache.source import find_source_type, local, model
from cr_cache.store.local import Store
from cr_cache.tests import TestCase

# A list of implementations to test. 
# The source_factory should stub out anything needed to let provision and
# discard be called. They should either work during the test suite, or
# mock out the backend [but this is the sole point of testing for each
# source, so beware tests that don't check anything.
# If the test would fail due to conditions outside the control of the test
# suite (e.g. missing platform support, requiring internet access etc) then
# raise a skip.
source_implementations = []
source_implementations.append(('model',
    {'source_factory': model.Source,
    'reference_config': """"""}))


class TestConfigConstruction(TestCase):

    scenarios = source_implementations

    def test_construct_signature(self):
        # Check that this source type will be constructable by the load
        # factory.
        child_sources = []
        def get_source(name):
            child_sources.append(name)
            result = Cache(
                name, None, provision=lambda x:['a'], discard=lambda x:None)
            return result
        conf_file = StringIO(self.reference_config)
        config = ConfigParser.ConfigParser()
        config.readfp(conf_file)
        self.source_factory(config, get_source)

    def test_provision_discard(self):
        # Check that this source type will be constructable by the load
        # factory.
        child_sources = []
        def get_source(name):
            child_sources.append(name)
            result = Cache(
                name, Store({}), provision=lambda x:['a'],
                discard=lambda x:None)
            return result
        conf_file = StringIO(self.reference_config)
        config = ConfigParser.ConfigParser()
        config.readfp(conf_file)
        source = self.source_factory(config, get_source)
        source.discard(source.provision(2))


class TestHelpers(TestCase):

    def test_find_source_type(self):
        self.assertEqual(model.Source, find_source_type('model'))

    def test_find_source_type_missing(self):
        self.assertThat(lambda: find_source_type('foo'), raises(ImportError))
