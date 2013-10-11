#!/bin/bash

TMP="`pwd`/configShoalAgent.py"
eval $TMP
service shoal_agent start
