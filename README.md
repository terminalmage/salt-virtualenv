_NOTE: This repo has been deleted and recreated. If you cloned it before 15 November 2016 @21:30 UTC, you should re-clone._

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

## Wait, RHEL/CentOS only? What about Debian/Ubuntu/SUSE/etc...?

Like it says above, this is a proof-of-concept. RHEL/CentOS is in my wheelhouse, Debian/Ubuntu/SUSE not so much. If we at [SaltStack](https://saltstack.com) decide to move forward with this, then our packaging team will expand this POC to other distros. However, for now this is RHEL/CentOS only. Sorry.

## Awesome! How the heck do I build this?

If you are so inclined, and already have a Fedora box with mock installed, the source RPM and the two RPMs that you need to pass to the mock command to provide two of the necessary ``BuildRequires`` can be found in the [salt-virtualenv](https://github.com/terminalmage/salt-virtualenv/tree/master/salt-virtualenv) directory.

However, to make it as easy as possible, this repo contains everything needed to build a Docker image which contains all the components necessary for building RPMs, and is pre-configured and ready-to-use. Additionally, within the container the spec and source files are expanded from the source RPM, for those interested in inspecting them. The build environment within the container is located in ``/home/builder/rpmbuild``, with the source files located in the ``SOURCES`` subdirectory, and the spec file located in the ``SPECS`` subdirectory.

Here's how to set up the Docker-based build environment and build the RPMs:

### 1) Clone the repo

```
% git clone https://github.com/terminalmage/salt-virtualenv
```

### 2) Create a data-only container

This provides persistent storage for the mock cache. We'll use it later on.

```
% docker run -v /var/cache/mock --name mock-cache busybox
Unable to find image 'busybox:latest' locally
latest: Pulling from library/busybox
56bec22e3559: Pull complete
Digest: sha256:29f5d56d12684887bdfa50dcd29fc31eea4aaf4ad3bec43daf19026a7ce69912
Status: Downloaded newer image for busybox:latest
```

### 3) Build the Docker image (optional)

Most users can skip this step and just use [terminalmage/salt-virtualenv](https://hub.docker.com/r/terminalmage/salt-virtualenv/), but for those who modify the Dockerfile in some way, you'll want to make sure to build the new image.

```
% cd /path/to/git/clone/salt-virtualenv
% sudo docker build -t myusername/salt-virtualenv .
```

If you do this, you'll need to replace all occurrences of ``terminalmage/salt-virtualenv`` below with the tag you used when you built the image.

### 4) Create a local destination for the packages we'll be building

This will be bound to ``/home/builder/mock`` in the Docker image when we run it.

```
% mkdir ~/mock
```

You don't have to use ``~/mock``, but if you do use something different, then you'll of course need to replace occurrences of ``~/mock`` with the location you choose.

### 5) Launch an instance of the build image

```
% sudo docker run --cap-add=SYS_ADMIN --privileged --volumes-from=mock-cache --rm -it -h rpmbuild -v ~/mock:/home/builder/mock terminalmage/salt-virtualenv
```

- ``--cap-add=SYS_ADMIN`` is needed by mock to chroot within the container
- ``--privileged`` is needed by mock to install the ``filesystem`` RPM within the chroot (this fails if ``/sys`` is mounted read-only, which is the default in unprivileged containers).
- ``--volumes-from=mock-cache`` ensures that we use the data-only container we created in step 2 to provide persistent storage for mock's rootfs and yum/dnf cache, keeping you from needing to re-download a bunch of stuff the next time you launch the container.
- ``~/mock`` should be replaced with whatever path you chose for the package destination, if it was different.


### 6) RHEL/CentOS 5 build requisites

Those not building for RHEL/CentOS 5 can skip to Step 7.

For RHEL/CentOS 5 our RPM spec requires a couple of packages not available in EPEL. So, we'll need to build these first. There's a helper script that will do this for you, all you need to do is run it:

```
[builder@rpmbuild ~]$ build-reqs
```

When complete, the build requisites will be located under ``/home/builder/mock``. This is where all the packages we build here will end up. If you've been following the directions so far, these packages will end up in ``~/mock`` (or whichever path you chose) on the host machine.

This should only be done the first time, since you'll already have them in your ``~/mock`` dir the next time.

### 7) Build the RPMs

When you started the Docker image, a message displayed which describes aliases that have been pre-configured to make building easy. If you missed this message, it can be viewed [here](https://github.com/terminalmage/salt-virtualenv/blob/master/salt-virtualenv/motd), or by running ``cat /etc/motd`` within the container.

The aliases are [here](https://github.com/terminalmage/salt-virtualenv/blob/master/salt-virtualenv/aliases). The build commands use a ``mockbuild`` script I wrote a while back to automate some of the more mundane arguments one needs to enter when using ``mock``.

### 8) Back on the host machine, retrieve packages from the local ``mock`` directory you created in Step 4

```
% cd ~/mock/salt/2016.3.4-2.el5_erik/x86_64
% ls -l
total 26436
-rw-rw-r-- 1 erik erik   566803 Nov 13 16:32 build.log
-rw-rw-r-- 1 erik erik    48242 Nov 13 16:32 root.log
-rw-rw-r-- 1 erik kdm   9489548 Nov 13 16:31 salt-2016.3.4-2.el5_erik.src.rpm
-rw-rw-r-- 1 erik kdm  15298701 Nov 13 16:32 salt-2016.3.4-2.el5_erik.x86_64.rpm
-rw-rw-r-- 1 erik kdm     14358 Nov 13 16:32 salt-api-2016.3.4-2.el5_erik.x86_64.rpm
-rw-rw-r-- 1 erik kdm     17127 Nov 13 16:32 salt-cloud-2016.3.4-2.el5_erik.x86_64.rpm
-rw-rw-r-- 1 erik kdm   1544552 Nov 13 16:32 salt-master-2016.3.4-2.el5_erik.x86_64.rpm
-rw-rw-r-- 1 erik kdm     33593 Nov 13 16:32 salt-minion-2016.3.4-2.el5_erik.x86_64.rpm
-rw-rw-r-- 1 erik kdm     14979 Nov 13 16:32 salt-ssh-2016.3.4-2.el5_erik.x86_64.rpm
-rw-rw-r-- 1 erik kdm     14719 Nov 13 16:32 salt-syndic-2016.3.4-2.el5_erik.x86_64.rpm
-rw-rw-r-- 1 erik erik      962 Nov 13 16:32 state.log
```

### 9) Profit!
