# !/usr/bin/env python
# -*- coding: utf-8 -*-

import tornado.httpclient
import xmltodict
import tornado.escape
import json
import time

def getSec(s):
    l = map(int, s.split(':')) # l = list(map(int, s.split(':'))) in Python 3.x
    return sum(n * sec for n, sec in zip(l[::-1], (60, 3600)))

http_client = tornado.httpclient.HTTPClient()
try:
    response = http_client.fetch('https://raw.githubusercontent.com/thuma/Transit-Stop-Identifier-Conversions-Sweden/master/skanerafiken-gtfs.csv')
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
		self.http_client = tornado.httpclient.AsyncHTTPClient()
		global cache
		global stops

		try:
			self.write(self.makeresponse(cache[self.get_argument('from')+self.get_argument('to')+self.get_argument('date')+'T'+self.get_argument('departureTime')+self.get_argument('arrivalTime')]))
			self.finish()
			return
		except:
			timedata = getSec(self.get_argument('departureTime'))
			try:
				for range in cache[self.get_argument('from')+self.get_argument('to')+self.get_argument('date')]:
					print "hh"+str(timedata)
					if range['last'] > timedata and timedata > rage['first']:
						self.write({'error':'trip not found in search'})
						self.finish()
						return
			except:
				hm = 1
		try:
			fromid = tornado.escape.url_escape(stops[self.get_argument('from')]['name'])+'|'+stops[self.get_argument('from')]['id']+'|0'
			toid = tornado.escape.url_escape(stops[self.get_argument('to')]['name'])+'|'+stops[self.get_argument('to')]['id']+'|0'
		except:
			self.write({'error':'from/to station not in network'})
			self.finish()
			return
		
		try:
			deptime = time.strptime(self.get_argument('date')+self.get_argument('departureTime'),'%Y-%m-%d%H:%M')
			deptime = time.mktime(deptime)
			deptime = deptime-120
			deptime = time.gmtime(deptime)
			
		except:
			self.write({'error':'departureTime HH:MM missing / error, date YYYY-MM-DD missing / error'})
			self.finish()
			return
			
		try:
			date = time.strftime('%Y-%m-%d+%H:%M',deptime)
		except:
			self.write({'error':'date YYYY-MM-DD HH:MM missing / error'})
			self.finish()
			return

		searchurl = 'http://www.labs.skanetrafiken.se/v2.2/resultspage.asp?cmdAction=next&selPointFr='+fromid+'&selPointTo='+toid+'&LastStart='+date+'&transportMode=31'
	
		self.myhttprequest = tornado.httpclient.HTTPRequest(searchurl, method='GET')
		self.http_client.fetch(self.myhttprequest, self.searchdone)

	def searchdone(self, response):
		http_client = tornado.httpclient.HTTPClient()
		alldata = xmltodict.parse(response.body)
		alldata = alldata['soap:Envelope']['soap:Body']
		
		first = "nodate"
		last = "nodate"
		for trip in alldata['GetJourneyResponse']['GetJourneyResult']['Journeys']['Journey']:
			cache[self.get_argument('from')+self.get_argument('to')+trip['DepDateTime'][:-3]+trip['ArrDateTime'][11:-3]] = trip
			if first == "nodate":
				first = trip["DepDateTime"][11:-3]
			else:
				last = trip["DepDateTime"][11:-3]
		try:
			cache[self.get_argument('from')+self.get_argument('to')+self.get_argument('date')].append({'first':getSec(first),'last':getSec(last)})
		except:
			cache[self.get_argument('from')+self.get_argument('to')+self.get_argument('date')] = []
			cache[self.get_argument('from')+self.get_argument('to')+self.get_argument('date')].append({'first':getSec(first),'last':getSec(last)})
		try:
			self.write(self.makeresponse(cache[self.get_argument('from')+self.get_argument('to')+self.get_argument('date')+'T'+self.get_argument('departureTime')+self.get_argument('arrivalTime')]))
			self.finish()
			return
		except:
			self.write({'error':'no trip found'})
			self.finish()
			return

	def makeresponse(self, data):
		outdata = {"travelerAge":35,	
			"travelerIsStudent":False,
			"sellername":"Skånetrafiken",
			"price":"",
			"currency":"SEK",
			"validPrice":True,
			"url":"http://www.skanetrafiken.se"
			}
		
		outdata['departureTime'] = self.get_argument('departureTime')
		outdata['arrivalTime'] = self.get_argument('arrivalTime')
		outdata['date'] = self.get_argument('date')
		outdata['from'] = self.get_argument('from')
		outdata['to'] = self.get_argument('to')
		outdata['price'] = data["Prices"]["PriceInfo"][3]["Price"]
		outdata['validPrice'] = 1
	
		return outdata

