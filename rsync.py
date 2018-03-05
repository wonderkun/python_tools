# use rsync to sync code from server
# coding = UTF8
# @author Kleist Zhou
# 2013/2/5

# Need pyinotify, pexpect
# please use easy_install to add in
import os
import sys
import pyinotify
import re

# your sync config
server = '199.245.60.73'
user = 'root'
password = ''
port = ''
source = './'
target = '/srv/www/love/public_html/'
options = "-rtvuC --delete --progress --exclude='rsync.py'"

#custom regular expression
rulers = (r"[#~.][\s\S]*", r"[\s\S]*[#~]", r"[\s\S]*_flymake.[\s\S]*")

if port != '':
    port = "-e 'ssh -p %d'" % (port)

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

class OnChangeHandler(pyinotify.ProcessEvent):
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

    def process_IN_CREATE(self, event):
        #print "Create file: %s " % os.path.join(event.path,event.name)
        self.syncFile(event.name)

    def process_IN_DELETE(self, event):
        #print "Delete file: %s " % os.path.join(event.path,event.name)
        self.syncFile(event.name)

    def process_IN_MODIFY(self, event):
        #print "Modify file: %s " % os.path.join(event.path,event.name)
        self.syncFile(event.name)

def auto_sync():
    global source
    wm = pyinotify.WatchManager()
    mask = pyinotify.IN_CREATE | pyinotify.IN_DELETE | pyinotify.IN_MODIFY
    notifier = pyinotify.Notifier(wm, OnChangeHandler())
    wm.add_watch(source, mask, rec=True, auto_add=True)
    notifier.loop()

def main():
    if len(sys.argv) == 2:
        option = sys.argv[1]
        if option == '-down':
            download()
        elif option == '-auto':
            auto_sync()
    else:
        sync()
        
# main
if __name__ == "__main__":
    main()