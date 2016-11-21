%if 0%{?rhel} <= 6
%global with_python27 1
%endif

# Override .elX.centos in /etc/rpm/macros.dist
%if 0%{?rhel}
%define dist .el%{rhel}
%endif

%global debug_package %{nil}
%global __os_install_post %{nil}
%global __arch_install_post %{nil}

%global include_tests 0

%global __virtualenv_parent_dir /opt
%global __virtualenv %{__virtualenv_parent_dir}/%{name}
%global __pybasever 2.7
%global __virtualenv_python %{buildroot}%{__virtualenv}/bin/python
%global __python python%{__pybasever}
%global __salttesting SaltTesting


# Remember to update the versions in Source0/Source1/Source2 if one of these is
# modified. A script on the docker build host needs to be able to parse out the
# URL, so we can't use RPM macros in the SourceN entries.
%global __salt_version 2016.3.4
%global __salttesting_ver 2016.10.26
%global __pyzmq_ver 16.0.1

%{!?pythonpath: %global pythonpath %(%{__python} -c "import os, sys; print(os.pathsep.join(x for x in sys.path if x))")}

Name: salt

# Remember to update the version in Source0 if this is modified. Rather than
# use rpmspec (which will likely not be available on a non-RH-based OS), a
# script needs to be able to parse out the URL, and so we can't use RPM macros.
Version: %{__salt_version}
Release: 3.salt_virtualenv%{?dist}
Summary: A parallel remote execution system

Group:   System Environment/Daemons
License: ASL 2.0
URL:     http://saltstack.org/
Source0: https://pypi.python.org/packages/d1/9e/95ad58e5fa399079761d96116f375c88a83a50684b29f5326fb941aa44b5/salt-2016.3.4.tar.gz
Source1: https://pypi.python.org/packages/a4/98/b15226a9ac520d42d9b33732bef302614d7eb47d9c386b9bc2f4e71894d2/SaltTesting-2016.10.26.tar.gz
Source2: https://pypi.python.org/packages/45/a6/208eb616ab0221679944631d93f4d05651422a16dd7828fc71e40dead6a7/pyzmq-16.0.1.tar.gz
Source3: %{name}-master
Source4: %{name}-syndic
Source5: %{name}-minion
Source6: %{name}-api
Source7: %{name}-master.service
Source8: %{name}-syndic.service
Source9: %{name}-minion.service
Source10: %{name}-api.service
Source11: README.fedora
Source12: %{name}-common.logrotate
Source13: salt.bash
Source14: make_wrappers.sh

AutoReq: no
AutoProv: no

BuildRoot: %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)

%ifarch %{ix86} x86_64
Requires: dmidecode
%endif

Requires: pciutils
Requires: which
Requires: yum-utils

%if 0%{?with_python27}

BuildRequires: openssl-devel
BuildRequires: python27-devel
BuildRequires: python27-virtualenv
BuildRequires: gzip

# No runtime dep on system python because we will be copying all python
# source files into the virtualenv

%else

BuildRequires: libyaml
BuildRequires: openssl-devel
BuildRequires: python-devel
BuildRequires: python-setuptools
BuildRequires: python-virtualenv
BuildRequires: gzip
Requires: python

%if ((0%{?rhel} >= 6 || 0%{?fedora} > 12) && 0%{?include_tests})

BuildRequires: git
BuildRequires: python-mock
BuildRequires: python-psutil
BuildRequires: python-six
BuildRequires: python-unittest2

%endif

%endif

%if ! (0%{?rhel} >= 7 || 0%{?fedora} >= 15)

Requires(post): chkconfig
Requires(preun): chkconfig
Requires(preun): initscripts
Requires(postun): initscripts

%else

%if 0%{?systemd_preun:1}

Requires(post): systemd-units
Requires(preun): systemd-units
Requires(postun): systemd-units

%endif

BuildRequires: systemd-units
Requires:      systemd-python

%endif

%description
Salt is a distributed remote execution system used to execute commands and
query data. It was developed in order to bring the best solutions found in
the world of remote execution together and make them better, faster and more
malleable. Salt accomplishes this via its ability to handle larger loads of
information, and not just dozens, but hundreds or even thousands of individual
servers, handle them quickly and through a simple and manageable interface.

%package master
Summary: Management component for salt, a parallel remote execution system
Group:   System Environment/Daemons
Requires: %{name} = %{version}-%{release}
%if (0%{?rhel} >= 7 || 0%{?fedora} >= 15)
Requires: systemd-python
%endif

%description master
The Salt master is the central server to which all minions connect.

%package minion
Summary: Client component for Salt, a parallel remote execution system
Group:   System Environment/Daemons
Requires: %{name} = %{version}-%{release}

%description minion
The Salt minion is the agent component of Salt. It listens for instructions
from the master, runs jobs, and returns results back to the master.

%package syndic
Summary: Master-of-master component for Salt, a parallel remote execution system
Group:   System Environment/Daemons
Requires: %{name}-master = %{version}-%{release}

%description syndic
The Salt syndic is a master daemon which can receive instruction from a
higher-level master, allowing for tiered organization of your Salt
infrastructure.

%package api
Summary: REST API for Salt, a parallel remote execution system
Group:   Applications/System
Requires: %{name}-master = %{version}-%{release}

%description api
salt-api provides a REST interface to the Salt master.

%package cloud
Summary: Cloud provisioner for Salt, a parallel remote execution system
Group:   Applications/System
Requires: %{name}-master = %{version}-%{release}

%description cloud
The salt-cloud tool provisions new cloud VMs, installs salt-minion on them, and
adds them to the master's collection of controllable minions.

%package ssh
Summary: Agentless SSH-based version of Salt, a parallel remote execution system
Group:   Applications/System
Requires: %{name} = %{version}-%{release}

%description ssh
The salt-ssh tool can run remote execution functions and states without the use
of an agent (salt-minion) service.

%prep
%setup -q -c
%setup -q -T -D -a 1
%setup -q -T -D -a 2

cd %{name}-%{version}

%build


%install
rm -rf %{buildroot}

# Create virtualenv
install -d -m 0755 %{buildroot}%{__virtualenv_parent_dir}
cd %{buildroot}%{__virtualenv_parent_dir}
virtualenv-%{__pybasever} --no-site-packages %{name}

%if 0%{?with_python27}
# Avoid needing to install Python from system packages by copying needed sofiles
# and adding to the library path.
install -d -m 0755 %{buildroot}%{_libdir}/%{name}
cp %{_libdir}/libpython%{__pybasever}* %{buildroot}%{_libdir}/%{name}/
install -d -m 0755 %{buildroot}%{_sysconfdir}/ld.so.conf.d
echo %{_libdir}/%{name} >%{buildroot}%{_sysconfdir}/ld.so.conf.d/%{name}.conf
chmod 0644 %{buildroot}%{_sysconfdir}/ld.so.conf.d/%{name}.conf
%endif

# Add wrappers
sh %{SOURCE14} -b %{buildroot}%{_bindir} -v %{__virtualenv} -w 'salt spm salt-api salt-call salt-cloud salt-cp salt-key salt-master salt-minion salt-proxy salt-run salt-ssh salt-syndic salt-unity' -p %{__pybasever} -m 0755

# Manually install pyzmq instead of using pip.
cd $RPM_BUILD_DIR/%{name}-%{version}/pyzmq-%{__pyzmq_ver}
%{__virtualenv_python} setup.py fetch_libzmq
# Building pyzmq with Python from ius results in ./configure trying to build
# with gcc44, but installing this as a built-time dep when it's not available
# makes it a runtime dep when the RPM is installed. Alias gcc44/g++44 to
# gcc/g++ to work around this.
%if 0%{?with_python27}
mkdir /tmp/bin
ln -s /usr/bin/gcc /tmp/bin/gcc44
ln -s /usr/bin/g++ /tmp/bin/g++44
export PATH=$PATH:/tmp/bin
%endif
%{__virtualenv_python} setup.py install -O1 --zmq=bundled

# Change into source directory
cd $RPM_BUILD_DIR/%{name}-%{version}/%{name}-%{version}

# Install deps into virtualenv
%{buildroot}%{__virtualenv}/bin/pip install -r requirements/zeromq.txt
%{buildroot}%{__virtualenv}/bin/pip install apache-libcloud cherrypy

# Install salt into virtualenv
%{__virtualenv_python} setup.py install -O1

%if 0%{?with_python27}

find %{buildroot}%{__virtualenv}/lib -type l -delete
mv %{buildroot}%{__virtualenv}/lib/python%{__pybasever}/site.py %{buildroot}%{__virtualenv}/lib/python%{__pybasever}/site.py.bak
cp -rv %{_libdir}/python%{__pybasever}/* %{buildroot}%{__virtualenv}/lib/python%{__pybasever} || /usr/bin/env true
mv %{buildroot}%{__virtualenv}/lib/python%{__pybasever}/site.py.bak %{buildroot}%{__virtualenv}/lib/python%{__pybasever}/site.py

%ifarch x86_64
rm %{buildroot}%{__virtualenv}/lib/python%{__pybasever}/config/libpython%{__pybasever}.so
ln -s %{_libdir}/%{name}/libpython%{__pybasever}.so %{buildroot}%{__virtualenv}/lib/python%{__pybasever}/config/libpython%{__pybasever}.so
%endif

rm %{buildroot}%{__virtualenv}/include/python%{__pybasever}
install -d -m 0755 %{buildroot}%{__virtualenv}/include/python%{__pybasever}
cp %{_includedir}/python%{__pybasever}/* %{buildroot}%{__virtualenv}/include/python%{__pybasever}

%endif

# Fix paths created by virtualenv (remove the buildroot)
find %{buildroot}%{__virtualenv}/bin -type f -exec sed -i "s#%{buildroot}%{__virtualenv_parent_dir}#%{__virtualenv_parent_dir}#g" {} \;

# Move/compress manpages
install -d -m 0755 %{buildroot}%{_mandir}/man1
install -d -m 0755 %{buildroot}%{_mandir}/man7
find %{buildroot}%{__virtualenv}/share/man/man1 -type f -exec mv {} %{buildroot}%{_mandir}/man1/ \;
find %{buildroot}%{__virtualenv}/share/man/man7 -type f -exec mv {} %{buildroot}%{_mandir}/man7/ \;
find %{buildroot}%{_mandir} -type f -not -name \*.gz -exec gzip {} \;

# Remove unneeded dir now that manpages have been moved out of virtualenv
rm -rf %{buildroot}%{__virtualenv}/share

# Add some directories
install -d -m 0755 %{buildroot}%{_var}/log/salt
touch %{buildroot}%{_var}/log/salt/minion
touch %{buildroot}%{_var}/log/salt/master
install -d -m 0755 %{buildroot}%{_var}/cache/salt
install -d -m 0755 %{buildroot}%{_sysconfdir}/salt
install -d -m 0755 %{buildroot}%{_sysconfdir}/salt/master.d
install -d -m 0755 %{buildroot}%{_sysconfdir}/salt/minion.d
install -d -m 0755 %{buildroot}%{_sysconfdir}/salt/pki
install -d -m 0755 %{buildroot}%{_sysconfdir}/salt/pki/master
install -d -m 0755 %{buildroot}%{_sysconfdir}/salt/pki/minion
install -d -m 0755 %{buildroot}%{_sysconfdir}/salt/cloud.conf.d
install -d -m 0755 %{buildroot}%{_sysconfdir}/salt/cloud.deploy.d
install -d -m 0755 %{buildroot}%{_sysconfdir}/salt/cloud.maps.d
install -d -m 0755 %{buildroot}%{_sysconfdir}/salt/cloud.profiles.d
install -d -m 0755 %{buildroot}%{_sysconfdir}/salt/cloud.providers.d

# Add the config files
install -p -m 0640 conf/minion %{buildroot}%{_sysconfdir}/salt/minion
install -p -m 0640 conf/master %{buildroot}%{_sysconfdir}/salt/master
install -p -m 0640 conf/cloud %{buildroot}%{_sysconfdir}/salt/cloud
install -p -m 0640 conf/roster %{buildroot}%{_sysconfdir}/salt/roster
install -p -m 0640 conf/proxy %{buildroot}%{_sysconfdir}/salt/proxy

%if ! (0%{?rhel} >= 7 || 0%{?fedora} >= 15)
install -d -m 0755 %{buildroot}%{_initrddir}
install -p %{SOURCE3} %{buildroot}%{_initrddir}/
install -p %{SOURCE4} %{buildroot}%{_initrddir}/
install -p %{SOURCE5} %{buildroot}%{_initrddir}/
install -p %{SOURCE6} %{buildroot}%{_initrddir}/
%else
# Add the unit files
install -d -m 0755 %{buildroot}%{_unitdir}
install -p -m 0644 %{SOURCE7} %{buildroot}%{_unitdir}/
install -p -m 0644 %{SOURCE8} %{buildroot}%{_unitdir}/
install -p -m 0644 %{SOURCE9} %{buildroot}%{_unitdir}/
install -p -m 0644 %{SOURCE10} %{buildroot}%{_unitdir}/
%endif

# Logrotate
install -p %{SOURCE11} .
install -d -m 0755 %{buildroot}%{_sysconfdir}/logrotate.d/
install -p -m 0644 %{SOURCE12} %{buildroot}%{_sysconfdir}/logrotate.d/salt

# Bash completion
install -d -m 0755 %{buildroot}%{_sysconfdir}/bash_completion.d/
install -p -m 0644 %{SOURCE13} %{buildroot}%{_sysconfdir}/bash_completion.d/salt.bash

%if ((0%{?rhel} >= 6 || 0%{?fedora} > 12) && 0%{?include_tests})
%check
cd $RPM_BUILD_DIR/%{name}-%{version}/%{name}-%{version}
mkdir %{_tmppath}/salt-test-cache
PYTHONPATH=%{pythonpath}:%{__virtualenv}/lib/python%{__pybasever}/site-packages:$RPM_BUILD_DIR/%{name}-%{version}/%{__salttesting}-%{__salttesting_ver} %{__virtualenv_python} setup.py test --runtests-opts=-u
%endif

%clean
rm -rf %{buildroot}

%files
%defattr(-,root,root,-)
%if 0%{?with_python27}
%{_libdir}/%{name}
%{_sysconfdir}/ld.so.conf.d/%{name}.conf
%endif
%{__virtualenv}
%{_bindir}/spm
%{_sysconfdir}/bash_completion.d/salt.bash
%{_sysconfdir}/logrotate.d/salt
%{_var}/cache/salt
%{_var}/log/salt
%doc $RPM_BUILD_DIR/%{name}-%{version}/%{name}-%{version}/LICENSE
%doc $RPM_BUILD_DIR/%{name}-%{version}/%{name}-%{version}/README.fedora
%doc %{_mandir}/man1/spm.1.*
%config(noreplace) %{_sysconfdir}/salt/

%files master
%defattr(-,root,root)
%doc %{_mandir}/man7/salt.7.*
%doc %{_mandir}/man1/salt-cp.1.*
%doc %{_mandir}/man1/salt-key.1.*
%doc %{_mandir}/man1/salt-master.1.*
%doc %{_mandir}/man1/salt-run.1.*
%doc %{_mandir}/man1/salt-unity.1.*
%{_bindir}/salt
%{_bindir}/salt-cp
%{_bindir}/salt-key
%{_bindir}/salt-master
%{_bindir}/salt-run
%{_bindir}/salt-unity
%if ! (0%{?rhel} >= 7 || 0%{?fedora} >= 15)
%attr(0755, root, root) %{_initrddir}/salt-master
%else
%{_unitdir}/salt-master.service
%endif
%config(noreplace) %{_sysconfdir}/salt/master
%config(noreplace) %{_sysconfdir}/salt/master.d
%config(noreplace) %{_sysconfdir}/salt/pki/master
%config(noreplace) %{_var}/log/salt/master

%files minion
%defattr(-,root,root)
%doc %{_mandir}/man1/salt-call.1.*
%doc %{_mandir}/man1/salt-minion.1.*
%doc %{_mandir}/man1/salt-proxy.1.*
%{_bindir}/salt-minion
%{_bindir}/salt-call
%{_bindir}/salt-proxy
%if ! (0%{?rhel} >= 7 || 0%{?fedora} >= 15)
%attr(0755, root, root) %{_initrddir}/salt-minion
%else
%{_unitdir}/salt-minion.service
%endif
%config(noreplace) %{_sysconfdir}/salt/minion
%config(noreplace) %{_sysconfdir}/salt/proxy
%config(noreplace) %{_sysconfdir}/salt/minion.d
%config(noreplace) %{_sysconfdir}/salt/pki/minion
%config(noreplace) %{_var}/log/salt/minion

%files syndic
%doc %{_mandir}/man1/salt-syndic.1.*
%{_bindir}/salt-syndic
%if ! (0%{?rhel} >= 7 || 0%{?fedora} >= 15)
%attr(0755, root, root) %{_initrddir}/salt-syndic
%else
%{_unitdir}/salt-syndic.service
%endif

%files api
%defattr(-,root,root)
%doc %{_mandir}/man1/salt-api.1.*
%{_bindir}/salt-api
%if ! (0%{?rhel} >= 7 || 0%{?fedora} >= 15)
%attr(0755, root, root) %{_initrddir}/salt-api
%else
%{_unitdir}/salt-api.service
%endif

%files cloud
%doc %{_mandir}/man1/salt-cloud.1.*
%{_bindir}/salt-cloud
%{_sysconfdir}/salt/cloud.conf.d
%{_sysconfdir}/salt/cloud.deploy.d
%{_sysconfdir}/salt/cloud.maps.d
%{_sysconfdir}/salt/cloud.profiles.d
%{_sysconfdir}/salt/cloud.providers.d
%config(noreplace) %{_sysconfdir}/salt/cloud

%files ssh
%doc %{_mandir}/man1/salt-ssh.1.*
%{_bindir}/salt-ssh
%config(noreplace) %{_sysconfdir}/salt/roster

%post
/sbin/ldconfig

%postun
/sbin/ldconfig

# less than RHEL 8 / Fedora 16
# not sure if RHEL 7 will use systemd yet
%if ! (0%{?rhel} >= 7 || 0%{?fedora} >= 15)

%preun master
  if [ $1 -eq 0 ] ; then
      /sbin/service salt-master stop >/dev/null 2>&1
      /sbin/chkconfig --del salt-master
  fi

%preun syndic
  if [ $1 -eq 0 ] ; then
      /sbin/service salt-syndic stop >/dev/null 2>&1
      /sbin/chkconfig --del salt-syndic
  fi

%preun minion
  if [ $1 -eq 0 ] ; then
      /sbin/service salt-minion stop >/dev/null 2>&1
      /sbin/chkconfig --del salt-minion
  fi

%post master
  /sbin/chkconfig --add salt-master

%post minion
  /sbin/chkconfig --add salt-minion

%postun master
  if [ "$1" -ge "1" ] ; then
      /sbin/service salt-master condrestart >/dev/null 2>&1 || :
  fi

%postun syndic
  if [ "$1" -ge "1" ] ; then
      /sbin/service salt-syndic condrestart >/dev/null 2>&1 || :
  fi

%postun minion
  if [ "$1" -ge "1" ] ; then
      /sbin/service salt-minion condrestart >/dev/null 2>&1 || :
  fi

%else

%preun master
%if 0%{?systemd_preun:1}
  %systemd_preun salt-master.service
%else
  if [ $1 -eq 0 ] ; then
    # Package removal, not upgrade
    /bin/systemctl --no-reload disable salt-master.service > /dev/null 2>&1 || :
    /bin/systemctl stop salt-master.service > /dev/null 2>&1 || :
  fi
%endif

%preun syndic
%if 0%{?systemd_preun:1}
  %systemd_preun salt-syndic.service
%else
  if [ $1 -eq 0 ] ; then
    # Package removal, not upgrade
    /bin/systemctl --no-reload disable salt-syndic.service > /dev/null 2>&1 || :
    /bin/systemctl stop salt-syndic.service > /dev/null 2>&1 || :
  fi
%endif

%preun minion
%if 0%{?systemd_preun:1}
  %systemd_preun salt-minion.service
%else
  if [ $1 -eq 0 ] ; then
    # Package removal, not upgrade
    /bin/systemctl --no-reload disable salt-minion.service > /dev/null 2>&1 || :
    /bin/systemctl stop salt-minion.service > /dev/null 2>&1 || :
  fi
%endif

%post master
%if 0%{?systemd_post:1}
  if [ $1 -gt 1 ] ; then
    /usr/bin/systemctl try-restart salt-master.service >/dev/null 2>&1 || :
  else
    %systemd_post salt-master.service
  fi
%else
  /bin/systemctl daemon-reload &>/dev/null || :
%endif

%post minion
%if 0%{?systemd_post:1}
  if [ $1 -gt 1 ] ; then
    /usr/bin/systemctl try-restart salt-minion.service >/dev/null 2>&1 || :
  else
    %systemd_post salt-minion.service
  fi
%else
  /bin/systemctl daemon-reload &>/dev/null || :
%endif

%postun master
%if 0%{?systemd_post:1}
  %systemd_postun_with_restart salt-master.service
%else
  /bin/systemctl daemon-reload &>/dev/null
  [ $1 -gt 0 ] && /bin/systemctl try-restart salt-master.service &>/dev/null || :
%endif

%postun syndic
%if 0%{?systemd_post:1}
  %systemd_postun_with_restart salt-syndic.service
%else
  /bin/systemctl daemon-reload &>/dev/null
  [ $1 -gt 0 ] && /bin/systemctl try-restart salt-syndic.service &>/dev/null || :
%endif

%postun minion
%if 0%{?systemd_post:1}
  %systemd_postun_with_restart salt-minion.service
%else
  /bin/systemctl daemon-reload &>/dev/null
  [ $1 -gt 0 ] && /bin/systemctl try-restart salt-minion.service &>/dev/null || :
%endif

%endif

%changelog
* Thu Nov 17 2016 SaltStack Packaging Team <packaging@saltstack.com> - 2016.3.4-3
- Update with bundled Python 2.7 for EL5 and EL6

* Tue Nov 15 2016 SaltStack Packaging Team <packaging@saltstack.com> - 2016.3.4-2
- Initial build (based off of upstream 2016.3.4 spec)
