#!/usr/bin/python
# coding:utf-8

import requests
import time
import sys
import argparse
import re
import threading
import json
import os

class Downloader(threading.Thread):

    def __init__(self,url=None,id=0,tmpFilename=None,filename=None,headers={},proxies={},RLock=None,block=1024*3):
        threading.Thread.__init__(self)
        self.id = str(id)
        self.filename = filename
        self.url = url
        self.headers = headers
        self.proxies = proxies
        self.RLock = RLock
        self.block = block
        self.tmpFilename = tmpFilename

    def run(self):

        with open(self.tmpFilename) as file:
            info = json.load(file)

        if info[self.id]["start"] >= info[self.id]["end"]:
            return

        headers["Range"]="bytes=%d-%d"%(info[self.id]["start"],info[self.id]["end"]-1)
        res = requests.get(self.url,headers=headers,stream=True,proxies=self.proxies)
        for chunk in res.iter_content(chunk_size = self.block):
            if chunk:
                self.RLock.acquire()
                print self.id,info[self.id]["start"],info[self.id]["end"]
                print headers["Range"]
                self.RLock.release()
                self.RLock.acquire()
                with open(self.tmpFilename,'r') as file:
                    info = json.load(file)
                    start = info[self.id]["start"]
                    info[self.id]["start"] = start + len(chunk)
                with open(self.tmpFilename,'w') as file:
                    json.dump(info,file)

                with open(self.filename,'r+b') as file:
                    file.seek(start)
                    var = file.tell()
                    file.write(chunk)
                    file.flush()
                self.RLock.release()

                time.sleep(0.5)

""" getTerminalSize()
 - get width and height of console
 - works on linux,os x,windows,cygwin(windows)
"""

__all__=['getTerminalSize']


def getTerminalSize():
   import platform
   current_os = platform.system()
   tuple_xy=None
   if current_os == 'Windows':
       tuple_xy = _getTerminalSize_windows()
       if tuple_xy is None:
          tuple_xy = _getTerminalSize_tput()
          # needed for window's python in cygwin's xterm!
   if current_os == 'Linux' or current_os == 'Darwin' or  current_os.startswith('CYGWIN'):
       tuple_xy = _getTerminalSize_linux()
   if tuple_xy is None:
       print "default"
       tuple_xy = (80, 25)      # default value
   return tuple_xy

def _getTerminalSize_windows():
    res=None
    try:
        from ctypes import windll, create_string_buffer

        # stdin handle is -10
        # stdout handle is -11
        # stderr handle is -12

        h = windll.kernel32.GetStdHandle(-12)
        csbi = create_string_buffer(22)
        res = windll.kernel32.GetConsoleScreenBufferInfo(h, csbi)
    except:
        return None
    if res:
        import struct
        (bufx, bufy, curx, cury, wattr,
         left, top, right, bottom, maxx, maxy) = struct.unpack("hhhhHhhhhhh", csbi.raw)
        sizex = right - left + 1
        sizey = bottom - top + 1
        return sizex, sizey
    else:
        return None

def _getTerminalSize_tput():
    # get terminal width
    # src: http://stackoverflow.com/questions/263890/how-do-i-find-the-width-height-of-a-terminal-window
    try:
       import subprocess
       proc=subprocess.Popen(["tput", "cols"],stdin=subprocess.PIPE,stdout=subprocess.PIPE)
       output=proc.communicate(input=None)
       cols=int(output[0])
       proc=subprocess.Popen(["tput", "lines"],stdin=subprocess.PIPE,stdout=subprocess.PIPE)
       output=proc.communicate(input=None)
       rows=int(output[0])
       return (cols,rows)
    except:
       return None


def _getTerminalSize_linux():
    def ioctl_GWINSZ(fd):
        try:
            import fcntl, termios, struct, os
            cr = struct.unpack('hh', fcntl.ioctl(fd, termios.TIOCGWINSZ,'1234'))
        except:
            return None
        return cr
    cr = ioctl_GWINSZ(0) or ioctl_GWINSZ(1) or ioctl_GWINSZ(2)
    if not cr:
        try:
            fd = os.open(os.ctermid(), os.O_RDONLY)
            cr = ioctl_GWINSZ(fd)
            os.close(fd)
        except:
            pass
    if not cr:
        try:
            cr = (env['LINES'], env['COLUMNS'])
        except:
            return None
    return int(cr[1]), int(cr[0])

def remove_nonchars(filename):
    (name, _) = re.subn(ur'[\\\/\:\*\?\"\<\>\|]', '', filename)
    return name

def main(url="",threadNum=5,filename=None,cookie="",UserAgent=None,referer="",proxy=""):

    filename = remove_nonchars(filename) if filename else remove_nonchars(url.split('/')[-1])
    tmpFilename = filename+".downtmp"
    total = 0
    UserAgent =  UserAgent if  (UserAgent) else "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/40.0.2214.111 Safari/537.36"
    headers = {"User-Agent":UserAgent,"Cookie": cookie,"Referer":referer}
    threadNum = int(threadNum)
    """
      如果服务器不支持断点续传,那就用一个线程下载
      线程的优先级顺序:从临时文件读取 > 用户参数指定 > 默认值
    """

    tmpHeaders = {"User-Agent":UserAgent,"Cookie": cookie,"Referer":referer,"Range": "bytes=0-4"}
    proxies = {"http":proxy,"https":proxy}

    # 测试requests是否支持次类型的代理,判断服务器是否支持断点续传功能,如果支持就获取文件总大小

    try :
        res = requests.get(url,headers=tmpHeaders,proxies=proxies)
    except ValueError as e:
        print "Maybe this kind of proxy is not supported by your requests,please update it by 'pip install requests --upgrade'."
        return
    except requests.exceptions.ConnectionError as e:
        print "Please check the url or the proxy,May be one of them is wrong."
        return
    try:
        crange = res.headers['content-range']
        total = int(re.match(r'^bytes 0-4/([\d]+)$', crange).group(1))-1
        support_continue = True  #支持断点续传功能
    except:
        support_continue = False  #不支持断点续传
        try:
            total = int(res.headers['content-length']) - 1
        except:
            total = 0
    threadInfo={}
    if support_continue:
        try:
            with open(tmpFilename,'r') as f:
                # 从下下载临时文件中获取线程数
                threadInfo = json.load(f)
                threadNum =  len(threadInfo)
        except :
            # 不存在临时文件
            # with open(tmpFilename,'w') as f:
            part = total//threadNum
            for i in range(threadNum):
                start = part * i
                if i == threadNum -1:
                    end = total + 1
                else :
                    end = start + part
                threadInfo[str(i)] = {"start":start,"end":end}

            with open(tmpFilename,'w') as f:
                json.dump(threadInfo,f)
    else :
        threadInfo[0] = {"start":0,"end":total}
        threadNum = 1
        with open(tmpFilename,'w') as f:
            json.dump(threadInfo,f)

        if os.path.exists(filename): #因为没有断点续传的功能,所以文件从新命名下载的文件
            os.remove(filename)

    with open(filename,'wb') as f:
        # pass  #创建文件,规定文件的大小
        f.truncate(total+1)

    threadList = []
    RLock = threading.Lock() # 获取一个锁
    for i in range(threadNum):
        threadList.append(Downloader(url=url,id=i,tmpFilename=tmpFilename,filename=filename,headers=headers,\
        proxies=proxies,RLock=RLock))
    startTime = time.time()
    sys.stdout.write("--"+time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time()))+"--"+" "*2+url+"\n")
    sys.stdout.write("长度: "+str(total) +" ({size}KB) ".format(size = str(total/1024))+"[{filename}]".format(filename=filename)+"\n")
    sys.stdout.flush()

    for thread  in  threadList:
        thread.setDaemon(True)
        thread.start()
    while True:
        try:
            columns = getTerminalSize()[0] - 2
            RLock.acquire()

            remainSize = 0
            with open(tmpFilename) as f:
                threadInfo = json.load(f)
                for i in threadInfo:
                    remainSize = remainSize+threadInfo[i]["end"] - threadInfo[i]["start"]
            RLock.release()
            downloadSize = total - remainSize
            if downloadSize == total:
                break
            filenameInfo = filename+" "*10
            downloadInfo = "]"+" "*6 + str(downloadSize/1024)+"KB"
            speedInfo = " "*6+str(int(downloadSize/1024/(time.time()-startTime)))+"KB/S"
            totalInfo = " "*6+str(total/1024)+"KB"
            percentageInfo = str(int(float(downloadSize)/float(total)*100))+"%["
            progressLength = columns - len(downloadInfo) - len(speedInfo) - len(totalInfo) - len(percentageInfo)-len(filenameInfo)

            progressInfo =  int(float(downloadSize)/float(total)*progressLength)*"="+">"+(progressLength-int(\
            float(downloadSize)/float(total)*progressLength)-1)*" "
            sys.stdout.write("\b"*columns+"zheshish")
            sys.stdout.write("\b"*columns+filenameInfo+percentageInfo+progressInfo+downloadInfo+speedInfo+totalInfo)
            sys.stdout.flush()
            time.sleep(0.5)
        except KeyboardInterrupt as e:
            sys.exit(1)
    try:
        os.remove(tmpFilename)
    except:
        pass
    sys.stdout.write("\n"+"--"+time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time()))+\
    "--"+" "*2+"[总耗时:%ds]"%(time.time()-startTime)+"\n")
if __name__ == "__main__":

    parser = argparse.ArgumentParser("")
    parser.add_argument("-u","--url",type=str,dest="url",help="target url.")
    parser.add_argument("-o","--output",type=str,dest="filename",help="download file to save.")
    parser.add_argument("-t","--thread",type=int,dest="thread",help="the thread num.")
    parser.add_argument("-a","--user-agent",type=str,dest="useragent",help="request user agent.")
    parser.add_argument("-r","--referer",type=str,dest="referer",help="request referer.")
    parser.add_argument("-c","--cookie",type=str,dest="cookie",help="request cookie.")
    parser.add_argument("-p","--proxy",type=str,dest="proxy",help="support http proxy and \
    socks5 proxy, you can input -p http://ip:port or socks5://ip:port. ")
    args = parser.parse_args()
    if not args.url:
        print "[*] Missing Url!"
        sys.exit(1)
    if not args.thread:
        args.thread = 5
    main(url=args.url,threadNum=args.thread,filename=args.filename,cookie=args.cookie,\
    UserAgent=args.useragent,referer=args.referer,proxy=args.proxy)
