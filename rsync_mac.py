# -*-coding:utf-8-*- 
# @author wonderkun
# Need  pexpect
# please use easy_install to add in
import os
import re
import threading
import hashlib
import time
import sys
import shutil
import argparse
import copy

def runCmd(cmd):
    global password
    if password == '':
        os.system(cmd)
    else:
        import pexpect
        print cmd
        child = pexpect.spawn(cmd)
        try:
            i = child.expect(['password: ', 'continue connecting (yes/no)?'])
            if i == 0:
                child.sendline(password)
            elif i == 1:
                child.sendline('yes')
        except pexpect.EOF:
            child.close()
        else:
            child.expect(pexpect.EOF)
            child.close()
def sync():
    global server, user, port, source, target, option
    cmd = "rsync %s %s %s %s@%s:%s" % (port, options, source, user, server, target)
    runCmd(cmd)

def download():
    global server, user, port, source, target, option
    cmd = "rsync %s %s %s@%s:%s" % (port, options, user, server, target)
    print cmd
    runCmd(cmd)

def auto_sync():
    global source
    try:
        fileMonitor = FileMonitor(monitorPath=source,default_proc_fun=HandleAllEvents())
        fileMonitor.setDaemon(True)
        fileMonitor.start()
        while True:
            time.sleep(2)
    except KeyboardInterrupt as e:
        print "[*] monitor system exit!"
        sys.exit()
class RawOutputFormat:
    """
    Format string representations.
    """
    def __init__(self, format=None):
        self.format = format or {}

    def simple(self, s, attribute):
        if not isinstance(s, str):
            s = str(s)
        return (self.format.get(attribute, '') + s +
                self.format.get('normal', ''))

    def punctuation(self, s):
        """Punctuation color."""
        return self.simple(s, 'normal')

    def field_value(self, s):
        """Field value color."""
        return self.simple(s, 'purple')

    def field_name(self, s):
        """Field name color."""
        return self.simple(s, 'blue')

    def class_name(self, s):
        """Class name color."""
        return self.format.get('red', '') + self.simple(s, 'bold')

class ColoredOutputFormat(RawOutputFormat):
    """
    Format colored string representations.
    """
    def __init__(self):
        f = {'normal': '\033[0m',
             'black': '\033[30m',
             'red': '\033[31m',
             'green': '\033[32m',
             'yellow': '\033[33m',
             'blue': '\033[34m',
             'purple': '\033[35m',
             'cyan': '\033[36m',
             'bold': '\033[1m',
             'uline': '\033[4m',
             'blink': '\033[5m',
             'invert': '\033[7m'}
        RawOutputFormat.__init__(self, f)

class Event(object):
    IN_CREATE = "Create"
    IN_DELETE = "Delete"
    IN_MODIFY = "Modify"

    def __init__(self,event=None,fileName=None):
        self.__eventAll = [Event.IN_CREATE,Event.IN_DELETE,Event.IN_MODIFY] 
        self.__event = event if self.__judge(event) else None
        self.__fileName = fileName
        self._out = ColoredOutputFormat()
    def getEvent(self):
        return self.__event
    def getFileName(self):
        return self.__fileName
    def __judge(self,event):
        if event in self.__eventAll:
            return True
        return False

    def __repr__(self):
        out = "[*] {event} file {fileName}".format(event=self.__event,fileName=self.__fileName)
        return self._out.class_name(out)
    def __str__(self):
        out = "[*] {event} file {fileName}".format(event=self.__event,fileName=self.__fileName)
        return self._out.class_name(out)
        
class _ProcessEvent:
    def __call__(self,event):
        eventX = event.getEvent()
        fileName = event.getFileName()
        method = getattr(self,"process"+eventX,None)
        if method is not None:
            return method(event)
        return self.processDefault(event)
    def __repr__(self):
        return '<%s>' % self.__class__.__name__
class PrintAllEvents(_ProcessEvent):
    def processDefault(self,event):
        print(event)
class HandleAllEvents(_ProcessEvent):
    def checkFileName(self, fileName):
        global rulers
        for ruler in rulers:
            p = re.compile(ruler)
            if p.match(fileName) != None:
                return False
        return True
    def syncFile(self, fileName):
        if self.checkFileName(fileName):
            sync()
    def processCreate(self, event):
        #print "Create file: %s " % os.path.join(event.path,event.name)
        print(event)
        self.syncFile(event.getFileName())
    def processDelete(self,event):
        print(event)
        self.syncFile(event.getFileName())
    def processModify(self,event):
        print(event)
        self.syncFile(event.getFileName())

class FileMonitor(threading.Thread):
    def __init__(self,monitorPath=None,backupPath=None,default_proc_fun=None):
        super(FileMonitor,self).__init__()
        self.monitorPath = os.path.abspath(monitorPath).rstrip("/")+"/"  if monitorPath is not None else os.getcwd()+"/"
        self.backupPath = os.path.abspath(backupPath).rstrip("/")+"/" if backupPath is not None else None
        self.pathFileHash = {}
        self.currentPathHash = {}
        self.getFileHash = self.useMd5sum if os.path.exists("/usr/bin/md5sum") else self.useHashLib
        self.walk(self.monitorPath)
        self.__default_proc_fun = default_proc_fun if default_proc_fun is not None else PrintAllEvents()
        
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
                    event = Event(Event.IN_CREATE,fileName)
                    self.__default_proc_fun(event)
                    self.pathFileHash[fileName] = md5
                elif md5 != self.pathFileHash[fileName]:
                    event = Event(Event.IN_MODIFY,fileName)
                    self.__default_proc_fun(event)
                    self.pathFileHash[fileName] = md5
                    if self.backupPath is not None:
                        try:
                            print "[*] try to move previous file to current path!"
                            shutil.copyfile(os.path.join(self.backupPath,fileName.replace(self.monitorPath,"",1)),fileName)
                        except Exception as e:
                            print "[*] move previous file to current path error!",e
    def run(self):
        print "[*] start monitor " + self.monitorPath
        while True:
            self.check(self.monitorPath)
            if len(self.currentPathHash) < len(self.pathFileHash):
                for fileName in self.pathFileHash:
                    if fileName not in self.currentPathHash.keys():
                        event = Event(Event.IN_DELETE,fileName)
                        self.__default_proc_fun(event)
                        if self.backupPath is not None:
                            try:
                                print "[*] try to move previous file to current path!"
                                oldFileName = os.path.join(self.backupPath,fileName.replace(self.monitorPath,"",1))
                                shutil.copyfile(oldFileName,fileName)
                            except Exception as e:
                                print "[*] repair deleted file error!",e
                # self.pathFileHash = self.currentPathHash # 不能这样写，这是一个浅拷贝
                self.pathFileHash = copy.deepcopy(self.currentPathHash)
            self.currentPathHash.clear() #清空字典
            time.sleep(1)
if __name__ == "__main__":
    parse = argparse.ArgumentParser("python rsync_mac.py")
    parse.add_argument("-m","--monitorPath",required=False,dest="monitorPath",type=str,default='./',help="the path to monitor.")
    parse.add_argument("-d","--down",required=False,dest="down",action="store_true",help="download code from the server.")
    parse.add_argument("-a","--auto",required=False,dest="auto",action="store_true",help="automatic synchronization code to server.")
    parse.add_argument("-s","--server",required=True,dest="server",type=str,default=None,help="the server ip to connect.")
    parse.add_argument("-u","--user",required=True,dest="user",type=str,default=None,help="the username to connect the ssh on the server.")
    parse.add_argument("-p","--port",required=False,dest="port",type=str,default='',help="the port to connect the ssh on the server.")
    parse.add_argument("-c","--password",required=True,dest="password",type=str,default=None,help="the password to connect the ssh on the server.")
    parse.add_argument("-t","--target",required=True,dest="target",type=str,default=None,help="the target dictionary to synchronization on the server.")
    args = parse.parse_args()
    # your sync config
    server = args.server
    user = args.user
    password = args.password
    port = args.port
    source = args.monitorPath
    target = args.target
    options = "-rtvuC --delete --progress --exclude='rsync.py'"
    rulers = (r"[#~.][\s\S]*", r"[\s\S]*[#~]", r"[\s\S]*_flymake.[\s\S]*",)
    if port is not '':
        port = "-e 'ssh -p %d'" % (port)
    if args.down:
        download()
    elif args.auto:
        auto_sync()
    else:
        sync()