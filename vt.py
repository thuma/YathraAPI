# !/usr/bin/env python
# -*- coding: utf-8 -*-

import tornado.httpclient
import tornado.escape
import tornado.httputil
import time
from bs4 import BeautifulSoup


http_client = tornado.httpclient.HTTPClient()
try:
    response = http_client.fetch('https://raw.githubusercontent.com/thuma/Transit-Stop-Identifier-Conversions-Sweden/master/vasttrafik-gtfs.csv')
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

		try:
			self.url = "http://reseplanerare.vasttrafik.se/bin/query.exe/sn\
?SGID="+stops[self.get_argument('from')]['id']+"\
&ZGID="+stops[self.get_argument('to')]['id']+"\
&date="+self.get_argument('date')+"\
&time="+tornado.escape.url_escape("14:30")+"\
&start=1\
&L=vs_vasttrafik\
&timesel=depart"

			
		except:
			self.write({'error':'from/to station not in network'})
			self.finish()
			return
		
		try:
			trip = cache[self.get_argument('date')+self.get_argument('from')+self.get_argument('to')+self.get_argument('departureTime')+self.get_argument('arrivalTime')]
			outdata = {"travelerAge":35,	
				"travelerIsStudent":False,
				"sellername":"Västtrafik",
				"price":"",
				"currency":"SEK",
				"validPrice":True
				}

			outdata['departureTime'] = self.get_argument('departureTime')
			outdata['arrivalTime'] = self.get_argument('arrivalTime')
			outdata['date'] = self.get_argument('date')
			outdata['from'] = self.get_argument('from')
			outdata['to'] = self.get_argument('to')
			outdata['price'] = trip['prisdata']['Kontoladdning']['Vuxen']
			outdata['validPrice'] = 1
			outdata['url'] = self.url
	
			self.write(outdata)
			self.finish()
			return
		except:
			notfoundincache = 1	
		
		self.http_client = tornado.httpclient.AsyncHTTPClient()
		try:
			cachekey = self.get_argument('date')+self.get_argument('from')+self.get_argument('to')+self.get_argument('departureTime')+self.get_argument('arrivalTime')
			header_setup = tornado.httputil.HTTPHeaders({"Cookie": cache[cachekey]['kaka']})
			request_setup = tornado.httpclient.HTTPRequest(cache[cachekey]['url'], method='GET', headers=header_setup, follow_redirects=True, max_redirects=3)
			self.http_client.fetch(request_setup, self.gotprice)
			return
		except:
			serachforprice = 1
		self.http_client.fetch(self.url, self.searchdone)
		
	def searchdone(self, response):
		global cache
		kaka = response.headers['Set-Cookie'].split(';')[0]

		bsdata = BeautifulSoup(response.body)
		lista = bsdata.find_all("td", { "headers" : "hafasOVLinks"})
		purl = {}
		for i in lista:
			depTime = i.parent.find_all("td", { "headers" : "hafasOVTimeDep"})[0].get_text().strip()
			arrTime = i.parent.find_all("td", { "headers" : "hafasOVTimeArr"})[0].get_text().strip()
			cachekey = self.get_argument('date')+self.get_argument('from')+self.get_argument('to')+depTime+arrTime
			cache[cachekey] = {}
			cache[cachekey]['url'] = i.parent.find_all("td", { "headers" : "hafasOVFares"})[0].find_all("a")[0]["href"]
			cache[cachekey]['kaka'] = kaka
		try:
			cachekey = self.get_argument('date')+self.get_argument('from')+self.get_argument('to')+self.get_argument('departureTime')+self.get_argument('arrivalTime')
			header_setup = tornado.httputil.HTTPHeaders({"Cookie": cache[cachekey]['kaka']})
			request_setup = tornado.httpclient.HTTPRequest(cache[cachekey]['url'], method='GET', headers=header_setup, follow_redirects=True, max_redirects=3)
			self.http_client.fetch(request_setup, self.gotprice)
		except:
			self.write({'Error':'no trip found'})
			self.finish()
			return	

	def gotprice(self, response):
			
		bsdata = BeautifulSoup(response.body)
		bsdata = bsdata.find_all("table", { "class" : "resultTablePriceInfo"})[0]
		rows = bsdata.find_all("tr")
		prisdata = {}
		for row in rows:
			fields = row.find_all("td")
			if len(fields) > 3:
				prisdata[fields[0].get_text().strip()] = {}
				prisdata[fields[0].get_text().strip()]['Vuxen'] = fields[1].get_text().split(' kr')[0].strip()
				prisdata[fields[0].get_text().strip()]['Ungdom'] = fields[2].get_text().split(' kr')[0].strip()
				prisdata[fields[0].get_text().strip()]['Skolungdom'] = fields[3].get_text().split(' kr')[0].strip()

		cache[self.get_argument('date')+self.get_argument('from')+self.get_argument('to')+self.get_argument('departureTime')+self.get_argument('arrivalTime')]['prisdata'] = prisdata
		
		try:
			trip = cache[self.get_argument('date')+self.get_argument('from')+self.get_argument('to')+self.get_argument('departureTime')+self.get_argument('arrivalTime')]
			outdata = {"travelerAge":35,	
				"travelerIsStudent":False,
				"sellername":"Västtrafik",
				"price":"",
				"currency":"SEK",
				"validPrice":True
				}

			outdata['departureTime'] = self.get_argument('departureTime')
			outdata['arrivalTime'] = self.get_argument('arrivalTime')
			outdata['date'] = self.get_argument('date')
			outdata['from'] = self.get_argument('from')
			outdata['to'] = self.get_argument('to')
			outdata['price'] = trip['prisdata']['Kontoladdning']['Vuxen']
			outdata['validPrice'] = 1
			outdata['url'] = self.url
	
			self.write(outdata)
			self.finish()
			return
		except:
			nofound = 1

		self.write({'Error':'no pricedata found'})
		self.finish()
		return 


