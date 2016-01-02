# -*- coding: utf-8 -*-
from __future__ import print_function
from gevent import monkey;
monkey.patch_all()
import requests
import json
import demjson
import urlparse
import sjstops
from urllib import quote

stations = sjstops.stations

def findprice(env, start_response):
    global stations
    trips = False
    start_response('200 OK', [('Content-Type', 'application/json')])
    getdata = urlparse.parse_qs(env['QUERY_STRING'])
    headers = {'content-type': 'application/json'}
    try:
        fromid = stations[getdata['from'][0]]
        toid = stations[getdata['to'][0]]
    except:
        return '{"error":"station not in netowrk"}'

    try:
        cfile = open('cache/sjbeta/'+getdata['from'][0]+getdata['to'][0]+getdata['date'][0], 'r')
        trips = json.load(cfile)
    except:
        pass
        
    if trips == False:
        trips = getDate(fromid,toid,getdata['date'][0])
        with open('cache/sjbeta/'+getdata['from'][0]+getdata['to'][0]+getdata['date'][0], 'w') as outfile:
            json.dump(trips, outfile)
            
    for trip in trips['journeys']:
        if trip["arrivalTime"]['time'] == getdata['arrivalTime'][0] and trip["departureTime"]['time'] == getdata['departureTime'][0]:
            trip = getDate(fromid,toid,getdata['date'][0],getdata['departureTime'][0],getdata['arrivalTime'][0])
            price = trip['price']['salesCategoryPrice']['SEAT']['STANDARD']['FIX']['journeyPriceDescription']['totalPrice']['amount']
            out = { 
                "departureTime":getdata['departureTime'][0],
               "arrivalTime":getdata['arrivalTime'][0],
               "date":getdata['date'][0],
               "from":getdata['from'][0],
               "to":getdata['to'][0],
               "travelerAge":35,
               "travelerIsStudent":False,
               "sellername":"SJ",
               "price":price,
               "currency":"SEK",
               "validPrice":True,
               "url":"https://beta.sj.se/#/tidtabell/"+quote(fromid['name'])+"/"+quote(toid['name'])+"/enkel/avgang/"+getdata['date'][0].replace("-","")+"-"+getdata['departureTime'][0].replace(":","")+"/avgang/"+getdata['date'][0].replace("-","")+"-"+getdata['departureTime'][0].replace(":","")+"/VU///0/"
               }
            return [json.dumps(out)]
    return ['{"error":"no trip found"}']

def getDate(fromid, toid, date, deptime = None, arrtime = None):
    # Get the basic details from the webpage:
    tokentext = requests.get('https://beta.sj.se/')

    cookieToken = tokentext.content.split('var sj =')
    cookieToken = cookieToken[1].split('</script>')[0].strip()[:-1]
    data = demjson.decode(cookieToken)

    dataSession = data['siteConfig']['sjService']['cookieToken']

    # Create cookies for the API:
    cookies = {dataSession['session']['name']:dataSession['session']['token'],
    dataSession['service']['name']:dataSession['service']['token'],
    'X-api.sj.se-language':'sv'}

    # Make validation:
    r = requests.get('https://beta.sj.se/v4/rest/security/currenttoken', cookies=cookies)

    # Populate request:
    jsonreq = { 
                "departureLocation":{"id":fromid['lId']+':'+fromid['pId']},
                "arrivalLocation":{"id":toid['lId']+':'+toid['pId']},
                "journeyDate":{"date":date},
                "consumers":[{"consumerCategory":{"id":"VU"},
                "personCustomer":{"id":None,"personName":None},
                "loyaltyId":None,
                "discountInstance":None,
                "discountCodeId":None,
                "discountSecurity":None}],
                "viaLocation":None,
                "minimumChangeoverTime":{
                    "days":"0",
                    "hours":"0",
                    "minutes":"0",
                    "duration":None}
                }

    # Request Timetable:
    r = requests.post('https://beta.sj.se/v4/rest/travels/searchdata',
                        cookies=cookies,
                        json=jsonreq)

    tripdata = r.json()

    # Get timetable and price token:
    tt = tripdata['timetableToken']
    pt = tripdata['pricingTokens']['STANDARD']['token']

    # Prepare get timetable:
    getparms = {'buses':'true',
        'expressbuses':'true',
        'highspeedtrains':'true',
        'onlydirectjourneys':'false',
        'onlysj':'false'}

    # Get timetable:
    url = 'https://beta.sj.se/v4/rest/travels/timetables/'+tt
    r = requests.get(url, params=getparms, cookies=cookies)

    trips = r.json()
    
    if deptime != None:
    # Get price for teach trip:
        for i, trip in enumerate(trips['journeys']):
            if trip["arrivalTime"]['time'] == arrtime and trip["departureTime"]['time'] == deptime:
                print("Getting price no: "+ str(i))
                url = 'https://beta.sj.se/v4/rest/travels/prices/'+pt+'/'+trip['journeyToken']
                r = requests.get(url, cookies=cookies)
                trip['price'] = r.json()
                return trip

    # Print all to screen:
    return trips
