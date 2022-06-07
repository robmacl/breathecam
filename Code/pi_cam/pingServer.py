#!/usr/bin/python

# v1 - 09/08/2016

import os
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

# If more than this many files backlogged (despite ping success), and backlog
# is increasing, then upload does not seem to be working. [count]
backlog_threshold = 10

# If the oldest image file is older than this, then image capture seems to be
# failing. [seconds]
#age_threshold = 120
age_threshold = 60

# If watchdog test fails on this many pings then something is wrong, and we
# should exit to force a reboot. [minutes]
#watchdog_threshold = 10
watchdog_threshold = 5


# Previous number of backlog images
prev_backlog = []

# Number of times which ping succeeded but the watchdog test failed.
failures = 0

while True:
    # Waiting first means we probably have a new image before we find the
    # image age, which prevents a spurious watchdog detect on startup.  (This
    # would be harmless in any case, since we need watchdog_threshold
    # consecutive failures before we reboot).
    time.sleep(60)

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
    # One fault that we *don't* deal with is that network access might
    # be failing in a way that would be recovered by reboot.  Probably
    # we should cover this, but one downside is that if there is no
    # network then we can't capture images for later upload because we
    # don't know the time.
    #
    # It is possible that the "backlog increasing" test could keep
    # failing when the network is connected (allowing pings) but
    # throughput is poor.  In comparison to this, when capture is
    # failing the test is more confident, and a fix from rebooting is
    # more likely.
    currentTime = int(time.time())
    files = glob.glob(conf.image_dir() + "*.jpg")

    # the age of the newest image file (sec)
    age = []
    for l in files:
        #l_time = int(l.split(conf.image_dir())[1].split('.')[0])
        l_time = os.stat(l).st_mtime
        diff = currentTime - l_time
        if not(age) or (diff < age):
            age = diff
    backlog = len(files)

    # If there are no images at all, then say images are really old to
    # possibly trigger watchdog.  The upload server always leaves at least one
    # image.
    if not(age):
        age = 1000000

    log.info("Image file backlog: %d, image age: %d", backlog, age)

    if success:
        if ((prev_backlog and (backlog > prev_backlog) and (backlog > backlog_threshold))
            or (age > age_threshold)):
            failures += 1
            log.warning("%d watchdog failures", failures)
        else:
            failures = 0
            
        if (failures >= watchdog_threshold):
            log.error("Repeated watchdog test failure, exiting to force reboot")
            exit()

    prev_backlog = backlog
