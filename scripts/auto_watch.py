from papirus import PapirusTextPos
import datetime
import time
import logging
from gpiozero import Button
import os
import subprocess
import sys

from check_weather import get_sf_weather
from get_transit import get_northbound_arrivals, get_southbound_arrivals

time.sleep(3)
if os.path.exists(r"/home/mikey/logs/watch.log"):
    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    ch.setFormatter(formatter)
    logger.addHandler(ch)
    logging.basicConfig(filename=r'/home/mikey/logs/watch.log',
                        level=logging.INFO,
                        format=' %(asctime)s - %(levelname)s - %(message)s',
                        handlers=[ch])

else:
    print("not file watcher")
    logging.basicConfig(level=logging.INFO,
                        format=' %(asctime)s - %(levelname)s - %(message)s')

my_511_token = sys.argv[1]

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
north_transit_button = Button(SW2, pull_up=False)
south_transit_button = Button(SW3, pull_up=False)
weather_button = Button(SW4, pull_up=False)
button5 = Button(SW5, pull_up=False)

def display_arivals(text, arrivals):
    logging.info("arivals {}".format(arrivals))
    text.Clear()
    for stop in sorted(arrivals.keys(), reverse=True):
        text1 = stop
        for route in arrivals[stop].keys():
            # truncating routes w/ long names, for bart with long ones
            text2 = (route[:5] + '.:') if len(route) > 5 else route + ":"
            # appending arrival times for each route
            for arrival in arrivals[stop][route]:
                text2 += " "
                text2 += str(arrival)
            text.AddText("{}\n{}".format(text1, text2), size=15, fontPath=font_path)
            time.sleep(5)
            text.Clear()

def setkey(device):
    global key
    pinnr = device.pin.number
    if pinnr == SW1: key = 'shutdown'
    elif pinnr == SW2: key = 'n_transit'
    elif pinnr == SW3: key = 's_transit'
    elif pinnr == SW4: key = 'weather'
    elif pinnr == SW5: key = 'button5'
    else:
        key = 0

def getkey():
    global key
    return key

try:
    key = 'none'
    font_path = "/home/mikey/nasalization-rg.ttf"
    text_size = 60

    text = PapirusTextPos(rotation=0)
    text.Clear()

    old_time = datetime.datetime.now().strftime("%H:%M")
    text.AddText(old_time, size=text_size, fontPath=font_path)
    time.sleep(10)
    logging.info("Entering watch loop")
    while True:
        # Define button press action (Note: inverted logic w.r.t. gpiozero)
        shutdown_button.when_released = setkey
        north_transit_button.when_released = setkey
        south_transit_button.when_released = setkey
        weather_button.when_released = setkey
        button5.when_released = setkey

        # check key
        key = getkey()
        if key == 'none':
            new_time = datetime.datetime.now().strftime("%H:%M")
            if old_time == new_time:
                time.sleep(1)
                continue
            text.Clear()
            text.AddText(new_time, size=text_size, fontPath=font_path)
            old_time = new_time
            time.sleep(.3)
        elif key == "shutdown":
            logging.info("shutting down")
            text.Clear()
            text.AddText("Bye :)", size=text_size, fontPath=font_path)
            time.sleep(2)
            shutdown_path = __file__.split("/")[:-1]
            shutdown_path = "/".join(shutdown_path)
            # if started script manually, from the scripts directory, will see blank path to file
            if shutdown_path == "":
                shutdown_path = "."
            subprocess.Popen(['sudo', '{}/shutdown.sh'.format(shutdown_path)])
            sys.exit()
        elif key == "n_transit":
            logging.info("getting n_transit")
            n_transit = get_northbound_arrivals(my_511_token=my_511_token)
            display_arivals(text, n_transit)
            key = 'none'
            old_time = "fake time"
        elif key == "s_transit":
            logging.info("getting s_transit")
            s_transit = get_southbound_arrivals(my_511_token)
            display_arivals(text, s_transit)
            key = 'none'
            old_time = "fake time"
        elif key == "weather":
            logging.info("getting weather")
            weather = get_sf_weather()
            text.Clear()
            text.AddText(weather, size=15, fontPath=font_path)
            time.sleep(7)
            key = 'none'
            old_time = "fake time"
        elif key == "button5":
            logging.info("button 5 pressed")
            key = 'none'

except Exception as e:
    logging.fatal(e, exc_info=True)  # log exception info at FATAL log level

