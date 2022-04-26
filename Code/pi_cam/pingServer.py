#!/usr/bin/python

# v1 - 09/08/2016

import time
import requests
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

while True:
    try:
        log.debug("Sending ping to server")

        r = requests.post(pingurl, data=pingpayload, timeout = 5)
        response2 = str(r.json)
        if (response2.find("200") > 0):
            log.info("Got a 200 from server, ping successful")
        else:
            log.warning("Bad response from server, ping failed: "
                        + response2)

    except:
        log.error("Unexpected error: "+str(sys.exc_info()[0]))

    time.sleep(60)
