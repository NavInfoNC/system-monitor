#!/usr/bin/python
from BaseHTTPServer import BaseHTTPRequestHandler,HTTPServer
from taskQueue import TaskQueue
from threading import Thread
import threading
import urlparse
import psutil
import json
import time

PORT_NUMBER = 9010

class httpCallback(BaseHTTPRequestHandler):
    def do_GET(self):
        response = {}
        parseResult = urlparse.urlparse(self.path)
        query = urlparse.parse_qs(parseResult.query)
        if self.path.startswith("/performance/start_collecting"):
            task = {}
            duration = query.get('duration')[0]
            interval = query.get('interval')[0]
            sha = query.get('sha')[0]
            server = query.get('server')[0]
            print("%s,%s,%s,%s" % (server, duration, interval, sha))
            if duration and interval and interval and server:
                response.setdefault("result", "success")
                ts = time.time()
                task.setdefault('startTimestamp', ts)
                task.setdefault('stopTimestamp', ts + int(duration))
                task.setdefault('duration', int(duration))
                task.setdefault('interval', int(interval))
                task.setdefault('server', server)
                task.setdefault('sha', sha)
                g_tasksQueue.addTask(task)
            else:
                response.setdefault("result", "failure")

            self.send_response(200)
            content = json.dumps(response, sort_keys=True, indent=4, separators=(',', ':'))
        elif self.path.startswith("/performance/stop_collecting"):
            print(self.path)
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

            self.send_response(200)
            content = json.dumps(response, sort_keys=True, indent=4, separators=(',', ':'))
        else:
            self.send_response(404)
            self.end_headers()
            return

        self.send_header('Content-type', 'text/plain')
        self.send_header('Content-length', "%d" % len(content))
        self.end_headers()
        self.wfile.write(content)
        return


class HttpServerThread(Thread):
    def __init__(self, protocol = "http"):
        ''' http server'''
        Thread.__init__(self)
        self.protocol = protocol
        self.server = None
        self.stopped = False
        #https://docs.python.org/2/library/threading.html#thread-objects
        #The entire Python program exits when no alive non-daemon threads are left.
        self.setDaemon(True)

    def run(self):
        if self.protocol == "https":
            print 'Started https server on port ' , HTTPS_PORT_NUMBER
            server = HTTPServer(('', HTTPS_PORT_NUMBER), httpCallback)
            #http://www.mynewsdesk.com/devcorner/blog_posts/a-simple-https-server-for-development-28395
            #openssl req -new -x509 -keyout server.pem -out server.pem -days 365 -nodes
            server.socket = ssl.wrap_socket(server.socket, server_side=True, certfile='server.pem')
        else:
            print 'Started http server on port ' , PORT_NUMBER
            server = HTTPServer(('', PORT_NUMBER), httpCallback)

        self.server = server
        while not self.stopped:
            self.server.handle_request()

    def stop(self):
        self.stopped = True
        self.server.server_close()
        self.server.socket.close()

class serverThread(threading.Thread):
    def __init__(self, name, loop, stop):
        threading.Thread.__init__(self)
        self.name = name
        self.loop = loop
        self.stop = stop

    def run(self):
        print "Starting " + self.name
        self.loop()

    def stop(self):
        self.stop()


g_rLock = threading.RLock()
g_tasksQueue = TaskQueue(10, g_rLock)

if __name__ == '__main__':
    taskThread = serverThread("tasks-thread", g_tasksQueue.loop, g_tasksQueue.stop)
    taskThread.start()
    http = HttpServerThread()
    http.start()
    try:
        while True:
            time.sleep(2)
    except KeyboardInterrupt:
        print '^C received, shutting down the web server'
        http.stop()
        taskThread.stop()
