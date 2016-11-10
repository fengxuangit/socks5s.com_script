#!/usr/bin/env python
# coding=utf-8

import os
import time
from models import *
import logging
from optparse import OptionParser

global mysql
mysql = MySQLHander()

logging.basicConfig(level=logging.DEBUG,  
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',  
                    datefmt='%Y/%m/%d %H:%M:%S')

logger = logging.getLogger(__name__)

def parse(filename):
    data = {}
    with open(filename) as f:
        for line in f.readlines():
            stream = line.split(' ')
            if not len(stream):
                break
            if stream[1] not in data:
                data[stream[1]] = int(stream[2].strip())
            else:
                data[stream[1]] += int(stream[2].strip())
    logger.info('parse Done!')
    for line in data.keys():
        sql = "select streamcount from s_user where port={0}".format(line)
        mysql.query(sql)
        stream = mysql.fetchOneRow()
        if stream is None:
            continue
        stream = stream[0]
        newstream = stream - (int(data[line]) / 1024)
        sql = "update s_user set streamcount={0} where port={1}".format(newstream, line)
        mysql.update(sql)
        time.sleep(0.2)
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
