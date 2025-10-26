#!/bin/bash

DIRECTION=/sys/class/gpio/gpio24/direction
VALUE=/sys/class/gpio/gpio24/value
EXPORT=/sys/class/gpio/export
if [ ! -f "$DIRECTION" ]; then
   echo 24 > "$EXPORT"
   sleep 0.1
   echo out > "$DIRECTION"
   echo 1 > "$VALUE" 
fi

if [ "$1" == "on" ]; then
    CURRENT=0
elif [ "$1" == "off" ]; then
    CURRENT=1
else
    CURRENT=$(cat ${VALUE})
fi
echo $CURRENT
if [ $CURRENT == "0" ]; then
   echo "SETTING ONE"
   echo 1 > "$VALUE"
else
   echo "SETTING ZERO"
   echo 0 > "$VALUE"
fi
