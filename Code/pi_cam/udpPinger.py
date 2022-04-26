#!/usr/bin/python

# v1 - 09/08/2016

import time
import socket
import glob
import sys
from socket import *
import logging
from serviceConfig import ServiceConfig

conf = ServiceConfig('./', 'udpPinger')
log = conf.logger

UDP_IP = ""
UDP_PORT = 6666

print("starting application with id: " + conf.camera_id())

sock = socket(AF_INET, SOCK_DGRAM)
sock.bind(('', 0))
sock.setsockopt(SOL_SOCKET, SO_BROADCAST, 1)

while True:
    try:
        currentTime = int(time.time())
        listOfFiles = glob.glob(conf.image_dir() + "*.jpg")

        minDiff = 100000000000
        diff = 0
        for l in listOfFiles:
            diff = currentTime - int(l.split(conf.image_dir())[1].split('.jpg')[0])
            if diff < minDiff:
                minDiff = diff

        message = ("RPI," + conf.camera_id() + "," +
                   str(len(listOfFiles)) + "," + str(minDiff))
        log.info("Sending " + message)
        sock.sendto(bytes(message, 'utf-8'), ('<broadcast>', UDP_PORT))
    except:
        log.error("Unexpected error: "+str(sys.exc_info()[0]))
        time.sleep(5.0)
        exit()

    time.sleep(5.0)
