# !/usr/bin/env python
# -*- coding: utf-8 -*-

import tornado.web

stops = {'7400001':'cst','7400708':'norra','7400492':'södra'}

class CachePrint(tornado.web.RequestHandler):
	def get(self):
		global stops
		self.write(stops)

class Handler(tornado.web.RequestHandler):

	@tornado.web.asynchronous
	def get(self):
		global stops
		try:
			fromname = stops[self.get_argument('from')]
			toname = stops[self.get_argument('to')]
			self.write({"departureTime": self.get_argument('departureTime'), "validPrice": 1, "from": self.get_argument('from'), "to": self.get_argument('to'), "url": "https://www.arlandaexpress.se/", "price": 260, "travelerIsStudent": 'false', "travelerAge": 35, "currency": "SEK", "arrivalTime": self.get_argument('arrivalTime'), "date": self.get_argument('date'), "sellername": "Arlandaexpress"})
			self.finish()
			return
		except:
			self.write({'error':'from/to station not in network'})
			self.finish()
			return
	
