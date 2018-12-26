#!/usr/bin/python
import time
import psutil
import threading
from sysInfoCollector import g_sysInfoCollector

def toMB(size):
    return float(size)/1024/1024

def toGB(size):
    return float(size)/1024/1024/1024

class PerformanceInfo:
    def __init__(self, processName):
        self.__reset()
        self.__isProcessCollector = False
        if processName:
            self.__isProcessCollector = True
            self.__processName = processName
            self.__procList = []
            for proc in psutil.process_iter():
                if proc.name() == processName:
                    p = psutil.Process(proc.pid)
                    self.__procList.append(p)

    def __reset(self):
        self.__core_num = psutil.cpu_count(logical=True)
        self.__cpuPercentList = []
        self.__memPercentList = []
        self.__usedMemList = []
        self.__freeMemList = []
        self.__ioReadBytesList = []
        self.__ioWriteBytesList = []
        self.__ioReadCountList = []
        self.__ioWriteCountList = []
        self.__allCpuPercentList = []

    def __cpuPercentSum(self):
        usageRate = 0
        if not self.__isProcessCollector:
            usageRate = g_sysInfoCollector.getCpuPercent()
        else:
            for p in self.__procList:
                usageRate += p.cpu_percent()
        return round(usageRate, 3)

    def __allCpuPercent(self):
        return g_sysInfoCollector.getAllCpuPercent()

    def __memPercent(self):
        usageRate = 0
        if not self.__isProcessCollector:
            usageRate = psutil.virtual_memory().percent
        else:
            for p in self.__procList:
                usageRate += p.memory_percent()
        return round(usageRate, 3)

    def __usedMem(self):
        usageRate = 0
        if not self.__isProcessCollector:
            usageRate = psutil.virtual_memory().used
        else:
            for p in self.__procList:
                usageRate += p.memory_info().vms
        return round(toGB(usageRate), 3)

    def __freeMem(self):
        usageRate = 0
        if not self.__isProcessCollector:
            usageRate = psutil.virtual_memory().free
        return round(toGB(usageRate), 3)

    def __ioReadBytes(self):
        usageRate = 0
        if not self.__isProcessCollector:
            usageRate = psutil.disk_io_counters().read_bytes
        else:
            for p in self.__procList:
                usageRate += p.io_counters().read_bytes
        return round(toMB(usageRate), 3)

    def __ioWriteBytes(self):
        usageRate = 0
        if not self.__isProcessCollector:
            usageRate = psutil.disk_io_counters().write_bytes
        else:
            for p in self.__procList:
                usageRate += p.io_counters().write_bytes
        return round(toMB(usageRate), 3)

    def __ioReadCount(self):
        usageRate = 0
        if not self.__isProcessCollector:
            usageRate = psutil.disk_io_counters().read_count
        else:
            for p in self.__procList:
                usageRate += p.io_counters().read_count
        return usageRate

    def __ioWriteCount(self):
        usageRate = 0
        if not self.__isProcessCollector:
            usageRate = psutil.disk_io_counters().write_count
        else:
            for p in self.__procList:
                usageRate += p.io_counters().write_count
        return usageRate

    def instantData(self):
        self.start()
        return self.stop()

    def start(self):
        self.__cpuPercentList.append(self.__cpuPercentSum())
        self.__memPercentList.append(self.__memPercent())
        self.__usedMemList.append(self.__usedMem())
        self.__freeMemList.append(self.__freeMem())
        self.__ioReadBytesList.append(self.__ioReadBytes())
        self.__ioWriteBytesList.append(self.__ioWriteBytes())
        self.__ioReadCountList.append(self.__ioReadCount())
        self.__ioWriteCountList.append(self.__ioWriteCount())
        self.__allCpuPercentList.append(self.__allCpuPercent())

    def stop(self):
        ioDict = {}
        ioDict.setdefault("readSize", self.__ioReadBytesList)
        ioDict.setdefault("writeSize", self.__ioWriteBytesList)
        ioDict.setdefault("readCount", self.__ioReadCountList)
        ioDict.setdefault("writeCount", self.__ioWriteCountList)

        memDict = {}
        memDict.setdefault("percent", self.__memPercentList)
        memDict.setdefault("used", self.__usedMemList)
        memDict.setdefault("free", self.__freeMemList)
        memDict.setdefault("total", round(toGB(psutil.virtual_memory().total), 3))

        cpuDict = {}
        cpuDict.setdefault("percent", self.__cpuPercentList)
        cpuDict.setdefault("coreNum", self.__core_num)
        #for i in range(self.__core_num):
        #    corePercentList = []
        #    for j in range(len(self.__allCpuPercentList)):
        #        corePercentList.append(self.__allCpuPercentList[j][i])
        #    cpuDict.setdefault("core" + str(i) + "Percent", corePercentList)
        cpuDict.setdefault("corePercent", self.__allCpuPercentList)

        resultDict = {}
        resultDict.setdefault("cpu", cpuDict)
        resultDict.setdefault("memory", memDict)
        resultDict.setdefault("io", ioDict)
        return resultDict

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

if __name__ == '__main__':
    sysInfoThread = serverThread("sysInfo-thread", g_sysInfoCollector.loop, g_sysInfoCollector.stop)
    sysInfoThread.start()
    time.sleep(1)

    p = PerformanceInfo(None)
    p.start()
    print(p.stop())

    time.sleep(5)
    p = PerformanceInfo("java")
    p.start()
    print(p.stop())

    time.sleep(10)
    sysInfoThread.stop()
