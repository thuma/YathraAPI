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
			self.write(cache[self.get_argument('date')+self.get_argument('from')+self.get_argument('to')])
			self.finish()
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
				trip['1stkl'] = resdelar[2].split('_')[1]
				trip['2ndkl'] = resdelar[3].split('_')[1] 
				cache[self.get_argument('date')+self.get_argument('from')+self.get_argument('to')][dep+arr] = trip
				 										
		except:
			notok = 1
		
		self.write(cache[self.get_argument('date')+self.get_argument('from')+self.get_argument('to')])
		self.finish()

		
		'''
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
				"sellername":"BTR",
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
			self.finish() '''

