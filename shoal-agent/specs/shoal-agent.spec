%define name shoal-agent
%define version 0.9.3
%define unmangled_version 0.9.3
%define release 1

Summary: A squid cache publishing and advertising tool designed to work in fast changing environments
Name: %{name}
Version: %{version}
Release: %{release}%{?dist}
Source0: %{name}-%{unmangled_version}.tar.gz
License: 'GPL3' or 'Apache 2'
Group: Development/Libraries
BuildArch: noarch
Vendor: Ian Gable <igable@uvic.ca>
Requires: python-netifaces >= 0.5 
Requires: python-pika >= 0.9.5
if 0%{?el6}
%else
Requires(post): systemd
Requires(preun): systemd
Requires(postun): systemd
%endif
if 0%{?el6}
%else
BuildRequires: systemd

%endif
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
mv $RPM_BUILD_ROOT/usr/shoal-agent-conf/shoal-agent.logrotate $RPM_BUILD_ROOT/etc/logrotate.d/shoal-agent
mv $RPM_BUILD_ROOT/usr/shoal-agent-conf/shoal-agent.sysconfig $RPM_BUILD_ROOT/etc/sysconfig/shoal/shoal-agent
%if 0%{?el6}
mv $RPM_BUILD_ROOT/usr/shoal-agent-conf/shoal-agent.init $RPM_BUILD_ROOT/%{_initddir}/shoal-agent                                       
%else
mv $RPM_BUILD_ROOT/usr/shoal-agent-conf/shoal.service $RPM_BUILD_ROOT/%{_unitdir}/shoal-agent.service
%endif
touch $RPM_BUILD_ROOT/var/log/shoal_agent.log



%post
%if 0%{?el6}
%else
%systemd_post shoal-agent.service
%endif

%preun
%if 0%{?el6}
%else
%systemd_preun shoal-agent.service
%endif

%postun
%if 0%{?el6}
%else
%systemd_postun_with_restart shoal-agent.service
%endif

%files 
%{python_sitelib}/shoal_agent
%{_bindir}/shoal-agent
%attr(nobody,nobody,-) /var/log/shoal-agent.log
%if 0%{?el6}
%{_initddir}/shoal-agent
%else
%{_unitdir}/shoal-agent.service
%endif
%config(noreplace) /etc/shoal/shoal_agent.conf
%config(noreplace) /etc/sysconfig/shoal/shoal-agent
%config(noreplace) /etc/logrotate.d/shoal-agent


