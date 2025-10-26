#!/bin/bash

DIRECTION=/sys/class/gpio/gpio23/direction
VALUE=/sys/class/gpio/gpio23/value
EXPORT=/sys/class/gpio/export
if [ ! -f "$DIRECTION" ]; then
  echo 23 > "$EXPORT"
  sleep 0.1
  echo out > "$DIRECTION"
  echo 1 > "$VALUE" # 1 means turned off
fi

if [ "$1" == "on" ]; then
   CURRENT=1
elif [ "$1" == "off" ]; then
   CURRENT=0
elif [ "$1" == "toggle" ]; then
   CURRENT=$(cat ${VALUE})
elif [ "$1" == "status" ]; then
   cat ${VALUE}
   exit 0
else 
   echo "Usage: $0 [on|off|toggle|status]"
   exit 0
fi
echo $CURRENT
if [ $CURRENT == "0" ]; then
  echo "SETTING ZERO"
  echo 1 > "$VALUE"
  $(dirname $0)/led.sh off

else
  echo "SETTING ONE"
  echo 0 > "$VALUE"
  $(dirname $0)/led.sh on
fi


