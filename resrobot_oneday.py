# -*- coding: utf-8 -*-

import requests
import sys
import urllib
import json
import gevent
from gevent import Greenlet

reload(sys)
sys.setdefaultencoding('utf8')

def getprice(apiurl, pricequery):
    try:
       r = requests.get(apiurl+pricequery)
       return r.json()
    except:
       return {'error':'Unable to get price'}


def pricerequest(pricequery):
    prices = {}
    sellers = {}
    sellers["NSB"]         = "http://api.yathra.se:8800/nsb/?"
    sellers["VT"]         = "http://api.yathra.se:8800/vt/?"
    sellers["AEX"]        = "http://api.yathra.se:8800/at/?"
    sellers["TIB"]         = "http://api.yathra.se:8800/tib/?"
    sellers["OT"]         = "http://api.yathra.se:8800/ot/?"
    sellers["SKTR"]     = "http://api.yathra.se:8800/sktr/?"
    sellers["NETTBUSS"]    = "http://api.yathra.se:8800/nettbuss/?"
    sellers["SJ"]         = "http://api.yathra.se:8800/sj/?"
    sellers["HLT"]        = "http://api.yathra.se:8800/hlt/?"
    sellers["SWEBUS"]     = "http://api.yathra.se:8800/swebus/?"
    sellers["BT"]        = "http://api.yathra.se:8800/bt/?"
    sellers["Snt"]         = "http://api.yathra.se:8800/snalltaget/?"
    sellers["JLT"]         = "http://api.yathra.se:8800/jlt/?"
    sellers["DTR"]         = "http://api.yathra.se:8800/dtr/?"
    sellers["LTK"]         = "http://api.yathra.se:8800/ltk/?"
    sellers["BTR"]        = "http://api.yathra.se:8800/btr/?"
    sellers["XTR"]         = "http://api.yathra.se:8800/xtr/?"
    sellers["KLT"]        = "http://api.yathra.se:8800/klt/?"
    sellers["MAS"]         = "http://api.yathra.se:8800/mas/?"
    sellers["SL"]         = "http://api.yathra.se:8088/sl/?"
    sellers["SVBU"]     = "http://api.yathra.se:8800/svenskabuss/?"
    sellers["MTR"]        = "http://api.yathra.se:8088/mtr/?"
    
    pricerequests = {}
    for seller in sellers:
        pricerequests[seller] = Greenlet.spawn(getprice, sellers[seller] ,pricequery)
    
    for seller in pricerequests:
        pricerequests[seller].join()
        if pricerequests[seller].successful():
            prices[seller] = pricerequests[seller].value

    return prices

fromid = '7400001'
toid = '7400002'
date = '2015-10-23'

url = 'https://api.resrobot.se/trip?'
trips = {'Trip':[]}

query = {
    'key':'886e3586-3fe5-4376-90ff-8817161a48cb',
    'originId':fromid,
    'destId':toid,
    'date': date,
    'time':'00:00',
    'numB':'0',
    'format':'json'}
    
row = 0
notfull = True
while notfull:
    r = requests.get(url+urllib.urlencode(query))
    data = r.json()
    for trip in data['Trip']:
        if trip['LegList']['Leg'][0]['Origin']['date'] == date:
            trip['idx'] = row
            trip['tripId'] = 'C-' + str(trip['idx'])

            if trip['LegList']['Leg'][-1]['type'] == 'WALK':
                del trip['LegList']['Leg'][-1]

            if trip['LegList']['Leg'][0]['type'] == 'WALK':
                del trip['LegList']['Leg'][0]
            
            if len(trip['LegList']['Leg']) != 1:
                trip['price'] = {"url":urllib.urlencode({
                    'from':trip['LegList']['Leg'][0]['Origin']['id'],
                    'to':trip['LegList']['Leg'][-1]['Destination']['id'],
                    'date':trip['LegList']['Leg'][0]['Origin']['date'],
                    'departureDate':trip['LegList']['Leg'][0]['Origin']['date'],
                    'departureTime':trip['LegList']['Leg'][0]['Origin']['time'][0:5],
                    'arrivalDate':trip['LegList']['Leg'][-1]['Destination']['date'],
                    'arrivalTime':trip['LegList']['Leg'][-1]['Destination']['time'][0:5]
                    })
                    }
                trip['price']['list'] =  pricerequest(trip['price']['url'])
                
            for i in range(len(trip['LegList']['Leg'])):
                tripinfo = trip['LegList']['Leg'][i]
                stops = []
                if 'Stops' in tripinfo:
                    for stop in tripinfo['Stops']['Stop']:
                        stops.append(stop['id'])
                trip['LegList']['Leg'][i]['price'] = {"url":urllib.urlencode({
                    'from':tripinfo['Origin']['id'],
                    'to':tripinfo['Destination']['id'],
                    'date':tripinfo['Origin']['date'],
                    'departureDate':tripinfo['Origin']['date'],
                    'departureTime':tripinfo['Origin']['time'][0:5],
                    'arrivalDate':tripinfo['Destination']['date'],
                    'arrivalTime':tripinfo['Destination']['time'][0:5],
                    'stops': ','.join(stops)})
                    }
                    
                trip['LegList']['Leg'][i]['price']['list'] =  pricerequest(
                    trip['LegList']['Leg'][i]['price']['url']
                    )
            
            #Print one trip at the time here:
            trips['Trip'].append(trip)
            print json.dumps(trip)
            
        else:
            notfull = False
            break 
        row = row + 1 
    query['context'] = data['scrF']
    
print json.dumps(trips)




