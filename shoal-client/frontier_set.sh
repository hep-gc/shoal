#!/bin/bash

outputstr=`shoal-client -f`
if [[ $? -eq 0 ]] ; then FRONTIER_SERVER=$outputstr ; fi 
echo $FRONTIER_SERVER
