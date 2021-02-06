#!/usr/bin/env python3
#wrist_light_show.py, a script that cycles colors in a pimoroni unicorn pHAT in waves to pulse with colorful light.

import logging
import datetime
import time
import unicornhat as uh
import rainbow
import random

def setAllPixels(r,g,b,brightness):
    uh.brightness(brightness)
    for x in range(8):
        for y in range(4):
            uh.set_pixel(x, y, r, g, b)
    uh.show()

def pulse(r,g,b,maxBrightness=.5,pulseTimeInterval=.01,brightStepInterval=1):
    brightRange = list(range(300,int(maxBrightness*1000),brightStepInterval))
    while True:
        for brightness in brightRange:
            setAllPixels(r,g,b,brightness/1000)
            time.sleep(pulseTimeInterval)
        brightRange.reverse()
        for brightness in brightRange:
            setAllPixels(r,g,b,brightness/1000)
            time.sleep(pulseTimeInterval)
        brightRange.reverse()

def wave(r,g,b,brightness):
    uh.brightness(brightness)
    random_distance = 80
    while True:
        new_r = r + int(random.uniform(-1*random_distance, random_distance))
        new_g = r + int(random.uniform(-1*random_distance, random_distance))
        for x in range(8):
            for y in range(4):
                uh.set_pixel(x, y, new_r, new_g, b)
            uh.show()
            time.sleep(.2)
            uh.clear()

if __name__ == "__main__":
    # this won't be run when imported
    logging.basicConfig(level=logging.DEBUG, format=' %(asctime)s - %(levelname)s - %(message)s')
    logging.disable(logging.DEBUG)
    logging.info('running lamp...')

    uh.set_layout(uh.PHAT)

    blueViolet = [138,43,226]
    r,g,b = blueViolet[0],blueViolet[1],blueViolet[2]
    #wave(r,g,b,.5)
    pulse(r, g, b)
