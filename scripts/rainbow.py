#!/usr/bin/env python

import colorsys
import math
import time
import datetime

import unicornhat as unicorn


unicorn.set_layout(unicorn.PHAT)
unicorn.rotation(0)
unicorn.brightness(0.5)

# print("Reticulating splines")
# time.sleep(.5)
# print("Enabled unicorn poop module!")
# time.sleep(.5)
# print("Pooping rainbows...")

def rainbow(endClockTime):
    unicorn.set_layout(unicorn.PHAT)
    unicorn.rotation(0)
    unicorn.brightness(.5)
    i = 0.0
    offset = 30
    while True:
        dt = datetime.datetime.now()
        clockTime = dt.strftime('%H%M')
        clockTime = int(clockTime)
        i = i + 0.3
        for y in range(4):
            for x in range(8):
                r = 0#x * 32
                g = 0#y * 32
                xy = x + y / 4
                r = (math.cos((x+i)/2.0) + math.cos((y+i)/2.0)) * 64.0 + 128.0
                g = (math.sin((x+i)/1.5) + math.sin((y+i)/2.0)) * 64.0 + 128.0
                b = (math.sin((x+i)/2.0) + math.cos((y+i)/1.5)) * 64.0 + 128.0
                r = max(0, min(255, r + offset))
                g = max(0, min(255, g + offset))
                b = max(0, min(255, b + offset))
                unicorn.set_pixel(x,y,int(r),int(g),int(b))
        unicorn.show()
        if clockTime == endClockTime:
            break
        time.sleep(0.01)

if __name__ == "__main__":
    rainbow(int(datetime.datetime.now().strftime("%H%M"))+1)
