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
dbm = try_imports(['dbm', 'dbm.ndbm'])
import os.path

from cr_cache.store import AbstractStore

class Store(AbstractStore):
    """General store for most crcache operations.

    Stores data in ~/.cache/crcache/state.db.
    Updates may be batched depending on the dbm implementation, with a lock
    kept in state.lck.
    """

    def __init__(self):
        self.dbm_path = os.path.expanduser('~/.cache/crcache/state')
        self.dbm_lock = os.path.expanduser('~/.cache/crcache/state.lck')
        self._locked = 0
        # Check it is usable, create empty db if needed.
        dir = os.path.dirname(self.dbm_path)
        if not os.path.exists(dir):
            os.makedirs(dir)
        self._lock()
        db = dbm.open(self.dbm_path, 'c')
        db.close()
        self._unlock()

    def __getitem__(self, item):
        return self._db[item].decode('utf8')

    def __setitem__(self, item, value):
        self._db[item] = value.encode('utf8')

    def __delitem__(self, item):
        del self._db[item]

    def lock_read(self):
        if self._lock():
            self._db = dbm.open(self.dbm_path, 'r')

    def lock_write(self):
        if self._lock():
            self._db = dbm.open(self.dbm_path, 'w')

    def _lock(self):
        if self._locked:
            self._locked += 1
            return False
        fd = os.open(self.dbm_lock, os.O_CREAT | os.O_EXCL)
        os.close(fd)
        self._locked = 1
        return True

    def _unlock(self):
        if not self._locked:
            raise AssertionError('not locked')
        self._locked -= 1
        if self._locked:
            return
        os.unlink(self.dbm_lock)

    def unlock(self):
        if self._locked == 1:
            self._db.close()
        self._unlock()
