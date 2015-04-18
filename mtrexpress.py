#!/usr/bin/python
from __future__ import print_function
from gevent.pywsgi import WSGIServer
from gevent import monkey;
monkey.patch_all()
import requests
import json
import urlparse

stations = {}
stationsget = requests.get('https://raw.githubusercontent.com/thuma/Transit-Stop-Identifier-Conversions-Sweden/master/mtrexpress.csv')
stationscsv = stationsget.text.split("\n")
for row in stationscsv:
    try:
        parts = row.strip().split(",")
        stations[parts[0]] = parts[1]
    except:
        pass

def application(env, start_response):
    global stations
    if env['PATH_INFO'] == '/':
        start_response('200 OK', [('Content-Type', 'application/json')])
        getdata = urlparse.parse_qs(env['QUERY_STRING'])
        headers = {'content-type': 'application/json'}
        
        try:
        	fromid = stations[getdata['from'][0]]
        	toid = stations[getdata['to'][0]]
        except:
        	return '{"error":"station not in netowrk"}'
        
        try:
            cfile = open(getdata['from'][0]+getdata['to'][0]+getdata['date'][0]+'.json', 'r')
            cjsondata = json.load(cfile)
            return output(getdata,cjsondata)
        except:
        	pass
        
        data = '{"amount":0,"net":0,"outbound":{"date":"'+getdata['date'][0]+'","origin_id":'+fromid+',"destination_id":'+toid+',"passengers":[{"passenger_type_id":1},{"passenger_type_id":4,"seat_type_id":1},{"passenger_type_id":3,"seat_type_id":1},{"passenger_type_id":6,"seat_type_id":1},{"passenger_type_id":2,"seat_type_id":1}],"addons":[]}}'
        r = requests.post("http://www.mtrexpress.se/api/mtr/transaction", data=data, headers=headers)

        token = r.json()['data']['transaction']['token']
                
        data = '{"token":"'+token+'","amount":0,"net":0,"outbound":{"date":"'+getdata['date'][0]+'","origin_id":'+fromid+',"destination_id":'+toid+',"passengers":[{"passenger_type_id":1},{"passenger_type_id":4,"seat_type_id":1},{"passenger_type_id":3,"seat_type_id":1},{"passenger_type_id":6,"seat_type_id":1},{"passenger_type_id":2,"seat_type_id":1}],"addons":[]}}' 
        r = requests.post("http://www.mtrexpress.se/api/mtr/products", data=data, headers=headers)
        jsondata = r.json()
        with open(getdata['from'][0]+getdata['to'][0]+getdata['date'][0]+'.json', 'w') as outfile:
            json.dump(jsondata, outfile)
            
        return output(getdata,jsondata)
        
    else:
        start_response('404 Not Found', [('Content-Type', 'text/html')])
        return '<h1>Not Found</h1>'
        
def output(getdata,data):
    for dep in data['data']["schedules"]["outbound"]:
       if dep["arrival_time"] == getdata['arrivalTime'][0] and dep["departure_time"] == getdata['departureTime'][0]:
           price = dep['products'][0]['unit_prices'][0]['real_price']
       	   out = { 
       	       "departureTime":getdata['departureTime'][0],
		       "arrivalTime":getdata['arrivalTime'][0],
		       "date":getdata['date'][0],
		       "from":getdata['from'][0],
		       "to":getdata['to'][0],
       	       "travelerAge":35,
		       "travelerIsStudent":False,
		       "sellername":"MTR Express",
		       "price":price,
		       "currency":"SEK",
		       "validPrice":True,
		       "url":"http://www.mtrexpress.se/#/boka-resa/er/"+str(int(getdata['from'][0][-4:]))+"_"+str(int(getdata['to'][0][-4:]))+"/v1/"+getdata['date'][0]
               }
		       
       	   return json.dumps(out)
    return '{"error":"no trip found"}'

if __name__ == '__main__':
    print('Serving on 8088...')
    WSGIServer(('', 8088), application).serve_forever()