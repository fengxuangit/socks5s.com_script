#!/usr/bin/env python
# coding=utf-8

import os
import ConfigParser
import logging
import random as rd
import time
import json
import string
from ftpupload import FtpAction

CONFIG_PATH = 'config.ini'
config = None

logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    datefmt='%Y/%m/%d %H:%M:%S')

logger = logging.getLogger(__name__)


def getrandomchar(num=6):
    return string.join(rd.sample(['z','y','x','w','v','u','t','s','r','q','p','o','n','m','l','k','j','i','h','g','f','e','d','c','b','a', '0', '1','2','3','4','5','6','7','8','9'], num)).replace(' ','')

def getconfig(section, option):
    global config
    if not config:
        config = ConfigParser.ConfigParser()
        confpath = os.path.join(os.path.dirname(__file__), CONFIG_PATH)
        config.read(confpath)
    return config.get(section, option)


def JsonParse(cardpass, mode="gen"):
    if mode == "gen":
        filename = "pass_{0}.json".format(int(time.time()))
    elif mode == "update":
        filename = "update_{0}.json".format(int(time.time()))
    elif mode == "stop":
        filename = "stop_{0}.json".format(int(time.time()))
    elif mode == "rechange":
        filename = "rechange_{0}.json".format(int(time.time()))
    fp = open(filename, 'wb')
    source = json.dumps(cardpass, indent=4)
    fp.write(source)
    fp.close()
    return filename

#拷贝到集群
def scp(filename, config={}):
    if not config:
        ftp = FtpAction(getconfig('ftp', 'host'), getconfig('ftp', 'username'), getconfig('ftp', 'password'))
        remotepath = os.path.join(getconfig('ftp', 'remotepath'))
    else:
        ftp = FtpAction(config['host'], config['username'], config['password'])
        remotepath = os.path.join(config['remotepath'])
    success = "{0}.SUCCESS".format(filename)
    with open(success, 'wb') as f:
        f.write('fuck')
    ftp.local_to_sftp(filename, remotepath, success)
    os.unlink(filename)
    os.unlink(success)
    logger.info("upload ok!")

def shell_exec(cmd):
    return commands.getstatusoutput(cmd)

if __name__ == '__main__':
    print getconfig('mysql', 'host')