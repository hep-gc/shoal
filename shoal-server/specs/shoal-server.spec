%define name shoal-server
%define version 1.0.0
%define unmangled_version 1.0.0
%define release 1
%define __python /usr/bin/python3

Summary: A squid cache publishing and advertising tool designed to work in fast changing environments
Name: %{name}
Version: %{version}
Release: %{release}%{?dist}
Source0: %{name}-%{unmangled_version}.tar.gz
License: 'GPL3' or 'Apache 2'
Group: Development/Libraries
BuildArch: noarch
Vendor: UVic HEPRC <rsobie@uvic.ca>
Requires: pygeoip >= 0.2.5 pika >= 0.9.11 web.py >= 0.3 python-requests >= 1.1.0 geoip2 >= 0.6.0 maxminddb >= 1.1.1 python-ipaddr >= 2.1.9 httpd >= 2.2.15 mod_wsgi >= 3.2
Url: http://github.com/hep-gc/shoal

%description
shoal-server maintains the list of running squids. It uses RabbitMQ to handle
incoming AMQP messages from squid servers. It provides a REST interface
for programatically retrieving a json formatted ordered list of squids.
It also provides a web interface for viewing the list.

%prep
%setup -n %{name}-%{unmangled_version}

%build
python3 setup.py build

%install
python3 setup.py install --single-version-externally-managed -O1 --root=$RPM_BUILD_ROOT
#Dish out the files and change permissions and any other requires setup here

mkdir -p $RPM_BUILD_ROOT/etc/{shoal,logrotate.d}
mkdir -p $RPM_BUILD_ROOT/etc/httpd/conf.d/
mkdir -p $RPM_BUILD_ROOT/var/log/
mkdir -p $RPM_BUILD_ROOT/var/www/shoal/{scripts,static,templates}
mkdir -p $RPM_BUILD_ROOT/var/www/shoal/static/{css,js,img}
mkdir -p $RPM_BUILD_ROOT/var/www/shoal/static/icons/

mv $RPM_BUILD_ROOT/usr/share/shoal-server/shoal_server.conf $RPM_BUILD_ROOT/etc/shoal/shoal_server.conf
mv $RPM_BUILD_ROOT/usr/share/shoal-server/shoal-server.logrotate $RPM_BUILD_ROOT/etc/logrotate.d/shoal-server
mv $RPM_BUILD_ROOT/usr/share/shoal-server/shoal.conf $RPM_BUILD_ROOT/etc/httpd/conf.d/
mv $RPM_BUILD_ROOT/usr/share/shoal-server/scripts/* $RPM_BUILD_ROOT/var/www/shoal/scripts/
mv $RPM_BUILD_ROOT/usr/share/shoal-server/static/* $RPM_BUILD_ROOT/var/www/shoal/static/
mv $RPM_BUILD_ROOT/usr/share/shoal-server/templates/* $RPM_BUILD_ROOT/var/www/shoal/templates/

rm -rf $RPM_BUILD_ROOT/%{python_sitelib}/shoal_server-%{unmangled_version}-py%{python_version}.egg-info
touch $RPM_BUILD_ROOT/var/log/shoal_server.log

%files 
%defattr(-,nobody,nobody) 
/var/www/shoal/*
%{python_sitelib}/shoal_server
%{_bindir}/shoal-server
%attr(0666,nobody,nobody) /var/log/shoal_server.log
%attr(0755,nobody,nobody) /var/www/shoal/scripts/shoal_wsgi.py
%config(noreplace) /etc/shoal/shoal_server.conf
%config(noreplace) /etc/logrotate.d/shoal-server
%config(noreplace) /etc/httpd/conf.d/shoal.conf

%post
python3 /var/www/shoal/scripts/setup_files.py
