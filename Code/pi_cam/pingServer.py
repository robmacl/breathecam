#!/usr/bin/python

# v1 - 09/08/2016

import time
import requests
import glob
import logging
from serviceConfig import ServiceConfig

conf = ServiceConfig('./', 'pingServer')
log = conf.logger

pingurl = "http://breathecam.cmucreatelab.org:80/location_pinger"

uuid = "".join("{:02x}".format(ord(c)) for c in conf.camera_id())
pingpayload = "id=" + conf.camera_id() + "&uuid=" + uuid

log.info("id: " + conf.camera_id())
log.info("pingurl: "+pingurl)
log.info("pingpayload: "+pingpayload)
log.info("starting application")

# Previous number of backlog images
prev_backlog = []

# Number of times which ping succeeded but the watchdog test failed.
failures = 0

while True:
    success = False
    try:
        log.debug("Sending ping to server")

        r = requests.post(pingurl, data=pingpayload, timeout = 5)
        response2 = str(r.json)
        if (response2.find("200") > 0):
            log.info("Got a 200 from server, ping successful")
            success = True
        else:
            log.warning("Bad response from server, ping failed: "
                        + response2)

    except:
        log.error("Unexpected error: "+str(sys.exc_info()[0]))


    # This is our watchdog code.  If we are pinging, but either:
    #  -- images are piling up, or
    #  -- we are not getting any new images
    #
    # then we exit, which causes a reboot in the launcher script. 
    currentTime = int(time.time())
    files = glob.glob(conf.image_dir() + "*.jpg")

    age = []
    diff = 0
    for l in files:
        diff = currentTime - int(l.split(conf.image_dir())[1].split('.jpg')[0])
        if not(age) or (diff < age):
            age = diff
    backlog = len(files)
    log.info("Image file backlog: %d, image age: %d", backlog, age or 0)

    if success:
        if ((prev_backlog and (backlog > prev_backlog) and (backlog > 10))
            or (age and age > 120)):
            failures += 1
            log.warning("%d watchdog failures", failures)
        else:
            failures = 0
            
        if (failures >= 10):
            log.error("Repeated watchdog test failure, exiting to force reboot")
            exit()

    prev_backlog = backlog
    time.sleep(60)
