## Who is responsible for this?!?!

My name is Erik Johnson, and I'm a Senior Engineer on the core development team at [SaltStack](https://saltstack.com). If you've participated in the community between early 2012 and today, then there's a good chance we've interacted in some way. Hopefully I haven't been a jerk to you.

## What is it?

A proof-of-concept for a potential method of distributing [SaltStack](https://saltstack.com) with all Python dependencies bundled within a virtualenv.

## Why?

[SaltStack](https://saltstack.com) releases starting with 2015.8.0 rely on [PyCrypto](https://www.dlitz.net/software/pycrypto/) 2.6.1 and [tornado](http://www.tornadoweb.org/) 4.2.1, which are not available in the repositories for most Linux distributions (especially LTS releases). This is part of the reason why we took steps to host our own [repository](https://repo.saltstack.com/), to provide these newer versions of needed dependencies.

However, [SaltStack](https://saltstack.com) obviously isn't the only project that uses these two modules, and upgrading them via our repositories can be problematic if you happen to:

1. Use other software which relies on the earlier versions of [PyCrypto](https://www.dlitz.net/software/pycrypto/) and [tornado](http://www.tornadoweb.org/) available in your distro's official repositories.

2. Have a company policy against non-essential upgrades.

This POC is an attempt to resolve these conflicts by distributing all Python dependencies in a [virtualenv](https://virtualenv.pypa.io/en/stable/). All of the Python bits get installed under ``/opt/salt``.

For RHEL/CentOS 5 and 6, this project goes a step further and distributes the entire Python 2.7.12 stdlib in the virtualenv, allowing all three RHEL/CentOS releases to use Python 2.7.

## Wait, RHEL/CentOS only? What about Debian/Ubuntu/SUSE/etc...?

Like it says above, this is a proof-of-concept. RHEL/CentOS is in my wheelhouse, Debian/Ubuntu/SUSE not so much. If we at [SaltStack](https://saltstack.com) decide to move forward with this, then our packaging team will expand this POC to other distros. However, for now this is RHEL/CentOS only. Sorry.

## Awesome! How the heck do I use this?

See the [wiki](https://github.com/terminalmage/salt-virtualenv/wiki).
