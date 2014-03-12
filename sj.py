# !/usr/bin/env python
# -*- coding: utf-8 -*-

import re
import json
import tornado.ioloop
import tornado.web
import tornado.httpclient
import tornado.httputil
import tornado.escape
import hlt

cache = {}

stops = open('snalltaget.json')
stops = json.load(stops)
stopsa = {}
for stop in stops['stops']:
	stopsa[str(stop['P']*100000+stop['L'])] = stop['N']
stops = {}

class CachePrint(tornado.web.RequestHandler):
	def get(self):
		self.write(cache)

class MainHandler(tornado.web.RequestHandler):
	cookie = ''
	
	def returnrequest(self, data):
		outdata = {"travelerAge":35,
		"travelerIsStudent":False,
		"sellername":"SJ",
		"price":"",
		"currency":"SEK",
		"validPrice":True,
		"url":"http://www.sj.se/"}
		
		outdata['departureTime'] = data['departureTime']
		outdata['arrivalTime'] = data['arrivalTime']
		outdata['date'] = data['departureDate']
		outdata['from'] = data['departureLocation']
		outdata['to'] = data['arrivalLocation']
		outdata['price'] = int(data['pricedata']['price'][:-2])
		outdata['validPrice'] = data['pricedata']['validPrice']
		outdata['soldOut'] = data['pricedata']['soldOut']
		outdata['url'] = 'http://www.sj.se/microsite/microsite/submit.form?f='+data['departureDate'].replace('-','')+'&G=false&F='+data['departureTime'][0:2]+'00&header.type=TRAVEL&3A=false&c='+data['arrivalLocation'][-5:]+'%3A0'+data['arrivalLocation'][0:2]+'&B='+data['departureLocation'][-5:]+'%3A0'+data['departureLocation'][0:2]+'&header.key=K253891809275136476&l=sv'
		
		self.returndata(outdata)
	
	def returnerror(self, data):
		returdata = {}
		returdata['error'] = data
		self.returndata(returdata)
		
	@tornado.web.asynchronous
	def get(self):
		global cache
		global stopsa
		self.searchdata = ''
		self.http_client = tornado.httpclient.AsyncHTTPClient()
		self.trips={}

		try:
			self.searchdata = 'travelQuery.outDateTime='+self.get_argument('date') +'T'+ tornado.escape.url_escape(self.get_argument('departureTime')[:2]+':00')
			self.getdate = self.get_argument('date')
			self.gettime = self.get_argument('departureTime')
		except:
			self.returnerror('Missing deparature time')
			return None
			
		try:
			self.getfrom = self.get_argument('from')
			self.fromname = stopsa[self.getfrom]
			self.searchdata +='&travelQuery.departureLocationName=' + tornado.escape.url_escape(self.fromname)
		except:
			self.returnerror('Missing deparature station')
			return None
		
		try:
			self.getto = self.get_argument('to')
			self.toname = stopsa[self.getto]
			self.searchdata +='&travelQuery.arrivalLocationName='+ tornado.escape.url_escape(self.toname)
		except:
			self.returnerror('Missing arrival station')
			return None

		try:
			self.gettotime = self.get_argument('arrivalTime')
		except:
			self.returnerror('Missing arrivalTime HH:MM')
			return None
		
		try:
			self.returnrequest(cache[self.getdate+self.getfrom+self.gettime+self.getto+self.gettotime])
			return None
		except:
			notfound = 1
			
		self.searchdata += '&_travelQuery.includeOnlySjProducer=on&'
		self.searchdata += '_travelQuery.includeOnlyNonStopTravel=on&'
		self.searchdata += 'travelQuery.includeExpressBuses=true&'
		self.searchdata += '_travelQuery.includeExpressBuses=on&'
		self.searchdata += 'travelQuery.campaignCode=&'
		self.searchdata += 'changeTravellerInfoRequest.selectedTravellerType=VU&'
		self.searchdata += 'travelQuery.outTimeDeparture=true&'
		self.searchdata += 'submitSearchLater=S%C3%B6k%20resa'
			
		request_setup = tornado.httpclient.HTTPRequest("https://mobil.sj.se/timetable/searchtravel.do", method='GET', follow_redirects=True, max_redirects=3)
		self.http_client.fetch(request_setup, self.gotsession)
		
	def gotsession(self,response):
		self.cookie = response.headers["set-cookie"].split(';')[0]
		header_setup = tornado.httputil.HTTPHeaders({"Cookie": self.cookie,'Content-Type':'application/x-www-form-urlencoded'})
		request_setup = tornado.httpclient.HTTPRequest("https://mobil.sj.se/timetable/searchtravel.do", method='POST', headers=header_setup, body=self.searchdata, follow_redirects=True, max_redirects=3)
		self.http_client.fetch(request_setup, self.doneserach)
	
	def doneserach(self, response):
		header_setup = tornado.httputil.HTTPHeaders({"Cookie": self.cookie})
		request_setup = tornado.httpclient.HTTPRequest("https://mobil.sj.se/api/timetable/departures", method='GET', headers=header_setup, follow_redirects=True, max_redirects=3)
		self.http_client.fetch(request_setup, self.gottrips)

	def gottrips(self, request):
		trips = tornado.escape.json_decode(request.body)

		if len(trips['data']['rows']) > 10:
			max = 10
		else:
			max = len(trips['data']['rows'])
	
		comma = ''
		getpricedata = 'journeyIds='
		for i in range(0, max):
			getpricedata += tornado.escape.url_escape(comma + trips['data']['rows'][i]['id'])
			comma = ','
		
		header_setup = tornado.httputil.HTTPHeaders({"Cookie": self.cookie,'Content-Type':'application/x-www-form-urlencoded'})
		request_setup = tornado.httpclient.HTTPRequest("https://mobil.sj.se/api/timetable/prices/bestforids", method='POST', headers=header_setup, body=getpricedata, follow_redirects=True, max_redirects=3)
		self.http_client.fetch(request_setup, self.gotprices )
		self.trips = trips
	
	def gotprices (self, request):
		global cache
		
		price =  tornado.escape.json_decode(request.body)
		price = price['data']
		trips = self.trips['data']['rows']

		for i in range(0, len(trips)):
			for j in range (0,len(price)):
				if price[j]['journeyId'] == trips[i]['id']:
					trips[i]['pricedata'] = price[j]
					trips[i]['departureDate'] = self.getdate
					trips[i]['departureLocation'] = self.getfrom
					trips[i]['arrivalLocation'] = self.getto
					stopfrom = self.getfrom 
					stopto = self.getto
					datefrom = self.getdate
					timefrom = trips[i]['departureTime']
					timeto = trips[i]['arrivalTime']
					cache[datefrom+stopfrom+timefrom+stopto+timeto] = trips[i]
					break
		
		try:
			self.returnrequest(cache[self.getdate+self.getfrom+self.gettime+self.getto+self.gettotime])

		except:
			self.returnerror('Trip not found in search')

	
	def returndata(self, trips):
		self.write(trips)
		self.finish()

application = tornado.web.Application([
    (r"/sj/", MainHandler),
    (r"/hlt/", hlt.HltHandler),
    (r"/sj/cache/", CachePrint),
])

application.listen(10074)
tornado.ioloop.IOLoop.instance().start()
 
