%define name shoal-client
%define version 0.6.5
%define unmangled_version 0.6.5
%define release 1

Summary: A squid cache publishing and advertising tool designed to work in fast changing environments
Name: %{name}
Version: %{version}
Release: %{release}%{?dist}
Source0: %{name}-%{unmangled_version}.tar.gz
License: 'GPL3' or 'Apache 2'
Group: Development/Libraries
BuildArch: noarch
Vendor: UVic HEPRC <rsobie@uvic.ca>
Requires: python >= 2.4
Url: http://github.com/hep-gc/shoal

%description
shoal-client is a simple python script typically configured to run with cron
to check for new squids periodically. shoal-client will configure cvmfs to
use the closest squid server to you by contacting the shoal server and then
editing your local cvmfs config file, typically /etc/cvmfs/default.local.
Before setting the cronjob in place make sure that shoal-client is
configured correctly

%prep
%setup -n %{name}-%{unmangled_version}

%build
python setup.py build

%install
python setup.py install --single-version-externally-managed -O1 --root=$RPM_BUILD_ROOT
mkdir -p $RPM_BUILD_ROOT/etc/shoal
mkdir -p $RPM_BUILD_ROOT/var/log
mv $RPM_BUILD_ROOT/usr/share/shoal-client/shoal_client.conf $RPM_BUILD_ROOT/etc/shoal/shoal_client.conf
touch $RPM_BUILD_ROOT/var/log/shoal_client.log
rm -rf $RPM_BUILD_ROOT/%{python_sitelib}/shoal_client-%{unmangled_version}-py%{python_version}.egg-info

%files
%defattr(-,root,root)
%{python_sitelib}/shoal_client
%{_bindir}/shoal-client
%config(noreplace) /etc/shoal/shoal_client.conf
%attr(-,nobody,nobody) /var/log/shoal_client.log
