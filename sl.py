# !/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import print_function
from gevent import monkey;
monkey.patch_all()
import requests
import json
import urlparse

stations = {}

try:
    with open('cache/sl/stations.json', 'r') as cachefile:
        stations = json.load(cachefile)
except:

    stationsget = requests.get('https://api.trafiklab.se/samtrafiken/gtfs/extra/agency_stops_275.txt?key=b4141ff657cfdd05df923ac21c057286')
    stationscsv = stationsget.text.split("\n")

    for row in stationscsv:
        try:
            parts = row.strip().split(",")
            stations[parts[1]] = {"StopPointNumber":parts[2]}
        except:
            pass

    stationsget = requests.get('http://api.sl.se/api2/LineData.json?model=StopPoint&key=0a28edfd9e8e49bf87c5ba27131ddb6a')

    stoppoints = stationsget.json()["ResponseData"]["Result"]
    points = {}
    stationsget = ""

    for point in stoppoints: 
        points[point["StopPointNumber"]] = point

    stoppoints = {}

    for station in stations:
        try:
            stations[station]["Zone"] = points[stations[station]["StopPointNumber"]]["ZoneShortName"]
        
            if float(points[stations[station]["StopPointNumber"]]["LocationNorthingCoordinate"]) > 59.2981056:
                stations[station]["N"] = "yes"
            else:
                stations[station]["N"] = "no"
        except:
            pass
            # Print missing data:
            #print(stations[station])

    points = {}

    with open('cache/sl/stations.json', 'w') as cachefile:
        json.dump(stations, cachefile)

def findprice(env, start_response):
    global stations
    start_response('200 OK', [('Content-Type', 'application/json')])
    getdata = urlparse.parse_qs(env['QUERY_STRING'])
    headers = {'content-type': 'application/json'}
    try:
        fromz  = stations[getdata['from'][0]]["Zone"]
        fromn  = stations[getdata['from'][0]]["N"]
        toz = stations[getdata['to'][0]]["Zone"]
        ton = stations[getdata['to'][0]]["N"]
    
    except:
        return '{"error":"station not in netowrk"}'
    
    if fromz == "A" and toz == "A":
       price = 25
    elif fromz == toz and fromn == ton:
       price = 25
    elif fromz == "A" and toz == "C":
       price = 50
    elif fromz == "C" and toz == "A":
       price = 50
    elif fromz == "B" or toz == "B":
       price = 37.5
    else:
       price = 50

    pricedata = {
       	       "departureTime":getdata['departureTime'][0],
		       "arrivalTime":getdata['arrivalTime'][0],
		       "date":getdata['date'][0],
		       "from":getdata['from'][0],
		       "to":getdata['to'][0],
       	       "travelerAge":35,
		       "travelerIsStudent":False,
		       "sellername":"SL",
		       "price":price,
		       "currency":"SEK",
		       "validPrice":True,
		       "url":"https://sl.se/sv/kop-biljett/#/reskassa"
    }
    
    return json.dumps(pricedata)
        
