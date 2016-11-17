#!/bin/bash

source /etc/profile

if [ $# -lt 1 ];then
    echo "no enguht parment"
    exit -1
fi


/usr/bin/python /home/fengxuan/shadowscript/reduce.py -z fuck01 -m async -p $1 >> /tmp/reduce.log 2>&1 &