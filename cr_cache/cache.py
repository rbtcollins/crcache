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

"""Resource Cache for caching resources."""

from cr_cache.store import write_locked

class Cache(object):
    """Keep track of compute resources.
    
    :attr name: The name of the cache.
    :attr store: The crcache.store.AbstractStore being used to persist cache
        state.
    """

    def __init__(self, name, provision, discard, store):
        """Create a Cache.

        :param name: The name of the cache, used in storing the cache state.
        :param provision: A callback to obtain one or more instances.
        :param discard: A callback to discard one or more instances.
        :store: A cr_cache.store for persisting the cache metadata.
        """
        self.name = name
        self._provision = provision
        self.store = store

    def provision(self, count):
        """Request count instances from the cache.

        :return: A list of instance ids.
        """
        instances = self._provision(count)
        with write_locked(self.store):
            for instance in instances:
                self.store['resource/' + instance] = self.name
            try:
                existing_instances = self.store['pool/' + self.name]
                self.store['pool/' + self.name] = ','.join(
                    instances + [existing_instances])
            except KeyError:
                self.store['pool/' + self.name] = ','.join(instances)
            return instances
