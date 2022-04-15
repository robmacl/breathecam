#!/usr/bin/python

# v1 - 09/08/2016

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

def write(s):
    currentTime = time.time()
    print str(currentTime)+": "+s
    logFile.flush()

f = open(NIKON_DIR+CONFIG_DIR+'id.txt','r')
id = (f.readline()).strip()
p = '{\'id\': \"'+id+'\"}'
payload = ast.literal_eval(p)
f.close()

s = open(NIKON_DIR+CONFIG_DIR+'pingserver.txt','r')
pingurl = s.readline().strip()
s.close()

uuid = "".join("{:02x}".format(ord(c)) for c in id)
pingpayload = "id="+id + "&uuid=" + uuid

################# setup logging #################
listOfFilesToMove = glob.glob(LOG_DIR+"ping_*.txt")
numberOfFilesToMove = len(listOfFilesToMove)
try:
    for x in range(0,numberOfFilesToMove):
        fileToMove = listOfFilesToMove[x].split(LOG_DIR)[1]
        print "Moving file "+fileToMove
        os.rename(LOG_DIR+fileToMove,LOG_DIR_OLD+fileToMove)
except:
    print "error moving log file"
    pass


log_Path = LOG_DIR+"ping_"+str(int(time.time()))+".txt"
logFile = open(log_Path, "a")
console = sys.stdout # This way we can restore the stdout back to the original console when we need it
sys.stdout = logFile
sys.stderr = logFile

###################################################

write("id: "+id)
write("pingurl: "+pingurl)
write("pingpayload: "+pingpayload)

write("starting application")

while True:

    try:
        write("Sending ping to server")

        r = requests.post(pingurl, data=pingpayload, timeout = 5)
        response2 = str(r.json)
        if (response2.find("200") > 0):
            write("Got a 200 from server, ping successful")
        else:
            write(response2)
            write("Bad response from server, ping failed")


    except:
        write("Unexpected error: "+str(sys.exc_info()[0]))



    time.sleep(60)


