#!/usr/bin/env python
# coding=utf-8

import os
import time
from models import *
import logging
from optparse import OptionParser
from common import *

global mysql
mysql = MySQLHander()

logging.basicConfig(level=logging.DEBUG,  
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',  
                    datefmt='%Y/%m/%d %H:%M:%S')

logger = logging.getLogger(__name__)
 

ftpconfig = {
    'host': "128.199.185.239",
    'username': 'fengxuan',
    'password': 'hyj123480',
    
}

def parse(filename):
    data = {}
    with open(filename) as f:
        for line in f.readlines():
            stream = line.split(' ')
            if not len(stream):
                break
            if int(stream[1]) < 1024:
                continue
            if stream[1] not in data:
                data[stream[1]] = int(stream[2].strip())
            else:
                data[stream[1]] += int(stream[2].strip())
    logger.info('parse Done!')
    scp(JsonParse(data), "update")
    logger.info('update Done!')
    #确保文件删除掉了 
    unlink(filename)

def unlink(filename, time=3):
    os.remove(filename)
    if os.path.exists(filename) and time != 0:
        unlink(filename, time - 1)
    return True


def usage():
    parser=OptionParser()
    parser.add_option("-f", "--file", type="string", dest="file", help="remotepath to upload json")
    if len(sys.argv) < 2:
        parser.print_help()
        sys.exit()
    global options
    (options, args) = parser.parse_args()


def main():
    usage()
    parse(options.file)

if __name__ == '__main__':
    main()
