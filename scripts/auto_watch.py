from papirus import PapirusTextPos
import datetime
import time
import logging
from gpiozero import Button
import os
import subprocess

time.sleep(20)

logging.basicConfig(filename = '~/logs/auto_watch.log', level=logging.DEBUG,
         format=' %(asctime)s - %(levelname)s - %(message)s')
logging.disable(logging.DEBUG)

# Defining EPD_SIZE
EPD_SIZE = 2.0

# Running as root only needed for older Raspbians without /dev/gpiomem
if not (os.path.exists('/dev/gpiomem') and os.access('/dev/gpiomem', os.R_OK | os.W_OK)):
    user = os.getuid()
    if user != 0:
        print('Please run script as root')
        sys.exit()
# Definitions for Papirus Zero
SW1 = 21
SW2 = 16
SW3 = 20
SW4 = 19
SW5 = 26

shutdown_button = Button(SW1, pull_up=False)
upButton = Button(SW2, pull_up=False)
downButton = Button(SW3, pull_up=False)
rightButton = Button(SW4, pull_up=False)
exitButton = Button(SW5, pull_up=False)

def setkey(device):
    global key
    pinnr = device.pin.number
    if   pinnr == SW1: key |= shutdown
    elif pinnr == SW2: key |= UP
    elif pinnr == SW3: key |= DOWN
    elif pinnr == SW4: key |= RIGHT
    elif pinnr == SW5: key |= LEFT|UP
    else:
        key = 0

def getkey():
    global key
    return key

try:
    font_path = "/home/mikey/Documents/Pi/nasalization-rg.ttf"
    text_size = 70

    text = PapirusTextPos(rotation=0)
    text.Clear()

    old_time = datetime.datetime.now().strftime("%H:%M")
    text.AddText(old_time, size=text_size, fontPath=font_path)
    time.sleep(10)
    logging.info("Entering watch loop")
    while True:
        # Define button press action (Note: inverted logic w.r.t. gpiozero)
        shutdown_button.when_released  = setkey
        upButton.when_released    = setkey
        downButton.when_released  = setkey
        rightButton.when_released = setkey
        exitButton.when_released = setkey

        # check key
        key = getKey()
        if key == 0:
            new_time = datetime.datetime.now().strftime("%H:%M")
            if old_time == new_time:
                time.sleep(1)
                continue
            text.Clear()
            text.AddText(new_time, size=text_size, fontPath=font_path)
            old_time = new_time
            time.sleep(1)
        elif key == "shutdown":
            logging.info("shutting down")
            subprocess.Popen(['sudo', 'shutdown', '-h', 'now'])
except Exception as e:
    logging.fatal(e, exc_info=True)  # log exception info at FATAL log level
