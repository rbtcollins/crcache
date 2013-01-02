crcache users guide
+++++++++++++++++++

Overview
========

crcache acts as a layer to obtain, use, and discard compute resources - be it
virtual machines, chroots or even physical machines. This is a common
requirement for testing environments, and having an abstraction layer allows
a single project setup to scale in dramatically different ways just by the
user reconfiguring their crcache config.

Requirements
============

* Python 2.6+ or 3.2+

* The 'extras' Python package.

* For testing a number of other packages (see setup.py).

Installation
============

Using pip is the easiest way to install crcache::

    $ pip install crcache

Configuration
=============

The default configuration is to have a single source ``local`` which runs
commands locally.

Search path
-----------

Configuration is looked up in ~/.config/crcache and $(pwd)/.crcache. Where
something is defined in both places, the first found definition wins, allowing
local configuration to supercede any configuration supplied in a project (which
might be version controlled and thus harder to change without side effects).

Sources
-------

Each ``source`` is a subdirectory of a config root -
``$root/sources/$sourcename``. Sources define how to provision one or more
compute resources.

A source called ``local`` will replace the implicit definition of the local
source.

The file ``source.conf`` is a .ini file that controls basic metadata for the
source::

    [DEFAULT]
    ; What sort of source is this?
    type=[local|pool|ssh]
    ; Do not discard instances if less than this many are running.
    ; Defaults to 0 - avoids caching expensive resources w/out warning.
    reserve=int
    ; Do not scale out beyond this many instances.
    ; Defaults to 0 - no limit.
    maximum=int
    ; Override the concurrency of returned instances, rather than probing.
    ; Defaults to 0 - autoprobe.
    concurrency=int
    ; For pools only
    sources=sourcename,sourcename,...
    ; For ssh only
    ssh_host=string

If a directory called ``provision.d`` exists as a sibling to ``source.conf`` then
its contents will be run as they are provisioned (using run-parts). The resource
name is supplied to the scripts as the first parameter - the script can call
``crcache run`` to execute commands on the resource.

Likewise for ``discard.d`` immediately before discarding an instance.

Command line
============

status
------

Provides details of sources and resources::

    $ crcache status
    source  cached  in-use max
    local   0       1      1
    pool    1       0      1

    $ crcache status -t
    source  cached  in-use max
    pool    1       0      1
    + local 
    local   0       1      1

    $ crcache status -v
    source: local
    cached: 
    in-use: local
    minimum: 1
    maximum: 1

    source: pool
    cached: local
    in-use:
    minimum: 1
    maximim: 1

    $ crcache status -a

acquire
-------

Checks a compute resource out for use::

    $ crcache -s pool acquire
    pool-0

    $ crcache status pool
    source  cached  in-use max
    pool    0       1      1

run
---

Runs a command on a checked out resource::

    $ crcache run -s pool-0 echo foo
    foo

copy
----

Copies files into (or out of) the resource::

    $ crcache cp pool-0:foo bar

release
-------

Returns a compute resource from use::

    $ crcache release pool0
    $ crcache status pool
    source  cached  in-use max
    pool    1       0      1

Internals
=========

Each source stores the instances it has obtained and has cached in the crcache
store, stored in $HOME/.cache/crcache/state.dbm.

API
===

The internal API is largely uninteresting for users - and see the DESIGN and
DEVELOPER documentation if you are interested. That said, one possibly common
need is creating additional source types, and so we cover that here.

Source types are looked up by looking for a python module with the same name
in the ``cr_cache.source.`` package namespace. They can be installed as a
third-party using namespace packages, or patched into the main crcache
source tree. Source modules should include a ``Source`` class, which the
source type loader looks for - you can subclass ``source.AbstractSource``
or just implement its contract. The loader will instantiate a ``Source``
instance with a ``ConfigParser`` and a ``get_source`` callback (which permits
sources to layer on other sources).

Sources are responsible for four things:

* Making instances that can run commands.

* Assigning unique (to the crcache instance) ids for the instances.

* Discarding such instances.

* Running commands on the instances.

Other operations, such as enforcing a limit on the number of instances, caching
of instances, are taken care of by crcache infrastructure.
