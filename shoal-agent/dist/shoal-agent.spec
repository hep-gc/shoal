%define name shoal-agent
%define version 0.6.0
%define unmangled_version 0.6.0
%define unmangled_version 0.6.0
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
Vendor: Mike Chester <mchester@uvic.ca>
Requires: netifaces >= 0.8 pika >= 0.9.13 python >= 2.6
Url: http://github.com/hep-gc/shoal

%description
UNKNOWN

%prep
%setup -n %{name}-%{unmangled_version} -n %{name}-%{unmangled_version}

%build
python setup.py build

%install
python setup.py install --single-version-externally-managed -O1 --root=$RPM_BUILD_ROOT --record=INSTALLED_FILES

%post
touch /var/log/shoal_agent.log
chown nobody:nobody /var/log/shoal_agent.log
chmod 0644 /etc/shoal/shoal_agent.conf
chkconfig --add shoal-agent


%clean
rm -rf $RPM_BUILD_ROOT

%files -f INSTALLED_FILES
%defattr(-,root,root)
