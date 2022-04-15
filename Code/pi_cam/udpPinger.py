#!/usr/bin/python

# v1 - 09/08/2016

import time
import socket
import glob
import sys
from socket import *


NIKON_DIR = "/home/pi/nikon/"
IMAGE_DIR = NIKON_DIR + "images/"
CONFIG_DIR = "config_files/"

f = open(NIKON_DIR+CONFIG_DIR+'id.txt','r')
id = (f.readline()).strip()
f.close()


UDP_IP = ""
UDP_PORT = 6666

print "starting application with id: "+id

sock = socket(AF_INET, SOCK_DGRAM)
sock.bind(('', 0))
sock.setsockopt(SOL_SOCKET, SO_BROADCAST, 1)

while True:
    try:
        currentTime = int(time.time())
        listOfFiles = glob.glob(IMAGE_DIR+"*.jpg")
        print "Number of files "+str(len(listOfFiles))

        minDiff = 100000000000
        diff = 0
        for l in listOfFiles:
            diff = currentTime - int(l.split(IMAGE_DIR)[1].split('.jpg')[0])
            if diff < minDiff:
                minDiff = diff

        MESSAGE = "RPI,"+id+","+str(len(listOfFiles))+","+str(minDiff)

        sock.sendto(MESSAGE, ('<broadcast>', UDP_PORT))
    except:
        print "Unexpected error: "+str(sys.exc_info()[0])
        time.sleep(5.0)
        exit()

    time.sleep(5.0)











