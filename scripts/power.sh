#!/bin/bash

if [ "$1" == "on" ]; then
   CURRENT=1
elif [ "$1" == "off" ]; then
   CURRENT=0
elif [ "$1" == "toggle" ]; then
   CURRENT=$(gpioget --as-is --numeric GPIO23)
elif [ "$1" == "status" ]; then
   CURRENT=$(gpioget --as-is --numeric GPIO23)
   if [ "$CURRENT" == "0" ]; then
	   echo on
   else 
	   echo off
   fi
   exit 0
else 
   echo "Usage: $0 [on|off|toggle|status]"
   exit 0
fi
echo $CURRENT
if [ $CURRENT == "0" ]; then
  echo "Turn off"
  gpioset -t0 GPIO23=1
  $(dirname $0)/led.sh off
else
  echo "Turn on"
  gpioset -t0 GPIO23=0
  $(dirname $0)/led.sh on
fi
