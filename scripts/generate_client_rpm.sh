#!/bin/bash

#
#Author: Colson Driemel <colsond@uvic.ca>
#

#in the future these arguments should be updated to use flags instead

#This script takes 0, 1 or 2 arguments
#With zero arguments:
#It assumes you are running from the script folder of a github checkout of
#shoal. It will attempt to set the shoal directory relative to that location.
#It also currently defaults to the shoal-agent-centos.spec file.
#
#With one argument:
#It assumes you are passing in the spec file that you would like to generate
#the rpm with. It assumes this spec file is in the shoal-agent folder of the
#github checkout.
#
#With two arguments:
#It assumes you are passing in a spec file and the shoal directory in that
#order. It still assumes the spec file is placed in the shoal-agent folder
#of the github checkout.



#check for arguments and if there are none attmept to contextulize
#
if [ $# -eq 0 ]
then
	echo "Setting shoal_dir to: $SHOAL_DIR"
	cd ..
	SHOAL_DIR=$PWD
	SPEC_DIR=$SHOAL_DIR/shoal-client/specs
	SPEC_FILE=shoal-client.spec
elif [ $# -eq 1 ]
then
	cd ..
	echo "Setting shoal_dir to: $PWD"
	SHOAL_DIR=$PWD
	echo "Setting spec_file to: $1"
	SPEC_DIR=$SHOAL_DIR/shoal-client/specs
    SPEC_FILE=$1
elif [ $# -eq 2 ]
then
    echo "Setting shoal_dir to $2" 
    SHOAL_DIR="$2"
    echo "Setting spec_file to: $1"
    SPEC_DIR=$SHOAL_DIR/shoal-client/specs
    SPEC_FILE=$1
fi

echo "Building Client source distribution."
cd $SHOAL_DIR/shoal-client/
python ./setup.py sdist

echo "Copying spec and tarball."
cp $SPEC_DIR/$SPEC_FILE ~/rpmbuild/SPECS
cp $SHOAL_DIR/shoal-client/dist/shoal-client**.tar.gz ~/rpmbuild/SOURCES

echo "Building agent RPM"
rpmbuild -ba ~/rpmbuild/SPECS/shoal-client.spec
