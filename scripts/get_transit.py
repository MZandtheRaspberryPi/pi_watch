import requests
import json
import pprint
from datetime import datetime
import pytz
import copy
# get_transit.py shows real time arrival predictions for stops

# for bart direction, 203806 is south

# issue for why gotta set encoding
# https://github.com/kennethreitz/requests/issues/2296
# notes on format of response
# http://assets.511.org/pdf/nextgen/developers/Open_511_Data_Exchange_Specification_v1.26_Transit.pdf
# can use this to lookup stop ids
# https://511.org/transit/agencies/stop-id
metro_mission_seventh_outbound_stop_id = 15539
metro_mission_seventh_inbound_stop_id = 17129
metro_mission_eleventh_inbound_stop_id = 15544
metro_mission_eleventh_outbound_stop_id = 15545
metro_mission_ninth_inbound_stop_id = 15542
metro_mission_ninth_outbound_stop_id = 15543
metro_outbound_civic_center_stop_id = 16997
metro_inbound_civic_center_stop_id = 15727
bart_civic_center = "CIVC"

muni = "SF"
bart = "BA"

inbound_muni = {muni: {"Missn&11": {"IB": metro_mission_eleventh_inbound_stop_id},
                       "CivCtr": {"IB": metro_inbound_civic_center_stop_id}}}

outbound_muni = {muni: {"Missn&11": {"OB": metro_mission_eleventh_outbound_stop_id},
                        "CivCtr": {"OB": metro_outbound_civic_center_stop_id}}}

southbound_bart = {bart: {"CivCtr": {bart_civic_center: ["S"]}}} # used to use these ids "203806", "203820", "203822", "204442",

northbound_bart = {bart: {"CivCtr": {bart_civic_center: ["N"]}}} # "203807", "203819", "203821", "204444",


def get_rt_arrivals_muni(agency_and_stops, my_511_token=""):
    arrivals = {}
    for agency in agency_and_stops.keys():
        for stop in agency_and_stops[agency].keys():
            for direction in agency_and_stops[agency][stop]:
                arrivals.setdefault(stop, {})

                url = "http://api.511.org/transit/StopMonitoring?api_key=" \
                        + my_511_token + "&agency=" + agency \
                        + "&stopCode=" \
                        + str(agency_and_stops[agency][stop][direction])

                response = requests.get(url)
                response.raise_for_status()
                response.encoding = 'utf-8-sig'  # trims off the BOM, or you could say 'utf-8' to leave it

                real_time_data = json.loads(response.text)
                utc_timezone = pytz.timezone("UTC")
                pst_timezone = pytz.timezone("US/Pacific")

                now = datetime.now()
                now = pst_timezone.localize(now)

                for arrival in real_time_data['ServiceDelivery']['StopMonitoringDelivery']['MonitoredStopVisit']:
                    direction_response = arrival['MonitoredVehicleJourney']['DirectionRef']
                    if direction_response not in list(agency_and_stops[agency][stop].keys()):
                        continue
                    line_ref = arrival['MonitoredVehicleJourney']['LineRef']
                    arrival_time = arrival['MonitoredVehicleJourney']['MonitoredCall']['ExpectedArrivalTime']
                    arrival_time = datetime.strptime(arrival_time, "%Y-%m-%dT%H:%M:%SZ")
                    arrival_time = utc_timezone.localize(arrival_time)
                    arrival_time_pst = arrival_time.astimezone(pst_timezone)
                    time_till_arrival = arrival_time_pst - now
                    seconds_till_arrival = round(time_till_arrival.seconds/60)
                    arrivals[stop].setdefault(line_ref, []).append(seconds_till_arrival)

    return arrivals

def get_rt_arrivals_bart(agency_and_stops, my_511_token="", str_real_time=True):
    arrivals = {}
    for agency in agency_and_stops.keys():
        for stop in agency_and_stops[agency].keys():
            for bart_stop_code in agency_and_stops[agency][stop].keys():
                arrivals.setdefault(stop, {})

                url = "http://api.511.org/transit/StopMonitoring?api_key=" \
                        + my_511_token + "&agency=" + agency \
                        + "&stopCode=" \
                        + bart_stop_code

                response = requests.get(url)
                response.raise_for_status()
                response.encoding = 'utf-8-sig' # trims off the BOM, or you could say 'utf-8' to leave it

                real_time_data = json.loads(response.text)
                utc_timezone = pytz.timezone("UTC")
                pst_timezone = pytz.timezone("US/Pacific")

                now = datetime.now()
                now = pst_timezone.localize(now)

                for arrival in real_time_data['ServiceDelivery']['StopMonitoringDelivery']['MonitoredStopVisit']:
                    direction_response = arrival['MonitoredVehicleJourney']['DirectionRef']
                    if direction_response not in agency_and_stops[agency][stop][bart_stop_code]:
                        continue
                    line_ref = arrival['MonitoredVehicleJourney']['LineRef']
                    arrival_time = arrival['MonitoredVehicleJourney']['MonitoredCall']['ExpectedArrivalTime']
                    arrival_time = datetime.strptime(arrival_time,
                                                     "%Y-%m-%dT%H:%M:%SZ")
                    arrival_time = utc_timezone.localize(arrival_time)
                    arrival_time_pst = arrival_time.astimezone(pst_timezone)
                    time_till_arrival = arrival_time_pst - now
                    time_till_arrival_str = str(round(time_till_arrival.seconds/60))
                    if real_time_data:
                        time_till_arrival_str += "*"
                    #arrival_time_pst_string = arrival_time_pst.strftime("%H:%M")
                    arrivals[stop].setdefault(line_ref, []).append(round(time_till_arrival.seconds/60))

    return arrivals

def get_rt_arrivals(agency_and_stops_muni, agency_and_stops_bart, my_511_token=""):
    muni_arrivals = get_rt_arrivals_muni(agency_and_stops_muni, my_511_token=my_511_token)
    bart_arrivals = get_rt_arrivals_bart(agency_and_stops_bart, my_511_token=my_511_token)
    arrivals = copy.deepcopy(muni_arrivals)
    for bart_arrival in bart_arrivals["CivCtr"].keys():
        arrivals["CivCtr"][bart_arrival] = bart_arrivals["CivCtr"][bart_arrival]
    return arrivals

def checkBart(my_511_token=""):
    url = "http://api.511.org/transit/StopMonitoring?api_key=" \
            + my_511_token + "&agency=" + "BA"

    response = requests.get(url)
    response.raise_for_status()
    response.encoding = 'utf-8-sig' # trims off the BOM, or you could say 'utf-8' to leave it

    real_time_data = json.loads(response.text)

    return real_time_data

def get_northbound_arrivals(my_511_token=""):
    north_arrivals = get_rt_arrivals(inbound_muni, northbound_bart, my_511_token=my_511_token)
    return north_arrivals

def get_southbound_arrivals(my_511_token=""):
    south_arrivals = get_rt_arrivals(outbound_muni, southbound_bart, my_511_token=my_511_token)
    return south_arrivals

if __name__ == "__main__":
    my_511_token = ""
    north_arrivals = get_rt_arrivals(inbound_muni, northbound_bart, my_511_token=my_511_token)
    south_arrivals = get_rt_arrivals(outbound_muni, southbound_bart, my_511_token=my_511_token)
    pprint.pprint(north_arrivals)
    pprint.pprint(south_arrivals)


    bart_data = checkBart(my_511_token=my_511_token)
    print("hi")
    # bart_text_file = open("bart_data.txt",'w')
    # bart_text_file.write(pprint.pformat(bart_data))
    # bart_text_file.close()
