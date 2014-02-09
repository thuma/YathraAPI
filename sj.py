# !/usr/bin/env python
# -*- coding: utf-8 -*-

import requests
import re
import json
import tornado.ioloop
import tornado.web
from threading import Thread

cache = {}

stops = open('snalltaget.json')
stops = json.load(stops)
stopsa = {}
for stop in stops['stops']:
	stopsa[str(stop['P']*100000+stop['L'])] = stop['N']
stops = {}



class MainHandler(tornado.web.RequestHandler):
	@tornado.web.asynchronous
	def get(self):
		Thread(target=self.makerequest).start()
		
	def returnrequest(self, data):
		outdata = {"travelerAge":35,
		"travelerIsStudent":False,
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
		
		tornado.ioloop.IOLoop.instance().add_callback(self.returndata, outdata)
	
	def returnerror(self, data):
		returdata = {}
		returdata['error'] = data
		tornado.ioloop.IOLoop.instance().add_callback(self.returndata, returdata)
	
	def makerequest(self):
		global cache
		global stopsa
		searchdata = {}

		try:
			searchdata['travelQuery.outDateTime'] = self.get_argument('date') +'T'+ self.get_argument('departureTime')[:2]+':00'
			getdate = self.get_argument('date')
			gettime = self.get_argument('departureTime')
		except:
			self.returnerror('Missing deparature time')
			return ''
			
		try:
			getfrom = self.get_argument('from')
			fromname = stopsa[getfrom]
			searchdata['travelQuery.departureLocationName'] = fromname
		except:
			self.returnerror('Missing deparature station')
			return ''
		
		try:
			getto = self.get_argument('to')
			toname = stopsa[getto]
			searchdata['travelQuery.arrivalLocationName'] = toname
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
		
		r = requests.get('https://mobil.sj.se/timetable/searchtravel.do', allow_redirects=True)
		cookie = r.cookies['JSESSIONID']
		cookies = dict(JSESSIONID=cookie)

		searchdata['_travelQuery.includeOnlySjProducer']='on'
		searchdata['_travelQuery.includeOnlyNonStopTravel']='on'
		searchdata['travelQuery.includeExpressBuses']='true'
		searchdata['_travelQuery.includeExpressBuses']='on'
		searchdata['travelQuery.campaignCode']=''
		searchdata['changeTravellerInfoRequest.selectedTravellerType']='VU'
		searchdata['travelQuery.outTimeDeparture']='true'
		searchdata['submitSearchLater']='Sök resa'
		

		r = requests.post('https://mobil.sj.se/timetable/searchtravel.do', data=searchdata, allow_redirects=True, cookies=cookies)

		r = requests.get('https://mobil.sj.se/api/timetable/departures', allow_redirects=True, cookies=cookies)

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
			return ''
		except:
			self.returnerror('Trip not found in search')
			return ''
		
	def returndata(self, trips):
		self.write(trips)
		self.finish()

application = tornado.web.Application([
    (r"/sj/", MainHandler),
])

application.listen(8888)
tornado.ioloop.IOLoop.instance().start()
 