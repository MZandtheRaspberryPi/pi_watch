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

# Definitions for Papirus Zero
SW1 = 21
SW2 = 16
SW3 = 20
SW4 = 19
SW5 = 26

# Defining EPD_SIZE
EPD_SIZE = 2.0

key = 'none'

def display_arivals(text, arrivals, logger, font_path):
    logger.info("arivals {}".format(arrivals))
    text.Clear()
    # example data
    # {'CivCtr': {'YL-N': [20, 50], 'RD-N': [12, 42], 'GN-N': [22, 37], 'BL-N': [2, 32]}, 'Missn&11': {'14R': [7, 13, 21], '14': [5, 7, 30]}}
    arrival_str_miss = "Missn&11" + "\n"
    arrival_str_civ = 'CivCtr' + "\n"
    civ_ctr_arrivals = sorted(arrivals["CivCtr"].keys(), reverse=True)
    miss_arrivals = sorted(arrivals["Missn&11"].keys(), reverse=True)

    for civ_arrival in civ_ctr_arrivals:
        arrival_times = [str(arriv) for arriv in arrivals["CivCtr"][civ_arrival]]
        arrival_times = ", ".join(arrival_times)
        str_to_add = civ_arrival + ": " +  arrival_times
        arrival_str_civ += str_to_add + "\n"

    for miss_arrival in miss_arrivals:
        arrival_times = [str(arriv) for arriv in arrivals["Missn&11"][miss_arrival]]
        arrival_times = ", ".join(arrival_times)
        str_to_add = miss_arrival + ": " + arrival_times
        arrival_str_miss += str_to_add + "\n"
    logger.info(arrival_str_miss)
    logger.info(arrival_str_civ)
    text.AddText(arrival_str_miss, size=15, fontPath=font_path, Id="Miss")
    time.sleep(3)
    text.RemoveText("Miss")
    text.AddText(arrival_str_civ, size=15, fontPath=font_path, Id="Civ")
    time.sleep(3)
    text.RemoveText("Civ")

def getkey():
    global key
    return key

def setkey(device):
    global key
    pinnr = device.pin.number
    if pinnr == SW1:
        key = 'shutdown'
    elif pinnr == SW2:
        key = 'n_transit'
    elif pinnr == SW3:
        key = 's_transit'
    elif pinnr == SW4:
        key = 'weather'
    elif pinnr == SW5:
        key = 'button5'
    else:
        key = 0


def main():
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.INFO)
    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    ch.setFormatter(formatter)
    logger.addHandler(ch)
    if os.path.exists(r"/home/mikey/logs/watch.log"):
        fh = logging.FileHandler(filename=r"/home/mikey/logs/watch.log")
        fh.setLevel(logging.DEBUG)
        fh.setFormatter(formatter)
        logger.addHandler(fh)

    my_511_token = sys.argv[1]

    # giving time for device service to startup, which is needed before init of Papirus
    time.sleep(20)

    try:
        global key
        # Running as root only needed for older Raspbians without /dev/gpiomem
        if not (os.path.exists('/dev/gpiomem') and os.access('/dev/gpiomem', os.R_OK | os.W_OK)):
            user = os.getuid()
            if user != 0:
                print('Please run script as root')
                sys.exit()

        shutdown_button = Button(SW1, pull_up=False)
        north_transit_button = Button(SW2, pull_up=False)
        south_transit_button = Button(SW3, pull_up=False)
        weather_button = Button(SW4, pull_up=False)
        button5 = Button(SW5, pull_up=False)

        font_path = "/home/mikey/nasalization-rg.ttf"
        text_size = 60

        text = PapirusTextPos(rotation=0)
        text.Clear()

        old_time = datetime.datetime.now().strftime("%H:%M")
        text.AddText(old_time, size=text_size, fontPath=font_path)
        logger.info("Entering watch loop")
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
                logger.info("shutting down")
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
                logger.info("getting n_transit")
                n_transit = get_northbound_arrivals(my_511_token=my_511_token)
                display_arivals(text, n_transit, logger, font_path)
                key = 'none'
                old_time = "fake time"
            elif key == "s_transit":
                logger.info("getting s_transit")
                s_transit = get_southbound_arrivals(my_511_token)
                display_arivals(text, s_transit, logger, font_path)
                key = 'none'
                old_time = "fake time"
            elif key == "weather":
                logger.info("getting weather")
                weather = get_sf_weather()
                text.Clear()
                text.AddText(weather, size=15, fontPath=font_path)
                time.sleep(7)
                key = 'none'
                old_time = "fake time"
            elif key == "button5":
                logger.info("button 5 pressed")
                key = 'none'
    except KeyboardInterrupt as e:
        logger.exception("keyboard interupt caught", exc_info=e)
    except Exception as e:
        logger.info("exception occured")
        logger.exception("Exception occured", exc_info=e)

if __name__ == "__main__":
    main()
