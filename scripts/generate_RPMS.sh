#!/bin/bash

#A script to generate the rpm files for the shoal project
#Run the script with "all" argument to generate all, or provide the argument of which rpm you'd like to generate (server, client, agent)
#clone the repo first and make sure that if any shoal products are installed to delete the installed config files otherwise they wont be included in rpm
#set the version numbers in the spec files in /dist/

if [ -f /etc/shoal/shoal_server.conf ];
then
   echo "Shoal config file detected at /etc/shoal"
   echo "Please remove these files before constructing RPMS or they will not be included"
   exit
fi
if [ -f /etc/shoal/shoal_agent.conf ];
then
   echo "Shoal config file detected at /etc/shoal"
   echo "Please remove these files before constructing RPMS or they will not be included"
   exit
fi
if [ -f /etc/shoal/shoal_client.conf ];
then
   echo "Shoal config file detected at /etc/shoal"
   echo "Please remove these files before constructing RPMS or they will not be included"
   exit
fi

if [ $# -eq 0 ]
then
    echo "Please provide argurgments."
    echo "Usage: ./generate_RPMS.sh <OPTION> <SHOAL_PATH>"
    echo "Options:"
    echo "all: generate all RPMs"
    echo "agent: generate agent RPM"
    echo "client: generate client RPM"
    echo "server: generate server RPM"
    echo "If <SHOAL_PATH> not specified default will be set to parent of active directory"
    exit
    
elif [ $# -eq 1 ]
then
    echo "Setting shoal_dir to: $SHOAL_DIR"
    cd ..
    SHOAL_DIR=$PWD
    
elif [ $# -eq 2 ]
then
    echo "Setting shoal_dir to $2" 
    SHOAL_DIR="$2"
fi

if [ "$1" == "client" ];
then
    #client
    cd $SHOAL_DIR/shoal-client/
    python $SHOAL_DIR/shoal-client/setup.py bdist_rpm
    exit

elif [ "$1" == "agent" ];
then
    #agent
    cd $SHOAL_DIR/shoal-agent/
    python $SHOAL_DIR/shoal-agent/setup.py bdist_rpm

    mkdir -p $HOME/rpmbuild/{BUILD,RPMS,SOURCES,SPECS,SRPMS}
    cp $SHOAL_DIR/shoal-agent/dist/shoal-agent-*.tar.gz $HOME/rpmbuild/SOURCES/.
    rpmbuild -ba shoal-agent.spec
    exit

elif [ "$1" == "server" ];
then
    #server
    #If you have already installed shoal when you build the RPM the configuration files will not be included.
    #Remove them from the installation directory prior to building RPMs
    cd $SHOAL_DIR/shoal-server/
    python $SHOAL_DIR/shoal-server/setup.py bdist_rpm --requires="pygeoip >= 0.2.5,pika >= 0.9.11,web.py >= 0.3,python-requests >= 1.1.0,geoip2 >= 0.6.0, maxminddb >= 1.1.1, python-ipaddr >= 2.1.9"
    exit
elif [ "$1" == "all" ];
then
    #client
    cd $SHOAL_DIR/shoal-client/
    python $SHOAL_DIR/shoal-client/setup.py bdist_rpm

    #agent
    cd $SHOAL_DIR/shoal-agent/
    python $SHOAL_DIR/shoal-agent/setup.py bdist_rpm

    mkdir -p $HOME/rpmbuild/{BUILD,RPMS,SOURCES,SPECS,SRPMS}
    cp $SHOAL_DIR/shoal-agent/dist/shoal-agent-*.tar.gz $HOME/rpmbuild/SOURCES/.
    rpmbuild -ba shoal-agent.spec

    #server
    #If you have already installed shoal when you build the RPM the configuration files will not be included.
    #Remove them from the installation directory prior to building RPMs
    cd $SHOAL_DIR/shoal-server/
    python $SHOAL_DIR/shoal-server/setup.py bdist_rpm --requires="pygeoip >= 0.2.5,pika >= 0.9.11,web.py >= 0.3,python-requests >= 1.1.0,geoip2 >= 0.6.0, maxminddb >= 1.1.1, python-ipaddr >= 2.1.9"
    
else
    echo "Invalid command please try again."
    echo "---------------------------------------------------------------------------"
    echo "Please provide argurgments."
    echo "Usage: ./generate_RPMS.sh <OPTION> <SHOAL_PATH>"
    echo "Options:"
    echo "all:    generate all RPMs"
    echo "agent:  generate agent RPM"
    echo "client: generate client RPM"
    echo "server: generate server RPM"
    echo "If <SHOAL_PATH> not specified default will be set to parent of active directory"
fi

exit
