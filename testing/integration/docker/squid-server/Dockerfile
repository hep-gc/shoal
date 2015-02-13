# Sets up a squid server with the shoal agent running
FROM centos
MAINTAINER Andre Charbonneau <Andre.Charbonneau@ssc-spc.gc.ca>

# Apply latest updates
RUN yum -y update; yum clean all


# Install epel repo
RUN yum install -y epel-release

# Install some useful tools
RUN yum install -y vim

# Install squid server
RUN yum install -y squid

# Configure squid server and check the configuration.
# (nothing to do for now)

# Install shoal prerequisites
RUN yum install -y git gcc python-setuptools python-netifaces python-devel
RUN easy_install pika


# Install shoal agent
RUN mkdir -p /tmp/work
WORKDIR /tmp/work
RUN git clone https://github.com/hep-gc/shoal.git
WORKDIR /tmp/work/shoal/shoal-agent
RUN python ./setup.py install

# Configure shoal agent
RUN sed -i 's/amqp_server_url = localhost/amqp_server_url = shoal-server/g' /etc/shoal/shoal_agent.conf
RUN sed -i 's/external_ip = /external_ip = xxx.xxx.xxx.xxx/g' /etc/shoal/shoal_agent.conf


# Start squid server and shoal agent
CMD /usr/sbin/squid ; sleep 5; /tmp/work/shoal/shoal-agent/shoal-agent
