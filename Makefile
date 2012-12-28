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

all: README.rst check

.testrepository:
	testr init

check: .testrepository
	testr run --parallel

check-xml:
	testr run --parallel --subunit | subunit2junitxml -o test.xml -f | subunit2pyunit

release:
	./setup.py sdist upload --sign

README.rst: cr_cache/commands/quickstart.py
	./crcache quickstart > $@

.PHONY: check check-xml release all
