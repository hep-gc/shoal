#!/usr/bin/env bash

# Script for producing the client RPMs and uploading to yum 
# repo and rebuilding the repo. These scripts are not 
# portable. Script derived from intructions hosted here:
#
# https://github.com/hep-gc/shoal/wiki/Building-RPMs-for-Shoal


cd ../shoal-client
python setup.py bdist_rpm
cd dist

if [ $# -eq "0" ]; then
  echo "Putting RPMs into production repo"
  cp *.noarch.rpm /var/www/html/repo/prod/sl/6X/x86_64/.
  cp *.src.rpm /var/www/html/repo/prod/sl/6X/x86_64/.
  createrepo --update /var/www/html/repo/prod/
elif [ "$1" == "--dev" ]; then
  echo "Putting RPMs into dev repo"
  cp *.noarch.rpm /var/www/html/repo/dev/sl/6X/x86_64/.
  cp *.src.rpm /var/www/html/repo/dev/sl/6X/x86_64/.
  createrepo --update /var/www/html/repo/dev/
else
  echo "Takes no arguments or --dev to build dev versions"
fi



