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

"""The crcache data store abstraction.

Interesting things here:
local: The default local persistent DB.
memory: An in-memory store for testing.
"""

class AbstractStore(object):
    """class defining the contract for Store types.
    
    Stores are expected to immediately expose changes to other instances opened
    in other processes.
    """

    def __getitem__(self, item):
        """Return item from the store.

        :param item: A string key to retrieve.
        :return: A string value.
        :raises KeyError: If the item is missing.
        """
        raise NotImplementedError(self.__getitem__)

    def __setitem__(self, item, value):
        """Set item into the store.

        :param item: A string key to set.
        :param value: A string value.
        """
        raise NotImplementedError(self.__setitem__)

    def __delitem__(self, item):
        """Delete item from the store.

        :param item: A string key to delete.
        :raises KeyError: If the item is missing.
        """
        raise NotImplementedError(self.__getitem__)
