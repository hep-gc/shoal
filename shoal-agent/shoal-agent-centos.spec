%define name shoal-agent
%define version 0.9.3
%define unmangled_version 0.9.3
%define release 1
%define python_version 2.6

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
shoal-agent runs on squid servers and publishes the load and IP of the
squid server to the shoal-server using a json formatted AMQP message at
regular intervals. The purpose of the shoal-agent is to advertise it's
existence to a central shoal-server so that when new cloud compute nodes
are booted they can contact the shoal-server and contextualize to the
nearest squid proxy.

%prep
%setup -n %{name}-%{unmangled_version}

%build
python setup.py build

%install
python setup.py install --single-version-externally-managed -O1 --root=$RPM_BUILD_ROOT
mkdir -p $RPM_BUILD_ROOT/etc/{shoal,init.d,logrotate.d,sysconfig}
mkdir $RPM_BUILD_ROOT/etc/sysconfig/shoal
mv $RPM_BUILD_ROOT/usr/shoal-agent-conf/shoal_agent.conf $RPM_BUILD_ROOT/etc/shoal/shoal_agent.conf
mv $RPM_BUILD_ROOT/usr/shoal-agent-conf/shoal-agent.init $RPM_BUILD_ROOT/etc/init.d/shoal-agent                                       
mv $RPM_BUILD_ROOT/usr/shoal-agent-conf/shoal-agent.logrotate $RPM_BUILD_ROOT/etc/logrotate.d/shoal-agent
mv $RPM_BUILD_ROOT/usr/shoal-agent-conf/shoal-agent.sysconfig $RPM_BUILD_ROOT/etc/sysconfig/shoal/shoal-agent

%clean
rm -rf $RPM_BUILD_ROOT

%post
touch /var/log/shoal_agent.log
chown nobody:nobody /var/log/shoal_agent.log


%files 
/usr/lib/python%{python_version}/site-packages/shoal_agent/*
/usr/lib/python%{python_version}/site-packages/shoal_agent-%{unmangled_version}-py%{python_version}.egg-info/*
/usr/bin/shoal-agent
%config(noreplace) /etc/shoal/shoal_agent.conf
%config(noreplace) /etc/sysconfig/shoal/shoal-agent
%config(noreplace) /etc/init.d/shoal-agent
%config(noreplace) /etc/logrotate.d/shoal-agent
