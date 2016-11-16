#!/bin/bash

#判断包管理工具
check_package_manager(){
    local manager=$1
    local systemPackage=''
    if cat /etc/issue | grep -q -E -i "ubuntu|debian";then
        systemPackage='apt'
    elif cat /etc/issue | grep -q -E -i "centos|red hat|redhat";then
        systemPackage='yum'
    elif cat /proc/version | grep -q -E -i "ubuntu|debian";then
        systemPackage='apt'
    elif cat /proc/version | grep -q -E -i "centos|red hat|redhat";then
        systemPackage='yum'
    else
        echo "unkonw"
    fi
 
    if [ "$manager" == "$systemPackage" ];then
        return 0
    else
        return 1
    fi
}

cluster(){
    currentpath=`pwd`
    useradd -d home/shadows/ -m shadows
    echo shadows:hyj123480 | chpasswd
    homepath=/home/shadows/
    #下载更新，下载软件
    echo -e "\033[33m update softwareing  \033[0m"
    if check_package_manager apt;then
        # apt-get -y update
        apt-get -y install tcpdump  python-dev python-pip gcc swig python-dev autoconf libtool vsftpd
    elif check_package_manager yum;then
        yum -y update
        yum -y install tcpdump python-setuptools openssl-devel gcc swig python-devel autoconf libtool vsftpd
        easy_install pip
    fi

    pip install shadowsocks
    pip install M2Crypto
    pip install gevent


    echo -e "\033[36m update software Done! \033[0m"
    
    

    #设置shadowsocks的根目录。ss的文件上传目录
    read -p "please input shadowsocks json root path: " ssrootjsonpath
    read -p "please input shadowsocks json upload path: " ssuploadjsonpath
    read -p "please input the ss root json to bak path: " ssjsonbakpath
    read -p "please input the tcp savefile path: " tcpsavefile

    if [ "x$ssrootjsonpath" == "x" ];then
        ssrootjsonpath=$homepath'/ssrootjsonpath'
    fi
    
    if [ "x$ssuploadjsonpath" == "x" ];then
        ssuploadjsonpath=$homepath'/ssuploadjsonpath'
    fi
    
    if [ "x$ssjsonbakpath" == "x" ];then
        ssjsonbakpath=$homepath"/ssjsonbakpath"
    fi
    
    if [ "x$tcpsavefile" == "x" ];then
        tcpsavefile=$homepath"/tcpsavefile"
    fi

    
    if [ ! -d "$ssrootjsonpath" ];then
        mkdir $ssrootjsonpath
    elif [ ! -d "$ssuploadjsonpath" ];then
        mkdir $ssuploadjsonpath
    elif [ ! -d "$ssjsonbakpath" ];then
        mkdir $ssjsonbakpath
    fi
    

    cp shadowsocks.json $ssrootjsonpath
    echo -e "\033[36m setting shadowsocks path Done! \033[0m"

    #设置启动抓包脚本
    program=$currentpath"/portnetwork.sh"
    cmd="/bin/bash "$program" /tmp/tcpdumpPath "$tcpsavefile" >> "$homepath"/log/portnetwork.log 2>&1 &"
    eval $cmd

    isrun=`ps aux | grep tcpdump | grep -v grep | awk -F ' ' '{print $2}'`

    if [ ${#isrun} -ne 0 ];then
        echo -e "\033[36m  start tcpdump Done! \033[0m"
    else
        echo -e "\033[32m start tcpdump failed! \033[0m"
    fi


    #设置将流量文件解析并同步到数据库
    # read -p "please input the ss root json to bak path" ssjsonbakpath
    program=$currentpath"/ParseStream.py"
    cmd="0 */1 * * * python "$program" -f "$tcpsavefile
    (crontab -l 2>/dev/null | grep -Fv $program; echo "$cmd") | crontab -
    COUNT=`crontab -l | grep $program | grep -v "grep"|wc -l `
    if [ $COUNT -lt 1 ]; then 
        echo "fail to add crontab $PROGRAM" 
        exit 1 
    fi

    echo -e "\033[36m setting ParseStream crontab command Done! \033[0m"
    

    #设置解析上传json数据脚本到crontab,一小时巡检一次
    program=$currentpath"/serverjsonparse.py"
    cmd="0 */1 * * * python "$program" -p "$ssuploadjsonpath" -b "$ssjsonbakpath" -r "$ssrootjsonpath"/shadowsocks.json"
    (crontab -l 2>/dev/null | grep -Fv $program; echo "$cmd") | crontab -
    COUNT=`crontab -l | grep $program | grep -v "grep"|wc -l ` 
    if [ $COUNT -lt 1 ]; then
        echo "fail to add crontab $PROGRAM"
        exit 1
    fi


    echo -e "\033[36m setting parseJson crontab command Done! \033[0m"

    echo -e "\033[32m starting seting shadowsocks \033[0m"
    
    isrun=`ps aux | grep ssserver | grep -v grep | awk -F ' ' '{print $2}'`
    if [ ${#isrun} -ne 0 ];then
        ssserver -c $ssrootjsonpath"/shadowsocks.json" -d start & 
        echo -e "\033[36m  start ssserver Done! \033[0m"
    else
        ssserver -c $ssrootjsonpath"/shadowsocks.json" -d restart 
        echo -e "\033[32m start ssserver failed! \033[0m"
    fi

}


if [ $# -lt 1 ];then
    echo -e "\033[31m usage: "$0" client or cluster  \033[0m"
    exit -1;
elif [ "$1"x = "client"x ];then
    client
elif [ "$1"x = "cluster"x ];then
    cluster
else
    echo "fuck U?"
    exit -1;
fi


