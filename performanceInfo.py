#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright (C)2018 NavInfo Co.,Ltd. All right reserved.

# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at

#     http://www.apache.org/licenses/LICENSE-2.0

# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import time
import psutil
import threading
import platform
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
        self.__allCpuPercentList.append(self.__allCpuPercent())
        self.__cpuPercentList.append(self.__cpuPercentSum())
        self.__memPercentList.append(self.__memPercent())
        self.__usedMemList.append(self.__usedMem())
        self.__freeMemList.append(self.__freeMem())
        self.__ioReadBytesList.append(self.__ioReadBytes())
        self.__ioWriteBytesList.append(self.__ioWriteBytes())
        self.__ioReadCountList.append(self.__ioReadCount())
        self.__ioWriteCountList.append(self.__ioWriteCount())

    def stop(self):
        ioDict = {}
        ioDict["readSize"] = self.__ioReadBytesList
        ioDict["writeSize"] = self.__ioWriteBytesList
        ioDict["readCount"] = self.__ioReadCountList
        ioDict["writeCount"] = self.__ioWriteCountList

        memDict = {}
        memDict["percent"] = self.__memPercentList
        memDict["used"] = self.__usedMemList
        memDict["free"] = self.__freeMemList
        memDict["total"] = round(toGB(psutil.virtual_memory().total), 3)

        cpuDict = {}
        cpuDict["coreNum"] = self.__core_num
        cpuDict["percent"] = self.__cpuPercentList
        cpuDict["corePercent"] = self.__allCpuPercentList

        cpuInfo = g_sysInfoCollector.getCpuInfo()
        cpuDict["model"] = cpuInfo.get("Model name", "Unknown")
        cpuDict["MHz"] = cpuInfo.get("CPU MHz", "Unknown")
        cpuDict["architecture"] = cpuInfo.get("Architecture", "Unknown")

        diskList = []
        for part in psutil.disk_partitions():
            mountPoint = part.mountpoint
            diskUsage = psutil.disk_usage(mountPoint)
            diskUsageDict = {}
            diskUsageDict["total"] = round(toGB(diskUsage.total), 3)
            diskUsageDict["percent"] = diskUsage.percent
            diskUsageDict["mountPoint"] = mountPoint
            diskUsageDict["device"] = part.device
            diskList.append(diskUsageDict)

        platformDict = {}
        platformDict["version"] = platform.version()
        platformDict["hostname"] = platform.node()
        platformDict["system"] = platform.system()
        platformDict["release"] = platform.release()
        platformDict["distribution"] = ''.join(platform.linux_distribution())

        resultDict = {}
        resultDict["cpu"] = cpuDict
        resultDict["memory"] = memDict
        resultDict["io"] = ioDict
        resultDict["disk"] = diskList
        resultDict["platform"] = platformDict

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
