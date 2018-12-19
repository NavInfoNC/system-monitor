#!/usr/bin/python
import time
import psutil

class ProcessInfo:
    def __init__(self, processName):
        print(processName)
        self.__processName = processName
        self.__reset()
        for proc in psutil.process_iter():
            if proc.name() == processName:
                p = psutil.Process(proc.pid)
                self.__procList.append(p)

    def __reset(self):
        self.__cpuList = []
        self.__memList = []
        self.__procList = []

    def __caluCPU(self):
        usageRate = 0
        for p in self.__procList:
            usageRate += p.cpu_percent()
        return round(usageRate, 3)

    def __caluMemory(self):
        usageRate = 0
        for p in self.__procList:
            usageRate += p.memory_percent()
        return round(usageRate, 2)

    def start(self):
        if not self.__procList:
            return False
        self.__cpuList.append(self.__caluCPU())
        self.__memList.append(self.__caluMemory())

    def stop(self):
        resultDict = {}
        resultDict.setdefault("cpu", self.__cpuList)
        resultDict.setdefault("mem", self.__memList)
        return resultDict

