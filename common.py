#!/usr/bin/env python
# coding=utf-8

import os
import ConfigParser

CONFIG_PATH = 'config.ini'
config = None

def getconfig(section, option):
    global config
    if not config:
        config = ConfigParser.ConfigParser()
        confpath = os.path.join(os.path.dirname(__file__), CONFIG_PATH)
        config.read(confpath)
    return config.get(section, option)


#拷贝到集群
def scp(filename):
    ftp = FtpAction(getconfig('ftp', 'host'), getconfig('ftp', 'username'), getconfig('ftp', 'password'))
    remotepath = os.path.join(getconfig('ftp', 'remotepath'))
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