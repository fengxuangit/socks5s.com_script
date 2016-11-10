#!/usr/bin/env python
#!-*- coding:utf-8 -*-

import os
import MySQLdb
import sys


class MySQLHander(object):
    def __init__(self):
        host     = '127.0.0.1'
        username = 'root'
        password = '123480'
        port     = '3306'
        database = 'shadow'
        charset  = 'utf-8'
        try:
            self._conn = MySQLdb.connect(host=host,
                         port=int(port),
                         user=username,
                         passwd=password,
                         db=database)
        except MySQLdb.Error, e:
            self.error_code = e.args[0]
            error_msg = 'MySQL error! ', e.args[0], e.args[1]
            print error_msg
            sys.exit()
        self._cur = self._conn.cursor()
        self._instance = MySQLdb


    def query(self,sql):
        try:
            self._cur.execute("SET NAMES utf8")
            result = self._cur.execute(sql)
        except MySQLdb.Error, e:
            self.error_code = e.args[0]
            print "DATABASE ERROR: ",e.args[0],e.args[1]
            result = False
        return result

    def update(self,sql):
        try:
            self._cur.execute("SET NAMES utf8")
            result = self._cur.execute(sql)
            self._conn.commit()
        except MySQLdb.Error, e:
            self.error_code = e.args[0]
            print "DATABASE ERROR: ",e.args[0],e.args[1]
            result = False
        return result
    
    def insert(self,sql):
        try:
            self._cur.execute("SET NAMES utf8")
            self._cur.execute(sql)
            self._conn.commit()
            return self._conn.insert_id()
        except MySQLdb.Error, e:
            self.error_code = e.args[0]
            print "DATABASE ERROR: ",e.args[0],e.args[1]
            return False

    def fetchAllRows(self):
        return self._cur.fetchall()

    def fetchOneRow(self):
        return self._cur.fetchone()

    def getRowCount(self):
        return self._cur.rowcount
              
    def commit(self):
        self._conn.commit()
            
    def rollback(self):
        self._conn.rollback()
       
    def __del__(self):
        try:
            self._cur.close()
            self._conn.close()
        except:
            pass
    
    def close(self):
        self.__del__()

class SqlMapTask(object):
    pass
