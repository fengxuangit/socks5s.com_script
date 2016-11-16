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
def scp(filename):
    # import ipdb;ipdb.set_trace()
    path = options.rpath
    cmd = "scp {0} fengxuan@{1}:{2}/".format(filename, "128.199.185.239", path)
    (status, output) = shell_exec(cmd)
    logger.info("upload file {0} to dir {1}".format(filename, path))
    # import ipdb;ipdb.set_trace()
    cmd = "touch {0}.SUCCESS &&scp {0}.SUCCESS fengxuan@{1}:{2}".format(filename, host[0], path)
    (status, output) = shell_exec(cmd)
    if status == 0:
        logger.info("host {0} upload ok !".format(host[0]))
    logger.info("scp ok!")
    os.remove(filename)
    os.remove("{0}.SUCCESS".format(filename))
 

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
    sco(JsonParse(data), "update")
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
