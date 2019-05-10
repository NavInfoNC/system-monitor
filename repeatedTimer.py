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

from time import sleep
from threading import Timer
from performanceInfo import PerformanceInfo

class RepeatedTimer:
    def __init__(self, interval, *args, **kwargs):
        self.__timer     = None
        self.__interval   = interval
        self.__procName   = args[0]
        self.__procInfo   = PerformanceInfo(self.__procName)
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
    print("starting...")
    rt1 = RepeatedTimer(1, "server_manager")
    rt2 = RepeatedTimer(2, "java")
    rt3 = RepeatedTimer(1, None)
    try:
        sleep(5)
    finally:
        result1 = rt1.stop()
        result2 = rt2.stop()
        result3 = rt3.stop()
        print(result1)
        print(result2)
        print(result3)
