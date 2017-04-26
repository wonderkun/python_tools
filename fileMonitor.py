import os
from pyinotify import WatchManager, Notifier, ProcessEvent, IN_DELETE, IN_CREATE, IN_MODIFY

class EventHandler(ProcessEvent):
    def process_IN_CREATE(self, event):
        print "[*] Create file:%s." %os.path.join(event.path,event.name)

        os.system('cp -rf %s /tmp/bak/'%(os.path.join(event.path,event.name)))
    def process_IN_DELETE(self, event):
        print "[*] Delete file:%s." %os.path.join(event.path,event.name)

    def process_IN_MODIFY(self, event):
        print "[*] Modify file:%s." %os.path.join(event.path,event.name)

def FsMonitor(path='.'):
    wm = WatchManager()
    mask = IN_DELETE | IN_CREATE | IN_MODIFY
    notifier = Notifier(wm, EventHandler())
    wm.add_watch(path, mask, auto_add= True, rec=True)
    print "[*] now starting monitor %s." %path
    
    while True:
        try:
            notifier.process_events()
            if notifier.check_events():
                print "check event true."
                notifier.read_events()
        except KeyboardInterrupt:
            print "keyboard Interrupt."
            notifier.stop()
            break

if __name__ == "__main__":
    FsMonitor("./")
