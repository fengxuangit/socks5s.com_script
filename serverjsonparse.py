#!/usr/bin/env python
# coding=utf-8

import sys
import os
import json
import commands
import time
import logging
import copy
from datetime import datetime
from optparse import OptionParser

global rootjsonfile, rootssjson

ssbakpath = '/tmp/bak/'

logging.basicConfig(level=logging.DEBUG,  
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',  
                    datefmt='%Y/%m/%d %H:%M:%S')

logger = logging.getLogger(__name__)



def shell_exec(cmd):
    return commands.getstatusoutput(cmd)

#重启ss服务
def restartss():
    (status, output) = shell_exec("ssserver -d stop")
    if status == 0 and output.find("stopped") >=0 :
        logger.info("restart shadow ok!")
        return True
    return False


#备份文件
def bakssfile():
    with open(rootjsonfile, 'rb') as f:
        source = f.read()
    backfile = "{0}/{1}.json".format(options.bak, datetime.now().strftime("%Y%m%d-%H-%M"))
    with open(backfile, 'wb') as f:
        f.write(source)
    return True


#更新port_password中端口号和密码
def updatejson(path):
    flag = False
    logger.info('check update file')
    for dirpath, dirnames, filenames in os.walk(path):
        for files in filenames:
            if not files.startswith('update')  or not files.endswith('json'):
                continue
            successfile = "{0}/{1}.SUCCESS".format(path, files)
            if not os.path.exists(successfile):
                logger.error("waitting update file")
                time.sleep(5)
            logger.info('deal update file')
            jsonfile = "{0}/{1}".format(path,files)
            fp2 = open(jsonfile, 'rb')
            resource = json.load(fp2)
            fp2.close()
            #这里是重写，更新
            for key in resource:
                rootssjson['port_password'][key] = resource[key]

            os.remove(jsonfile)
            os.remove(successfile)
            flag = True
    if not flag:
        logger.info('no update file')
        return flag
    if bakssfile() == True:
        with open(rootjsonfile, 'wb') as fp1:
            fp1.write(json.dumps(rootssjson, indent=4))
    restartss()
    logger.info("update ok!")


#生成一堆账号
def generatejson(path):
    flag = False
    logger.info('check generate file')
    for dirpath, dirnames, filenames in os.walk(path):
        for files in filenames:
            if not files.startswith('pass') or not files.endswith('json'):
                continue
            successfile = "{0}/{1}.SUCCESS".format(path, files)
            if not os.path.exists(successfile):
                logger.error("waitting genterate fileing")
                time.sleep(5)
            logger.info('deal generate file')
            jsonfile = "{0}/{1}".format(path,files)
            fp2 = open(jsonfile, 'rb')
            resource = json.load(fp2).copy()
            #将生产的端口密码更新到port_password中
            rootssjson['port_password'].update(resource)
            fp2.close()
            os.remove(jsonfile)
            os.remove(successfile)
            flag = True
    if not flag:
        logger.info('no generate file')
        return flag
    if bakssfile() == True:
        with open(rootjsonfile, 'wb') as fp1:
            fp1.write(json.dumps(rootssjson, indent=4))
    restartss()
    logger.info("update done!")

def stopjson(path):
    flag = False
    logger.info('check stop file')
    for dirpath, dirnames, filenames in os.walk(path):
        for files in filenames:
            if not files.startswith('stop') or not files.endswith('json'):
                continue
            successfile = "{0}/{1}.SUCCESS".format(path, files)
            if not os.path.exists(successfile):
                logger.error("waitting stop fileing")
                time.sleep(5)
            logger.info('deal stop file')
            jsonfile = "{0}/{1}".format(path,files)
            fp2 = open(jsonfile, 'rb')
            resource = copy.deepcopy(json.load(fp2))
            del rootssjson['port_password'][str(resource[0])]
            fp2.close()
            os.remove(jsonfile)
            os.remove(successfile)
            flag = True
    if not flag:
        logger.info('no update file')
        return flag
    if bakssfile() == True:
        with open(rootjsonfile, 'wb') as fp1:
            fp1.write(json.dumps(rootssjson, indent=4))
    restartss()
    logger.info("stop done!")



def usage():
    parser = OptionParser()
    parser.add_option("-p", "--path", type="string", dest="path", help="json path to parse", default="/home/fengxuan/upjson")
    parser.add_option("-b", "--bak", type="string", dest="bak", help="bak path", default="/home/fengxuan/bakjson")
    parser.add_option("-r", "--root", type="string", dest="root", help="the root json to parse", default="/tmp/shadowsocks3.json")
    if len(sys.argv) < 2:
        parser.print_help()
        sys.exit()
    global options
    (options, args) = parser.parse_args()


def main():
    usage()
    global rootjsonfile, rootssjson
    rootjsonfile = options.root
    path = options.path
    fp1 = open(rootjsonfile, 'rb')
    rootssjson = json.load(fp1).copy()
    fp1.close()
    generatejson(path)
    updatejson(path)
    stopjson(path)

if __name__ == '__main__':
    #p /Users/apple/wwwroot/webapp/shadow/script/serverjsonparse.py -p /tmp/upjson -b /tmp/bak -r /Users/apple/Downloads/shadowsocks3.json
    main()
