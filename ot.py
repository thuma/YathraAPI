# !/usr/bin/env python
# -*- coding: utf-8 -*-

import tornado.httpclient
import json
import cache

http_client = tornado.httpclient.HTTPClient()
try:
    response = http_client.fetch('https://raw.githubusercontent.com/thuma/Transit-Stop-Identifier-Conversions-Sweden/master/ostgotatrafiken-gtfs.csv')
    list_data = response.body
except tornado.httpclient.HTTPError as e:
    print "Error:", e
http_client.close()
stops = {}
list_data = list_data.split('\n')

for row in list_data:
	try:
		parts = row.split(';')
		stops[parts[4]] = {}
		stops[parts[4]]['id'] = parts[3]
		stops[parts[4]]['name'] = parts[0]
	except:
		parts = ''


class CachePrint(tornado.web.RequestHandler):
	def get(self):
		self.write('{"none":"none"}')

class Empty():
     getdate = ''
     getfrom = ''
     gettime = ''
     getto = ''
     gettotime = ''

class Handler(tornado.web.RequestHandler):

	@tornado.web.asynchronous
	def get(self):
		global stops
		try:
			fromstring = stops[self.get_argument('from')]['id']
			tostring = stops[self.get_argument('to')]['id']
		except:
			self.write({'error':'from/to station not in network'})
			self.finish()
			return
		self.getdate = self.get_argument('date')
		self.getfrom = 	self.get_argument('from')
		self.gettime = self.get_argument('departureTime')
		self.getto = self.get_argument('to')
		self.gettotime = self.get_argument('arrivalTime')
		
		
		try:
			price = cache.get('ot', self)
			outdata = {"travelerAge":35,	
				"travelerIsStudent":False,
				"sellername":"Östgötatr.",
				"price":"",
				"currency":"SEK",
				"validPrice":True,
				"url":"http://www.ostgotatrafiken.se"
				}
		
			outdata['departureTime'] = self.get_argument('departureTime')
			outdata['arrivalTime'] = self.get_argument('arrivalTime')
			outdata['date'] = self.get_argument('date')
			outdata['from'] = self.get_argument('from')
			outdata['to'] = self.get_argument('to')
			outdata['price'] = price['Prices'][3]['Price']
			outdata['validPrice'] = 1
	
			self.write(outdata)
			self.finish()
			return	
		except:		
			notfound = 1

		
		self.http_client = tornado.httpclient.AsyncHTTPClient()
		# Generate search object.
		query = {}
		query['startId'] = fromstring
		query['endId'] = tostring
                query['startType'] = 'stop'
                query['endType'] = 'stop' 
                query['startLl'] = '58.417065%2C15.624088'
                query['endLl'] = '58.417065%2C15.624088'
		query['date'] = self.get_argument('date')+'+'+self.get_argument('departureTime') 
		query['direction'] = '0' 
		query['span'] = 'default'
		query['traffictype'] = '127'
		query['changetime'] = '0'
		query['priority'] = '0'
		query['walk'] = 'false'
		self.url = 'http://www.ostgotatrafiken.se'

		headdata = {}
		headdata['Content-Type'] = 'application/json; charset=UTF-8' 
		getstring = '?'
		
		for key in query:
		    getstring += key + '=' + query[key] + '&'
                 
		self.myhttprequest = tornado.httpclient.HTTPRequest('http://www.ostgotatrafiken.se/ajax/Journey/Find'+getstring, method='GET', headers=headdata)
		self.http_client.fetch(self.myhttprequest, self.searchdone)

	def searchdone(self, response):
		global cache
		
		trips = json.loads(response.body)
                #print trips
                
		for trip in trips:
			data = Empty()
			data.getdate = trip['Departure'][:10]
			data.getfrom = self.getfrom 
			data.gettime = trip['Departure'][-8:-3]
			data.getto = self.getto
			data.gettotime = trip['Arrival'][-8:-3]
			price = cache.store('ot', data, trip)

		try:
			price = cache.get('ot', self)
			outdata = {"travelerAge":35,	
				"travelerIsStudent":False,
				"sellername":"Östgötatr.",
				"price":"",
				"currency":"SEK",
				"validPrice":True,
				"url":"http://www.ostgotatrafiken.se"
				}
		
			outdata['departureTime'] = self.get_argument('departureTime')
			outdata['arrivalTime'] = self.get_argument('arrivalTime')
			outdata['date'] = self.get_argument('date')
			outdata['from'] = self.get_argument('from')
			outdata['to'] = self.get_argument('to')
			outdata['price'] = price['Prices'][3]['Price']
			outdata['validPrice'] = 1
	
			self.write(outdata)
			self.finish()
			return	
		except:		
			self.write({'error':'No trip found'})
			self.finish()

