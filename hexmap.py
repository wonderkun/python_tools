#!/bin/python
###############################################
# File Name : hexmap.py
#    Author : rootkiter
#    E-mail : rootkiter@rootkiter.com
#   Created : 2017-03-21 12:36:59
###############################################

class hexmap:
    def __init__(self,string):
        self.string=string

    def __str__(self):
        (offset,hexdata,charbuf)=(0,"","")
        result=""
        for char in self.string:
            if ord(char)>=33 and ord(char)<=126:
                charbuf+=char
            elif ord(char)==0:
                charbuf+='.'
            else:
                charbuf+="*"

            hexdata+="%02x" % (ord(char))
            offset+=1
            i=(offset)%16
            if i==0:
                buf="0x%04x\t%-48s\t%-16s" % ((offset-1)/16*16,hexdata,charbuf)
                result += buf+"\n"
                hexdata=""
                charbuf=""
            elif (i%8==0):
                hexdata+="  "
            else:
                hexdata+=" "
        buf="0x%04x\t%-48s\t%-16s" % ((offset-1)/16*16,hexdata,charbuf)
        result += buf+"\n"
        result += "-----> packet size :hex(0x%x),ord(%d) <-------" % (len(self.string),len(self.string))
        return result


import sys
if __name__=='__main__':
    testdata = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    '''
    0x0000  41 42 43 44 45 46 47 48  49 4a 4b 4c 4d 4e 4f 50    ABCDEFGHIJKLMNOP
    0x0010  51 52 53 54 55 56 57 58  59 5a                      QRSTUVWXYZ      
    -----> packet size :hex(0x1a),ord(26) <-------
    '''
    print str(hexmap(testdata))
