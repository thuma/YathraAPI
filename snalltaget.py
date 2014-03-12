# !/usr/bin/env python
# -*- coding: utf-8 -*-

import re
import json
import requests
import tornado.httpclient
from threading import Thread

snalltagetstops = open('snalltaget.json')
snalltagetstops = json.load(snalltagetstops)
snalltagetstopsa = {}
for stop in snalltagetstops['stops']:
	snalltagetstopsa[str(stop['P']*100000+stop['L'])] = stop['N']

snalltagetstops = {}

snalltagetcache = {}


class SnalltagetHandler(tornado.web.RequestHandler):
	@tornado.web.asynchronous
	def get(self):
		Thread(target=self.makerequest).start()
		
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
		
		tornado.ioloop.IOLoop.instance().add_callback(self.returndata, outdata)
	
	def returnerror(self, data):
		returdata = {}
		returdata['error'] = data
		tornado.ioloop.IOLoop.instance().add_callback(self.returndata, returdata)
	
	def makerequest(self):
		global snalltagetcache
		global snalltagetstopsa

		query = {}
		
		try:
			query['DepartureDateTime'] = self.get_argument('date') +' '+ self.get_argument('departureTime')[:2]+':00'
			getdate = self.get_argument('date')
			gettime = self.get_argument('departureTime')
		except:
			self.returnerror('Missing deparature time')
			return ''
			
		try:
			getfrom = self.get_argument('from')
			fromname = snalltagetstopsa[getfrom]
			query['DepartureLocationId'] = int(getfrom[-5:])
			query['DepartureLocationProducerCode'] = int(getfrom[:2])
		except:
			self.returnerror('Missing deparature station')
			return ''
		
		try:
			getto = self.get_argument('to')
			toname = snalltagetstopsa[getto]
			query['ArrivalLocationId'] = int(getto[-5:])
			query['ArrivalLocationProducerCode'] = int(getto[:2])
		except:
			self.returnerror('Missing arrival station')
			return ''

		try:
			gettotime = self.get_argument('arrivalTime')
		except:
			self.returnerror('Missing arrivalTime HH:MM')
			return ''
			
		query['TravelType'] = "E"
		query['Passengers'] = [{"PassengerCategory":"VU"}]
		
		try:
			self.returnrequest(snalltagetcache[getdate+getfrom+gettime+getto+gettotime])
			return ''
		except:
			notfound = 1
		
		r = requests.get('https://boka.snalltaget.se/boka-biljett')
		cookie = r.cookies["Token"]
		cookies = dict(Token=cookie)
		
		headers = {'content-type': 'application/json'}

		r = requests.post('https://boka.snalltaget.se/api/timetables', data=json.dumps(query), headers=headers, cookies=cookies)

		trips = r.json()
			
		try:
			if len(trips['JourneyAdvices']) > 10:
				max = 10
			else:
				max = len(trips['JourneyAdvices'])
		except:
			self.returnerror('No trip found list empty')
			return ''
			
		pquery = {'TimetableId':trips['Id'], 'JourneyConnectionReferences':[]}

		for i in range(0, max):
			pquery['JourneyConnectionReferences'].append(trips['JourneyAdvices'][i]['JourneyConnectionReference'])

		r = requests.post('https://boka.snalltaget.se/api/journeyadvices/lowestprices', data=json.dumps(pquery), headers=headers, cookies=cookies)

		price = r.json()

		for i in range(0, len(trips['JourneyAdvices'])):
			for j in range (0,len(price)):
				if price[j]['JourneyConnectionReference'] == trips['JourneyAdvices'][i]['JourneyConnectionReference']:
					trips['JourneyAdvices'][i]['IsSleeperTrain'] = price[j]['IsSleeperTrain']
					trips['JourneyAdvices'][i]['LowestTotalPrice'] = price[j]['LowestTotalPrice']
					trips['JourneyAdvices'][i]['Currency'] = price[j]['Currency']
					stopfrom = str(trips['JourneyAdvices'][i]['DepartureLocation']['ProducerCode']*100000 + trips['JourneyAdvices'][i]['DepartureLocation']['LocationId'])
					stopto = str(trips['JourneyAdvices'][i]['ArrivalLocation']['ProducerCode']*100000 +trips['JourneyAdvices'][i]['ArrivalLocation']['LocationId'])
					datefrom = trips['JourneyAdvices'][i]['DepartureDateTime'][:10]
					timefrom = trips['JourneyAdvices'][i]['DepartureDateTime'][11:16]
					timeto = trips['JourneyAdvices'][i]['ArrivalDateTime'][11:16]
					trips['JourneyAdvices'][i]['ArrivalDateTime']
					snalltagetcache[datefrom+stopfrom+timefrom+stopto+timeto] = trips['JourneyAdvices'][i]
					break
		try:
			self.returnrequest(snalltagetcache[getdate+getfrom+gettime+getto+gettotime])
			return ''
		except:
			self.returnerror('Trip not found in search')
			return ''
		
	def returndata(self, trips):
		self.write(trips)
		self.finish()


