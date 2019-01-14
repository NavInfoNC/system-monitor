#!/bin/bash

if [[ $HOSTNAME == 'wl-load-test' ]];then
	dst=/etc/ncserver/system-monitor
	mkdir -p $dst
elif [[ $HOSTNAME == 'wl-server-build' ]];then
	dst=$USER@navicore.mapbar.com:/etc/ncserver/system-monitor
else
	echo "can't support auto deploy for your MACHINE"
	exit
fi


find . -iname "*.sh" | xargs chmod +x > /dev/null 2>&1
find . -iname "*.py" | xargs chmod +x > /dev/null 2>&1
find . -iname "*.sh" | xargs -i dos2unix -n {} {} > /dev/null 2>&1

rsync -avP *.py restart.sh html $dst
