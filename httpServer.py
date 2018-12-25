#!/usr/bin/python
from performanceInfo import PerformanceInfo
from flup.server.fcgi import WSGIServer
from taskQueue import TaskQueue
from threading import Thread
from cgi import parse_qs
import threading
import platform
import psutil
import json
import time
from sysInfoCollector import g_sysInfoCollector

def webapp(environ, start_response):
    method = environ.get('REQUEST_METHOD')
    content = "404 not found"
    if method == 'GET':
        response = {}
        query = parse_qs(environ.get('QUERY_STRING'))
        path = environ.get('PATH_INFO')
        print("method:%s, query:%s, path:%s" %(method, query, path))
        if path.startswith("/performance/start_collecting") and query:
            task = {}
            duration = query.get('duration')
            interval = query.get('interval')
            hash = query.get('hash')
            server = query.get('server')
            if duration and interval and hash:
                serverName = None
                if server:
                    serverName = server[0]
                response.setdefault("result", "succeeded")
                ts = time.time()
                task.setdefault('startTimestamp', ts)
                task.setdefault('stopTimestamp', ts + int(duration[0]))
                task.setdefault('duration', int(duration[0]))
                task.setdefault('interval', int(interval[0]))
                task.setdefault('server', serverName)
                task.setdefault('sysInfoCollector', g_sysInfoCollector)
                task.setdefault('hash', hash[0])
                g_tasksQueue.addTask(task)
            else:
                response.setdefault("result", "failed")
        elif path.startswith("/performance/stop_collecting") and query:
            hash = query.get('hash')[0]
            task = g_tasksQueue.getTaskBySha(hash)
            if task:
                taskResult = task.get('response')
                result = "failed"
                if taskResult:
                    result = "succeeded"
                    response.update(taskResult)
                response.setdefault("result", result)
            else:
                response.setdefault("result", "failed")
        elif path.startswith("/performance/real_time"):
            p = PerformanceInfo(None)
            response.setdefault("result", "succeeded")
            response.setdefault("system", p.instantData())
        else:
            start_response('404 NOT FOUND', [('Content-Type', 'application/json')])
            return content

    content = json.dumps(response, sort_keys=True, indent=4, separators=(',', ':'))
    start_response('200 OK', [('Content-Type', 'application/json')])
    return content

class serverThread(threading.Thread):
    def __init__(self, name, loop, stop):
        threading.Thread.__init__(self)
        self.name = name
        self.loop = loop
        self.stop = stop

    def run(self):
        self.loop()

    def stop(self):
        self.stop()


g_rLock = threading.RLock()
g_tasksQueue = TaskQueue(10, g_rLock)

if __name__ == '__main__':
    print(platform.python_version())
    sysInfoThread = serverThread("sysInfo-thread", g_sysInfoCollector.loop, g_sysInfoCollector.stop)
    sysInfoThread.start()
    taskThread = serverThread("tasks-thread", g_tasksQueue.loop, g_tasksQueue.stop)
    taskThread.start()
    WSGIServer(webapp, bindAddress='/etc/ncserver/system_monitor/system_monitor.sock', umask=0000).run()
    taskThread.stop()
    sysInfoThread.stop()
