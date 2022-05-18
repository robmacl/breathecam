#!/usr/bin/python

# v1 - 09/08/2016

import time
import requests
import glob
import logging
import sys
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

# If more than this many files backlogged (despite ping success), then upload
# does not seem to be working. [count]
backlog_threshold = 10

# If the oldest file (since last successful ping) is older than this, then
# image capture seems to be failing. [seconds]
age_threshold = 120

# If watchdog test fails on this many pings then something is wrong, and we
# should exit to force a reboot. [minutes]
watchdog_threshold = 10


# Previous number of backlog images
prev_backlog = []

# Number of times which ping succeeded but the watchdog test failed.
failures = 0

# The last time that ping failed. This is used to disregard image backlogs
# that may be due to periods of connection failure.
fail_time = int(time.time())

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
    #  -- image backlog is increasing (upload failing), or
    #  -- we are not getting any new images (image capture failing)
    #
    # If either test fails on watchdog_threshold consecutive pings,
    # then we exit, which causes a reboot in the launcher script.
    #
    # For age, we don't count images from before the last ping failure
    # (or startup), since we might not yet have captured a new image.
    # This avoids a spurious watchdog trip at startup (which would not
    # anyway cause a reboot unless it repeats).
    #
    # One fault that we *don't* deal with is that network access might
    # be failing in a way that would be recovered by reboot.  Probably
    # we should cover this, but one downside is that if there is no
    # network then we can't capture images for later upload because we
    # don't know the time.
    #
    # It is possible that the "backlog increasing" test could keep
    # failing when the network is connected (allowing pings) but
    # throughput is poor.
    #
    # Compared to the upload backlog test, when capture is failing the
    # test is more confident, and a fix from rebooting is more likely.
    currentTime = int(time.time())
    files = glob.glob(conf.image_dir() + "*.jpg")

    # the age of the newest image file (sec)
    age = []
    for l in files:
        l_time = int(l.split(conf.image_dir())[1].split('.jpg')[0])
        if l_time > fail_time:
            diff = currentTime - l_time
            if not(age) or (diff < age):
                age = diff
    backlog = len(files)
    log.info("Image file backlog: %d, image age: %d", backlog, age or 0)

    if success:
        if ((prev_backlog and (backlog > prev_backlog) and (backlog > backlog_threshold))
            or (age and age > age_threshold)):
            failures += 1
            log.warning("%d watchdog failures", failures)
        else:
            failures = 0
            
        if (failures >= watchdog_threshold):
            log.error("Repeated watchdog test failure, exiting to force reboot")
            exit()

    prev_backlog = backlog
    time.sleep(60)
