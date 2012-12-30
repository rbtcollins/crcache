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
