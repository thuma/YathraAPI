# -*- coding: utf-8 -*-

import requests
import sys
import urllib
import json
import gevent
from gevent import Greenlet

reload(sys)
sys.setdefaultencoding('utf8')
sellers = {}
sellers["NSB"]         = "http://127.0.0.1:8800/nsb/?"
sellers["VT"]         = "http://127.0.0.1:8800/vt/?"
sellers["AEX"]        = "http://127.0.0.1:8800/at/?"
sellers["TIB"]         = "http://127.0.0.1:8800/tib/?"
sellers["OT"]         = "http://127.0.0.1:8800/ot/?"
sellers["SKTR"]     = "http://127.0.0.1:8800/sktr/?"
sellers["NETTBUSS"]    = "http://127.0.0.1:8800/nettbuss/?"
sellers["SJ"]         = "http://127.0.0.1:8800/sj/?"
sellers["HLT"]        = "http://127.0.0.1:8800/hlt/?"
sellers["SWEBUS"]     = "http://127.0.0.1:8800/swebus/?"
sellers["BT"]        = "http://127.0.0.1:8800/bt/?"
sellers["Snt"]         = "http://127.0.0.1:8800/snalltaget/?"
sellers["JLT"]         = "http://127.0.0.1:8800/jlt/?"
sellers["DTR"]         = "http://127.0.0.1:8800/dtr/?"
sellers["LTK"]         = "http://127.0.0.1:8800/ltk/?"
sellers["BTR"]        = "http://127.0.0.1:8800/btr/?"
sellers["XTR"]         = "http://127.0.0.1:8800/xtr/?"
sellers["KLT"]        = "http://127.0.0.1:8800/klt/?"
sellers["MAS"]         = "http://127.0.0.1:8800/mas/?"
sellers["SL"]         = "http://127.0.0.1:8088/sl/?"
sellers["SVBU"]     = "http://127.0.0.1:8800/svenskabuss/?"
sellers["MTR"]        = "http://127.0.0.1:8088/mtr/?"


def getprice(apiurl, pricequery):
    try:
       r = requests.get(apiurl+pricequery)
       return r.json()
    except:
       return {'error':'Unable to get price'}


def pricerequest(pricequery):
    global sellers
    prices = {}

    pricerequests = {}
    for seller in sellers:
        pricerequests[seller] = Greenlet.spawn(getprice, sellers[seller] ,pricequery)
    
    for seller in pricerequests:
        print "wait:" + seller
        pricerequests[seller].join()
        if pricerequests[seller].successful():
            print seller
            prices[seller] = pricerequests[seller].value

    return prices

def get(env, start_response):

    fromid = '7400001'
    toid = '7400002'
    startdate = '2015-11-23'
    starttime = '00:00'
    enddate = '2015-11-23'
    endtime = '24:00'

    url = 'https://api.resrobot.se/trip?'
    trips = {'Trip':[]}

    query = {
        'key': '886e3586-3fe5-4376-90ff-8817161a48cb',
        'originId': fromid,
        'destId': toid,
        'date': startdate,
        'time': starttime,
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
                    print trip['price']['url']
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
                
                    print trip['LegList']['Leg'][i]['price']['url']
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
        
    start_response('200 OK', [('Content-Type', 'application/json')])
    return json.dumps(trips)




