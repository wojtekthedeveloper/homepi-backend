#!/bin/bash

if [ "$1" == "on" ]; then
    gpioset -t0 GPIO24=0
elif [ "$1" == "off" ]; then
    gpioset -t0 GPIO24=1
fi
