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

import extras

ConfigParser = extras.try_imports(['ConfigParser', 'configparser'])
from StringIO import StringIO
import subprocess

from testtools.matchers import Equals, MatchesAny, raises

from cr_cache.cache import Cache
from cr_cache.source import (
    find_source_type,
    local,
    model,
    pool,
    ssh,
    TooManyInstances,
    UnknownInstance,
    )
from cr_cache.store.memory import Store
from cr_cache.tests import TestCase


def find_src_address():
    """Find an address we can ssh to.

    127.0.0.1 isn't safe as bind mounted home dirs in lxc containers will
    suffer host key collisions. Instead we use (an arbitrary) outbound src
    address, which will be more unique. If there is no such address, we use
    localhost, to handle working on the host itself with no networking.
    """
    routes = subprocess.check_output(['ip', 'route'])
    routes = routes.decode('utf8')
    address = None
    for line in routes.splitlines():
        if ' src ' in line:
            return line.split(' ')[-2]
    return 'localhost'


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
    'reference_config': """""",
    'test_maximum': 0}))
source_implementations.append(('pool',
    {'source_factory': pool.Source,
    'reference_config': """[DEFAULT]
sources=a,b,c
""",
    'test_maximum': 0}))
source_implementations.append(('local',
    {'source_factory': local.Source,
    'reference_config': """[DEFAULT]
""",
    'test_maximum': 1}))
source_implementations.append(('ssh',
    {'source_factory': ssh.Source,
    'reference_config': """[DEFAULT]
ssh_host=%s
""" % find_src_address(),
    'test_maximum': 1}))


class TestSourceInterface(TestCase):

    scenarios = source_implementations

    def make_source(self):
        # Make a source from the parameters of the scenario.
        child_sources = []
        store = Store({})
        backend = model.Source(None, None)
        def get_source(name):
            child_sources.append(name)
            result = Cache(name, store, backend)
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
        count = 2
        if self.test_maximum and self.test_maximum < count:
            count = self.test_maximum
        source.discard(source.provision(count))

    def test_has_children_attribute(self):
        # To simplify the clients of Cache, all sources offer a children
        # attribute.
        source = self.make_source()
        source.children

    def test_has_maximum_attribute(self):
        # Sources may have a limit to the number of resources they can have
        # provisioned at any one time.
        source = self.make_source()
        "%d" % source.maximum

    def test_maximum_exceeded(self):
        if not self.test_maximum:
            self.skip("Cannot test maximum.")
        source = self.make_source()
        self.assertThat(lambda: source.provision(self.test_maximum + 1),
            raises(TooManyInstances))
        source.discard(source.provision(self.test_maximum))
        # It might be tempting to allocate maximum here then try for one
        # more and expect that to fail, but that assigns too much
        # responsibility for tracking to sources: sources know how to
        # make, run and delete, not track usage - caches do that.

    def test_run(self):
        source = self.make_source()
        resource = source.provision(1)[0]
        self.addCleanup(source.discard, [resource])
        # NB: we can't assume sys.executable is present, as sources may be
        # returning machines with different python versions etc.
        proc = source.subprocess_Popen(resource, 
            ['echo', 'foo'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        out, err = proc.communicate()
        self.assertThat(out, MatchesAny(Equals(b'foo\n'), Equals(b'foo\r\n')))
        self.assertEqual(0, proc.returncode)

    def test_run_bad_resource(self):
        source = self.make_source()
        self.assertThat(lambda:source.subprocess_Popen('invalid', ['echo']),
            raises(UnknownInstance))


class TestHelpers(TestCase):

    def test_find_source_type(self):
        self.assertEqual(model.Source, find_source_type('model'))

    def test_find_source_type_missing(self):
        self.assertThat(lambda: find_source_type('foo'), raises(ImportError))
