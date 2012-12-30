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

"""The crcache local data store.

This store uses a simple python ndb for storing active/pooled instance
metadata.
"""

from extras import try_imports
dbm = try_imports(['anydbm', 'dbm'])
import os.path

from cr_cache.store import AbstractStore

class Store(AbstractStore):
    """General store for most crcache operations.

    Stores data in ~/.cache/crcache/state.dbm.

    Each operation opens-and-closes the file to avoid caches some dbm
    implementations have internally.
    """

    def __init__(self):
        self.dbm_path = os.path.expanduser('~/.cache/crcache/state.dbm')
        # Check it is usable, create empty db if needed.
        dir = os.path.dirname(self.dbm_path)
        if not os.path.exists(dir):
            os.makedirs(dir)
        db = dbm.open(self.dbm_path, 'c')
        db.close()

    def __getitem__(self, item):
        db = dbm.open(self.dbm_path, 'r')
        try:
            return db[item]
        finally:
            db.close()

    def __setitem__(self, item, value):
        db = dbm.open(self.dbm_path, 'w')
        try:
            db[item] = value
        finally:
            db.close()

    def __delitem__(self, item):
        db = dbm.open(self.dbm_path, 'w')
        try:
            del db[item]
        finally:
            db.close()

