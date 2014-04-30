#!/usr/bin/env python
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
def getSec(s):
    l = map(int, s.split(':')) # l = list(map(int, s.split(':'))) in Python 3.x
    return sum(n * sec for n, sec in zip(l[::-1], (60, 3600)))

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
&time="+tornado.escape.url_escape(self.get_argument('departureTime'))+"\
&start=1\
&L=vs_vasttrafik\
&timesel=depart"

			
		except:
			self.write({'error':'from/to station not in network'})
			self.finish()
			return
		
		try:
			cachekey = self.get_argument('date')+self.get_argument('from')+self.get_argument('to')
			for i in cache[cachekey]:
				i = cache[cachekey][i]
				depSec = getSec(i['departureTime'])
				arrSec = getSec(i['arrivalTime'])
				maxDepSec = getSec(self.get_argument('departureTime')) + 4*60
				minDepSec = maxDepSec - 8*60
				maxArrSec = getSec(self.get_argument('arrivalTime')) + 4*60
				minArrSec = maxArrSec - 8*60
				if maxDepSec >= depSec and depSec >= minDepSec and maxArrSec >= arrSec and arrSec >= minArrSec:
					outdata = {"travelerAge":35,	
						"travelerIsStudent":False,
						"sellername":"Västtrafik",
						"price":"",
						"currency":"SEK"
						}

					outdata['departureTime'] = i['departureTime']
					outdata['arrivalTime'] = i['arrivalTime']
					outdata['date'] = self.get_argument('date')
					outdata['from'] = self.get_argument('from')
					outdata['to'] = self.get_argument('to')
					outdata['price'] = i['prisdata']['Kontoladdning']['Vuxen']
					outdata['validPrice'] = 1
					outdata['url'] = self.url
	
					self.write(outdata)
					self.finish()
					return
		except:
			notfoundincache = 1	
		
		self.http_client = tornado.httpclient.AsyncHTTPClient()
		try:
			cachekey = self.get_argument('date')+self.get_argument('from')+self.get_argument('to')
			for i in cache[cachekey]:
				i = cache[cachekey][i]
				depSec = getSec(i['departureTime'])
				arrSec = getSec(i['arrivalTime'])
				maxDepSec = getSec(self.get_argument('departureTime')) + 4*60
				minDepSec = maxDepSec - 8*60
				maxArrSec = getSec(self.get_argument('arrivalTime')) + 4*60
				minArrSec = maxArrSec - 8*60
				self.pdep = i['departureTime']
				self.parr = i['arrivalTime']
				if maxDepSec >= depSec and depSec >= minDepSec and maxArrSec >= arrSec and arrSec >= minArrSec:
					header_setup = tornado.httputil.HTTPHeaders({"Cookie": cache[cachekey][i['departureTime']+i['arrivalTime']]['kaka']})
					request_setup = tornado.httpclient.HTTPRequest(cache[cachekey][i['departureTime']+i['arrivalTime']]['url'], method='GET', headers=header_setup, follow_redirects=True, max_redirects=3)
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
			cachekey = self.get_argument('date')+self.get_argument('from')+self.get_argument('to')
			try:
				hej = cache[cachekey]
			except:
				cache[cachekey] = {}
			
			try:
				hej = cache[cachekey][depTime+arrTime]
			except:
				cache[cachekey][depTime+arrTime] = {}

			cache[cachekey][depTime+arrTime]['url'] = i.parent.find_all("td", { "headers" : "hafasOVFares"})[0].find_all("a")[0]["href"]
			cache[cachekey][depTime+arrTime]['kaka'] = kaka
			cache[cachekey][depTime+arrTime]['departureTime'] = depTime
			cache[cachekey][depTime+arrTime]['arrivalTime'] = arrTime
		
		try:
			cachekey = self.get_argument('date')+self.get_argument('from')+self.get_argument('to')
			for i in cache[cachekey]:
				i = cache[cachekey][i]
				depSec = getSec(i['departureTime'])
				arrSec = getSec(i['arrivalTime'])
				maxDepSec = getSec(self.get_argument('departureTime')) + 4*60
				minDepSec = maxDepSec - 8*60
				maxArrSec = getSec(self.get_argument('arrivalTime')) + 4*60
				minArrSec = maxArrSec - 8*60
				self.pdep = i['departureTime']
				self.parr = i['arrivalTime']
				if maxDepSec >= depSec and depSec >= minDepSec and maxArrSec >= arrSec and arrSec >= minArrSec:
					header_setup = tornado.httputil.HTTPHeaders({"Cookie": cache[cachekey][i['departureTime']+i['arrivalTime']]['kaka']})
					request_setup = tornado.httpclient.HTTPRequest(cache[cachekey][i['departureTime']+i['arrivalTime']]['url'], method='GET', headers=header_setup, follow_redirects=True, max_redirects=3)
					self.http_client.fetch(request_setup, self.gotprice)
					return
		except:
			errorinfind = 1
		self.write({'error':'trip time not found '})
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

		cache[self.get_argument('date')+self.get_argument('from')+self.get_argument('to')][self.pdep+self.parr]['prisdata'] = prisdata
		
		if 1 == 1:
			cachekey = self.get_argument('date')+self.get_argument('from')+self.get_argument('to')
			for i in cache[cachekey]:
				i = cache[cachekey][i]
				depSec = getSec(i['departureTime'])
				arrSec = getSec(i['arrivalTime'])
				maxDepSec = getSec(self.get_argument('departureTime')) + 4*60
				minDepSec = maxDepSec - 8*60
				maxArrSec = getSec(self.get_argument('arrivalTime')) + 4*60
				minArrSec = maxArrSec - 8*60
				if maxDepSec >= depSec and depSec >= minDepSec and maxArrSec >= arrSec and arrSec >= minArrSec:
					outdata = {"travelerAge":35,	
						"travelerIsStudent":False,
						"sellername":"Västtrafik",
						"price":"",
						"currency":"SEK"
						}

					outdata['departureTime'] = i['departureTime']
					outdata['arrivalTime'] = i['arrivalTime']
					outdata['date'] = self.get_argument('date')
					outdata['from'] = self.get_argument('from')
					outdata['to'] = self.get_argument('to')
					outdata['price'] = i['prisdata']['Kontoladdning']['Vuxen']
					outdata['validPrice'] = 1
					outdata['url'] = self.url
	
			self.write(outdata)
			self.finish()
			return
		#except:
			nofound = 1

		self.write({'Error':'no pricedata found'})
		self.finish()
		return 


