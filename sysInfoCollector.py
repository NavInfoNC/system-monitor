#!/usr/bin/python
import time
import psutil

class SystemInfoCollector:
    def __init__(self, interval):
        self.__interval = interval
        self.__reset()

    def __reset(self):
        self.__core_num = psutil.cpu_count(logical=True)
        self.__lastAllCpuPercent = []
        psutil.cpu_percent(percpu=True)

    def getCpuPercent(self):
        return sum(self.__lastAllCpuPercent) / self.__core_num

    def getAllCpuPercent(self):
        return self.__lastAllCpuPercent

    def loop(self):
        self.__running = True
        while(self.__running):
            self.__lastAllCpuPercent = psutil.cpu_percent(percpu=True)
#            print(self.__lastAllCpuPercent)
            time.sleep(self.__interval)

    def stop(self):
        self.__running = False


g_sysInfoCollector = SystemInfoCollector(1)

