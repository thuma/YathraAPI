# !/usr/bin/env python
# -*- coding: utf-8 -*-

import tornado.httpclient
import json
import time

from bs4 import BeautifulSoup


http_client = tornado.httpclient.HTTPClient()
try:
    response = http_client.fetch('https://raw.githubusercontent.com/thuma/Transit-Stop-Identifier-Conversions-Sweden/master/ostgotatrafiken-gtfs.csv')
    list_data = response.body
except tornado.httpclient.HTTPError as e:
    print "Error:", e
http_client.close()
cache = {}
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
		
		self.http_client = tornado.httpclient.AsyncHTTPClient()
		# Generate search object.
		query = {}
		query['start'] = fromstring
		query['end'] = tostring
		query['date'] = self.get_argument('date')+' '+self.get_argument('departureTime') 
		query['direction'] = '0' 
		query['span'] = 'default'
		query['traffictype'] = ''
		query['changetime'] = ''
		query['priority'] = ''
		query['walk'] = ''
		self.url = 'http://www.ostgotatrafiken.se'

		headdata = {}
		headdata['Content-Type'] = 'application/json; charset=UTF-8'

		self.myhttprequest = tornado.httpclient.HTTPRequest('http://www.ostgotatrafiken.se/rest/TravelHelperWebService.asmx/FindJourney', method='POST', headers=headdata, body=json.dumps(query)) 
		self.http_client.fetch(self.myhttprequest, self.searchdone)

	def searchdone(self, response):
		global cache
		
		trips = json.loads(response.body)
		trips = trips['d']

		for trip in trips:
			cache[time.strftime("%Y-%m-%d",time.localtime(float(trip['Departure'][6:-5])))+self.get_argument('from')+self.get_argument('to')+trip['strDeparture']+trip['strArrival']] = trip
			
		try:
			price = cache[self.get_argument('date')+self.get_argument('from')+self.get_argument('to')+self.get_argument('departureTime')+self.get_argument('arrivalTime')]
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

