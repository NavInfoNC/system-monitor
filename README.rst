System info agent 
=================

本工程用于采集服务器性能数据。

Depends
===

linux: lscpu

python-lib: psutil, flup1.0

API
===

前缀 PREFIX 为::

   http://<hostname>/<sock_url_prefix>

如果没有特殊说明，都是GET请求。

发起服务器性能统计请求
----------------------

Request::

    GET /performance/start_collecting?hash=<hash>&duration=<duration>&interval=<interval>&server=<server>

注：
    <hash>:在请求端通过MD5("URL_PREFFIX;PID;CurrentTimestamp")计算出来
    <duration>:采集持续时长
    <interval>:采集间隔
    <server>:采集指定服务的性能信息

Response:

.. code-block:: jss
   
    {
        "result":"succeeded/failed",
    }

处理逻辑:

    如果query不完整，则Response中的result字段为failed，否则返回succeed

停止服务器性能统计请求
----------------------

Request::

    GET /performance/stop_collecting?hash=<hash>

Response:

.. code-block:: jss
   
    {
        "result":"succeeded/failed",
        "system":PerformanceInfo,
        "process":PerformanceInfo
    }

    PerformanceInfo = 
    {
        "cpu":CpuInfo
        "memory":MemoryInfo
        "io":IoInfo
        "disk":DiskInfo[]
        "platform":PlatformInfo
    }

    CpuInfo = 
    {
        "percent":[],
        "coreNum":
        "corePercent":[[],[],[]]
        "architecture":
        "model":
        "MHz":
    }

    MemoryInfo = 
    {
        "percent":[],
        "used":[],
        "total":totalSize,
    }

    IoInfo =
    {
        "readSize":[],
        "writeSize":[],
        "readCount":[],
        "writeCount":[],
    }

    PlatformInfo =
    {
        "version":version,
        "hostname":hostname,
        "system":system,
        "release":release
        "distribution":distribution
    }

    DiskInfo =
    {
        "mountPoint":mountPoint
        "device":device
        "total":total,
        "used":used
    }

处理逻辑:

    如果在发起服务器性能请求时，没有server名称，代理将只采集system的性能指标
    request中的散列与代理端存储的散列值一致，则返回代理中采集的性能指标，result为succeed，否则为failed

实时采集服务器性能数据
----------------------

Request::

    GET /performance/real_time

Response:

.. code-block:: jss

    {
        "result":"succeeded/failed",
        "system":PerformanceInfo,
    }

