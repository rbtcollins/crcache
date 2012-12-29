crcache users guide
+++++++++++++++++++

Overview
========

crcache acts as a layer to obtain, use, and discard compute resources - be it
virtual machines, chroots or even physical machines. This is a common
requirement for testing environments, and having an abstraction layer allows
a single project setup to scale in dramatically different ways just by the
user reconfiguring their crcache config.

Installation
============

Using pip is the easiest way to install crcache::

    $ pip install crcache

Configuration
=============

The default configuration is to have a project ``fallback`` that acts as a
fallback for unknown projects and a single source ``local`` that the fallback
project binds to.

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
    type=[local|pool]
    ; Do not discard instances if less than this many are running.
    ; Defaults to 0 - caching is usually done at the project level.
    reserve=int
    ; Do not scale out beyond this many instances.
    ; Defaults to 0 - no limit.
    maximum=int
    ; Override the concurrency of returned instances, rather than probing.
    ; Defaults to 0 - autoprobe.
    concurrency=int
    ; For pools only
    sources=sourcename,sourcename,...

If a directory called ``provision.d`` exists as a sibling to ``source.conf`` then
its contents will be run on instances as they are provisioned (using run-parts).

Likewise for ``discard.d`` immediately before discarding an instance.

Projects
--------

Each ``project`` is a subdirectory of a config root -
``$root/projects/$projectname``. Projects bind sources to project specific
configuration.

A project called ``fallback`` will replace the implicit definition of the
fallback project. Defining it with no source bindings will cause calls
for unknown projects to fail.

The file ``project.conf`` is a .ini file that controls basic metadata for
projects::

    [DEFAULT]
    ; Do not discard instances if less than this many are running.
    ; Defaults to 0 - no caching of instances.
    reserve=int
    ; Do not scale out beyond this many instances.
    ; Defaults to 0 - no limit.
    maximum=int
    ; Override the concurrency of returned instances, rather than probing.
    ; Defaults to 0 - autoprobe.
    concurrency=int
    ; A comma separated list of sources to draw from.
    ; defaults to an empty list - will make the project unusable.
    sources=sourcename,sourcename,...

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

    $ crcache -p pool acquire
    pool0

    $ crcache status pool
    source  cached  in-use max
    pool    0       1      1

run
---

Runs a command on a checked out resource::

    $ crcache run pool0 echo foo
    foo

copy
----

Copies files into (or out of) the resource::

    $ crcache cp pool0:foo bar

release
-------

Returns a compute resource from use::

    $ crcache release pool0
    $ crcache status pool
    source  cached  in-use max
    pool    1       0      1
