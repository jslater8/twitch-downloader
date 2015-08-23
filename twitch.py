import urllib2
import json
import sys
import subprocess
import time
import signal
import os
import threading
import psutil


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

def getStream(name):
    url = 'https://api.twitch.tv/kraken/streams/' + name
    contents = urllib2.urlopen(url)
    return json.loads(contents.read().decode('utf-8'))

def isOnline(name):
    try:
        data = getStream(name)
        if data['stream'] == None:
            status = 1
        else:
            status = 0
    except:
        status = 2
    return status


PROCNAME = "python.exe"

if __name__ == '__main__':
    signal.signal(signal.SIGINT, signal_handler)
    running = False
    counter = 0
    name = getName()
    if not os.path.exists(name):
        os.makedirs(name)
    while(True):
        if not isOnline(name):
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
                process = subprocess.Popen(['livestreamer', \
                 'twitch.tv/' + name, 'best', '-o', \
                   str(counter) + '--' + str(start) + '.mp4'])
                counter = counter + 1
            if process.returncode == None:
                running = True
            else:
                running = False
            os.chdir('..')
        elif isOnline(name) == 1:
            print 'not online'
        else:
            print 'not strimmer'
            sys.exit()
        time.sleep(60*10)
            
    

    