# -*- coding: utf-8 -*-

import gevent
from gevent import Greenlet
from gevent import monkey;
monkey.patch_all()
import requests
import sys
import urllib
import json
import time
import urlparse

with open('../resrobot.key', 'r') as keyfile:
    key = keyfile.read().strip()

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
sellers["SJ"]         = "http://127.0.0.1:8088/sj/?"
sellers["HLT"]        = "http://127.0.0.1:8800/hlt/?"
sellers["SWEBUS"]     = "http://127.0.0.1:8088/swebus/?"
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

running = {}

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
        pricerequests[seller].join()
        if pricerequests[seller].successful():
            prices[seller] = pricerequests[seller].value

    return prices

def get(env, start_response):
    getdata = urlparse.parse_qs(env['QUERY_STRING'])
    fromid = getdata['from'][0]
    toid = getdata['to'][0]
    date = getdata['date'][0]
    tripno = int(getdata['tripno'][0])
    
    combined = fromid+toid+date
    
    while combined in running:
	print "lets sleep"
        time.sleep(1)
    
    try: 
        with open('cache/trips/'+fromid+toid+date+str(tripno), 'r') as data_file:
            print "founddata"
            start_response('200 OK', [('Content-Type', 'application/json')])
            returndata = data_file.read()
            print "fileread"
            return [returndata]
    except:
        print "Detailed cached failed"
        
    try:
        with open('cache/trips/'+fromid+toid+date) as data_file:    
            trips = json.load(data_file)
            start_response('200 OK', [('Content-Type', 'application/json')])
            print "found in cache"
            
    except:
        running[combined] = True
        print "not in cache" 
        url = 'https://api.resrobot.se/trip?'
        trips = {'Trip':[]}

        query = {
        'key': key,
        'originId': fromid,
        'destId': toid,
        'date': date,
        'time': '00:00',
        'numB':'0',
        'format':'json'}
    
        row = 0
        notfull = True
        
        while notfull:
            r = requests.get(url+urllib.urlencode(query))
            data = r.json()
        
            for trip in data['Trip']:
                if trip['LegList']['Leg'][0]['Origin']['date'] == date:
                    LegList = trip['LegList']['Leg']
                    trip['idx'] = row
                    trip['tripId'] = 'C-' + str(trip['idx'])
                    trip['LegList'] = {'Leg':[]}
                    
                    for i in range(len(LegList)):
                        if LegList[i]['type'] != 'WALK' and LegList[i]['type'] != 'TRSF': 
                            trip['LegList']['Leg'].append(LegList[i])  
            
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
                    trips['Trip'].append(trip)
                else:
                    with open('cache/trips/'+fromid+toid+date, 'w') as data_file:    
                        json.dump(trips, data_file)
                    notfull = False
                    del(running[combined])
                    break 
                row = row + 1
            query['context'] = data['scrF']
    
    
    start_response('200 OK', [('Content-Type', 'application/json')])
    try:
        trip = trips['Trip'][tripno]
    except:
        return '{"Status":"end"}'
    
    if 'price' in trip:
        print trip['price']
        trip['price']['list'] = pricerequest(trip['price']['url'])
    
    for i in range(len(trip['LegList']['Leg'])):
        print trip['LegList']['Leg'][i]['price']
        trip['LegList']['Leg'][i]['price']['list'] = pricerequest(trip['LegList']['Leg'][i]['price']['url'])
        
    with open('cache/trips/'+fromid+toid+date+str(tripno), 'w') as data_file:    
        json.dump(trip, data_file)

    return json.dumps(trip)



