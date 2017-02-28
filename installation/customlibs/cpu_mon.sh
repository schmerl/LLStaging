#!/bin/bash
nPid=$1;
nTimes=100; # change it as you wish
delay=0.1; # change it as you wish
strCalc=`top -d $delay -b -n $nTimes -p $nPid \
  |grep $nPid \
  |sed -r -e "s;\s\s*; ;g" -e "s;^ *;;" \
  |cut -d' ' -f9 \
  |tr '\n' '+' \
  |sed -r -e "s;(.*)[+]$;\1;" -e "s/.*/scale=2;(&)\/$nTimes/"`;
cpu_util=`echo "$strCalc" |bc -l`
echo $cpu_util
