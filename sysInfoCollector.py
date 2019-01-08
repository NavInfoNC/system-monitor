#!/usr/bin/python
import os
import time
import psutil
from threading import Timer

class SystemInfoCollector:
    def __init__(self, interval):
        assert(interval > 0)
        self.__interval = interval
        self.__cpu_info = {}
        self.__reset()

    def __parseCpuInfo(self):
        p = os.popen("lscpu")
        line = p.readline()
        while(line):
            info = line.split(":")
            key = info[0]
            value = info[1].strip()
            self.__cpu_info[key] = value
            line = p.readline()

    def __reset(self):
        self.__core_num = psutil.cpu_count(logical=True)
        self.__lastAllCpuPercent = []
        self.__parseCpuInfo()
        psutil.cpu_percent(percpu=True)

    def getCpuPercent(self):
        return sum(self.__lastAllCpuPercent) / self.__core_num

    def getAllCpuPercent(self):
        return self.__lastAllCpuPercent

    def getCpuInfo(self):
        return self.__cpu_info

    def loop(self, duration = 0):
        self.__running = True
        count = 0
        while(self.__running):
            self.__lastAllCpuPercent = psutil.cpu_percent(percpu=True)
            time.sleep(self.__interval)
            count += self.__interval
            if (duration > 0 and count * self.__interval >= duration):
                self.__running = False

    def stop(self):
        self.__running = False


g_sysInfoCollector = SystemInfoCollector(1)

if __name__ == '__main__':
    g_sysInfoCollector.loop(3)
    print(g_sysInfoCollector.getCpuPercent())
    print(g_sysInfoCollector.getAllCpuPercent())
    print(g_sysInfoCollector.getCpuInfo())
