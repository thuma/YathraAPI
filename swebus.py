# !/usr/bin/env python
# -*- coding: utf-8 -*-

import tornado.httpclient
from bs4 import BeautifulSoup


http_client = tornado.httpclient.HTTPClient()
try:
    response = http_client.fetch('https://raw.githubusercontent.com/thuma/Transit-Stop-Identifier-Conversions-Sweden/master/swebus-gtfs.csv')
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
		stops[parts[0]]['id'] = parts[2]
		stops[parts[0]]['name'] = parts[3]
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
			price = cache[self.get_argument('date')+self.get_argument('from')+self.get_argument('to')+self.get_argument('departureTime')+self.get_argument('arrivalTime')]
			outdata = {"travelerAge":35,	
				"travelerIsStudent":False,
				"sellername":"Swebuss",
				"price":"",
				"currency":"SEK",
				"validPrice":True
				}
		
			outdata['departureTime'] = self.get_argument('departureTime')
			outdata['arrivalTime'] = self.get_argument('arrivalTime')
			outdata['date'] = self.get_argument('date')
			outdata['from'] = self.get_argument('from')
			outdata['to'] = self.get_argument('to')
			outdata['price'] = price['Price1']
			outdata['validPrice'] = 1
			outdata['url'] = price['url']
	
			self.write(outdata)
			self.finish()
			return
		except:
			notfoundincache = 1	
		
		
		self.http_client = tornado.httpclient.AsyncHTTPClient()
		try:
			self.url = 'http://www.swebus.se/Express/Sokresultat/\
?from='+stops[self.get_argument('from')]['id']+'\
&fromtype=BusStop\
&to='+stops[self.get_argument('to')]['id']+'\
&totype=BusStop\
&away='+self.get_argument('date')+'\
&Adult=1\
&Child=0\
&Youth=0\
&Student=0\
&Pensioner=0\
&Pet=0\
&campaignCode=\
&id=1101\
&epslanguage=sv-SE'
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
			#self.http_client.fetch(self.myhttprequest, self.searchdone)
			#return
			end = 1
		lista = html_data.find(id='bookingSearchResultsAway').findAll("div", { "class" : "Accordion" })
		lista = lista[0].findAll("table") 

		for i in lista:
                        data = {}
			data['url'] = self.url
                        data['Departure'] = i.findAll("th", { "class" : "Departure" })[0].string.strip()
                        data['Arrival'] = i.findAll("th", { "class" : "Arrival" })[0].string.strip()
                        data['Price1'] = i.findAll("th", { "class" : "Price1" })[0].findAll("input")[0]['value']
                        data['Price2'] = i.findAll("th", { "class" : "Price2" })[0].findAll("input")[0]['value']
                        data['Price3'] = i.findAll("th", { "class" : "Price3" })[0].findAll("input")[0]['value']

                        cache[self.get_argument('date')+self.get_argument('from')+self.get_argument('to')+data['Departure']+data['Arrival']] = data
                
                try:
			price = cache[self.get_argument('date')+self.get_argument('from')+self.get_argument('to')+self.get_argument('departureTime')+self.get_argument('arrivalTime')]
			outdata = {"travelerAge":35,	
				"travelerIsStudent":False,
				"sellername":"Swebuss",
				"price":"",
				"currency":"SEK",
				"validPrice":True
				}
		
			outdata['departureTime'] = self.get_argument('departureTime')
			outdata['arrivalTime'] = self.get_argument('arrivalTime')
			outdata['date'] = self.get_argument('date')
			outdata['from'] = self.get_argument('from')
			outdata['to'] = self.get_argument('to')
			outdata['price'] = price['Price1']
			outdata['validPrice'] = 1
			outdata['url'] = price['url']
	
			self.write(outdata)
			self.finish()
			return
		except:
			notfoundincache = 1	
                        
                self.write('{"Error":"No trip found"}')
                self.finish()
		
