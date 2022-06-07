#!/usr/bin/python3

import RPi.GPIO as gp
import os
import sys
import logging

logger = logging.getLogger('ArducamMux')

gp.setwarnings(False)
gp.setmode(gp.BOARD)

gp.setup(7, gp.OUT)
gp.setup(11, gp.OUT)
gp.setup(12, gp.OUT)

# These codes go to GPIO 7, 11, 12 to switch the mux.
mux_codes = [
    [False, False, True],
    [True, False, True],
    [False, True, False],
    [True, True, False]
    ]

def select (cam_id):
    '''Select a camera input 0..3 on the Arducam multi-camera adapter'''
    if cam_id < 0 or cam_id > 3:
        logger.warning('Camera ID out of range: %d', cam_id)
        cam_id = 0

    logger.info('Selecting camera %d', cam_id)
    i2c = "i2cset -y 1 0x70 0x00 0x0%x" % (cam_id + 0x4)
    os.system(i2c)
    gp.output(7, mux_codes[cam_id][0])
    gp.output(11, mux_codes[cam_id][1])
    gp.output(12, mux_codes[cam_id][2])

if __name__ == "__main__":
    select(int(sys.argv[1]))
