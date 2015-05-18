# !/usr/bin/env python
# -*- coding: utf-8 -*-

import tornado.httpclient
import random
import tornado.escape
import json

http_client = tornado.httpclient.HTTPClient()
try:
    response = http_client.fetch('https://raw.githubusercontent.com/thuma/Transit-Stop-Identifier-Conversions-Sweden/master/blataget-gtfs.csv')
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
		stops[parts[0]] = {}
		stops[parts[0]]['name'] = parts[1]
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
		fromstring = ''
		tostring = ''
		try:
			fromname = tornado.escape.url_escape(stops[self.get_argument('from')]['name'])
			toname = tornado.escape.url_escape(stops[self.get_argument('to')]['name'])
		except:
			self.write({'error':'from/to station not in network'})
			self.finish()
			return
		
		try:
			self.cachesend()
			return		
		except:
			notincache = 1

		req = "action=get_travel_info_ajax"+"&dep="+fromname+"&dest="+toname+"&num=1"+"&depDate="+self.get_argument('date')+"&retDate="+self.get_argument('date')+"&nocache="+str(random.randint(0, 1000))
	
		self.http_client = tornado.httpclient.AsyncHTTPClient()
		self.myhttprequest = tornado.httpclient.HTTPRequest("http://www.blataget.com/wp-admin/admin-ajax.php", method='POST', headers=None, body=req) 

		self.http_client.fetch(self.myhttprequest, self.searchdone)

	def searchdone(self, response):
		global cache
		data = json.loads(response.body)
		
		cache[self.get_argument('date')+self.get_argument('from')+self.get_argument('to')] = {}
		try:
			for trip in data['depDetail']:
				resdelar = data['depDetail'][trip].split(' ')
				dep = resdelar[0]
				arr = resdelar[1]
				trip = {}
				trip['1stkl'] = resdelar[2].split('_')[1].replace(':',"").replace('-','')
				trip['2ndkl'] = resdelar[3].split('_')[1].replace(':',"").replace('-','')
				try:
					trip['3ndkl'] = resdelar[4].split('_')[1].replace(':',"").replace('-','')
				except:
					trip['3ndkl'] = 99999
				cache[self.get_argument('date')+self.get_argument('from')+self.get_argument('to')][dep+arr] = trip
				 										
		except:
			notok = 1
		
		try:
			self.cachesend()
		except:
			self.write({'error':'no data for that trip'})
			self.finish()
			return
		
		
		
		
	def cachesend(self):
		global cache
		outdata = {"travelerAge":35,	
				"travelerIsStudent":False,
				"sellername":"BlåTåget",
				"price":"",
				"currency":"SEK",
				"validPrice":True,
				"url":"http://www.blataget.com"
				}
		
		outdata['departureTime'] = self.get_argument('departureTime')
		outdata['arrivalTime'] = self.get_argument('arrivalTime')
		outdata['date'] = self.get_argument('date')
		outdata['from'] = self.get_argument('from')
		outdata['to'] = self.get_argument('to')
		outdata['validPrice'] = 1
		
		trip = cache[self.get_argument('date')+self.get_argument('from')+self.get_argument('to')][self.get_argument('departureTime')+self.get_argument('arrivalTime')]
		
		try:
			stkl = int(trip['1stkl'])
		except:
			stkl = 99999
		
		try:
			ndkl = int(trip['2ndkl'])
		except:
			ndkl = 99999
		
		try:
			gkl = int(trip['3ndkl'])
		except:
			gkl = 99999
			
		if stkl < ndkl:
			outdata['price'] = stkl
		else:
			outdata['price'] = ndkl
		if outdata['price'] > gkl:
			outdata['price'] = gkl
		
		if outdata['price'] == 99999:
			self.write({'Error':'Sould out'})
			self.finish()
			return
			
		self.write(outdata)
		self.finish()

 		
		
		




