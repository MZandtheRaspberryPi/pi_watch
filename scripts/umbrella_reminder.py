#!/usr/bin/env python3
# ubrellaReminder.py a python script that scrapes weather.gov
# looks for rain in the closest forecast and tells me to bring an umbrella

import bs4
import requests
import textMyself
import logging
import sys

logging.basicConfig(filename=r'/home/mikey/logs/umbrellaReminderLog.txt',
                    level=logging.DEBUG,
                    format=' %(asctime)s - %(levelname)s - %(message)s')
logging.disable(logging.DEBUG)

try:

    url = ("https://forecast.weather.gov/MapClick"
           ".php?lat=37.7744&lon=-122.4089#.XVC6b-hKjIU")

    accountSID = sys.argv[1]
    authToken = sys.argv[2]
    myTwilioNumber = sys.argv[3]
    myCellPhone = sys.argv[4]

    res = requests.get(url)
    res.raise_for_status()

    soupObject = bs4.BeautifulSoup(res.text, features='lxml')
    content = soupObject.find(id="detailed-forecast-body")
    content = content.select("div")

    forecast = content[0].get_text()

    logging.info("got forecast")
    logging.info(forecast)

    if "rain" in forecast.lower():
        logging.info("rain found")
        textMyself.textmyself('Bring an umbrella, it may rain! \n\n'+forecast,
                              accountSID, authToken, myTwilioNumber, myCellPhone)
        logging.info("text sent")
except:
    logging.exception("fatal error.")
