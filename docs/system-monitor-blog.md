@[TOC](Linux系统信息监控软件)


该软件是使用python2.7开发的，目的用于采集服务器性能数据。

git地址 (https://github.com/NavInfo2/system-monitor.git)。

## 1. 功能特点
* 支持服务器硬件信息及性能实时展示。
* 配合压力测试工具（https://github.com/NavInfo2/visual-wrk)，在压测过程中将数据同步至压测的发起方。

## 2. 部署

### 1) 安装依赖
```
    sudo apt-get install nginx
    sudo apt-get install python2.7
    sudo pip install flup==1.0
    sudo pip install psutil
```

### 2) nginx配置

在/etc/nginx/sites-enabled/default的nginx配置中增加以下配置: 

```
    location ~ ^/system_monitor/api/v1(?<path_info>/.*)$
    {   
        include fastcgi_params;
        fastcgi_param SCRIPT_FILENAME /scripts$fastcgi_script_name;
        fastcgi_param PATH_INFO $path_info;
        fastcgi_pass unix:/etc/ncserver/system-monitor/.ncserver.sock;
    }   
    
    location /nc/v1/system_monitor
    {   
        alias /etc/ncserver/system-monitor/html;
        index index.html;
    }   
```

配置完成后重启nginx

 ```
	 sudo service nginx restart 
 ```

### 3) 部署软件
```
    git clone git@github.com:NavInfo2/system-monitor.git
    cd system-monitor
    sudo ./deploy.sh
    cd /etc/ncserver/system-monitor/
    sudo python httpServer.py
```
## 3. 系统信息采集项
* 系统信息
* CPU硬件信息
* 内存总量
* 硬盘使用率
* CPU实时使用率
* 内存实时使用率
* IO实时读写大小
* IO实时读写次数

## 4. 在线信息展示图
在部署完成后，即可通过http://<host>/nc/v1/system_monitor/去访问系统性能的在线展示图。
![在线展示图](http://upload-images.jianshu.io/upload_images/16641961-ba363b935e429b81?imageMogr2/auto-orient/strip%7CimageView2/2/w/1240)
