%global __python python26
%{!?python_sitelib: %global python_sitelib %(%{__python} -c "from distutils.sysconfig import get_python_lib; print(get_python_lib())")}

%define _eggname distribute

Summary:        Easily download, build, install, upgrade, and uninstall Python packages
Name:           python26-%{_eggname}
Version:        0.6.49
Release:        1%{?dist}
License:        Public Domain and Python
Group:          Development/Libraries
URL:            https://pypi.python.org/pypi/%{_eggname}/%{version}
Source0:        https://pypi.python.org/packages/f3/2b/e97c01487b7636ba3fcff5e73db995c66c524d54d0907d238311524f67c8/%{_eggname}-%{version}.tar.gz
BuildRequires:  python26-devel
Requires:       python26
BuildRoot:      %{_tmppath}/%{name}-%{version}-buildroot-%(id -nu)
BuildArch:      noarch

%description
Easily download, build, install, upgrade, and uninstall Python packages

%prep
%setup -n %{_eggname}-%{version}

%build
%{__python} setup.py build

%install
rm -rf %{buildroot}
%{__python} setup.py install -O1 --skip-build --root %{buildroot}

%clean
rm -rf %{buildroot}

%files
%defattr(-,root,root,-)
%{python_sitelib}/*
%{_bindir}/*

%changelog
* Tue Nov 15 2016 SaltStack Packaging Team <packaging@saltstack.com> 0.6.49-1
- Initial build
