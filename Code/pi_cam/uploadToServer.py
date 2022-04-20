#!/usr/bin/python3
import os
import time
import requests
import glob
import sys
import logging

from serviceConfig import ServiceConfig

config = ServiceConfig('./', 'upload')

BULK_UPLOAD_SIZE = 10

while True:
    time.sleep(0.1)

    try:
        # We sort by modification time and don't send the most recent
        # file, to avoid race condition where the image is currently
        # being captured and only partly written.
        images = glob.glob(config.imageDir()+"*.jpg")
        l = [(os.stat(i).st_mtime, i) for i in images]
        l.sort()
        listOfFiles = [i[1] for i in l]

        files = []
        numberToSend = 0
        if len(listOfFiles) > 1:
            if len(listOfFiles) > (BULK_UPLOAD_SIZE+1):
                numberToSend = BULK_UPLOAD_SIZE
            else:
                numberToSend = 1
            logging.info("Sending "+str(numberToSend)+" file(s)")
            for x in range(0,numberToSend):
                logging.debug('Sending ' + listOfFiles[x]);
                files.append(('images[]', (listOfFiles[x], open(listOfFiles[x], 'rb'), 'image/png')))
            payload = {'id': config.cameraID(), 'useEXIF': 'false'}
            r = requests.post(config.serverURL(), data=payload, files=files, timeout=10)

            response2 = str(r.json)
            if (response2.find("200") > 0):
                logging.info("Got a 200 from server, image upload successful")
                logging.debug("Deleting Image(s)")
                for x in range(0,numberToSend):
                    try:
                        os.remove(listOfFiles[x])
                    except:
                        logging.warning("File "+listOfFiles[x]+" failed to delete")
            else:
                logging.error("Bad response from server, image upload failed")
        else:
            logging.debug("No images to upload...")
            time.sleep(5)

    except:
        logging.error("Unexpected error: ", sys.exc_info())
        time.sleep(5.0)
        continue
