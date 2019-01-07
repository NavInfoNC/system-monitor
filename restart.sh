#!/bin/bash
cd `dirname $(readlink -f $0)`

pids=`ps aux | grep -v grep | grep "httpServer.py"`
if [[ $? == 0 ]];then
	for p in $pids;do
		kill -9 $p
	done
fi

chgrp ncserver -R . > /dev/null 2>&1
chmod ug+rw    -R . > /dev/null 2>&1

nohup python httpServer.py &