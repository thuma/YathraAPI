# !/usr/bin/env python
# -*- coding: utf-8 -*-

import requests


r = requests.get('https://mobil.sj.se/timetable/searchtravel.do', allow_redirects=True)
cookie = r.cookies['JSESSIONID']
cookies = dict(JSESSIONID=cookie)


searchdata = {}
searchdata['travelQuery.departureLocationName']='Lund C'
searchdata['travelQuery.arrivalLocationName']='Varberg'
searchdata['_travelQuery.includeOnlySjProducer']='on'
searchdata['_travelQuery.includeOnlyNonStopTravel']='on'
searchdata['travelQuery.includeExpressBuses']='true'
searchdata['_travelQuery.includeExpressBuses']='on'
searchdata['travelQuery.campaignCode']=''
searchdata['changeTravellerInfoRequest.selectedTravellerType']='VU'
searchdata['travelQuery.outTimeDeparture']='true'
searchdata['travelQuery.outDateTime']='2014-02-20T12:00'
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
