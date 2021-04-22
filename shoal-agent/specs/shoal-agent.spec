%define name shoal-agent
%define version 1.0.1
%define unmangled_version 1.0.1
%define release 1
%define group_shoal_num %(grep -c "^shoal" /etc/group)
%define user_shoal_num %(grep -c "^shoal" /etc/passwd)

Summary: A squid cache publishing and advertising tool designed to work in fast changing environments
Name: %{name}
Version: %{version}
Release: %{release}%{?dist}
Source0: %{name}-%{unmangled_version}.tar.gz
License: 'GPL3' or 'Apache 2'
Group: Development/Libraries
BuildArch: noarch
Vendor: UVic HEPRC <rsobie@uvic.ca>
Requires: python-netifaces >= 0.5 
Requires: python-pika >= 0.9.5
%if 0%{?el6}
%else
Requires(post): systemd
Requires(preun): systemd
Requires(postun): systemd
%endif
%if 0%{?el6}
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
%if %{group_shoal_num} == 0
sudo groupadd shoal
%endif
%if %{user_shoal_num} == 0
sudo useradd shoal -g shoal
%endif
sudo python -m pip install pystun
mkdir -p $RPM_BUILD_ROOT/etc/{shoal,init.d,logrotate.d}
mkdir -p $RPM_BUILD_ROOT/var/log
mv $RPM_BUILD_ROOT/usr/share/shoal-agent/shoal_agent.conf $RPM_BUILD_ROOT/etc/shoal/shoal_agent.conf
mv $RPM_BUILD_ROOT/usr/share/shoal-agent/shoal-agent.logrotate $RPM_BUILD_ROOT/etc/logrotate.d/shoal-agent
%if 0%{?el6}
mkdir -p $RPM_BUILD_ROOT/%{_initddir}
mv $RPM_BUILD_ROOT/usr/share/shoal-agent/shoal-agent.init $RPM_BUILD_ROOT/%{_initddir}/shoal-agent
rm $RPM_BUILD_ROOT/usr/share/shoal-agent/shoal-agent.service
%else
mkdir -p $RPM_BUILD_ROOT/%{_unitdir}
mv $RPM_BUILD_ROOT/usr/share/shoal-agent/shoal-agent.service $RPM_BUILD_ROOT/%{_unitdir}/shoal-agent.service
rm $RPM_BUILD_ROOT/usr/share/shoal-agent/shoal-agent.init
%endif
rm -rf $RPM_BUILD_ROOT/%{python_sitelib}/shoal_agent-%{unmangled_version}-py%{python_version}.egg-info
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
%attr(-,shoal,shoal) /var/log/shoal_agent.log
%if 0%{?el6}
%{_initddir}/shoal-agent
%else
%{_unitdir}/shoal-agent.service
%endif
%config(noreplace) /etc/shoal/shoal_agent.conf
%config(noreplace) /etc/logrotate.d/shoal-agent
%config(noreplace) /usr/bin/shoal-agent-installation.sh


