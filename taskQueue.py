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

    def getTaskBySha(self, sha):
        task = {}
        if not sha:
            return task
        self.__rLock.acquire()
        for index in range(self.__queue.qsize()):
            task = self.__queue.get()
            taskSha = task.get('sha')
            if sha == taskSha:
                break
            self.__queue.put(taskSha)
        timer = task.get("timer")
        task.setdefault("response", timer.stop())
        self.__rLock.release()
        return task

    def addTask(self, task):
        self.__rLock.acquire()
        timer = RepeatedTimer(task.get('interval'), task.get('server'))
        task.setdefault('timer', timer)
        self.__queue.put(task)
        self.__rLock.release()

    def __filterExpiredTasks(self):
        if self.empty():
            return
        self.__rLock.acquire()
        queueSize = self.__queue.qsize()
        for index in range(queueSize):
            task = self.__queue.get(False)
            stopTimestamp = task.get("stopTimestamp")
            if stopTimestamp + g_timeout < time.time():
                print('remove invalid task:%s' %(task.get('sha')))
                continue
            elif stopTimestamp + g_timeout//5 < time.time() and not task.get("response"):
                timer = task.get("timer")
                task.setdefault("response", timer.stop())
                print('response:%s' %(task.get('response')))
                self.__queue.put(task)
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
    task.setdefault('sha', 123)
    tasksQueue.addTask(task)
    tasksQueue.loop()

