#!/usr/bin/python
import Queue
import time
import threading
from repeatedTimer import RepeatedTimer

g_timeout = 1 * 5

class TaskQueue:
    def __init__(self, size, rLock):
        self.__queue = Queue.Queue(size)
        self.__running = False
        self.__rLock = rLock

    def empty(self):
        self.__rLock.acquire()
        result = self.__queue.empty()
        self.__rLock.release()
        return result

    def getTaskBySha(self, hash):
        task = {}
        if not hash:
            return task
        self.__rLock.acquire()
        for index in range(self.__queue.qsize()):
            task = self.__queue.get()
            taskSha = task.get('hash')
            if hash == taskSha:
                break
            self.__queue.put(taskSha)
        sysInfoTimer = task.get("sysInfoTimer")
        if sysInfoTimer:
            task.setdefault("response", sysInfoTimer.stop())
        self.__rLock.release()
        return task

    def addTask(self, task):
        self.__rLock.acquire()
        serverName = task.get('server')
        sysInfoTimer = RepeatedTimer(task.get('interval'), serverName)
        task.setdefault('sysInfoTimer', sysInfoTimer)
        self.__queue.put(task)
        self.__rLock.release()

    def __filterExpiredTasks(self):
        if self.empty():
            return
        self.__rLock.acquire()
        queueSize = self.__queue.qsize()
        for index in range(queueSize):
            task = []
            task = self.__queue.get(False)
            if not task:
                continue
            stopTimestamp = task.get("stopTimestamp")
            response = task.get("response")
            if stopTimestamp + g_timeout < time.time():
                print('remove invalid task:%s' %(task.get('hash')))
                continue
            elif stopTimestamp + g_timeout//5 < time.time() and not response:
                sysInfoTimer = task.get("sysInfoTimer")
                task.setdefault("response", sysInfoTimer.stop())
            else:
                self.__queue.put(task)
        self.__rLock.release()

    def loop(self):
        self.__running = True
        while(self.__running):
            time.sleep(1)
            self.__filterExpiredTasks()

    def stop(self):
        self.__running = False

if __name__ == '__main__':
    rLock = threading.RLock()
    tasksQueue = TaskQueue(10, rLock)

    t = threading.Timer(8, tasksQueue.stop);
    t.start()

    task = {}
    currentTime = time.time()
    task.setdefault('startTimestamp', currentTime)
    task.setdefault('stopTimestamp', currentTime + 5)
    task.setdefault('duration', 5)
    task.setdefault('interval', 1)
    task.setdefault('hash', 123)
    task.setdefault('server', None)
    tasksQueue.addTask(task)
    tasksQueue.loop()

