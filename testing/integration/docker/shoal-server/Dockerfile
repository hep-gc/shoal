# Sets up a shoal server (which also runs the rabbitmq server)
FROM centos
MAINTAINER Andre Charbonneau <Andre.Charbonneau@ssc-spc.gc.ca>

# Apply latest updates
RUN yum -y update; yum clean all


# Install epel repo
RUN yum install -y epel-release

# Install some useful tools
RUN yum install -y vim

# Install shoal server prerequisites
RUN yum install -y git gcc python-setuptools python-netifaces python-devel
RUN easy_install pika

# Install rabbitmq server
RUN yum install -y rabbitmq-server


# Install shoal server
RUN mkdir -p /tmp/work
WORKDIR /tmp/work
RUN git clone https://github.com/hep-gc/shoal.git
WORKDIR /tmp/work/shoal/shoal-server
RUN python ./setup.py install

# Configure shoal server
RUN sed -i 's/amqp_server_url = shoal.heprc.uvic.ca/amqp_server_url = localhost/g' /etc/shoal/shoal_server.conf


# Start rabbitmq and shoal server
CMD rabbitmq-server -detached; sleep 5; /tmp/work/shoal/shoal-server/shoal-server
