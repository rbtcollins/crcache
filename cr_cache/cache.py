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

from cr_cache.store import write_locked, read_locked

class Cache(object):
    """Keep track of compute resources.
    
    Cache state is stored in a persistent store. The key pool/name is used
    to track owned instances, allocated/name to track instances handed out
    to users, and resource/instance, to map instances back to the cache.

    The cache is a hierarchical composite structure - each cache can have
    child caches that it draws resources from.

    :attr name: The name of the cache.
    :attr store: The crcache.store.AbstractStore being used to persist cache
        state.
    :attr reserve: The low water policy point for the cache.
    :attr maximum: The high water policy point for the cache.
        This is never higher than the sum of the high water policies of any
        child caches (found via source.maximum).
    """

    def __init__(self, name, store, source, reserve=0, maximum=0):
        """Create a Cache.

        :param name: The name of the cache, used in storing the cache state.
        :param store: A cr_cache.store for persisting the cache metadata.
        :param source: A cr_cache.source.AbstractSource used to fulfill
            requests for resources when the cache is empty, to discard
            resources that are no longer needed, and to provide introspection
            of the tree structure of layered sources.
        :param reserve: If non-zero, only discard instances returned to the
            cache via discard, if the total provisioned-but-not-discarded would
            be above the reserve.
        :param maximum: If non-zero, reject requests for resources if the total
            provisioned-but-not-discarded would exceed maximum. This is capped
            by the maximum of the provided source.
        """
        self.name = name
        self.store = store
        self.source = source
        self.reserve = reserve
        if self.source.maximum > 0:
            if maximum > 0:
                maximum = min(self.source.maximum, maximum)
            else:
                maximum = self.source.maximum
        self.maximum = maximum

    def available(self):
        """Report on the number of resources that could be returned.

        :return: A count of the number of available resources. 0 means
            unlimited.
        """
        if not self.maximum:
            return 0
        with read_locked(self.store):
            return self.maximum - len(
                set(self._get_set('allocated/' + self.name)))

    def cached(self):
        """How many instances are sitting in the reserve ready for use."""
        with read_locked(self.store):
            return len(
                set(self._get_set('pool/' + self.name))) - len(
                set(self._get_set('allocated/' + self.name)))

    def discard(self, instances, force=False):
        """Discard instances.

        :param instances: A list of string ids previously returned from a
            provision() call.
        :param Force: When False (the default), as long as the cache is above
            the reserved count, discards will be passed to the discard routine
            immediately. Otherwise they will be held indefinitely. When True,
            instances are never held in reserve.
        """
        instances = list(instances)
        prefix = self.name + '-'
        for instance in instances:
            assert instance.startswith(prefix), \
                "instance %r not owned by cache %r" % (instance, self.name)
        instances = [instance[len(prefix):] for instance in instances]
        # Lock first, to avoid races.
        to_discard = []
        with write_locked(self.store):
            allocated = len(self._get_set('allocated/' + self.name))
            keep_count = self.reserve - allocated + len(instances)
            for pos, instance in enumerate(instances):
                if force or pos >= keep_count:
                    to_discard.append(instance)
            self._set_remove('allocated/' + self.name, instances)
        # XXX: Future - avoid long locks by having a gc queue and moving
        # instances in there, and then doing the api call and finally cleanup.
            for instance in to_discard:
                del self.store['resource/' + instance]
            self._set_remove('pool/' + self.name, to_discard)
        if not to_discard:
            return
        self.source.discard(to_discard)

    def fill_reserve(self):
        """If the cache is below the low watermark, fill it up."""
        with write_locked(self.store):
            existing = set(self._get_set('pool/' + self.name))
            missing = self.reserve - len(existing)
            if missing:
                self._get_resources(missing)

    def in_use(self):
        """How many instances are checked out of this cache?"""
        with read_locked(self.store):
            return len(set(self._get_set('allocated/' + self.name)))

    def provision(self, count):
        """Request count instances from the cache.

        Instance ids that are returned are prefixed with the cache name, to
        ensure no collisions between layered sources.

        :return: A list of instance ids.
        """
        with write_locked(self.store):
            # XXX: Future, have a provisionally allocated set and move cached
            # entries there, then do the blocking API calls, then return
            # everything.
            existing = set(self._get_set('pool/' + self.name))
            if self.maximum and (len(existing) + count) > self.maximum:
                raise ValueError('Instance limit exceeded.')
            allocated = set(self._get_set('allocated/' + self.name))
            cached = list(existing - allocated)[:count]
            count = count - len(cached)
            new_instances = self._get_resources(count)
            instances = new_instances + cached
            self._update_set('allocated/' + self.name, instances)
            return set([self.name + '-' + instance for instance in instances])

    def provision_from_cache(self, count):
        """Request up to count instances but only cached ones.
        
        This difference from provision() in that it will return up to the
        requested amount rather than all-or-nothing, and it never triggers
        a backend-provisioning call.
        """
        with write_locked(self.store):
            existing = set(self._get_set('pool/' + self.name))
            allocated = set(self._get_set('allocated/' + self.name))
            cached = list(existing - allocated)[:count]
            self._update_set('allocated/' + self.name, cached)
            return set([self.name + '-' + instance for instance in cached])

    def _get_resources(self, count):
        """Get some resources.

        Assumes the store is already locked.
        """
        # note that this may leak (allocated in a child, not owned by this) if
        # a source fails.
        new_instances = self.source.provision(count)
        for instance in new_instances:
            self.store['resource/' + instance] = self.name
        self._update_set('pool/' + self.name, new_instances)
        return new_instances

    def _update_set(self, setname, items):
        """Add items to the list stored in setname.

        :param setname: A name like pool/foo.
        :param items: A list of strings.
        """
        try:
            existing_instances = [self.store[setname]]
            if existing_instances == ['']:
                existing_instances = []
            self.store[setname] = ','.join(
                sorted(list(items) + existing_instances))
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
        if existing_instances:
            return existing_instances.split(',')
        else:
            return []

    def _set_remove(self, setname, items):
        """Remove items from a stored list.

        :param setname: A name like pool/foo.
        :param items: An iterable of strings.
        """
        existing_instances = set(self._get_set(setname))
        existing_instances.difference_update(items)
        self.store[setname] = ','.join(sorted(existing_instances))
