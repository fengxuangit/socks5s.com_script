#!/usr/bin/env python
# coding=utf-8

import time
from random import random
import hashlib
import os
import sys

from models import *

m2 = hashlib.md5()
cardnum = []
cardpass = []


def getrandom(number):
    global cardnum
    global cardpass
    m2 = hashlib.md5() 
    for num in xrange(number):
        m2.update("{0}{1}".format(time.time(), random()))
        cardnum.append(m2.hexdigest())
        m2.update("{0}{1}".format(time.time(), random()))
        cardpass.append(m2.hexdigest())

def main():
    if len(sys.argv) < 2:
        print "{0} money number".format(sys.argv[0])
        sys.exit()
    mysql = MySQLHander()
    money = int(sys.argv[1])
    number = int(sys.argv[2])
    filename = "{0}/card_{1}_{2}.txt".format(os.path.split(os.path.realpath(__file__))[0], money, int(time.time()))
    fp = open(filename, 'ab')
    getrandom(number)
    for num in xrange(number):
        sql = "insert into s_card(`cardnum`, `cardpass`, `money`) values('{0}', '{1}',{2})".format(cardnum[num], cardpass[num], money)
        fp.write("{0} {1} \n".format(cardnum[num], cardpass[num]))
        mysql.insert(sql)
        print "[*] {0} ok".format(num)
    fp.close()
    print  "Done!"

if __name__ == '__main__':
    main()
