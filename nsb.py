#!/usr/bin/env python
# -*- coding: utf-8 -*-

import tornado.httpclient
import tornado.escape

http_client = tornado.httpclient.HTTPClient()
try:
    response = http_client.fetch('https://raw.githubusercontent.com/thuma/Transit-Stop-Identifier-Conversions-Sweden/master/nsb-gtfs.csv')
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
		stops[parts[0]] = {}
		stops[parts[0]]['name'] = parts[1]
	except:
		parts = ''
		
class CachePrint(tornado.web.RequestHandler):
	def get(self):
		global stops
		self.write(stops)

class Handler(tornado.web.RequestHandler):
	@tornado.web.asynchronous
	def get(self):
		global stops
		self.http_client = tornado.httpclient.AsyncHTTPClient()
		try:
			test = stops[self.get_argument('from')]
			test2 = stops[self.get_argument('to')]
			self.http_client.fetch('http://api1.yathra.se/prisAPI/nsb.php?'+self.request.uri.split('?')[1], self.gotdata)
		except:
			datamissing = 1
		self.write({'error':' from / to not in network'})
		self.finish()
		return 

	def gotdata(self, data):
		self.write(data)
		self.finish()
		return 
	
