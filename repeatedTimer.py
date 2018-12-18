#!/usr/bin/python
from time import sleep
from threading import Timer
from processInfo import ProcessInfo

class RepeatedTimer:
    def __init__(self, interval, *args, **kwargs):
        self.__timer     = None
        self.__interval   = interval
        self.__procName   = args[0]
        self.__procInfo   = ProcessInfo(self.__procName)
        self.__procStart  = self.__procInfo.start
        self.__procStop   = self.__procInfo.stop
        self.__kwargs     = kwargs
        self.__is_running = False
        self.start()

    def __run(self):
        self.__is_running = False
        self.start()
        self.__procStart()

    def start(self):
        if not self.__is_running:
            self.__timer = Timer(self.__interval, self.__run)
            self.__timer.start()
            self.__is_running = True

    def stop(self):
        self.__timer.cancel()
        self.__is_running = False
        return self.__procStop()

if __name__ == '__main__':
    print "starting..."
    rt = RepeatedTimer(1, "server_manager")
    rt1 = RepeatedTimer(2, "java")
    try:
        sleep(5)
    finally:
        result1 = rt.stop()
        result2 = rt1.stop()
        print(result1, result2)
