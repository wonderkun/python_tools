#!/usr/bin/python
# -*- coding: utf-8 -*-
import os
import hashlib
import threading
import shutil
import time
import sys
import argparse

class FileMonitor(threading.Thread):
    def __init__(self,monitorPath=None,backupPath=None):
        super(FileMonitor,self).__init__()
        self.monitorPath = os.path.abspath(monitorPath).rstrip("/")+"/"  if monitorPath is not None else os.getcwd()+"/"
        self.backupPath = os.path.abspath(backupPath).rstrip("/")+"/" if backupPath is not None else None
        self.pathFileHash = {}
        self.currentPathHash = {}
        self.getFileHash = self.useMd5sum if os.path.exists("/usr/bin/md5sum") else self.useHashLib
        self.walk(self.monitorPath)
        # print len(self.pathFileHash)

    def useMd5sum(self,fileName):
        return os.popen("md5sum " +fileName+" | awk '{print $1}'").read().strip("\n")
    def useHashLib(self,fileName):
        fileContent = open(fileName).read()
        md5 =  hashlib.md5()
        md5.update(fileContent)
        return md5.hexdigest()

    def walk(self,path):
        allFile = os.listdir(path)
        for afile in allFile:
            fileName = os.path.join(path,afile)
            if os.path.isdir(fileName):
                self.walk(fileName)
            else:
                md5 = self.getFileHash(fileName)
                self.pathFileHash[fileName] = md5

    def check(self,path):
        allFile = os.listdir(path)
        for afile in allFile:
            fileName = os.path.join(path,afile)
            if os.path.isdir(fileName):
                self.check(fileName)
            else:
                md5 = self.getFileHash(fileName)
                self.currentPathHash[fileName] = md5
                if fileName not in self.pathFileHash.keys():
                    print "\033[40;31m"+"[*] Warning:"+fileName+" is created!"+"\033[0m"

                    try:
                        if not os.path.exists("/tmp/maybeShell"):
                            os.mkdir("/tmp/maybeShell")
                        newFileName = os.path.join("/tmp/maybeShell",os.path.basename(fileName))
                        shutil.copyfile(fileName,newFileName)
                        print "[*] backup this file to "+ newFileName
                    except Exception as e:
                        print "[*] backup this file error!",e
                    try:
                        os.remove(fileName)
                    except Exception as e:
                        print "[*] remove this file error!"
                elif md5 != self.pathFileHash[fileName]:
                     print "\033[40;31m"+"[*] Warning:"+fileName+" is changed!"+"\033[0m"
                     try:
                         if not os.path.exists("/tmp/maybeShell"):
                             os.mkdir("/tmp/maybeShell")
                         newFileName = os.path.join("/tmp/maybeShell",os.path.basename(fileName))
                         shutil.copyfile(fileName,newFileName)
                         print "[*] backup this file to "+ newFileName
                     except Exception as e:
                         print "[*] backup this file error!",e
                     if self.backupPath is not None:
                         try:
                             print "[*] try to move previous file to current path!"
                             shutil.copyfile(os.path.join(self.backupPath,fileName.lstrip(self.monitorPath)),fileName)
                         except Exception as e:
                             print "[*] move previous file to current path error!",e
    def run(self):
        print "[*] start monitor " + self.monitorPath
        while True:
            self.check(self.monitorPath)
            if len(self.currentPathHash) < len(self.pathFileHash):
                for fileName in self.pathFileHash:
                    if fileName not in self.currentPathHash.keys():
                        print "\033[40;31m"+"[*] Warning: "+fileName+" is deleted!"+"\033[0m"
                        if self.backupPath is not None:
                            try:
                                print "[*] try to move previous file to current path!"
                                oldFileName = os.path.join(self.backupPath,fileName.replace(self.monitorPath,"",1))
                                shutil.copyfile(oldFileName,fileName)
                            except Exception as e:
                                print "[*] repair deleted file error!",e
            self.currentPathHash.clear() #清空字典
            time.sleep(2)




if __name__ == "__main__":
    parse = argparse.ArgumentParser("python python_file_monitor.py")
    parse.add_argument("-p","--monitorPath",required=False,type=str,default=None,help="the path to monitor.")
    parse.add_argument("-b","--backupPath",required=False,type=str,default=None,help="the backupPath to recover the file.")
    args = parse.parse_args()
    try:
        fileMonitor = FileMonitor(monitorPath=args.monitorPath,backupPath=args.backupPath)
        fileMonitor.setDaemon(True)
        fileMonitor.start()
        while True:
            time.sleep(1)
    except KeyboardInterrupt as e:
        print "[*] monitor system exit!"
        sys.exit()
