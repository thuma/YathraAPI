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
		stops[parts[0]] = parts[1]
	except:
		parts = ''

list_data = ''

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
		try:
			fromid = stops[self.get_argument('from')]
			toid = stops[self.get_argument('to')]
		except:
			self.write({'error':'from/to station not in network'})
			self.finish()
			return
		      
		try:
			deptime = time.strptime(self.get_argument('date')+self.get_argument('departureTime'),'%Y-%m-%d%H:%M')
			deptime = time.mktime(deptime)
			deptime = deptime-120
			deptime = time.localtime(deptime)
			
		except:
			self.write({'error':'departureTime HH:MM missing / error, date YYYY-MM-DD missing / error'})
			self.finish()
			return
			
		try:
			date = time.strftime('%Y-%m-%d+%H:%M',deptime)
		except:
			self.write({'error':'date YYYY-MM-DD HH:MM missing / error'})
			self.finish()
			return

		searchurl = 'https://api.trafiklab.se/sl/reseplanerare.json?key=ad42ec1df5f5e85ee60b8daec082f4e5&S='+fromid+'&Z='+toid+'&time='+self.get_argument('departureTime')
	
		self.myhttprequest = tornado.httpclient.HTTPRequest(searchurl, method='GET')
		self.http_client.fetch(self.myhttprequest, self.searchdone)

	def searchdone(self, response):
		http_client = tornado.httpclient.HTTPClient()
		alldata = trips = tornado.escape.json_decode(response.body)

		for trip in alldata['HafasResponse']['Trip']:
			if trip['Summary']['DepartureTime']['#text'] == self.get_argument('departureTime'):
				self.write({'pris':trip['Summary']['PriceInfo']['TariffZones']})
				self.finish()
				return
			
		self.write({'error':'no trip found'})
		self.finish()
		return