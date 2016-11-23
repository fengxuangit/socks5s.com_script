#!/usr/bin/env python
# coding=utf-8

from common import *
from models import *


global mysql
mysql = MySQLHander()

def main():
	sql = "select port,username,streamcount from s_user where buytime>1";
	mysql.query(sql)
	result = mysql.fetchAllRows()
	for r in result:
		sql = "update s_ssaccount set username='{0}',streamcount={1} where port={2}".format(r[1],int(r[2]), r[0]);
		mysql.update(sql)
	print "done"


if __name__ == '__main__':
	main()
	mysql.close()