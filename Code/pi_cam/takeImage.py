# import time
# import os
# import glob
# import sys
import subprocess
# import ast
# import requests
# from datetime import datetime
# from time import gmtime, strftime, mktime

import logging


interval = 5

f = open(HOME_DIR+CONFIG_DIR+'id.txt','r')
id = (f.readline()).strip()
p = '{\'id\': \"'+id+'\"}'
payload = ast.literal_eval(p)
f.close()

s = open(HOME_DIR+CONFIG_DIR+'pingserver.txt','r')
pingurl = s.readline().strip()
s.close()

uuid = "".join("{:02x}".format(ord(c)) for c in id)
pingpayload = "id="+id + "&uuid=" + uuid



# Formerly related to writing files in a different place than the
# output directory.  This seems to be mainly to rename the image file
# to one with the timestamp.
#
# With the logs the OLD directory is actually an old log, from a
# previous run, while with images we are just moving grabbed images to
# the output folder (and renaming).
def movePics(newName):
    logging.info("rename & move picture to 'images' folder ("+str(newName)+")")
    fileToRename = glob.glob(IMAGE_DIR_OLD+"*.JPG")
    fileToRename = fileToRename + glob.glob(IMAGE_DIR_OLD+"*.jpg")
    numberOfFilesToRename = len(fileToRename)
    try:
        if numberOfFilesToRename > 0:
            logging.info("renaming file "+fileToRename[0])
            os.rename(fileToRename[0],IMAGE_DIR+str(newName)+".jpg")
        else:
            logging.info("no files to rename...")
            exit()
    except:
        logging.warning("error renaming file: "+fileToRename[0])





def checkInternet():
    try:
        print "Sending ping to server"

        r = requests.post(pingurl, data=pingpayload, timeout = 5)
        response2 = str(r.json)
        if (response2.find("200") > 0):
            print "Got a 200 from server, ping successful"
            return 1
    except:
        print "Unexpected error: "+str(sys.exc_info()[0])

    return 0

while not checkInternet():
    logging.info("waiting for time sync")
    time.sleep(5.0)

time.sleep(30)

logging.info("Removing old files on computer")
removePics()

while True:
    startTime = time.time()
    if ((int(startTime) % interval) == 0):
        usage = checkDiskUsage()
        logging.info("Disk Usage = "+str(usage)+"%")
        if usage < 90:

            logging.info("Take & download an image")
            logging.info("\r\n"+subprocess.check_output(captureImageAndDownload, shell=True))

            movePics(int(startTime))

            endTime = time.time()
            logging.info("******************* process took "+str(endTime-startTime)+" seconds ****************")
        else:
            logging.warning("Disk too full...")
            time.sleep(5.0)
    else:
        time.sleep(0.1)
