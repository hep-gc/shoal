# Sets up a shoal server (which also runs the rabbitmq server)
FROM ubuntu
MAINTAINER Andre Charbonneau <Andre.Charbonneau@ssc-spc.gc.ca>
ENV DEBIAN_FRONTEND noninteractive

# Add the application resources URL
RUN echo "deb http://archive.ubuntu.com/ubuntu/ $(lsb_release -sc) main universe" >> /etc/apt/sources.list

# Update the sources list
RUN apt-get update -y

# Install basic applications
RUN apt-get install -y tar git curl vim nano wget dialog net-tools build-essential

# Install shoal server prerequisites
RUN apt-get install -y gcc 
RUN apt-get install -y python python-dev python-distribute python-pip python-pika

# Install rabbitmq server
RUN apt-get install -y rabbitmq-server

# Install shoal server
RUN mkdir -p /tmp/work
WORKDIR /tmp/work
RUN git clone https://github.com/hep-gc/shoal.git
WORKDIR /tmp/work/shoal/shoal-server

# Configure shoal server
RUN sed -i 's/amqp_server_url = shoal.heprc.uvic.ca/amqp_server_url = localhost/g' /tmp/work/shoal/shoal-server/shoal_server.conf

RUN python ./setup.py install

# Install httpd
# RUN apt-get install -y apache2

# Expose ports
EXPOSE 8080

# Start rabbitmq and shoal server
WORKDIR /root
CMD /etc/init.d/rabbitmq-server start && sleep 5 && /tmp/work/shoal/shoal-server/shoal-server
