System info agent 
=================

本工程用于采集服务器性能数据。

API
===

前缀 PREFIX 为::

   http://<hostname>/<sock_url_prefix>

如果没有特殊说明，都是GET请求。

发起服务器性能统计请求
----------------------

Request::

    GET /performance/start_collecting?sha=<sha>&duration=<duration>&interval=<interval>&server=<server>

注：
    <sha>:在请求端通过SHA1("URL_PREFFIX;PID;CurrentTimestamp")计算出来
    <duration>:采集持续时长
    <interval>:采集间隔
    <server>:采集指定服务的性能信息

Response:

.. code-block:: jss
   
    {
        result:"succeeded/failed",
        systemCpu:[],
        systemMem:[],
        processCpu:[],
        processMem:[],
        processReadSize:[],
        processWriteSize:[],
        processReadCount:[],
        processWriteCount:[]
    }

处理逻辑:

    如果query不完整，则Response中的result字段为failed，否则返回succeed

停止服务器性能统计请求
----------------------

Request::

    GET /performance/stop_collecting?sha=<sha>

Response:

.. code-block:: jss
   
    {
        result:"succeeded/failed",
        systemCpu:[],
        systemMem:[],
        processCpu:[],
        processMem:[],
        processReadSize:[],
        processWriteSize:[],
        processReadCount:[],
        processWriteCount:[]
    }

处理逻辑:

    request中的散列与代理端存储的散列值一致，则返回代理中采集的性能指标，result为succeed，否则为failed


