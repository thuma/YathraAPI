# !/usr/bin/env python
# -*- coding: utf-8 -*-

import tornado.httpclient
import time
from bs4 import BeautifulSoup


http_client = tornado.httpclient.HTTPClient()
try:
    response = http_client.fetch('https://raw.githubusercontent.com/thuma/Transit-Stop-Identifier-Conversions-Sweden/master/nettbuss-gtfs.csv')
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
		stops[parts[0]]['id'] = parts[1]
		stops[parts[0]]['name'] = parts[5]
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
			pricea = cache[self.get_argument('date')+self.get_argument('from')+self.get_argument('to')]
		
			price = pricea[self.get_argument('departureTime')+self.get_argument('arrivalTime')]
			outdata = {"travelerAge":35,	
				"travelerIsStudent":False,
				"sellername":"NettBuss",
				"price":"",
				"currency":"SEK",
				"validPrice":True
				}
		
			outdata['departureTime'] = self.get_argument('departureTime')
			outdata['arrivalTime'] = self.get_argument('arrivalTime')
			outdata['date'] = self.get_argument('date')
			outdata['from'] = self.get_argument('from')
			outdata['to'] = self.get_argument('to')
			outdata['price'] = price['Pris'][:-4]
			outdata['validPrice'] = 1
			outdata['url'] = pricea['url']
	
			self.write(outdata)
			self.finish()
			return
		except:
			try:
				tid = cache[self.get_argument('date')+self.get_argument('from')+self.get_argument('to')]
				self.write('{"error":"No trip found"}')
				self.finish()
				return
			except: 			
				notfoundincache = 1	
		
		self.http_client = tornado.httpclient.AsyncHTTPClient()
		try:
			self.url = 'https://www.nettbuss.se/bokning/valj-avgang?s=0-'+stops[self.get_argument('from')]['id']+'-'+stops[self.get_argument('to')]['id']+'-'+self.get_argument('date').replace("-","")
			self.myhttprequest = tornado.httpclient.HTTPRequest(self.url) 
			self.http_client.fetch(self.myhttprequest, self.searchdone)
		except:
			self.write({'error':'from/to station not in network'})
			self.finish()
			return
		
	def searchdone(self, response):
		global cache
		html_data = response.body
		try:
			html_data = BeautifulSoup(html_data)
		except:
			self.write({'error':'error in nettbuss response'})
			self.finish()
			return

		lista = html_data.find(id='departuresLoaderId')
		
		rader = lista.find_all("td", { "class" : "cell1"})
		
		datestops = self.get_argument('date')+self.get_argument('from')+self.get_argument('to')
		cache[datestops] = {}
		cache[datestops]['url'] = self.url
		
		for i in rader:
			med = i.parent.find_all("td", { "class" : "cell1"})[0].get_text()
			avg = i.parent.find_all("td", { "class" : "cell2"})[0].get_text()
			ank = i.parent.find_all("td", { "class" : "cell3"})[0].get_text()
			tid = i.parent.find_all("td", { "class" : "cell4"})[0].get_text()
			byte = i.parent.find_all("td", { "class" : "cell5"})[0].get_text()
			pris = i.parent.find_all("td", { "class" : "cell6"})[0].get_text()

			cache[datestops][avg+ank] = {}
			cache[datestops][avg+ank]['Res med'] = med
			cache[datestops][avg+ank]['Restid'] = tid
			cache[datestops][avg+ank]['Byte'] = byte
			cache[datestops][avg+ank]['Pris'] = pris

		self.get()
		return

	