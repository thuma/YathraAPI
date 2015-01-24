# !/usr/bin/env python
# -*- coding: utf-8 -*-

import re
import json
import tornado.httpclient
import tornado.ioloop
import time
from functools import partial

snalltagetstops = open('snalltaget.json')
snalltagetstops = json.load(snalltagetstops)
snalltagetstopsa = {}
for stop in snalltagetstops['stops']:
	snalltagetstopsa[str(stop['P']*100000+stop['L'])] = stop['N']

snalltagetstops = {}

snalltagetcache = {}

def remove_key(key):
    global snalltagetcache
    del snalltagetcache[key]

class CachePrint(tornado.web.RequestHandler):
	def get(self):
		global snalltagetcache
		self.write(snalltagetcache)


class Handler(tornado.web.RequestHandler):
	
	@tornado.web.asynchronous
	def get(self):
		self.http_client = tornado.httpclient.AsyncHTTPClient()
		global snalltagetcache
		global snalltagetstopsa

		self.query = {}
		
		try:
			self.query['DepartureDateTime'] = self.get_argument('date') +' '+ self.get_argument('departureTime')[:2]+':00'
			self.getdate = self.get_argument('date')
			self.gettime = self.get_argument('departureTime')
		except:
			self.returnerror('Missing deparature time')
			return
			
		try:
			self.getfrom = self.get_argument('from')
			self.fromname = snalltagetstopsa[self.getfrom]
			self.query['DepartureLocationId'] = int(self.getfrom[-5:])
			self.query['DepartureLocationProducerCode'] = int(self.getfrom[:2])
		except:
			self.returnerror('Missing deparature station')
			return
		
		try:
			self.getto = self.get_argument('to')
			self.toname = snalltagetstopsa[self.getto]
			self.query['ArrivalLocationId'] = int(self.getto[-5:])
			self.query['ArrivalLocationProducerCode'] = int(self.getto[:2])
		except:
			self.returnerror('Missing arrival station')
			return

		try:
			self.gettotime = self.get_argument('arrivalTime')
		except:
			self.returnerror('Missing arrivalTime HH:MM')
			return
			
		self.query['TravelType'] = "E"
		self.query['Passengers'] = [{"PassengerCategory":"VU"}]
		
		try:
			self.returnrequest(snalltagetcache[self.getdate+self.getfrom+self.gettime+self.getto+self.gettotime])
			return
		except:
			notfound = 1
		
		headers = tornado.httputil.HTTPHeaders({'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
							'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Ubuntu Chromium/32.0.1700.107 Chrome/32.0.1700.107 Safari/537.36',
							'Accept-Encoding': 'gzip,deflate,sdch',
							'Accept-Language': 'sv-SE,sv;q=0.8,en-US;q=0.6,en;q=0.4'})

		self.request_setup = tornado.httpclient.HTTPRequest("https://boka.snalltaget.se/boka-biljett", method='GET', follow_redirects=True, max_redirects=3, request_timeout=4.0,headers=headers, validate_cert=False)
		self.http_client.fetch(self.request_setup, self.gotsession)
		self.retry = 0
		
		
	def gotsession(self,response):
		
		self.retry = self.retry + 1
		try:
			self.cookie = response.headers["set-cookie"].split(';')[0]
		except:
			if self.retry > 2:
			  self.http_client.fetch(self.request_setup, self.gotsession)
			return 

		header_setup = tornado.httputil.HTTPHeaders({'Accept':'application/json, text/plain, */*',
'Accept-Encoding':'gzip,deflate,sdch',
'Accept-Language':'sv-SE',
'Connection':'keep-alive',
'Content-Type':'application/json;charset=UTF-8',
'Cookie':self.cookie,
'Host':'boka.snalltaget.se',
'Origin':'https://boka.snalltaget.se',
'Referer':'https://boka.snalltaget.se/boka-biljett',
'User-Agent':'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Ubuntu Chromium/32.0.1700.107 Chrome/32.0.1700.107 Safari/537.36'})
		
		request_setup = tornado.httpclient.HTTPRequest("https://boka.snalltaget.se/api/timetables", method='POST', headers=header_setup, body=json.dumps(self.query), follow_redirects=True, max_redirects=3,validate_cert=False)
		self.http_client.fetch(request_setup, self.gottrips)

	def gottrips(self, response):
		
		try:
			self.trips = json.loads(response.body)
		except:
			self.write({'error':'no data in response from Snalltaget, timetable'})
			self.finish()
			return
		
		
		try:
			if len(self.trips['JourneyAdvices']) > 10:
				maxint = 10
			else:
				maxint = len(self.trips['JourneyAdvices'])
		except:
			self.returnerror('No trip times found')
			return
			
		pquery = {'TimetableId':self.trips['Id'], 'JourneyConnectionReferences':[]}
		
		exist = 0
		for i in range(0, len(self.trips['JourneyAdvices'])):
			if self.trips['JourneyAdvices'][i]['DepartureDateTime'][11:16] == self.gettime and self.trips['JourneyAdvices'][i]['ArrivalDateTime'][11:16] == self.gettotime:
				exist = 1
				
			if exist == 1:
				pquery['JourneyConnectionReferences'].append(self.trips['JourneyAdvices'][i]['JourneyConnectionReference'])
				if len(pquery['JourneyConnectionReferences']) > 9:	
					break

		if exist == 0:
			self.returnerror('Trip not found in search')
			return None
		

		header_setup = tornado.httputil.HTTPHeaders({'Accept':'application/json, text/plain, */*',
'Accept-Encoding':'gzip,deflate,sdch',
'Accept-Language':'sv-SE',
'Connection':'keep-alive',
'Content-Type':'application/json;charset=UTF-8',
'Host':'boka.snalltaget.se',
"Cookie": self.cookie,
'Origin':'https://boka.snalltaget.se',
'Referer':'https://boka.snalltaget.se/boka-biljett',
'User-Agent':'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Ubuntu Chromium/32.0.1700.107 Chrome/32.0.1700.107 Safari/537.36'})
		
		request_setup = tornado.httpclient.HTTPRequest("https://boka.snalltaget.se/api/journeyadvices/lowestprices", method='POST',  body=json.dumps(pquery), headers=header_setup, follow_redirects=True, max_redirects=3,validate_cert=False)
		self.http_client.fetch(request_setup, self.gotprices)

	def gotprices(self, response):
		global snalltagetcache
		try:
			price = json.loads(response.body)
		except:
			self.write({'error':'no data in response from Snalltaget, price'})
			self.finish()
			return

		for i in range(0, len(self.trips['JourneyAdvices'])):
			for j in range (0,len(price)):
				if price[j]['JourneyConnectionReference'] == self.trips['JourneyAdvices'][i]['JourneyConnectionReference']:
					self.trips['JourneyAdvices'][i]['IsSleeperTrain'] = price[j]['IsSleeperTrain']
					self.trips['JourneyAdvices'][i]['LowestTotalPrice'] = price[j]['LowestTotalPrice']
					self.trips['JourneyAdvices'][i]['Currency'] = price[j]['Currency']
					stopfrom = str(self.trips['JourneyAdvices'][i]['DepartureLocation']['ProducerCode']*100000 + self.trips['JourneyAdvices'][i]['DepartureLocation']['LocationId'])
					stopto = str(self.trips['JourneyAdvices'][i]['ArrivalLocation']['ProducerCode']*100000 + self.trips['JourneyAdvices'][i]['ArrivalLocation']['LocationId'])
					datefrom = self.trips['JourneyAdvices'][i]['DepartureDateTime'][:10]
					timefrom = self.trips['JourneyAdvices'][i]['DepartureDateTime'][11:16]
					timeto = self.trips['JourneyAdvices'][i]['ArrivalDateTime'][11:16]
					self.trips['JourneyAdvices'][i]['ArrivalDateTime']
                                        cachekey = datefrom+stopfrom+timefrom+stopto+timeto
                                        snalltagetcache[cachekey] = self.trips['JourneyAdvices'][i]
                                        tornado.ioloop.IOLoop.instance().add_timeout(time.time()+3600*8, partial(remove_key,cachekey))
                                        break
		try:
			self.returnrequest(snalltagetcache[self.getdate+self.getfrom+self.gettime+self.getto+self.gettotime])
			return
		except:
			self.returnerror('Trip not found in search')
			return

	def returnrequest(self, data):
		outdata = {"travelerAge":35,
		"travelerIsStudent":False,
		"price":"101",
		"currency":"SEK",
		"validPrice":True,
		"url":"https://boka.snalltaget.se/boka-biljett#!/step1?from="+str(data['DepartureLocation']['LocationId'])+"&to="+str(data['ArrivalLocation']['LocationId'])+"&date="+data['DepartureDateTime'][:10],"sellername":'Snälltåget'}
		
		outdata['departureTime'] = data['DepartureDateTime'][11:16]
		outdata['arrivalTime'] = data['ArrivalDateTime'][11:16]
		outdata['date'] = data['DepartureDateTime'][:10]
		outdata['from'] = data['DepartureLocation']['LocationNameShort']
		outdata['to'] = data['ArrivalLocation']['LocationNameShort']
		outdata['price'] = int(data['LowestTotalPrice'])
		outdata['currency'] = data['Currency']
		self.write(outdata)
		self.finish()
		
	
	def returnerror(self, data):
		self.write({'error':data})
		self.finish()


