#!/bin/bash

if [[ $HOSTNAME == 'wl-load-test' ]];then
	dst=/etc/ncserver/system-monitor
	mkdir -p $dst
elif [[ $HOSTNAME == 'wl-server-build' ]];then
	dst=$1@navicore.mapbar.com:/etc/ncserver/system-monitor
else
	echo "can't support auto deploy for your MACHINE"
	exit
fi

find $dir -iname "*.py" | xargs chmod +x > /dev/null 2>&1
rsync -avP *.py $dst
rsync -avP html/* $dst/html/

if [[ $HOSTNAME == 'wl-load-test' ]];then
	chgrp ncserver $dst/* > /dev/null 2>&1
fi
