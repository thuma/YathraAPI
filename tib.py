# !/usr/bin/env python
# -*- coding: utf-8 -*-

import tornado.httpclient
import json
import time

http_client = tornado.httpclient.HTTPClient()
try:
    response = http_client.fetch('https://raw.githubusercontent.com/thuma/Transit-Stop-Identifier-Conversions-Sweden/master/tib-gtfs.csv')
    list_data = response.body
except tornado.httpclient.HTTPError as e:
    print "Error:", e
http_client.close()
cache = {}
stops = {}
list_data = list_data.split('\n')

for row in list_data:
    try:
        parts = row.split(',')
        stops[parts[5]] = {}
        stops[parts[5]]['id'] = parts[0]
        stops[parts[5]]['name'] = parts[1]
    except:
        parts = ''


class CachePrint(tornado.web.RequestHandler):
    def get(self):
        global cache
        self.write(cache)

class Handler(tornado.web.RequestHandler):

    @tornado.web.asynchronous
    def get(self):
        global cache
        global stops
        try:
            fromstring = stops[self.get_argument('from')]['id']
            tostring = stops[self.get_argument('to')]['id']
        except:
            self.write({'error':'from/to station not in network'})
            self.finish()
            return

        try:
            price = cache[self.get_argument('date')+self.get_argument('from')+self.get_argument('to')+self.get_argument('departureTime')+self.get_argument('arrivalTime')]
            
            if int(price['Prices'][3]['Price']) > 1:
                outdata = {"travelerAge":35,    
                    "travelerIsStudent":False,
                    "sellername":"Tågkomp.",
                    "price":"",
                    "currency":"SEK",
                    "validPrice":True,
                    "url":"http://www.tagkompaniet.se/#sd="+self.get_argument('date')+";ed="+self.get_argument('date')+";tab=0;from=740"+self.get_argument('from')[2:]+";to=740"+self.get_argument('to')[2:]
                    }
        
                outdata['departureTime'] = self.get_argument('departureTime')
                outdata['arrivalTime'] = self.get_argument('arrivalTime')
                outdata['date'] = self.get_argument('date')
                outdata['from'] = self.get_argument('from')
                outdata['to'] = self.get_argument('to')
                outdata['price'] = round(price['Prices'][3]['Price'],2)
                outdata['validPrice'] = 1
            else:
                outdata = {"error":"no trip found"}
    
            self.write(outdata)
            self.finish()
            return    
        except:        
            notfound = 1

        self.http_client = tornado.httpclient.AsyncHTTPClient()
        # Generate search object.
        query = {}
        query['from'] = fromstring
        query['to'] = tostring
        query['when'] = self.get_argument('date')+'T'+self.get_argument('departureTime')+':00.000Z'

        headdata = {}
        headdata['Content-Type'] = 'application/json'

        self.myhttprequest = tornado.httpclient.HTTPRequest('http://www.tagkompaniet.se/tripfinder.asmx/FindTrips', method='POST', headers=headdata, body=json.dumps(query)) 
        self.http_client.fetch(self.myhttprequest, self.searchdone)

    def searchdone(self, response):
        global cache
        
        trips = json.loads(response.body)
        trips = trips['d']['Result']
        
        for trip in trips:
            fromtime = time.localtime(float(trip['StartTime'][6:-5]))
            totime = time.localtime(float(trip['EndTime'][6:-5]))
            cache[time.strftime("%Y-%m-%d",fromtime)+self.get_argument('from')+self.get_argument('to')+time.strftime("%H:%M",fromtime)+time.strftime("%H:%M",totime)] = trip
            
        try:
            price = cache[self.get_argument('date')+self.get_argument('from')+self.get_argument('to')+self.get_argument('departureTime')+self.get_argument('arrivalTime')]
            
            if int(price['TotalPrice']['Full']) > 1:
                outdata = {"travelerAge":35,    
                    "travelerIsStudent":False,
                    "sellername":"Tågkomp.",
                    "price":"",
                    "currency":"SEK",
                    "validPrice":True,
                    "url":"http://www.tagkompaniet.se/#sd="+self.get_argument('date')+";ed="+self.get_argument('date')+";tab=0;from=740"+self.get_argument('from')[2:]+";to=740"+self.get_argument('to')[2:]
                    }
        
                outdata['departureTime'] = self.get_argument('departureTime')
                outdata['arrivalTime'] = self.get_argument('arrivalTime')
                outdata['date'] = self.get_argument('date')
                outdata['from'] = self.get_argument('from')
                outdata['to'] = self.get_argument('to')
                outdata['price'] = round(price['TotalPrice']['Full'],2)
                outdata['validPrice'] = 1
            else:
                outdata = {"error":"no trip found"}
    
            self.write(outdata)
            self.finish()
            return    
        except:        
            self.write({'error':'No trip found'})
            self.finish()


    
