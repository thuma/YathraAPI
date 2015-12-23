# !/usr/bin/env python
# -*- coding: utf-8 -*-
import hashlib
import requests
import os
import json
import time
import urlparse
from bs4 import BeautifulSoup


list_data = ''

#with open ('../Transit-Stop-Identifier-Conversions-Sweden/swebus-gtfs.csv', 'r') as myfile:
#    list_data = myfile.readlines()

response = requests.get('https://raw.githubusercontent.com/thuma/Transit-Stop-Identifier-Conversions-Sweden/c0adf021a71a7fb9f640d7907204613318915b61/swebus-gtfs.csv')
list_data = response.content
list_data = list_data.split('\n')

stops = {}

for row in list_data:
    try:
        parts = row.split(',')
        stops[parts[0]] = {}
        stops[parts[0]]['type'] = parts[2]
        stops[parts[0]]['id'] = parts[1]
        stops[parts[0]]['name'] = parts[3]
    except:
        parts = ''
     

type={'0':'BusStop','1':'City'}

def getDayPrice(fromid, toid, fromdate):
    global stops
    global type
        
    url = 'http://www.swebus.se/Express/Sokresultat/\
?from='+stops[fromid]['id']+'\
&fromtype='+type[stops[fromid]['type']]+'\
&to='+stops[toid]['id']+'\
&totype='+type[stops[toid]['type']]+'\
&away='+fromdate+'\
&Adult=1\
&Child=0\
&Youth=0\
&Student=0\
&Pensioner=0\
&Pet=0\
&campaignCode='

    print url
    hash = hashlib.sha224(url).hexdigest()
    
    cachepath = 'cache/swebus/%s' % hash
    all = {}
    
    try:
        statinfo = os.stat(cachepath)
    except:
        statinfo = False
    if statinfo:
        if (time.time() - statinfo.st_mtime) < 3600:
            with open(cachepath, 'r') as cachefile:
                return json.load(cachefile)
    
    pricehtml = requests.get(url).content
    html_data = BeautifulSoup(pricehtml, 'html.parser')
    lista = html_data.find(id='bookingSearchResultsAway').findAll('div', { 'class' : 'Accordion' })
    lista = lista[0].findAll('table') 
    
    for i in lista:
        data = {}
        data['Departure'] = i.findAll('th', { 'class' : 'Departure' })[0].string.strip()
        data['Arrival'] = i.findAll('th', { 'class' : 'Arrival' })[0].string.strip()
        data['url'] = url
        
        try:
            data['Price1'] = i.findAll('th', { 'class' : 'Price1' })[0].findAll('input')[0]['value'].split(' ')[0]
        except:
            data['Price1'] = ''
        
        try:
            data['Price2'] = i.findAll('th', { 'class' : 'Price2' })[0].findAll('input')[0]['value'].split(' ')[0]
        except:
            data['Price2'] = ''
        
        try:
            data['Price3'] = i.findAll('th', { 'class' : 'Price3' })[0].findAll('input')[0]['value'].split(' ')[0]
        except:
            data['Price3'] = ''
        
        all[data['Departure']] = data
    
    with open(cachepath, 'w') as cachefile:
        json.dump(all, cachefile)    
    return all

def getprice(fromid, toid, fromdate, fromtime, todate, totime):
    
    try:
        all = getDayPrice(fromid, toid, fromdate)
    except:
        all = {"no":"data"}
    
    all = getDayPrice(fromid, toid, fromdate)
    
    if fromtime in all:
        if all[fromtime]['Arrival'] == totime:
            outdata = {'travelerAge':35,    
                'travelerIsStudent':False,
                'sellername':'Swebus',
                'price':all[fromtime]['Price1'],
                'currency':'SEK',
                'validPrice':True,
                'departureDate': fromdate,
                'departureTime': fromtime,
                'arrivalDate':todate,
                'arrivalTime':totime,
                'from':fromid,
                'to':toid,
                'url':all[fromtime]['url']
                }
            return json.dumps(outdata)
    return '{"error":"no trip found"}'

def findprice(env, start_response):
    global stops
    start_response('200 OK', [('Content-Type', 'application/json')])
    getdata = urlparse.parse_qs(env['QUERY_STRING'])
    
    if getdata['from'][0] not in stops:
        return['{"error":"Missing from station"}']
    if getdata['to'][0] not in stops:
        return['{"error":"Missing from station"}']
    
    return [
        getprice(getdata['from'][0],
        getdata['to'][0],
        getdata['departureDate'][0],
        getdata['departureTime'][0],
        getdata['arrivalDate'][0],
        getdata['arrivalTime'][0])
        ]

#print getprice('7400001', '7400002', '2015-12-10', '12:36', '2015-12-10','15:55')