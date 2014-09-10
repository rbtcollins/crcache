Design / Architecture of crcache
++++++++++++++++++++++++++++++++

NB: This document describes intent as much as actuality. The code has
precedence where things differ (though for to-implement features, the code may
simply be not-yet-written).

Primary Goals
=============

* Provide an abstraction layer so that test runners like testrepository or in
  general any process that needs to run in isolated or repeatable environments
  can do so without needing to re-invent the wheel.

* Make it possible for projects to have project specific config in-tree and
  machine/environment specific config maintained on the machine/environment.

* Layer heavily on things like OpenStack, LXC, Docker and so forth: this is
  an abstraction layer primarily, not an implementation layer.

Musts
=====

* Be command line drivable (make it easy to use from many languages including
  the console).

* Be able to run things locally without any configuration.

* Let users do arbitrary operations to customise compute environment
  provisioning / resetting / reuse.

* Not require long lived daemon processes - when not being actively used,
  crcache should be gone. [Optional features may require daemons].

* Be able to organise computing resources - not all things are equal. (No
  explict modelling needed - just provide a language for users to differentiate
  different resources).

* Be able to copy files in and out of the computing environment. While providing
  the basic run-a-command facility is enough to let sftp or rsync work, it is
  hard to implement safe temp file handling without a higher level interface.

Secondary Goals
===============

Clean UI, predictable behaviour, small-tools feel.

Problem domain
==============

Consider a generic parallelising test runner and a test suite that uses
machine-scoped resources such as well known ports, database or message queue
servers and fixed paths on disk.

Any attempt to parallelise that test suite will run into significant immediate
problems - the code base will have to be made generic, so that test servers run
on ephemeral ports, so that the test database uses random names (and possibly
still require a mutex on schema operations in different databases... depending
on the database engine) - all predictable resources need to be made unique.
Failing to do that will cause sporadic failures in the test suite when the
parallel execution happens to place contending tests opposite each other. The
greater the parallelism, the worse the issue.

To run the test suite in parallel, it needs to be isolated. The most robust
form of isolation is N separate machines with shared nothing, but thats a lot
of overhead to manage. Virtual machines, containers or chroots offer varying
degrees of less isolation but with correspondingly lower overhead for
management. We can model any of these test environments - local processes,
chroots, containers, VM's or even separate physical machines with one model.

For efficiency, it would be desirable to minimise repeated work involved with
setting up and tearing down virtualised environments. It is from this aspect
that the ``cache`` in the name ``crcache`` is drawn. The model needs to be
compatible with sophisticated approaches such as lvm snapshots, golden cloud
images and hot prepped instances.

Concepts
========

To deal with compute clouds (such as Openstack or EC2) we need to allow for
configuration for a whole class of resources at once. This implies a minimum
of three concepts:

1. Individual resources, which represent a computing context we can run commands
   in. Resources need a unique name for users to address them, and we need to
   have a type such that we can dispatch the right code (e.g. ssh, subprocess,
   whatever) when requested to action things.

2. A source of compute resources, which act as a factory for individual
   resources. A given source is the combination of of a source type with
   the user supplied parameters for that type to make a concrete source.

3. A parameterisable source type, which is selected by the user to configure
   things.

Any given project will have its own configuration to perform on a machine
(e.g. installing dependencies, checking out source code). This could imply a
third concept - ``Project``, but can also be represented as just a layered
source of resources, where the layer consumes from the layer below and performs
whatever configuration is needed.

After configuring a resource for a project, the resource is ready to be used.
To mask latency or avoid repeated work, preparing multiple resources in advance
may be useful, which also argues for a new concept - ``resource pools``.

However, there isn't (yet) any clear important differentiator between a source
of compute resources and a pool that draws from other sources - we can treat
a pool as just another source. So, like project, pooled resources will exist
but only as a specialised resource source.

It can be argued that sources like EC2 which require credentials and so on
should be given two levels of configuration - global and per-project-binding.
In the interest of minimising concepts, that is not done today.

Some resources can share local file trees very efficiently, e.g. via COW file
systems, bind mounting, bind mounting with layered file sytems, or even cluster
file systems. This offers huge performance benefits when used, so this becomes
a necessary concept:

3. Filesystem exporting.

We need to let users run arbitrary code under crcaches control from time to
time, so thats also a necessary concept:

4. Extension points.

The lifecycle of a resource, with all optimisations in place, will be something
like:

1. Provision, either statically configured or dynamically via some API.
   [needs source, produces resource]

2. Perform per-project configuration and place into a pool ready for use.
   The pool might be a stopped lxc container, or a running but idle cloud
   instance.
   [needs resource, pool source, produces resource]

3. Take it out of the pool and perform per-revision configuration.
   [needs pool, produces allocated resource]

4. Run some commands on it / copy files to or from it.
   [needs allocated resource]

5. Reset it to pool-status. This might involve stopping it and doing an lvm
   rollback, unmounting an aufs filesystem from a chroot, or doing nothing.
   [needs allocated resource, discards resource]

6. Repeat 3-5 as needed.

7. Unprovision, either dynamically, or by a user removing the configuration
   data.
   [needs source, pooled resource]


Resource Source
===============

Scale
-----

Sources have a range of concurrency. Fixed resources have the lower and upper
bounds the same, indicating that there is no way to discard such resources.
However, they start out with none allocated. Sources with non-zero lower bounds
could be preferentially used to fill pool requests.

Provision
---------

Sources need an API call to obtain another resource from the source. Allowing
users to run arbitrary code on the resource as it is obtained will allow
significant flexability with little code overhead.

Discard
-------

Sources need to be able to discard a resource they previously created. While
perhaps a corner case, allowing users to run arbitrary code on the resource
prior to discarding it is symmetrical and that helps predictability.

Local source
------------

Runs commands locally. Possible configuration options:

* Explicit concurrency.

* Override CWD.

* Do a sudo call ?

* Make file copies not copy (e.g. cp -al, or symlink...)

* Can import filesystems by bind mounting or even just running in the right
  dir.

SSH source
----------

Runs commands by sshing into a host. Possible configuration options:

* Host to ssh into

* Optional source to layer on? [permits bastion hosts]
  Raises the question of shared use of a bastion host - how to avoid locking
  other users out when the actual resource being used is behind the bastion
  host, while still not permitting the bastion host to be gc'd.

* Number of instances to export ?

Chroot source
-------------

Makes chroots. Configuration options:

* command line to instantiate a chroot

* command line to execute a command in a chroot

* control the user to run commands as

* import filesystems by bind mounting

* Layers on a base level source.

* Number of chroots to permit ?

LXC source
----------

Make LXC containers. Same basic options as chroots.

Docker source
-------------

Likewise.

Cloud source
------------

* cloud provider credentials, machine image id.

* SSH private key to use to make connections.

Pool source
-----------

A pool backends onto other sources. Configuration:

* One or more sources

* Minimum scale - able to be dialed up higher than the sum of the minimum scale
  for the backend sources. (Dialing it lower would have no impact, because the 
  backends would maintain their own minimums.

Compute Resource
================

Concurrency
-----------

Any given machine, be it virtual or physical, has an intrinsic degree of
concurrency. This matters to users that are scheduling work - for instance, a
test suite that has a natively parallel test runner might want to run one
instance of it per machine, but be spread over several physical machines to get
better concurrency. Something orchestrating runs with that runner would want to
know N(machines) rather than N(cpus) when scheduling work. Conversely, a test
runner that is itself serial and only ever uses one CPU per process might want
to run some M processes per physical machine, where M is the number of actual
cores in the machine.

We can expose the concurrency (ideally the effective cores, but as an
approximation the number of cpu's the OS sees) to clients of crcache. If we
choose not to expose this, users could just provision single-core resources
everywhere, but that has its own inefficiencies and the more cores machines
have the more getting this right will matter.

Users may want to control this - e.g. to deal with poor CPU topologies so
offering an extension point to override (or perhaps mutate) the auto-detected
value makes sense. OTOH users could just wrap crcache calls.

An important distinction to surface is the difference between machines and
concurrency within a machine. Tools like testrepository wish to be able to
query the concurrency at both levels - but we can perhaps let such tools
deal with crcache at the level of 'machine' and query concurrency within
a machine themselves.

Running tasks
-------------

We need to be able to run tasks on a resource. To do that you need a network
location, username and credentials. We can bundle those all up and offer a
remote shell facility, with minimal loss of generality.

crcache is a choke point on command execution, so it can offer an extension
point both before and after commands are run (and perhaps even wrap the
input and output of commands). Uses for this are to fix up paths, environment
variables, squelch noise at the source. However, most of the same capability
can be done by wrapping crcache itself, so this should be a second-pass
feature.

File handoffs
-------------

A common task will be synchronising some local file with the resource, and
retrieving build products post-execution. While anything can be build on the
run-a-task abstraction, offering direct file handling simplifies correctness
for handling of temporary files, and makes debugging considerably easier for
users. In particular, if there are extension points to influence task running,
file transfer done on top of running tasks would be subject to the same side
effects.

Filesytem imports
-----------------

What sort of imports can this resource utilise?

* rsync

* bind mount

* others in future?

Code layout
===========

One conceptual thing per module, packages for anything where multiple types
are expected (e.g. cr_cache.commands, cr_cache.ui).

Generic driver code should not trigger lots of imports: code dependencies
should be loaded when needed. For example, argument validation uses argument
types that each command can import, so the core code doesn't need to know about
all types.

The tests for the code in cr_cache.foo.bar is in cr_cache.tests.foo.test_bar.
Interface tests for cr_cache.foo is in cr_cache.tests.foo.test___init__.

Key modules
===========

cache
-----

Responsible for arbitrating use of sources. Takes care to stay within limits,
manage reserved resources etc.

source
------

Pluggable interface for supplying compute resources. Takes care of making,
discarding, and running commands on compute resources.

ui
--

User interfaces.

commands
--------

Tasks users can perform.

External integration
====================

The command, ui, parsing etc objects should all be suitable for reuse from
other programs - e.g. to provide a GUI or web status page with pool status.
