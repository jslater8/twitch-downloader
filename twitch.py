import urllib2
import json
import sys
import subprocess
import time
import signal
import os
import threading
import psutil
import streamlink as sl


def signal_handler(signal, frame):
    print 'You pressed Ctrl-C'


def getName():
    if '-f' in sys.argv:
        index = sys.argv.index('-f')
        name = sys.argv[index + 1]
    else:
        print 'no stream name'
        sys.exit()
    return name

def isDownload():
    return '-nd' not in sys.argv

def getStream(name):
    streams = sl.streams("twitch.tv/" + name)
    return bool(streams)

def isOnline(name):
    return getStream(name)


PROCNAME = "python.exe"

def oldmain():
    signal.signal(signal.SIGINT, signal_handler)
    running = False
    counter = 0
    time2 = time.time()
    name = getName()
    if not os.path.exists(name):
        os.makedirs(name)
    while(True):
        try:
            online = isOnline(name)
            if online:
                os.chdir(name)
                start = time.strftime("%d-%m-%H-%M")
                size = sum(os.path.getsize(f) for f in os.listdir('.') if os.path.isfile(f))
                if size > 50000000000:
                    print 'size too big'
                    for proc in psutil.process_iter():
                        if proc.name() == PROCNAME and proc.pid != os.getpid():
                            proc.kill()
                    break
                if not running:
                    print "starting dl"
                    process = subprocess.Popen(['streamlink', \
                     'twitch.tv/' + name, 'best', '-o', \
                       str(counter) + '--' + str(start) + '.mp4'])
                    counter = counter + 1
                if process.returncode == None:
                    running = True
                else:
                    running = False
                os.chdir('..')
            else:
                print 'not online'
            time.sleep(10)
            #print time.time() - time2
            time2 = time.time()
        except KeyboardInterrupt:
            print "keyboard interrupt exiting"
            exit(0)
        else:
            print "exception trying again"

if __name__ == '__main__':
    name = getName()
    dl = isDownload()
    if not os.path.exists(name):
        os.makedirs(name)
    while(True):
        try:
            online = isOnline(name)
            if online:
                os.chdir(name)
                start = time.strftime("%d-%m-%H-%M")
                size = sum(os.path.getsize(f) for f in os.listdir('.') if os.path.isfile(f))
                if size > 75*1000*1000*1000:
                    print "size too big"
                    exit(1);
                if dl:
                    subprocess.call(['streamlink', 'twitch.tv/' + name, 'best', '-o ' + str(start) + '.mp4'])
                else:
                    subprocess.call(['streamlink', 'twitch.tv/' + name, 'best'])
                os.chdir('..')
            else:
                print 'offline'
            time.sleep(10)
        except KeyboardInterrupt:
            print 'keyboard'
            exit(0)
        except Exception as e:
            print 'exception' + str(e) + ' trying again'
