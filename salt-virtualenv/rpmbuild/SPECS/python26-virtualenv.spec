%global __python python26
%{!?python_sitelib: %global python_sitelib %(%{__python} -c "from distutils.sysconfig import get_python_lib; print(get_python_lib())")}

%define _eggname virtualenv

Summary:        Virtual Python Environment builder
Name:           python26-%{_eggname}
Version:        15.0.3
Release:        1%{?dist}
# Mostly Public Domain apart from parts of HMAC.py and setup.py, which are Python
License:        Public Domain and Python
Group:          Development/Libraries
URL:            https://pypi.python.org/pypi/%{_eggname}
Source0:        https://pypi.python.org/packages/8b/2c/c0d3e47709d0458816167002e1aa3d64d03bdeb2a9d57c5bd18448fd24cd/%{_eggname}-%{version}.tar.gz
BuildRequires:  python26-devel
Requires:       python26
BuildRoot:      %{_tmppath}/%{name}-%{version}-buildroot-%(id -nu)
BuildArch:      noarch

%description
Virtual Python Environment builder

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
%{_bindir}/virtualenv*

%changelog
* Sun Nov 13 2016 SaltStack Packaging Team <packaging@saltstack.com> 15.0.3-1
- Initial build
