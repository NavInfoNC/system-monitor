#!/usr/bin/python
#    Copyright (C)2018 NavInfo Co.,Ltd. All right reserved.

#    Licensed under the Apache License, Version 2.0 (the "License");
#    you may not use this file except in compliance with the License.
#    You may obtain a copy of the License at

#        http://www.apache.org/licenses/LICENSE-2.0

#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS,
#    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#    See the License for the specific language governing permissions and
#    limitations under the License.

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
