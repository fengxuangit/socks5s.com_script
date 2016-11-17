#!/usr/bin/env python
# coding=utf-8

import time
from random import random
import hashlib
import sys
import commands
import json
import string
import logging
from ftpupload import FtpAction
from common import *
from optparse import OptionParser

from models import *

cardpass = {}
global mysql
mysql = MySQLHander()

logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    datefmt='%Y/%m/%d %H:%M:%S')

logger = logging.getLogger(__name__)




#生成ss账号密码
def generatepass(number):
    global cardpass
    sql = "select max(port) from s_ssaccount"
    mysql.query(sql)
    start = mysql.fetchOneRow()
    if start[0] == None:
        start = 10000
    else:
        start = int(start[0]) + 1
    for num in xrange(start, start + number):
        cardpass[num] = getrandomchar()
        print num
    insertdb(cardpass)
    scp(JsonParse(cardpass))


def insertdb(cardpass):
    for card in cardpass:
        sql = "insert into s_ssaccount(`port`, `pass`) values({0}, '{1}')".format(card, cardpass[card])
        mysql.insert(sql)
    logger.info("insert db ok!")


#如果用户的流量超过，停止用户访问
def stopUser():
    logger.info("start stoping check")
    sql = "select id,port from s_user where streamcount < 0"
    mysql.query(sql)
    users = mysql.fetchAllRows()
    if len(users) == 0:
        return None
    portlist = []
    for user in users:
        sql = "update s_user set streamcount=0,port=0,sspass='' where id={0}".format(user[0])
        mysql.update(sql)
        portlist.append(user[1])
    logger.info("uploading stop file...")
    scp(JsonParse(portlist, 'stop'))
    logger.info("stoped ok!")


#每天将付费用户的使用天数-1
def reducetime():
    sql = "select buytime,port,id from s_user where buytime > 0"
    mysql.query(sql)
    vip = mysql.fetchAllRows()
    for v in vip:
        sql = "update s_user set buytime={0} where id={1}".format(int(v[0]) -1, v[2])
        mysql.update(sql)
        if int(v[0]) == 1:
            deleteUser({'port':v[1], 'id':v[2]})
    logger.info("reducetime ok!")


#将用户的ss账号的密码置空, s_ssaccount账号将状态置为0，密码修改
def deleteUser(info):
    newpass = getrandomchar()
    sql = "update s_ssaccount set pass='{0}',status=0 where port={1}".format(newpass, info['port'])
    mysql.update(sql)
    sql = "update s_user set port=0,sspass='',streamcount=0 where id={0}".format(info['id'])
    mysql.update(sql)
    updateportpass = {info['port']:newpass}
    filename = JsonParse(updateportpass, 'update')
    logger.info("uploading update file...")
    scp(filename)
    logger.info("deleteUser ok!")


def async(port):
    sql = "select pass from s_ssaccount where port={0}".format(port)
    mysql.query(sql)
    result = mysql.fetchOneRow()
    if result is None:
        logger.critical('No such pass or port!')
        return False
    rechange = {port:result[0]}
    filename = JsonParse(rechange, 'update')
    logger.info("uploading rechange file...")
    scp(filename)
    logger.info("upload rechange file ok!")



def usage():
    parser=OptionParser()
    parser.add_option("-m", "--mode", type="string", dest="mode", help="Runmode Synchronous or Asynchronous")
    parser.add_option("-n", "--number", type="int", dest="number", help="Runmode Synchronous or Asynchronous")
    parser.add_option("-z", "--zone", type="string", dest="zone", help="host zone ", default="fuck01")
    parser.add_option("-p", "--port", type="string", dest="port", help="the port to update")
    parser.add_option("-r", "--rpath", type="string", dest="rpath", help="remotepath to upload json", default="/root/ssuploadjsonpath")
    if len(sys.argv) < 2:
        parser.print_help()
        sys.exit()
    global options
    (options, args) = parser.parse_args()

def main():
    usage()
    if options.mode == 'generate':
        generatepass(options.number)
    elif options.mode == 'daily':
        reducetime()
        stopUser()
    elif options.mode == 'async':
        async(options.port)

if __name__ == '__main__':
    #python reduce.py -z fuck01 -m generate -n 10 #生成10个ss账号
    #python reduce.py -z fuck01 -m daily  -r 每天巡检任务
    #python reduce.py -z fuck01 -m async -p 10002 更新指定端口信息
    main()
    mysql.close()
