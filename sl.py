# !/usr/bin/env python
# -*- coding: utf-8 -*-

import json
import tornado.httpclient

http_client = tornado.httpclient.HTTPClient()
try:
    response = http_client.fetch('https://github.com/thuma/Transit-Stop-Identifier-Conversions-Sweden/raw/master/sl-gtfs.csv')
    list_data = response.body
except httpclient.HTTPError as e:
    print "Error:", e
http_client.close()

cache = {}
stops = {}

list_data = list_data.split('\n')
for row in list_data:
	try:
		parts = row.split(';')
		stops[parts[1]] = parts[0]
	except:
		parts = ''

list_data = ''

file = open('../sl.key', 'r')
key = file.readline().strip()
file.close()

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
		global key
		
		try:
			fromid = stops[self.get_argument('from')]
			toid = stops[self.get_argument('to')]
		except:
			self.write({'error':'from/to station not in network'})
			self.finish()
			return
		      
		try:
			date = self.get_argument('date').split('-')
			date = date[2]+'.'+date[1]+'.'+date[0]
		except:
			self.write({'error':'date error should be YYYY-MM-DD'})
			self.finish()
			return

		searchurl = 'https://api.trafiklab.se/sl/reseplanerare.json?key='+key+'&Date='+date+'&S='+fromid+'&Z='+toid+'&time='+self.get_argument('departureTime')
	
		self.myhttprequest = tornado.httpclient.HTTPRequest(searchurl, method='GET')
		self.http_client.fetch(self.myhttprequest, self.searchdone)

	def searchdone(self, response):
		http_client = tornado.httpclient.HTTPClient()
		
		alldata = tornado.escape.json_decode(unicode(response.body, 'latin-1'))

		for trip in alldata['HafasResponse']['Trip']:
			if trip['Summary']['DepartureTime']['#text'] == self.get_argument('departureTime'):
				
				pris = '125'
				if trip['Summary']['PriceInfo']['TariffZones'] == 'A':
				  pris = '25'
				elif trip['Summary']['PriceInfo']['TariffZones'] == 'AB':
				  pris = '37,5'
				elif trip['Summary']['PriceInfo']['TariffZones'] == 'ABC':
				  pris = '50'
				  
				outdata = {
					  "travelerAge":35,	
					  "travelerIsStudent":False,
					  "sellername":"SL",
					  "price":pris,
					  "currency":"SEK",
					  "validPrice":True,
					  "url":"http://sl.se/#/Travel/SearchTravelById/null/null/"+self.get_argument('from')+"/"+self.get_argument('to')+"/"+self.get_argument('date')+"%2520"+self.get_argument('departureTime').replace(":","_")+"/depart/sv/null/null/null/null/null/null/null/null/false/null/0",
					  "departureTime":self.get_argument('departureTime'),
					  "arrivalTime":self.get_argument('arrivalTime'),
					  "date":self.get_argument('date'),
					  "from":self.get_argument('from'),
					  "to":self.get_argument('to')
					  }
				self.write(outdata)
				self.finish()
				return
			
		self.write({'error':'no trip found'})
		self.finish()
		return