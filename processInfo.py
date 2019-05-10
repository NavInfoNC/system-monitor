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
        self.__cpuPercentList = []
        self.__memPercentList = []
        self.__procList = []

    def __cpuPercent(self):
        usageRate = 0
        for p in self.__procList:
            usageRate += p.cpu_percent()
        return round(usageRate, 3)

    def __memPercent(self):
        usageRate = 0
        for p in self.__procList:
            usageRate += p.memory_percent()
        return round(usageRate, 2)

    def start(self):
        if not self.__procList:
            return False
        self.__cpuPercentList.append(self.__cpuPercent())
        self.__memPercentList.append(self.__memPercent())

    def stop(self):
        resultDict = {}
        resultDict.setdefault("cpu", self.__cpuPercentList)
        resultDict.setdefault("mem", self.__memPercentList)
        return resultDict

