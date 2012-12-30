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
    
    Cache state is stored in a persistent store. The key pool/name is used
    to track owned instances, allocated/name to track instances handed out
    to users, and resource/instance, to map instances back to the cache.

    :attr name: The name of the cache.
    :attr store: The crcache.store.AbstractStore being used to persist cache
        state.
    :attr reserve: The low water policy point for the cache.
    """

    def __init__(self, name, provision, discard, store, reserve=0):
        """Create a Cache.

        :param name: The name of the cache, used in storing the cache state.
        :param provision: A callback to obtain one or more instances.
        :param discard: A callback to discard one or more instances.
        :param store: A cr_cache.store for persisting the cache metadata.
        :param reserve: If non-zero, only discard instances returned to the
            cache via discard, if the total provisioned-but-not-discarded would
            be above the reserve.
        """
        self.name = name
        self._discard = discard
        self._provision = provision
        self.store = store
        self.reserve = reserve

    def discard(self, instances):
        """Discard instances.

        As long as the cache is above the reserved count, discards will be
        passed to the discard routine immediately. Otherwise they will be
        held indefinitely.
        """
        instances = list(instances)
        # Lock first, to avoid races.
        to_discard = []
        with write_locked(self.store):
            allocated = len(self._get_set('allocated/' + self.name))
            keep_count = self.reserve - allocated + len(instances)
            for pos, instance in enumerate(instances):
                if pos >= keep_count:
                    to_discard.append(instance)
            self._set_remove('allocated/' + self.name, instances)
        # XXX: Future - avoid long locks by having a gc queue and moving
        # instances in there, and then doing the api call and finally cleanup.
            for instance in to_discard:
                del self.store['resource/' + instance]
            self._set_remove('pool/' + self.name, to_discard)
        self._discard(to_discard)

    def provision(self, count):
        """Request count instances from the cache.

        :return: A list of instance ids.
        """
        with write_locked(self.store):
            # XXX: Future, have a provisionally allocated set and move cached
            # entries there, then do the blocking API calls, then return
            # everything.
            existing = set(self._get_set('pool/' + self.name))
            allocated = set(self._get_set('allocated/' + self.name))
            cached = list(existing - allocated)[:count]
            count = count - len(cached)
            new_instances = self._provision(count)
            for instance in new_instances:
                self.store['resource/' + instance] = self.name
            self._update_set('pool/' + self.name, new_instances)
            instances = new_instances + cached
            self._update_set('allocated/' + self.name, instances)
            return set(instances)

    def _update_set(self, setname, items):
        """Add items to the list stored in setname.

        :param setname: A name like pool/foo.
        :param items: A list of strings.
        """
        try:
            existing_instances = self.store[setname]
            self.store[setname] = ','.join(sorted(items + [existing_instances]))
        except KeyError:
            self.store[setname] = ','.join(sorted(items))

    def _get_set(self, setname):
        """Get a serialised set from the store.

        :param setname: A name like allocated/foo.
        :return; A list of strings.
        """
        try:
            existing_instances = self.store[setname]
        except KeyError:
            existing_instances = ''
        return existing_instances.split(',')

    def _set_remove(self, setname, items):
        """Remove items from a stored list.

        :param setname: A name like pool/foo.
        :param items: An iterable of strings.
        """
        existing_instances = set(self._get_set(setname))
        existing_instances.difference_update(items)
        self.store[setname] = ','.join(sorted(existing_instances))
