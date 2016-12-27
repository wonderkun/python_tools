#!/usr/bin/python
#-*-coding:utf-8-*-  


 
import time,sys,os
import random
from evdev import InputDevice
from select import select
import threading 


tchar = [
'''  ___   
 / _ \  
| | | | 
| | | | 
| |_| | 
 \___/  
        ''',''' __  
/_ | 
 | | 
 | | 
 | | 
 |_| ''',''' ___   
|__ \  
   ) | 
  / /  
 / /_  
|____| ''',''' ____   
|___ \  
  __) | 
 |__ <  
 ___) | 
|____/  ''',''' _  _    
| || |   
| || |_  
|__   _| 
   | |   
   |_|   ''',''' _____  
| ____| 
| |__   
|___ \  
 ___) | 
|____/  ''','''   __   
  / /   
 / /_   
| '_ \  
| (_) | 
 \___/  ''',''' ______  
|____  | 
    / /  
   / /   
  / /    
 /_/     ''','''  ___   
 / _ \  
| (_) | 
 > _ <  
| (_) | 
 \___/  ''','''  ___   
 / _ \  
| (_) | 
 \__, | 
   / /  
  /_/   '''
]






'''
这个题真是复杂,弄了两个多小时,才做的像个样子!!!!!!

只可以在linux上跑,必须用root权限运行,

#一个线程模拟滚动输出,一个线程监听按键输入

'''

def detectInputKey():
    print "I　am runing !!"
    dev = InputDevice('/dev/input/event4')
    global runable       
    select([dev], [], [])   #忽略第一次输入
    for event in dev.read():
        pass
    
    select([dev], [], [])
    for event in dev.read():
        # for event in dev.read():
        if event:
            runable=False
            return
                


if  __name__=='__main__':
    if len(sys.argv)<2:
        print  sys.argv[0]+" filename "
        exit(0)     
    filename=sys.argv[1]
    
with open(filename,'r') as f:
    contents=f.readlines()
    
runable=True
thread2=threading.Thread(target=detectInputKey)
thread2.start()

while runable:
    
    os.system('cls' if os.name == 'nt' else 'clear')
    print "抽奖开始(输入任意字符,滚动结束):\n\n\n\n"
    
    line=random.randint(0,len(contents)-1)
    print '\n'.join([''.join([''.join(((tchar[int(c)] if c.isdigit() else db).split('\n'))[i]) for c in contents[line].strip('\n')]) for i in range(6)])
    print "\n\n\n\n\n\n\n"
    print "请输入任意字符，抽奖！！！"    
    time.sleep(0.1)
    
thread2.join()
print "\033[48;31m中奖的号码为:{num}\033[0m".format(num=contents[line])

    
