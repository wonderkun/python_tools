#!/bin/python
###############################################
# File Name : tablemap.py
#    Author : rootkiter
#    E-mail : rootkiter@rootkiter.com
#   Created : 2017-03-21 12:39:09
###############################################

class tablemap:
    def __init__(self):
        self.tableTitle=""
        self.title={}
        self.titlelist=[]
        self.item = {}
        self.itemnamelen=0
        self.itemlist = []

    def setTitle(self,title):
        self.tableTitle = title

    def additem(self,title,itemname,itemvalue):
        if(title not in self.title):
            self.title[title]=len(title)
            self.titlelist.append(title)
        if(itemname not in self.item):
            self.item[itemname] = {}
            self.itemlist.append(itemname)
        self.item[itemname][title]=str(itemvalue)
        if(self.title[title] < len(str(itemvalue))):
            self.title[title] = len(str(itemvalue))
        if(len(itemname) > self.itemnamelen):
            self.itemnamelen = len(itemname)
        return True

    def getItemString(self,List,itemname,itemList=None):
        result = "| "
        if(itemList == None):
            formatString = "%%-%ds |" % self.itemnamelen
            result += formatString % itemname
            for citem in List:
                if(citem.startswith('-')):
                    item = citem[1::]
                    formatString = " %%-%ds |" % self.title[item]
                    itembuf = (((self.title[item] - len(item))/2)*' ')+item
                    result += formatString % (itembuf)
                else:
                    item = citem
                    formatString = " %%%ds |" % self.title[item]
                    itembuf = item+(((self.title[item] - len(item))/2)*' ')
                    result += formatString % (itembuf)
        else:
            formatString = "%%-%ds |" % self.itemnamelen
            result += formatString % itemname
            for citem in List:
                if(citem.startswith('-')):
                    item = citem[1::]
                    formatString = " %%-%ds |" % self.title[item]
                else:
                    item = citem
                    formatString = " %%%ds |" % self.title[item]
                try:
                    result += formatString % str(itemList[item])
                except Exception, e:
                    result += formatString % ""
        return result

    def printMap(self,titleList=None):
        result = ""
        formatString = "| "
        lineK        = "+-"
        List = []
        if(titleList == None):
            List = self.titlelist
        else:
            List = titleList

        for item in List:
            if(item.replace('-','') not in self.titlelist):
                return ""
        formatString += "%%%ds |" % self.itemnamelen
        lineK += self.itemnamelen*'-' + "-+"
        for citem in List:
            if(citem.startswith('-')):
                item=citem[1::]
                formatString += " %%-%ds |" % self.title[item]
            else:
                item=citem
                formatString += " %%%ds |" % self.title[item]
            lineK += "-"+ self.title[item]*'-' + "-+"

        if(len(self.tableTitle)>0):
            maxlen = len(lineK)
            noplen = (maxlen-len(self.tableTitle)-4)/2
            TBTitle = " "*noplen+"*"+self.tableTitle +"*"
            result += "+"+'-'*(maxlen-2)+"+" +"\n"
            result += "|"+TBTitle +" "*(maxlen-2-len(TBTitle))+"|\n"

        result += lineK +"\n"
        result += self.getItemString(List,str(len(self.itemlist))) + "\n"

        result += lineK +"\n"
        for item in self.itemlist:
            try:
                result += self.getItemString(List,item,self.item[item]) +"\n"
            except Exception, e:
                str(e)
        result += lineK +"\n"
        return result

import sys
if __name__=='__main__':
    tbmap = tablemap()
    tbmap.additem("title1",'item1',"Hello 1*1")
    tbmap.additem("title2",'item1',"Hello 1*2 AAAAA")
    tbmap.additem("title1",'item2',"Hello 2*1 BBBBB")
    tbmap.additem("title2",'item2',"Hello 2*2")
    '''
    +-------+-----------------+-----------------+
    |       |      title1     |      title2     |
    +-------+-----------------+-----------------+
    | item1 |       Hello 1*1 | Hello 1*2 AAAAA |
    | item2 | Hello 2*1 BBBBB |       Hello 2*2 |
    +-------+-----------------+-----------------+
    '''
    print tbmap.printMap()
############################################################
    '''
    +-------+-----------------+-----------------+
    |       |      title2     |     title1      |
    +-------+-----------------+-----------------+
    | item1 | Hello 1*2 AAAAA | Hello 1*1       |
    | item2 |       Hello 2*2 | Hello 2*1 BBBBB |
    +-------+-----------------+-----------------+
    '''
    tbmap.setTitle("Hello Table")
    print tbmap.printMap(['title2','-title1'])
