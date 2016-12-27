#!/usr/bin/python 
#-*-coding:utf-8-*- 

import math.
import sys


def sushu(n):
      
    try:
        n=float(n)
        big=int(math.sqrt(n))+1
    except Exception as  e:
        return False 
    else:
        n=int(n)
        if n==1:
            return False
        if n==2:
            return True
        for  i in range(2,big):
            if n%i==0:
                return False
     
        return True
        

def input():
    global n 
    if len(sys.argv)>1:
        try:
            n=int(sys.argv[1])
        except Exception as e:
            print e 
            return False       
            
    for i in range(1,n+1):

        if(sushu(i)):
            print i,



if  __name__=="__main__":
    
    n=10
    input()
    