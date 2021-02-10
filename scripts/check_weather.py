#!/usr/bin/env python3
# ubrellaReminder.py a python script that scrapes weather.gov
# looks for rain in the closest forecast and tells me to bring an umbrella

import bs4
import requests
import logging
import os

if os.path.exists(r"~/logs/check_weather_log.txt"):
    logging.basicConfig(filename=r'~/logs/check_weather_log.txt',
                        level=logging.INFO,
                        format=' %(asctime)s - %(levelname)s - %(message)s')
else:
    logging.basicConfig(level=logging.INFO,
                        format=' %(asctime)s - %(levelname)s - %(message)s')


def get_sf_weather():
    logging.info("calling url")
    url = ("https://forecast.weather.gov/MapClick"
           ".php?lat=37.7744&lon=-122.4089#.XVC6b-hKjIU")

    res = requests.get(url)
    res.raise_for_status()
    logging.info("got response")

    soupObject = bs4.BeautifulSoup(res.text)
    content = soupObject.find(id="detailed-forecast-body")
    content = content.select("div")

    forecast = content[0].get_text()
    title = content[0].next.text
    logging.info("forecast: {}".format(forecast))
    logging.info("title: {}".format(title))

    trimmed_forecast = forecast[len(title):]

    full_forecast = "{}: {}".format(title, trimmed_forecast)

    logging.info("got forecast")
    logging.info(full_forecast)

    return full_forecast

if __name__ == "__main__":
    forecast = get_sf_weather()
    print(forecast)