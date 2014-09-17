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

"""Configuration of cr_cache."""

import os.path

import yaml

from cr_cache import cache
from cr_cache.source import find_source_type
from cr_cache.store import local as local_store


def default_path():
    """Return a list of directories to search for configuration data.
    
    Defaults to ~/.config/crcache, $(pwd)/.crcache
    """
    homedir_config = os.path.expanduser(os.path.join('~', '.config', 'crcache'))
    cwd_config = os.path.join(os.getcwd(), '.crcache')
    return [homedir_config, cwd_config]


def sources(roots):
    """Return a list of the known sources."""
    return set(source_dirs(roots).keys())


def source_dirs(roots):
    """Return a map of source name -> config dir."""
    result = {}
    for root in roots:
        try:
            names = os.listdir(os.path.join(root, 'sources'))
        except OSError:
            continue
        for name in names:
            if name in result:
                continue
            result[name] = os.path.join(root, 'sources', name)
    return result


class Config(object):
    """Represents a full configuration of crcache.

    This provides a cache of sources, allowing a recursive definition for
    source loading.
    """

    def __init__(self):
        self._source_dirs = source_dirs(default_path())
        self._sources = {}
        self._store = local_store.Store()

    def get_source(self, name):
        """Get a cr_cache.cache.Cache configured for the source called name.
        
        Results are cached in self._sources, and returned from there if present.
        """
        if name in self._sources:
            return self._sources[name]
        path = self._source_dirs.get(name)
        if name == 'local' and path is None:
            config = {}
            source_type = find_source_type('local')
        else:
            path = os.path.join(path, 'source.conf')
            with open(path, 'rt') as f:
                config = yaml.safe_load(f)
            source_type = find_source_type(config['type'])
        source = source_type(config, self.get_source)
        kwargs = {}
        if 'reserve' in config:
            reserve = int(config['reserve'])
            kwargs['reserve'] = reserve
        result = cache.Cache(name, self._store, source, **kwargs)
        self._sources[name] = result
        return result
