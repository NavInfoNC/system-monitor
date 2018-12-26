#!/bin/bash

if [[ $HOSTNAME == 'wl-load-test' ]];then
	dst=/etc/ncserver/system-monitor
else
	dst=$1@navicore.mapbar.com:/etc/ncserver/system-monitor
fi

if [[ ! -d $dst ]];then
    mkdir -p $dst
fi
echo dst: $dst

find $dir -iname "*.py" | xargs chmod +x > /dev/null 2>&1

rsync -avP *.py $dst
