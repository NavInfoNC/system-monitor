#!/bin/bash

if [[ $HOSTNAME == 'wl-server-build' ]];then
	dst=$USER@navicore.mapbar.com:/etc/ncserver/system-monitor
else
	dst=/etc/ncserver/system-monitor
	mkdir -p $dst
fi


find . -iname "*.sh" | xargs chmod +x > /dev/null 2>&1
find . -iname "*.py" | xargs chmod +x > /dev/null 2>&1
find . -iname "*.sh" | xargs -i dos2unix -n {} {} > /dev/null 2>&1

rsync -avP *.py restart.sh html $dst
