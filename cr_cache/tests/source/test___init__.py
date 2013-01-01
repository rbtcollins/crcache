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
from cr_cache.source import find_source_type, local, model, pool
from cr_cache.store.memory import Store
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
source_implementations.append(('pool',
    {'source_factory': pool.Source,
    'reference_config': """[DEFAULT]
sources=a,b,c
"""}))


class TestConfigConstruction(TestCase):

    scenarios = source_implementations

    def make_source(self):
        # Make a source from the parameters of the scenario.
        child_sources = []
        store = Store({})
        backend = model.Source(None, None)
        def get_source(name):
            child_sources.append(name)
            result = Cache(
                name, store, backend.provision, discard=backend.discard)
            return result
        conf_file = StringIO(self.reference_config)
        config = ConfigParser.ConfigParser()
        config.readfp(conf_file)
        return self.source_factory(config, get_source)

    def test_construct_signature(self):
        # Check that this source type will be constructable by the load
        # factory.
        self.make_source()

    def test_provision_discard(self):
        source = self.make_source()
        source.discard(source.provision(2))

    def test_has_children_attribute(self):
        # To simplify the clients of Cache, all sources offer a children
        # attribute.
        source = self.make_source()
        source.children


class TestHelpers(TestCase):

    def test_find_source_type(self):
        self.assertEqual(model.Source, find_source_type('model'))

    def test_find_source_type_missing(self):
        self.assertThat(lambda: find_source_type('foo'), raises(ImportError))
