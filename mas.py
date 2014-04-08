# !/usr/bin/env python
# -*- coding: utf-8 -*-

import tornado.httpclient
import json

http_client = tornado.httpclient.HTTPClient()
try:
    response = http_client.fetch('https://raw.githubusercontent.com/thuma/Transit-Stop-Identifier-Conversions-Sweden/master/masexpressen.csv')
    list_data = response.body
except httpclient.HTTPError as e:
    print "Error:", e

http_client.close()
cache = {}
stops = {}

list_data = list_data.split('\n')
for row in list_data:
	try:
		parts = row.split(',')
		stops[parts[0]] = parts[1]
	except:
		parts = ''

class CachePrint(tornado.web.RequestHandler):
	def get(self):
		global cache
		self.write(cache)

class Handler(tornado.web.RequestHandler):

	@tornado.web.asynchronous
	def get(self):
		self.http_client = tornado.httpclient.AsyncHTTPClient()
		global cache
		global stops
		fromid = ''
		toid = ''
		try:
			fromid = stops[self.get_argument('from')]
			toid = stops[self.get_argument('to')]
		except:
			self.write({'error':'from/to station not in network'})
			self.finish()
			return

		self.myhttprequest = tornado.httpclient.HTTPRequest('http://masexpressen.se/ajax/get_travel_plans?date_outbound='+self.get_argument('date')+'&date_return='+self.get_argument('date')+'&from_stop_id='+fromid+'&to_stop_id='+toid+'&travellers%5B15%5D=1', method='GET') 
		self.http_client.fetch(self.myhttprequest, self.searchdone)

	def searchdone(self, response):
		global cache
		global stops
		
		try:	
			trips = json.loads(response.body)
		except:
			self.write({'error':'Error contacting MASexpress server'})
			self.finish()
			return

		try:
			trips = trips['message']['plans']['outbound']
			for date in trips:
				for trip in trips[date]:
					cache[date+self.get_argument('from')+self.get_argument('to')+trip['entry_time']+trip['exit_time']] = trip
			
			righttrip = cache[self.get_argument('date')+self.get_argument('from')+self.get_argument('to')+self.get_argument('departureTime')+self.get_argument('arrivalTime')]				

			outdata = {"travelerAge":35,	
				"travelerIsStudent":False,
				"sellername":"Masexpressen",
				"price":"",
				"currency":"SEK",
				"validPrice":True
				}
		
			outdata['departureTime'] = self.get_argument('departureTime')
			outdata['arrivalTime'] = self.get_argument('arrivalTime')
			outdata['date'] = self.get_argument('date')
			outdata['from'] = self.get_argument('from')
			outdata['to'] = self.get_argument('to')
			outdata['price'] = righttrip['total_price'][:-3]
			outdata['validPrice'] = True
			outdata['url'] = 'http://thuma.github.io/gettopost.html#http://masexpressen.se/&&&from='+stops[self.get_argument('from')]+'&to='+stops[self.get_argument('date')]+'&date_outbound='+self.get_argument('date')+'&date_return='+self.get_argument('date')+'&type_15=1&type_16=0&type_20=0&type_17=0&type_18=0&btn_continue=S%F6k+avg%E5ngar'

			self.write(outdata)
			self.finish()
			return
		except:		
			self.write({'error':'No trip found'})
			self.finish()




