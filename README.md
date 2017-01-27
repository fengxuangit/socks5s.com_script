#这个仓库存放的是shadow项目的一些脚本

## Overview

**shadowsocks交易网站** 这个网站是http://www.socks5s.com/ 上面的后端源码，因为无法获取支付宝和微信的API，所以使用第三方自动发卡平台，编写自动卡密生成工具。

后端是自己开发的一整套程序配合前台 <a href="https://github.com/fengxuangit/socks5s.com">socks5s.com前台源码</a>  的包括集群数据同步，流量统计等工具。





##card.py
生成卡密的工具

##reduce.py
UI服务器上运行的定时脚本,用来监测数据库的状态,和同步数据,异步操作

##port_network.sh
集群服务器上运行的基于端口的流量统计工具，参见 <a href="https://github.com/fengxuangit/port_stream_count">port_stream_count</a>

##ParseStream.py
集群服务器上运行将流量包同步到数据库的脚本。

##models.py
mysql封装类

##serverjsonparse.py
集群服务器上将UI服务器上传的JSON数据解析到shadowsocks文件中的脚本

##install.sh
安装脚本

##ftpupload.py
FTP上传封装类,用来上传文件

##install.sh
安装脚本

##network-analysis.sh
流量分析脚本
