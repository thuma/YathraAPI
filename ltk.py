# !/usr/bin/env python
# -*- coding: utf-8 -*-

import tornado.httpclient
from bs4 import BeautifulSoup


http_client = tornado.httpclient.HTTPClient()
try:
    response = http_client.fetch('https://raw.githubusercontent.com/thuma/Transit-Stop-Identifier-Conversions-Sweden/master/lanstrafikenkronoberg-gtfs.csv')
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
		fromstring = ''
		tostring = ''
		try:
			fromstring = stops[self.get_argument('from')]['name']+'|'+stops[self.get_argument('from')]['id']+'|0'
			tostring = stops[self.get_argument('to')]['name']+'|'+stops[self.get_argument('to')]['id']+'|0'
		except:
			self.write({'error':'from/to station not in network'})
			self.finish()
			return
		
		try:
			price = cache[self.get_argument('date')+self.get_argument('from')+self.get_argument('to')+self.get_argument('departureTime')+self.get_argument('arrivalTime')]
			outdata = {"travelerAge":35,	
				"travelerIsStudent":False,
				"sellername":"LTK",
				"price":"",
				"currency":"SEK",
				"validPrice":True
				}
		
			outdata['departureTime'] = self.get_argument('departureTime')
			outdata['arrivalTime'] = self.get_argument('arrivalTime')
			outdata['date'] = self.get_argument('date')
			outdata['from'] = self.get_argument('from')
			outdata['to'] = self.get_argument('to')
			outdata['price'] = price['prices'][3]
			outdata['validPrice'] = 1
			outdata['url'] = price['url']
	
			self.write(outdata)
			self.finish()
			return
		except:
			notfoundincache = 1	
			
		self.http_client = tornado.httpclient.AsyncHTTPClient()
		req = 'inpPointFr_ajax='+tornado.escape.url_escape(fromstring)
		req +='&inpPointTo_ajax='+tornado.escape.url_escape(tostring)
		req +='&inpPointInterm_ajax='
		req +='&selRegionFr=741'
		req +='&inpPointFr=%C5s+Gamla+K%F6pstad++%5BH%E5llplats%5D'
		req +='&optTypeFr=0'
		req +='&inpPointTo=Varberg+Station+%28Bussterm%29++%5BH%E5llplats%5D'
		req +='&optTypeTo=0'
		req +='&inpPointInterm='
		req +='&selDirection=0'
		req +='&inpTime='+tornado.escape.url_escape(self.get_argument('departureTime'))
		req +='&inpDate='+self.get_argument('date')
		req +='&optReturn=0'
		req +='&selDirection2=0'
		req +='&inpTime2=23%3A34'
		req +='&inpDate2=2014-03-11'
		req +='&trafficmask=1'
		req +='&trafficmask=2'
		req +='&trafficmask=4'
		req +='&Submit=S%F6k'
		req +='&selChangeTime=0'
		req +='&selWalkSpeed=0'
		req +='&selPriority=0'
		req +='&cmdAction=search'
		req +='&EU_Spirit=False'
		req +='&TNSource=KRONOBERG'
		req +='&SupportsScript=True'
		req +='&Language=se'
		req +='&VerNo=7.1.1.2.0.38p3'
		req +='&Source=querypage_adv'
		req +='&MapParams='
		self.url = 'http://thuma.github.io/gettopost.html#http://www.ltk.fskab.se/querypage_adv.aspx&&&'+req
		self.myhttprequest = tornado.httpclient.HTTPRequest('http://www.ltk.fskab.se/querypage_adv.aspx', method='POST', headers=None, body=req) 

		self.http_client.fetch(self.myhttprequest, self.searchdone)

	def searchdone(self, response):
		global cache
		html_data = response.body
		try:
			html_doc = BeautifulSoup(html_data)
		except:
			self.http_client.fetch(self.myhttprequest, self.searchdone)
			return

		scripts = html_doc.find_all('script')

		for script in scripts:
			rad = script.string
			try:
				rad = rad.strip()
			except:
				rad = "nodatainstring"
			if rad[:8] == 'dValidFr':
				done = rad

		rawprice = done.split('\n')
		tripdata = {}

		for row in rawprice:
			row = row.strip()
			if row[:9] == 'priceArr[':
				parts = row.split('(')
				rownumb = row.split(']')[0].split('[')[1]
				tripdata[rownumb] = {}
				tripdata[rownumb]['prices'] = parts[1][1:-2].split('\',\'')
				

		for index in tripdata:
			svar = html_doc.find(id="result-"+index)
			data = svar.find_all('td')
			tripdata[index]['times'] = {}
			tripdata[index]['times']['dep'] = data[1].string
			tripdata[index]['times']['arr'] = data[2].string
			tripdata[index]['times']['dur'] = data[3].string
			tripdata[index]['times']['changes'] = data[4].string
			tripdata[index]['url'] = self.url
			cache[self.get_argument('date')+self.get_argument('from')+self.get_argument('to')+tripdata[index]['times']['dep']+tripdata[index]['times']['arr']] = tripdata[index]

		try:
			price = cache[self.get_argument('date')+self.get_argument('from')+self.get_argument('to')+self.get_argument('departureTime')+self.get_argument('arrivalTime')]
			outdata = {"travelerAge":35,	
				"travelerIsStudent":False,
				"sellername":"LTK",
				"price":"",
				"currency":"SEK",
				"validPrice":True
				}
		
			outdata['departureTime'] = self.get_argument('departureTime')
			outdata['arrivalTime'] = self.get_argument('arrivalTime')
			outdata['date'] = self.get_argument('date')
			outdata['from'] = self.get_argument('from')
			outdata['to'] = self.get_argument('to')
			outdata['price'] = price['prices'][3]
			outdata['validPrice'] = 1
			outdata['url'] = price['url']
	
			self.write(outdata)
			self.finish()
			return	
		except:		
			self.write({'error':'No trip found'})
			self.finish()

		
