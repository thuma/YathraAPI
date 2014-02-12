# !/usr/bin/env python
# -*- coding: utf-8 -*-

import re
import json
import tornado.ioloop
import tornado.web
import tornado.httpclient
import tornado.httputil
import tornado.escape

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
	
	def returnerror(self, data):
		returdata = {}
		returdata['error'] = data
		
	@tornado.web.asynchronous
	def get(self):
		global cache
		global stopsa
		self.searchdata = ''
		self.http_client = tornado.httpclient.AsyncHTTPClient()

		try:
			self.searchdata = 'travelQuery.outDateTime='+self.get_argument('date') +'T'+ tornado.escape.url_escape(self.get_argument('departureTime')[:2]+':00')
			getdate = self.get_argument('date')
			gettime = self.get_argument('departureTime')
		except:
			self.returnerror('Missing deparature time')
			return ''
			
		try:
			getfrom = self.get_argument('from')
			fromname = stopsa[getfrom]
			self.searchdata +='&travelQuery.departureLocationName=' + tornado.escape.url_escape(fromname)
		except:
			self.returnerror('Missing deparature station')
			return ''
		
		try:
			getto = self.get_argument('to')
			toname = stopsa[getto]
			self.searchdata +='&travelQuery.arrivalLocationName='+ tornado.escape.url_escape(toname)
		except:
			self.returnerror('Missing arrival station')
			return ''

		try:
			gettotime = self.get_argument('arrivalTime')
		except:
			self.returnerror('Missing arrivalTime HH:MM')
			return ''
		
		try:
			self.returnrequest(cache[getdate+getfrom+gettime+getto+gettotime])
			return ''
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
		print 'got cookie'
		self.cookie = response.headers["set-cookie"].split(';')[0]
		header_setup = tornado.httputil.HTTPHeaders({"Cookie": self.cookie,'Content-Type':'application/x-www-form-urlencoded'})
		request_setup = tornado.httpclient.HTTPRequest("https://mobil.sj.se/timetable/searchtravel.do", method='POST', headers=header_setup, body=self.searchdata, follow_redirects=True, max_redirects=3)
		self.http_client.fetch(request_setup, self.doneserach)
	
	def doneserach(self, response):
		header_setup = tornado.httputil.HTTPHeaders({"Cookie": self.cookie})
		request_setup = tornado.httpclient.HTTPRequest("https://mobil.sj.se/api/timetable/departures", method='GET', headers=header_setup, follow_redirects=True, max_redirects=3)
		self.http_client.fetch(request_setup, self.gottrips)

	def gottrips(self, request):
		print request.body
		self.write(request.body)
		self.finish()
	
	def temp():
		trips = r.json()

		if len(trips['data']['rows']) > 10:
			max = 10
		else:
			max = len(trips['data']['rows'])
	
		getpricedata = {'journeyIds':''}
		comma = ''
		
		for i in range(0, max):
			getpricedata['journeyIds'] = getpricedata['journeyIds'] + comma + trips['data']['rows'][i]['id']
			comma = ','

		r = requests.post('https://mobil.sj.se/api/timetable/prices/bestforids', data=getpricedata, allow_redirects=True, cookies=cookies)
	
	def gotprices (self, request):
		global cache
		price = r.json()
		price = price['data']
		trips = trips['data']['rows']

		for i in range(0, len(trips)):
			for j in range (0,len(price)):
				if price[j]['journeyId'] == trips[i]['id']:
					trips[i]['pricedata'] = price[j]
					trips[i]['departureDate'] = getdate
					trips[i]['departureLocation'] = getfrom
					trips[i]['arrivalLocation'] = getto
					stopfrom = getfrom 
					stopto = getto
					datefrom = getdate
					timefrom = trips[i]['departureTime']
					timeto = trips[i]['arrivalTime']
					cache[datefrom+stopfrom+timefrom+stopto+timeto] = trips[i]
					break
		
		try:
			self.returnrequest(cache[getdate+getfrom+gettime+getto+gettotime])

		except:
			self.returnerror('Trip not found in search')

	
	def returndata(self, trips):
		self.write(trips)
		self.finish()

application = tornado.web.Application([
    (r"/sj/", MainHandler),
    (r"/sj/cache/", CachePrint),
])

application.listen(10074)
tornado.ioloop.IOLoop.instance().start()
 
