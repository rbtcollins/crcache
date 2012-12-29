Developing crcache
++++++++++++++++++

Releases
========

To do a release:

1. Update crcache/__init__.py to the new version.

2. Commit, make a signed tag.

3. Run `./setup.py sdist upload -s`.

4. Push the tag and trunk.

Hacking
=======

(See also doc/DESIGN.rst).

The primary repository is https://github.com/rbtcollins/crcache. Please branch
from there and use pull requests to submit changes. Bug tracking is the github
bug tracker.

Coding style
============

Pep8. Be liberal with pylint. Pragmatism over purity.

Test everything that can be sensibly tested.

Tests
=====

Can be run either with `./setup.py test` (which should install the needed
dependencies) or `testr run` (if you have installed testrepository). If for
some reason `setup.py test` does not install dependencies, they can be found
by looking in ``setup.py``.

Copyright
=========

Contributions need to be dual licensed (see COPYING), but no copyright
assignment or grants are needed.

