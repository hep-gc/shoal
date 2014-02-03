#!/bin/bash

TMP="~/shoal/phantomSensors/configShoalAgent.py"
SHOAL_AGENT_STATUS="`service shoal_agent status`";
if grep -q "shoal_agent is running" <<<$TESTVAR; then
exit 0
else
eval $TMP
  shoal-agent &
fi
