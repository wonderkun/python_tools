#!/usr/bin/python
# coding:utf-8
import requests
import argparse
from collections import namedtuple

class CollectionInfo(object):
    """docstring for CoInfo.
        .hg  https://github.com/kost/dvcs-ripper
        index.bak
        index.php.bak
        index.php.
        .index.php
        index.php~
        index.pyc
        .index.php.swp
        .index.php.swpx
        .index.php.swm
        index.tar.gz
        index.rar
        index.zip
        www.rar
        www.zip
        .svn   https://pan.baidu.com/s/1mrNpB
        .git
        .DS_Store  https://github.com/lijiejie/ds_store_exp
        .index.php.swo
        .index.php.swn
        robots.txt
        phpstorm/   .idea/workspace.xml
        CVS http://www.am0s.com/CVS/Root 返回根信息 http://www.am0s.com/CVS/Entries 返回所有文件的结构
        bk clone http://url/name dir
        WEB-INF/web.xml 

    """
    def __init__(self,url='',file=''):

        self.url = url
        self.file = file

        self.fileBackList = ['.bak','.','~','.pyc','.swp','.swpx','.swm','.swo','.swn']
        self.fileList = ['.viminfo','index.bak','index.tar.gz','index.zip','index.rar','www.tar.gz','www.rar','www.zip','.svn','.git','.DS_Store',
        'robots.txt','.idea/','.hg','www.7z','WEB-INF/web.xml','WEB-INF/classes/','WEB-INF/lib/','WEB-INF/src/',
        'WEB-INF/database.properties','CVS/','CVS/Root','CVS/Entries','phpMyAdmin','phpmyadmin']
        self.vimBackList = ['','~','.swp','.swpx','.swm','.swo','.swn']
        self.UrlList = []
        self.getUrlList()
        self.Row = namedtuple("Row",["url","status_code"])
        self.table = []

    def getUrlList(self):
        for file in self.fileBackList:
            self.UrlList.append(self.url.rstrip('/')+'/'+self.file+file)
        for file in self.fileList:
            self.UrlList.append(self.url.rstrip('/')+'/'+file)
        for file in self.vimBackList :
            self.UrlList.append(self.url.rstrip('/')+'/'+'.'+self.file+file)

    def printSelf(self):
        for i in self.UrlList:
            print i

    def sendRequest(self,cookies="",agent=""):
        cookies = cookies
        User_Agent = agent if agent is not  "" else "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.87 Safari/537.36"
        header = {
        "User-Agent":User_Agent,
        "Cookie":cookies
        }
        for  url in self.UrlList:
            res = requests.get(url,headers=header)
            print url ,res.status_code
            if res.status_code != 404:
                self.table.append(self.Row(url,res.status_code))

    def pprinttable(self):
        rows = self.table

        if len(rows) > 0:
            headers = rows[0]._fields
            lens = []
            for i in range(len(rows[0])):
                lens.append(len(max([x[i] for x in rows] + [headers[i]],key=lambda x:len(str(x)))))
            formats = []
            hformats = []
            for i in range(len(rows[0])):
                if isinstance(rows[0][i], int):
                    formats.append("%%%dd" % lens[i])
                else:
                    formats.append("%%-%ds" % lens[i])
                hformats.append("%%-%ds" % lens[i])

            pattern = " | ".join(formats)
            hpattern = "|"+" | ".join(hformats)+"|"
            separator = "+"+"-+-".join(['-' * n for n in lens])+"+"

            print separator
            print hpattern % tuple(headers)
            print separator
            _u = lambda t: t.decode('UTF-8', 'replace') if isinstance(t, str) else t
            for line in rows:
                # print separator
                print hpattern % tuple(_u(t) for t in line)
            print separator

        # elif len(rows) == 1:
        #     row = rows[0]
        #     hwidth = len(max(row._fields,key=lambda x: len(x)))
        #     for i in range(len(row)):
        #         print "%*s = %s" % (hwidth,row._fields[i],row[i])




if __name__ == '__main__':

    parse = argparse.ArgumentParser("python coinfo.py")
    parse.add_argument("-u",'--url',required=True,type=str,default='',help="The start url to find back files.")
    parse.add_argument('-f','--file',type=str,default='index.php',help='The file name to find!')
    args = parse.parse_args()
    coll = CollectionInfo(args.url,args.file)
    coll.sendRequest()
    coll.pprinttable()
