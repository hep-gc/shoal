%define name shoal-agent
%define version 0.9.2
%define unmangled_version 0.9.2
%define release 1

Summary: A squid cache publishing and advertising tool designed to work in fast changing environments
Name: %{name}
Version: %{version}
Release: %{release}
Source0: %{name}-%{unmangled_version}.tar.gz
License: 'GPL3' or 'Apache 2'
Group: Development/Libraries
BuildRoot: %{_tmppath}/%{name}-%{version}-%{release}-buildroot
Prefix: %{_prefix}
BuildArch: noarch
Vendor: Ian Gable <igable@uvic.ca>
Requires: python-netifaces >= 0.5 python-pika >= 0.9.5
Url: http://github.com/hep-gc/shoal

%description
UNKNOWN

%prep
%setup -n %{name}-%{unmangled_version}

%build
python setup.py build

%install
python setup.py install --single-version-externally-managed -O1 --root=$RPM_BUILD_ROOT --record=INSTALLED_FILES

%clean
rm -rf $RPM_BUILD_ROOT

%post
touch /var/log/shoal_agent.log
chown 0644 nobody:nobody /var/log/shoal_agent.log


%files -f INSTALLED_FILES
%defattr(-,root,root)
