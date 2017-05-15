#!/usr/bin/python
#-*_coding:utf-8-*-


import requests
import json
from collections import namedtuple
import argparse


class Zoomeye():
    def __init__(self,username="",password="",hostPrint="",webPrint=""):
        self.username = username
        self.password = password
        self.apiUrl = "https://api.zoomeye.org/"
        self.table = []  # 存储结果

        self.hostPrint = hostPrint.split()
        self.webPrint = webPrint.split()

        self.__login()
        self.id = 0

    def __login(self):
        data = '{"username":"'+self.username+'","password":"'+self.password+'"}'
        req = self.__http(searchKind="user",method="POST",data=data,proxy={})
        result = json.loads(req.text)
        # print result
        self.__accessToken__ = result["access_token"]

    def searchWeb(self,header={},data=""):
        """
        参数
        query	string	查询关键词	必须	port:80 nginx
        page	integer	翻页参数(默认为1)	可选	7
        facets	string	统计项目，如果为多个，使用, 号分隔各个统计项	可选	app,device

        Web 应用搜索过滤器

        app	     string	Web 应用信息	         webapp:wordpress
        header	 string	HTTP headers	       header:server
        keywords string	meta 属性关键词	        keywords:baidu.com
        desc	 string	HTTP description 属性	  desc:hello
        title	 string	HTTP Title 标题信息	     title: baidu
        ip	     string	IP 地址	              ip:192.168.1.1
        site	 string	site 搜索	              site:baidu.com
        city	 string	城市名称	             city:beijing
        country	 string	国家名称	             country:china

        返回值
        matches	string	结果集
        facets	string	统计结果
        total	integer	结果总数

        """
        return self.__http(searchKind="web",header = header ,method="GET",data=data)


    def searchHost(self,header={},data=""):
        """
        host 搜索
        参数:

        query	string	查询关键词	必需	port:80 nginx
        page	integer	翻页参数(默认为1)	可选	7
        facets	string	统计项目，如果为多个，使用, 号分隔各个统计项	可选	app,device

        搜索过滤器:

        app	    string	应用，产品	app: ProFTD
        ver	    string	版本	ver:2.1
        device	string	设备类型	device:router
        os	    string	操作系统	os:windows
        service	string	服务类型	service:http
        ip	    string	IP 地址	ip:192.168.1.1
        cidr	string	CIDR 格式地址	cidr:192.168.1.1/24
        hostname string	主机名称	hostname:google.com
        port	string	端口号	port:80
        city	string	城市名称	city:beijing
        country	string	国家名称	country:china
        asn	    integer	ASN 号码	asn:8978

        返回值
        matches	string	结果集
        facets	string	统计结果
        total	integer	结果总数
        """
        return self.__http(searchKind="host",header = header ,method="GET",data=data)

    def searchHander(self,searchKind="host",start=0,end=100,query="",facets=""):
        header = {
            "Authorization":"JWT " + self.__accessToken__
        }

        startPage = 0
        endPage = 0
        if (end - start -10)<0:  #  因为一页是10条记录
            startPage = start/10+1
            endPage = startPage+1
        else:
            startPage = start/10+1
            endPage  = end/10+1

        for i in range(startPage,endPage):
            data = "query="+query+"&page="+str(i)+"&facets="+facets
            if searchKind == "host":
                req = self.searchHost(header=header,data=data)
            elif searchKind == "web" :
                req = self.searchWeb(header=header,data=data)
            # req = self.__http(searchKind="host",header = header ,method="GET",data=data)
            # print "[*] get response of page "+str(i)
            result =  json.loads(req.text)
            matches = result["matches"]
            self.printHander(searchKind,matches)
        self.pprinttable()
            # self.Row = namedtuple("Row",["id","ip","port","city","country","continent","organization","service","banner","app","version","os"])

    def pprinttable(self):
        rows = self.table
        # print rows
        # return

        if len(rows) > 0:
            headers = rows[0]._fields
            lens = []
            for i in range(len(rows[0])):
                # max( [x[i] for x in rows] + [headers[i]],key=lambda x:len(str(x)) )
                lens.append(len(max( [x[i] for x in rows] + [headers[i]],key=lambda x:len(str(x)))))
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



    def __http(self,searchKind="host",header ={},proxy={},method="GET",data=""):

        searchKind = searchKind.lower()
        if searchKind == "user":
            url = self.apiUrl + "user/login"
        elif searchKind == "host":
            url = self.apiUrl + "host/search"
        elif searchKind == "web":
            url = self.apiUrl+"web/search"
        else :
            return

        method = method.upper()
        if method == "GET":
            try :
                req = requests.get(url,params=data,proxies=proxy,headers = header,timeout=4)
                # print req.url
                return req
            except  Exception as e:
                print "[*] an error occur:",e
                return
        elif method == "POST":
            try:
                req = requests.post(url,data=data,proxies=proxy,headers = header,timeout=4)
                return req
            except  Exception as e:
                print "[*] an error occur:",e
                return
        else :
            return

    def printHander(self,searchKind="host",matches=[]):

        hostPrintList = {  # host 打印参数和对应键值之间的关系
            "I":"ip",
            "P":"port",
            "CI":"city",
            "CY":"country",
            "CT":"continent",
            "S":"service",
            "B":"banner",
            "A":"app",
            "V":"version",
            "O":"os"
        }
        webPrintList = {  # web 打印参数和对应键值之间的关系
            "I":"ip",
            "DV":"dbver",
            "DN":"dbname",
            "CI":"city",
            "CY":"country",
            "CT":"continent",
            "L":"language",
            "WV":"webappVer",
            "WN":"webappName",
            "SV":"serverVer",
            "SN":"serverName"
        }

        # self.hostPrint =
        if searchKind == "host":
            printFormat = ["id"] + [ hostPrintList[x] for x in self.hostPrint]
        elif searchKind == "web":
            printFormat = ["id"] + [webPrintList[x] for x in self.webPrint]

        # print printFormat
        self.Row = namedtuple("Row",printFormat)
        # print json.dumps(matches,indent=4)
        content = {}

        if searchKind == "host":
            ### for host search
            for matche in matches:
                self.id += 1
                content["id"] = str(self.id)
                content["ip"] = matche["ip"].replace("\r\n","")
                content["port"] = str(matche["portinfo"]["port"]).replace("\r\n","")
                content["city"] = matche["geoinfo"]["city"]["names"]["en"].replace("\r\n","")
                content["country"] = matche["geoinfo"]["country"]["names"]["en"].replace("\r\n","")
                content["continent"] = matche["geoinfo"]["continent"]["names"]["en"].replace("\r\n","")
                # organization = match["geoinfo"]["organization"].replace("\r\n","")
                content["service"] = matche["portinfo"]["service"].replace("\r\n","")
                content["banner"] = matche["portinfo"]["banner"][:30].replace("\r\n","")
                content["app"] = matche["portinfo"]["app"].replace("\r\n","")
                content["version"] = matche["portinfo"]["version"].replace("\r\n","")
                content["os"] =  matche["portinfo"]["os"].replace("\r\n","")
                # self.table.append(self.Row(str(self.id),ip,port,city,country,continent,service,banner,app,version,os))
                row = []
                for name in printFormat:
                    row.append(content[name])
                self.table.append(self.Row(*row))

        # self.Row = namedtuple("Row",["id","ip","dbver","dbname","city","country","continent","language","webappVer","webappName","serverVer","serverName"])
        elif searchKind == "web":
            ### for web search
            for matche in matches:
                self.id += 1
                content["id"] = str(self.id)
                content["ip"] = matche["ip"][0].replace("\r\n","")
                content["dbver"] = matche["db"][0]["version"].replace("\r\n","") if matche["db"][0]["version"] else ""
                content["dbname"] = matche["db"][0]["name"].replace("\r\n","")
                content["city"] = matche["geoinfo"]["city"]["names"]["en"].replace("\r\n","")
                content["country"] = matche["geoinfo"]["country"]["names"]["en"].replace("\r\n","")
                content["continent"] = matche["geoinfo"]["continent"]["names"]["en"].replace("\r\n","")
                content["language"] = matche["language"][0].replace("\r\n","")
                content["webappVer"] = matche["webapp"][0]["version"].replace("\r\n","") if  matche["webapp"][0]["version"] else ""
                content["webappName"] = matche["webapp"][0]["name"].replace("\r\n","")
                content["serverVer"] = matche["server"][0]["version"].replace("\r\n","") if  matche["server"][0]["version"] else ""
                content["serverName"] = matche["server"][0]["name"].replace("\r\n","")
                # self.table.append(self.Row(str(self.id),ip,dbver,dbname,city,country,continent,language,webappVer,webappName,serverVer,serverName))

                row = []
                for name in printFormat:
                    row.append(content[name])
                self.table.append(self.Row(*row))

if __name__== '__main__':

    parse = argparse.ArgumentParser("python zoomeye.py")
    parse.add_argument("-t",'--type',required=False,type=str,default='host',help="搜索类型,可以是 host 或者 web,默认是host搜索.")
    parse.add_argument('-q','--query',required=True,type=str,help="过滤条件,多个条件之间用空格隔开,例如: \"port:21 os:windows\",具体过滤条件,参考serchHost()和searchWeb()函数中的注释.")

    parse.add_argument("-hp","--hostPrint",required=False,type=str,default="I P CI CY CT S B A V O",help="打印host搜索结果的列,例如:I 代表打印ip列. I->ip ,P->port ,CI->city ,CY->country,CT->continent,S->service,B->banner,A->app,V->version,O->os. 这些值之间用空格隔开,默认是显示所有.")
    parse.add_argument("-wp","--webPrint",required=False,type=str,default="I DV DN CI CY CT L WV WN SV SN",help="打印web搜索结果的列,例如:I 代表打印ip列. I->ip ,DV->dbver ,DN->dbname ,CI->city,CY->country,CT->continent,L->language,WV->webappVer,WN->webappName,SV->serverVer,SN->serverName. 这些值之间用空格隔开,默认是显示所有.")
    parse.add_argument("-s","--start",required=False,type=int,default=0,help="取搜索结果的开始行,默认从第一行开始.")
    parse.add_argument("-e","--end",required=False,type=int,default=100,help="取搜索结果的结束行,默认到100行结束.")
    args = parse.parse_args()

    zoomeye = Zoomeye(username="729173164@qq.com",password="",hostPrint=args.hostPrint,webPrint=args.webPrint)  # 修改这里为自己的账号和密码
    zoomeye.searchHander(searchKind=args.type,start=args.start,end=args.end,query=args.query,facets="")
