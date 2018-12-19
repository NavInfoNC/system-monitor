#!/usr/bin/python
#from BaseHTTPServer import BaseHTTPRequestHandler,HTTPServer
from flup.server.fcgi import WSGIServer
from taskQueue import TaskQueue
from threading import Thread
from cgi import parse_qs
import threading
import platform
import psutil
import json
import time

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
            sha = query.get('sha')
            server = query.get('server')
            print("%s,%s,%s,%s" % (server, duration, interval, sha))
            if duration and interval and sha and server:
                response.setdefault("result", "success")
                ts = time.time()
                task.setdefault('startTimestamp', ts)
                task.setdefault('stopTimestamp', ts + int(duration[0]))
                task.setdefault('duration', int(duration[0]))
                task.setdefault('interval', int(interval[0]))
                task.setdefault('server', server[0])
                task.setdefault('sha', sha[0])
                g_tasksQueue.addTask(task)
            else:
                response.setdefault("result", "failure")
            content = json.dumps(response, sort_keys=True, indent=4, separators=(',', ':'))
        elif path.startswith("/performance/stop_collecting") and query:
            sha = query.get('sha')[0]
            task = g_tasksQueue.getTaskBySha(sha)
            if task:
                taskResult = task.get('response')
                result = "failure"
                if taskResult:
                    result = "success"
                response.setdefault("result", result)
                response.setdefault("log", taskResult)
            else:
                response.setdefault("result", "failure")

            content = json.dumps(response, sort_keys=True, indent=4, separators=(',', ':'))
        else:
            start_response('404 NOT FOUND', [('Content-Type', 'text/html')])
            return content

    start_response('200 OK', [('Content-Type', 'text/html')])
    return content

class serverThread(threading.Thread):
    def __init__(self, name, loop, stop):
        threading.Thread.__init__(self)
        self.name = name
        self.loop = loop
        self.stop = stop

    def run(self):
        #print "Starting " + self.name
        self.loop()

    def stop(self):
        self.stop()


g_rLock = threading.RLock()
g_tasksQueue = TaskQueue(10, g_rLock)

if __name__ == '__main__':
    print(platform.python_version())
    taskThread = serverThread("tasks-thread", g_tasksQueue.loop, g_tasksQueue.stop)
    taskThread.start()
    WSGIServer(webapp, bindAddress='/tmp/zhaogq.sock', umask=0000).run()
    taskThread.stop()
