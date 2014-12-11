# Sets up a squid server with the shoal agent running
FROM centos
MAINTAINER Andre Charbonneau <Andre.Charbonneau@ssc-spc.gc.ca>

# Apply latest updates
RUN yum update -y

# Install epel repo
RUN yum install -y epel-release

# Install squid server
RUN yum install -y squid

# Install shoal prerequisites
RUN yum install -y python-setuptools python-netifaces python-devel
RUN easy_install pika
RUN yum install -y git gcc


# Install shoal agent
RUN echo "Installing shoal agent..."
RUN mkdir -p /tmp/work
WORKDIR /tmp/work
RUN git clone https://github.com/hep-gc/shoal.git
WORKDIR /tmp/work/shoal/shoal-agent
RUN python ./setup.py install

