#!/usr/bin/python


# v1 - 09/08/2016
# v2 - 01/11/2017 - implement timeout for upload

from datetime import datetime
from urllib import urlretrieve
from time import gmtime, strftime, mktime
import os
import time
import socket
import httplib
import requests
import glob
import sys
import ast


NIKON_DIR = "/home/pi/nikon/"
LOG_DIR = NIKON_DIR+"logs/"
LOG_DIR_OLD = LOG_DIR+"old/"
IMAGE_DIR = NIKON_DIR + "images/"
IMAGE_DIR_OLD = "/root/"
CONFIG_DIR = "config_files/"
BULK_UPLOAD_SIZE = 10

def write(s):
    currentTime = time.time()
    print str(currentTime)+": "+s
    logFile.flush()

f = open(NIKON_DIR+CONFIG_DIR+'id.txt','r')
id = (f.readline()).strip()
p = '{\'id\': \"'+id+'\", \'useEXIF\': \'false\'}'
payload = ast.literal_eval(p)
f.close()

g = open(NIKON_DIR+CONFIG_DIR+'server.txt','r')
url = g.readline().strip()
g.close()

################# setup logging #################
listOfFilesToMove = glob.glob(LOG_DIR+"upload_*.txt")
numberOfFilesToMove = len(listOfFilesToMove)
try:
    for x in range(0,numberOfFilesToMove):
        fileToMove = listOfFilesToMove[x].split(LOG_DIR)[1]
        print "Moving file "+fileToMove
        os.rename(LOG_DIR+fileToMove,LOG_DIR_OLD+fileToMove)
except:
    print "error moving log file"
    pass


log_Path = LOG_DIR+"upload_"+str(int(time.time()))+".txt"
logFile = open(log_Path, "a")
console = sys.stdout # This way we can restore the stdout back to the original console when we need it
sys.stdout = logFile
sys.stderr = logFile

###################################################

write("id: "+id)
write("url: "+url)

write("starting application")

while True:

    time.sleep(0.1)

    try:


        l = [(os.stat(i).st_mtime, i) for i in glob.glob(IMAGE_DIR+"*.jpg")]
        l.sort()
        listOfFiles = [i[1] for i in l]
        files = []
        numberToSend = 0
        if len(listOfFiles) > 1:
            if len(listOfFiles) > (BULK_UPLOAD_SIZE+1):
                numberToSend = BULK_UPLOAD_SIZE
            else:
                numberToSend = 1
            write("Sending "+str(numberToSend)+" file(s): ")
            for x in range(0,numberToSend):
                write("                 ["+listOfFiles[x]+"]")
                files.append(('images[]', (listOfFiles[x], open(listOfFiles[x], 'rb'), 'image/png')))
            r = requests.post(url, data=payload, files=files, timeout=10)

            response2 = str(r.json)
            if (response2.find("200") > 0):
                write("Got a 200 from server, image upload successful")
                write("Deleting Image(s)")
                for x in range(0,numberToSend):
                    try:
                        os.remove(listOfFiles[x])
                    except:
                        write("File "+listOfFiles[x]+" failed to delete")
            else:
                write("Bad response from server, image upload failed")
        else:
            write("No images to upload...")
            time.sleep(5)

    except:
        write("Unexpected error: "+str(sys.exc_info()[0]))
        time.sleep(5.0)
        continue











