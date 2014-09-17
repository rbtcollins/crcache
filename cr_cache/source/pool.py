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

"""Pool multiple other sources into one source."""

from cr_cache import source

class Source(source.AbstractSource):
    """A pool of other sources.
    
    Configured via
    sources: [name,name,..]
    in the config.

    Each source will be obtained from the get_source callback (which should
    return a Cache object, not a raw source), as cached resourcs are preferred
    when provisioning.
    """

    def _init(self):
        source_names = self.config.get('sources')
        self.children = list(map(self.get_source, source_names))
        child_maximums = list(map(lambda x:x.maximum, self.children))
        if 0 not in child_maximums:
            self.maximum = sum(child_maximums)

    def provision(self, count):
        cached_instances = []
        # Gather cached resources first.
        for child in self.children:
            cached_instances.extend(
                child.provision_from_cache(count-len(cached_instances)))
        count -= len(cached_instances)
        new_instances = []
        for child in self.children:
            if not count:
                break
            if child.maximum:
                request_count = min(child.available(), count)
            else:
                request_count = count
            child_instances = child.provision(request_count)
            new_instances.extend(child_instances)
            count -= len(child_instances)
        return cached_instances + new_instances

    def discard(self, instances):
        discard_map = {}
        for instance in instances:
            name, _ = instance.split('-', 1)
            discard_map.setdefault(name, []).append(instance)
        for child in self.children:
            if child.name in discard_map:
                child.discard(discard_map[child.name])
        # Note that discards for no longer configured children are
        # currently silently discarded.

    def subprocess_Popen(self, resource, *args, **kwargs):
        try:
            name, child_resource = resource.split('-', 1)
        except ValueError:
            raise source.UnknownInstance("No such resource %r." % resource)
        for child in self.children:
            if child.name == name:
                return child.source.subprocess_Popen(
                    child_resource, *args, **kwargs)
        raise source.UnknownInstance("No such resource %r." % resource)
