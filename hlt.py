from bs4 import BeautifulSoup
import re
import json
import tornado.ioloop
import tornado.web
import tornado.httpclient
import tornado.httputil
import tornado.escape


http_client = tornado.httpclient.HTTPClient()
try:
    response = http_client.fetch("https://raw.github.com/thuma/TSC-Tables/master/hallandstrafiken-gtfs.csv")
    allstops = response.body.split('\n')
    rubriker = allstops[0].split(';')
    del allstops[0]
    hltids = {}
    for stop in allstops:
		stopdelar = stop.split(';')
		try:
			ids[stopdelar[4]] = stopdelar
		except:
			print 'end'
    print hltids
 	
except tornado.httpclient.HTTPError as e:
    print "Error:", e
http_client.close()


class HltSearch(tornado.web.RequestHandler):
	@tornado.web.asynchronous
	def get(self):
		global hltids
		self.http_client = tornado.httpclient.AsyncHTTPClient()
		
		#Get parametera
		searchdata='inpPointFr_ajax=Varberg+Station+%28T%E5g%29%7C6699%7C0&inpPointTo_ajax=%C5s+Gamla+K%F6pstad%7C6014%7C0&inpPointInterm_ajax=&selRegionFr=741&inpPointFr=Varberg+Station+%28T%E5g%29++%5BH%E5llplats%5D&optTypeFr=0&inpPointTo=%C5s+Gamla+K%F6pstad++%5BH%E5llplats%5D&optTypeTo=0&inpPointInterm=&selDirection=0&inpTime=10%3A03&inpDate=2014-03-22&optReturn=0&selDirection2=0&inpTime2=02%3A03&inpDate2=2014-03-01&trafficmask=1&trafficmask=2&trafficmask=4&Submit=S%F6k&selChangeTime=0&selWalkSpeed=0&selPriority=0&cmdAction=search&EU_Spirit=False&TNSource=HALLAND&SupportsScript=True&Language=se&VerNo=7.1.1.2.0.38p3&Source=querypage_adv&MapParams='
		
		#Search
		request_setup = tornado.httpclient.HTTPRequest("http://193.45.213.123/halland/v2/querypage_adv.aspx", body=searchdata, method='POST')
		self.http_client.fetch(request_setup, self.searchDone)
		
	def searchDone():
		#soup = BeautifulSoup()
		#soup2 = soup.find(id="result-3")
		#soup2.find_all('td')[1].string
		