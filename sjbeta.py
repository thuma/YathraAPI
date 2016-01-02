# -*- coding: utf-8 -*-
from __future__ import print_function
from gevent import monkey;
monkey.patch_all()
import requests
import json
import demjson
import urlparse
stations = {}

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
            price = trip['price']['salesCategoryPrice']['SEAT']['STANDARD']['FIX']['journeyPriceDescription']['totalPrice']['amount']
            out = { 
                "departureTime":getdata['departureTime'][0],
               "arrivalTime":getdata['arrivalTime'][0],
               "date":getdata['date'][0],
               "from":getdata['from'][0],
               "to":getdata['to'][0],
               "travelerAge":35,
               "travelerIsStudent":False,
               "sellername":"'SJ",
               "price":price,
               "currency":"SEK",
               "validPrice":True,
               "url":"https://www.sj.se/"
               }
            return [json.dumps(out)]
    return ['{"error":"no trip found"}']

def getDate(fromid, toid, date):
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

    # Get price for teach trip:
    for i, trip in enumerate(trips['journeys']):
        url = 'https://beta.sj.se/v4/rest/travels/prices/'+pt+'/'+trip['journeyToken']
        r = requests.get(url, cookies=cookies)
        trips['journeys'][i]['price'] = r.json()

    # Print all to screen:
    return trips

stationsraw = [
  {
    "name": "Abbekås",
    "synonyms": [
      "ABBEKÅS"
    ],
    "lId": "01006",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 55.39388888888889,
      "lon": 13.593333333333334
    }
  },
  {
    "name": "Abborrträsk",
    "synonyms": [
      "ABBORRTRÄSK",
      "ABBORRTRÆSK"
    ],
    "lId": "01095",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 65.44888888888889,
      "lon": 19.386388888888888
    }
  },
  {
    "name": "Abisko turiststation",
    "synonyms": [
      "ABISKO TURISTSTATION"
    ],
    "lId": "00114",
    "prio": 1,
    "pId": "074",
    "pos": {
      "lat": 68.35666666666665,
      "lon": 18.78611111111111
    }
  },
  {
    "name": "Abisko Östra",
    "synonyms": [
      "ABISKO OSTRA",
      "ABISKO ÖSTRA",
      "ABISKO ØSTRA"
    ],
    "lId": "00151",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 68.34833333333333,
      "lon": 18.829166666666666
    }
  },
  {
    "name": "Abrahamsberg T-bana",
    "synonyms": [
      "ABRAHAMSBERG T-BANA"
    ],
    "lId": "21689",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.336666666666666,
      "lon": 17.952777777777776
    }
  },
  {
    "name": "Adak",
    "synonyms": [
      "ADAK"
    ],
    "lId": "13940",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 65.34888888888888,
      "lon": 18.592777777777776
    }
  },
  {
    "name": "Adelsö kyrka",
    "synonyms": [
      "ADELSÖ KYRKA",
      "ADELSØ KYRKA"
    ],
    "lId": "01007",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.35944444444445,
      "lon": 17.529722222222222
    }
  },
  {
    "name": "Adelöv Marknadsplatsen",
    "synonyms": [
      "ADELÖV MARKNADSPLATSEN",
      "ADELÖV MARKNPL",
      "ADELØV MARKNADSPLATSEN",
      "ADELØV MARKNPL"
    ],
    "lId": "04051",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 58.01277777777778,
      "lon": 14.667777777777777
    }
  },
  {
    "name": "Adolfström",
    "synonyms": [
      "ADOLFSTRÖM",
      "ADOLFSTRØM"
    ],
    "lId": "01214",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 66.27805555555555,
      "lon": 16.650555555555552
    }
  },
  {
    "name": "Aga",
    "synonyms": [
      "AGA"
    ],
    "lId": "23962",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.34638888888889,
      "lon": 18.154999999999998
    }
  },
  {
    "name": "Agunnaryd kyrka",
    "synonyms": [
      "AGUNNARYD KYRKA"
    ],
    "lId": "10006",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 56.74666666666667,
      "lon": 14.146666666666667
    }
  },
  {
    "name": "Akalla T-bana",
    "synonyms": [
      "AKALLA T-BANA"
    ],
    "lId": "21677",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.414722222222224,
      "lon": 17.912777777777777
    }
  },
  {
    "name": "Alanäs vägskäl",
    "synonyms": [
      "ALANÄS VÄGSKÄL",
      "ALANÆS VÆGSKÆL"
    ],
    "lId": "29193",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 64.16444444444446,
      "lon": 15.674999999999999
    }
  },
  {
    "name": "Alberga",
    "synonyms": [
      "ALBERGA"
    ],
    "lId": "20769",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.278888888888886,
      "lon": 16.11916666666667
    }
  },
  {
    "name": "Alby Centralgatan Medelpad",
    "synonyms": [
      "ALBY CENTRALGATAN MEDELPAD"
    ],
    "lId": "15094",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 62.495555555555555,
      "lon": 15.476944444444445
    }
  },
  {
    "name": "Alby T-bana",
    "synonyms": [
      "ALBY T-BANA"
    ],
    "lId": "21731",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.239444444444445,
      "lon": 17.845277777777778
    }
  },
  {
    "name": "Alfta",
    "synonyms": [
      "ALFTA",
      "ALFTA BSTN"
    ],
    "lId": "00589",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 61.344722222222224,
      "lon": 16.064722222222223
    }
  },
  {
    "name": "Algutsrum rastplats",
    "synonyms": [
      "ALGUTSRUM RASTPLATS"
    ],
    "lId": "22381",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 56.68194444444444,
      "lon": 16.521944444444443
    }
  },
  {
    "name": "Alingsås",
    "synonyms": [
      "ALINGSAS",
      "ALINGSÅS",
      "ALINGSÅS STN"
    ],
    "lId": "00018",
    "prio": 1,
    "pId": "074",
    "pos": {
      "lat": 57.92666666666666,
      "lon": 12.532222222222224
    }
  },
  {
    "name": "Alleparken",
    "synonyms": [
      "ALLEPARKEN",
      "ALLÉPARKEN"
    ],
    "lId": "24814",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.32888888888889,
      "lon": 17.973611111111108
    }
  },
  {
    "name": "Allerum skola",
    "synonyms": [
      "ALLERUM SKOLA"
    ],
    "lId": "21771",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 56.111666666666665,
      "lon": 12.693611111111112
    }
  },
  {
    "name": "Allsta",
    "synonyms": [
      "ALLSTA"
    ],
    "lId": "27549",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 62.324444444444445,
      "lon": 17.220555555555553
    }
  },
  {
    "name": "Almbro",
    "synonyms": [
      "ALMBRO"
    ],
    "lId": "10011",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.19555555555555,
      "lon": 15.247499999999999
    }
  },
  {
    "name": "Almnäs",
    "synonyms": [
      "ALMNÄS",
      "ALMNÆS"
    ],
    "lId": "01096",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.17194444444444,
      "lon": 17.523333333333333
    }
  },
  {
    "name": "Almunge skola",
    "synonyms": [
      "ALMUNGE SKOLA"
    ],
    "lId": "01008",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.86694444444444,
      "lon": 18.071666666666665
    }
  },
  {
    "name": "Almunge station",
    "synonyms": [
      "ALMUNGE STATION"
    ],
    "lId": "12806",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.875277777777775,
      "lon": 18.046111111111113
    }
  },
  {
    "name": "Almvik by",
    "synonyms": [
      "ALMVIK BY"
    ],
    "lId": "14090",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 57.82694444444445,
      "lon": 16.46722222222222
    }
  },
  {
    "name": "Alnarp Kungsgårdsvägen",
    "synonyms": [
      "ALNARP KUNGSGÅRDSVÄGEN"
    ],
    "lId": "24319",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 55.65833333333333,
      "lon": 13.087777777777779
    }
  },
  {
    "name": "Alnaryd",
    "synonyms": [
      "ALNARYD"
    ],
    "lId": "10013",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 56.340833333333336,
      "lon": 15.430833333333332
    }
  },
  {
    "name": "Alnö Vi centrum",
    "synonyms": [
      "ALNÖ VI CENTRUM",
      "ALNØ VI CENTRUM"
    ],
    "lId": "00399",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 62.42777777777778,
      "lon": 17.41611111111111
    }
  },
  {
    "name": "Alsen bygdegård",
    "synonyms": [
      "ALSEN BYGDEGÅRD"
    ],
    "lId": "13422",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 63.38666666666666,
      "lon": 13.923888888888888
    }
  },
  {
    "name": "Alsike station",
    "synonyms": [
      "ALSIKE STATION",
      "ALSIKE STN"
    ],
    "lId": "12828",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.7575,
      "lon": 17.761388888888888
    }
  },
  {
    "name": "Alstad Stationsvägen",
    "synonyms": [
      "ALSTAD STATIONSVÄGEN",
      "ALSTAD STATIONSVÆGEN",
      "ALSTAD STATIONV"
    ],
    "lId": "16529",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 55.453611111111115,
      "lon": 13.208888888888888
    }
  },
  {
    "name": "Alster E18",
    "synonyms": [
      "ALSTER E18"
    ],
    "lId": "10017",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.401666666666664,
      "lon": 13.611666666666666
    }
  },
  {
    "name": "Alster Lantmännen",
    "synonyms": [
      "ALSTER LANTMÄNN",
      "ALSTER LANTMÄNNEN",
      "ALSTER LANTMÆNN",
      "ALSTER LANTMÆNNEN"
    ],
    "lId": "22224",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.400277777777774,
      "lon": 13.609166666666667
    }
  },
  {
    "name": "Alsterbro",
    "synonyms": [
      "ALSTERBRO"
    ],
    "lId": "14082",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 56.94277777777778,
      "lon": 15.914444444444445
    }
  },
  {
    "name": "Alstermo Larmgatan",
    "synonyms": [
      "ALSTERMO LARMGATAN"
    ],
    "lId": "24759",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 56.975,
      "lon": 15.65611111111111
    }
  },
  {
    "name": "Altorp station",
    "synonyms": [
      "ALTORP STATION",
      "ALTORP STN"
    ],
    "lId": "20868",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.41,
      "lon": 18.072777777777777
    }
  },
  {
    "name": "Alunda busstation",
    "synonyms": [
      "ALUNDA BSTN",
      "ALUNDA BUSSTATION"
    ],
    "lId": "00734",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 60.0625,
      "lon": 18.080277777777777
    }
  },
  {
    "name": "Alunda gångtunneln",
    "synonyms": [
      "ALUNDA GÅNGTUNNELN"
    ],
    "lId": "07106",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 60.0625,
      "lon": 18.080555555555556
    }
  },
  {
    "name": "Alvastra klosterruin",
    "synonyms": [
      "ALVASTRA KLOSTERRUIN",
      "ALVASTRAKLOSTER"
    ],
    "lId": "25016",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 58.29833333333333,
      "lon": 14.659444444444444
    }
  },
  {
    "name": "Alvastra vägskäl",
    "synonyms": [
      "ALVASTRA VSK",
      "ALVASTRA VÄGSKÄL",
      "ALVASTRA VÆGSKÆL"
    ],
    "lId": "01009",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 58.301111111111105,
      "lon": 14.670555555555556
    }
  },
  {
    "name": "Alvesta",
    "synonyms": [
      "ALVESTA",
      "ALVESTA STN"
    ],
    "lId": "00004",
    "prio": 1,
    "pId": "074",
    "pos": {
      "lat": 56.89861111111111,
      "lon": 14.556111111111111
    }
  },
  {
    "name": "Alvik Minneberg",
    "synonyms": [
      "ALVIK MINNEBERG"
    ],
    "lId": "50837",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.33916666666667,
      "lon": 17.989722222222223
    }
  },
  {
    "name": "Alvik T-bana",
    "synonyms": [
      "ALVIK T-BANA"
    ],
    "lId": "20755",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.33361111111111,
      "lon": 17.979999999999997
    }
  },
  {
    "name": "Alvik väg 94 Luleå",
    "synonyms": [
      "ALVIK VÄG 94 LULEÅ",
      "ALVIK VÆG 94 LULEÅ"
    ],
    "lId": "14860",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 65.56777777777778,
      "lon": 21.77583333333333
    }
  },
  {
    "name": "Alviks strand",
    "synonyms": [
      "ALVIKS STRAND"
    ],
    "lId": "24925",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.3275,
      "lon": 17.981944444444444
    }
  },
  {
    "name": "Ambjörby ICA Skogsstjärnan",
    "synonyms": [
      "AMBJÖRBY ICA SKOGSSTJÄRNAN",
      "AMBJØRBY ICA SKOGSSTJÆRNAN"
    ],
    "lId": "04321",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 60.4975,
      "lon": 13.168888888888889
    }
  },
  {
    "name": "Ambjörnarp centrum",
    "synonyms": [
      "AMBJÖRNARP CENTRUM",
      "AMBJØRNARP CENTRUM"
    ],
    "lId": "12084",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 57.42111111111111,
      "lon": 13.293333333333333
    }
  },
  {
    "name": "Amborseröd",
    "synonyms": [
      "AMBORSERÖD",
      "AMBORSERØD"
    ],
    "lId": "16224",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 58.39472222222222,
      "lon": 11.326666666666666
    }
  },
  {
    "name": "Amhult resecentrum",
    "synonyms": [
      "AMHULT RESECENTRUM"
    ],
    "lId": "71633",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 57.70944444444445,
      "lon": 11.780000000000001
    }
  },
  {
    "name": "Ammarnäs",
    "synonyms": [
      "AMMARNÄS",
      "AMMARNÆS"
    ],
    "lId": "00306",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 65.9575,
      "lon": 16.20777777777778
    }
  },
  {
    "name": "Amsbergskorsning E16",
    "synonyms": [
      "AMSBERGSKORSNING E16"
    ],
    "lId": "13000",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 60.529444444444444,
      "lon": 15.337777777777779
    }
  },
  {
    "name": "Anderslöv",
    "synonyms": [
      "ANDERSLÖV",
      "ANDERSLÖV TORG",
      "ANDERSLØV",
      "ANDERSLØV TORG"
    ],
    "lId": "01097",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 55.43805555555555,
      "lon": 13.317222222222222
    }
  },
  {
    "name": "Anderstorp",
    "synonyms": [
      "ANDERSTORP",
      "ANDERSTORP STN"
    ],
    "lId": "00518",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 57.280277777777776,
      "lon": 13.627222222222223
    }
  },
  {
    "name": "Aneby",
    "synonyms": [
      "ANEBY",
      "ANEBY STN"
    ],
    "lId": "00379",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 57.836111111111116,
      "lon": 14.810555555555556
    }
  },
  {
    "name": "Angarn kyrka",
    "synonyms": [
      "ANGARN KYRKA"
    ],
    "lId": "20606",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.535,
      "lon": 18.1725
    }
  },
  {
    "name": "Angered centrum",
    "synonyms": [
      "ANGERED CENTRUM"
    ],
    "lId": "25606",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 57.795833333333334,
      "lon": 12.049166666666666
    }
  },
  {
    "name": "Ankarede",
    "synonyms": [
      "ANKAREDE"
    ],
    "lId": "13177",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 64.81805555555555,
      "lon": 14.237222222222222
    }
  },
  {
    "name": "Ankarsrum station",
    "synonyms": [
      "ANKARSRUM STATION",
      "ANKARSRUM STN"
    ],
    "lId": "00907",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 57.69972222222222,
      "lon": 16.334444444444443
    }
  },
  {
    "name": "Ankarsrum väg 40",
    "synonyms": [
      "ANKARSRUM VÄG 40"
    ],
    "lId": "38855",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 57.70777777777778,
      "lon": 16.329722222222223
    }
  },
  {
    "name": "Anneberg kiosken Småland",
    "synonyms": [
      "ANNEBERG KIOSKEN SMÅLAND"
    ],
    "lId": "10026",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 57.72277777777778,
      "lon": 14.806111111111111
    }
  },
  {
    "name": "Anneberg station",
    "synonyms": [
      "ANNEBERG STATION",
      "ANNEBERG STN"
    ],
    "lId": "00285",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 57.53916666666667,
      "lon": 12.100555555555555
    }
  },
  {
    "name": "Annelund TA",
    "synonyms": [
      "ANNELUND TA"
    ],
    "lId": "04220",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 57.99055555555556,
      "lon": 13.093055555555557
    }
  },
  {
    "name": "Annelöv S",
    "synonyms": [
      "ANNELÖV S",
      "ANNELØV S"
    ],
    "lId": "24307",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 55.83444444444444,
      "lon": 13.022777777777778
    }
  },
  {
    "name": "Ansta",
    "synonyms": [
      "ANSTA"
    ],
    "lId": "43711",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.69027777777777,
      "lon": 16.577222222222222
    }
  },
  {
    "name": "Anten",
    "synonyms": [
      "ANTEN"
    ],
    "lId": "12509",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 57.98916666666667,
      "lon": 12.440277777777778
    }
  },
  {
    "name": "Antnäs",
    "synonyms": [
      "ANTNÄS",
      "ANTNÄS E4",
      "ANTNÆS",
      "ANTNÆS E4"
    ],
    "lId": "14859",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 65.54833333333333,
      "lon": 21.84611111111111
    }
  },
  {
    "name": "Anttis affären",
    "synonyms": [
      "ANTTIS AFFÄREN",
      "ANTTIS AFFÆREN"
    ],
    "lId": "14791",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 67.26611111111112,
      "lon": 22.778888888888886
    }
  },
  {
    "name": "Anttis väg 395",
    "synonyms": [
      "ANTTIS VÄG 395"
    ],
    "lId": "14795",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 67.2538888888889,
      "lon": 22.7825
    }
  },
  {
    "name": "Aplared centrum",
    "synonyms": [
      "APLARED CENTRUM"
    ],
    "lId": "12410",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 57.64944444444444,
      "lon": 13.074166666666667
    }
  },
  {
    "name": "Apokätno",
    "synonyms": [
      "APOKÄTNO",
      "APOKÄTNO STN",
      "APOKÆTNO",
      "APOKÆTNO STN"
    ],
    "lId": "01540",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 66.4563888888889,
      "lon": 19.723333333333333
    }
  },
  {
    "name": "Arboga",
    "synonyms": [
      "ARBOGA",
      "ARBOGA STN"
    ],
    "lId": "00262",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.39694444444444,
      "lon": 15.840833333333334
    }
  },
  {
    "name": "Arboga Kungsörsvägen Teknikpk",
    "synonyms": [
      "ARBOGA KUNGSÖRSVÄGEN TEKNIKPK"
    ],
    "lId": "21274",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.39472222222222,
      "lon": 15.887777777777778
    }
  },
  {
    "name": "Arboga Teknikpark",
    "synonyms": [
      "ARBOGA TEKNIKPARK"
    ],
    "lId": "25841",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.39472222222222,
      "lon": 15.895277777777777
    }
  },
  {
    "name": "Arboga Ålbrovägen",
    "synonyms": [
      "ARBOGA ÅLBROVÄGEN"
    ],
    "lId": "45146",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.45333333333333,
      "lon": 15.747499999999999
    }
  },
  {
    "name": "Arbrå",
    "synonyms": [
      "ARBRÅ",
      "ARBRÅ STN"
    ],
    "lId": "00615",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 61.47027777777778,
      "lon": 16.38
    }
  },
  {
    "name": "Ardala",
    "synonyms": [
      "ARDALA"
    ],
    "lId": "01440",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 58.36027777777778,
      "lon": 13.337777777777779
    }
  },
  {
    "name": "Arholma brygga",
    "synonyms": [
      "ARHOLMA BRYGGA"
    ],
    "lId": "24314",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.85111111111111,
      "lon": 19.1075
    }
  },
  {
    "name": "Arild bussplatsen",
    "synonyms": [
      "ARILD BUSSPLATSEN"
    ],
    "lId": "00745",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 56.27305555555555,
      "lon": 12.576944444444445
    }
  },
  {
    "name": "Arjeplog",
    "synonyms": [
      "ARJEPLOG",
      "ARJEPLOG BSTN"
    ],
    "lId": "00873",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 66.05222222222221,
      "lon": 17.89611111111111
    }
  },
  {
    "name": "Arjeplog torget",
    "synonyms": [
      "ARJEPLOG TORGET"
    ],
    "lId": "23792",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 66.05027777777778,
      "lon": 17.887777777777778
    }
  },
  {
    "name": "Arkelstorp affären",
    "synonyms": [
      "ARKELSTORP AFFAREN",
      "ARKELSTORP AFFÄREN",
      "ARKELSTORP AFFÆREN"
    ],
    "lId": "01010",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 56.17305555555555,
      "lon": 14.28277777777778
    }
  },
  {
    "name": "Arkösund",
    "synonyms": [
      "ARKÖSUND",
      "ARKØSUND"
    ],
    "lId": "00841",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 58.49,
      "lon": 16.93611111111111
    }
  },
  {
    "name": "Arlanda C",
    "synonyms": [
      "ARLANDA C",
      "ARN"
    ],
    "lId": "00556",
    "prio": 1,
    "pId": "074",
    "pos": {
      "lat": 59.64944444444444,
      "lon": 17.929166666666667
    }
  },
  {
    "name": "Arlanda Gränsgatan",
    "synonyms": [
      "ARLANDA GRÄNSGATAN"
    ],
    "lId": "10537",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.63583333333333,
      "lon": 17.929444444444446
    }
  },
  {
    "name": "Arlöv",
    "synonyms": [
      "ARLÖV",
      "ARLÖV SOCKERBIT",
      "ARLØV",
      "ARLØV SOCKERBIT"
    ],
    "lId": "16532",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 55.63194444444444,
      "lon": 13.070277777777777
    }
  },
  {
    "name": "Arninge",
    "synonyms": [
      "ARNINGE"
    ],
    "lId": "01168",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.46277777777778,
      "lon": 18.13277777777778
    }
  },
  {
    "name": "Arnö Mejramvägen",
    "synonyms": [
      "ARNÖ MEJRAMVÄGEN",
      "ARNØ MEJRAMVÆGEN"
    ],
    "lId": "10038",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 58.72777777777778,
      "lon": 17.023888888888887
    }
  },
  {
    "name": "Arnöviken",
    "synonyms": [
      "ARNÖVIKEN",
      "ARNØVIKEN"
    ],
    "lId": "10039",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 61.69638888888888,
      "lon": 17.385833333333334
    }
  },
  {
    "name": "Arrie",
    "synonyms": [
      "ARRIE"
    ],
    "lId": "12631",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 55.5175,
      "lon": 13.086944444444445
    }
  },
  {
    "name": "Arvidsjaur busstation",
    "synonyms": [
      "ARVIDSJAUR BSTN",
      "ARVIDSJAUR BUSSTATION"
    ],
    "lId": "14619",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 65.59222222222222,
      "lon": 19.1825
    }
  },
  {
    "name": "Arvika",
    "synonyms": [
      "ARVIKA",
      "ARVIKA STN"
    ],
    "lId": "00221",
    "prio": 1,
    "pId": "074",
    "pos": {
      "lat": 59.65333333333333,
      "lon": 12.591111111111111
    }
  },
  {
    "name": "Arvika busstation",
    "synonyms": [
      "ARVIKA BSTN",
      "ARVIKA BUSSTATION"
    ],
    "lId": "10040",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.655277777777776,
      "lon": 12.586944444444445
    }
  },
  {
    "name": "Arvikafestivalen",
    "synonyms": [
      "ARVIKAFESTIVALEN"
    ],
    "lId": "11754",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.64833333333333,
      "lon": 12.620833333333334
    }
  },
  {
    "name": "Asarum Storgatan",
    "synonyms": [
      "ASARUM STORGATAN"
    ],
    "lId": "00583",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 56.20888888888889,
      "lon": 14.83361111111111
    }
  },
  {
    "name": "Askeby affären",
    "synonyms": [
      "ASKEBY AFFÄREN",
      "ASKEBY AFFÆREN"
    ],
    "lId": "10045",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 58.408055555555556,
      "lon": 15.849722222222223
    }
  },
  {
    "name": "Askersby Asker byväg",
    "synonyms": [
      "ASKER BYVÄG",
      "ASKER BYVÆG",
      "ASKERSBY ASKER BYVÄG",
      "ASKERSBY ASKER BYVÆG"
    ],
    "lId": "10046",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.151111111111106,
      "lon": 15.474444444444444
    }
  },
  {
    "name": "Askersund",
    "synonyms": [
      "ASKERSUND",
      "ASKERSUND BSTN"
    ],
    "lId": "00610",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 58.87888888888889,
      "lon": 14.9075
    }
  },
  {
    "name": "Askims torg",
    "synonyms": [
      "ASKIMS TORG"
    ],
    "lId": "59092",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 57.63472222222222,
      "lon": 11.936944444444444
    }
  },
  {
    "name": "Asmundtorp Toftavägen",
    "synonyms": [
      "ASMUNDTORP TOFTAVÄGEN",
      "ASMUNDTORP TOFTAVÆGEN"
    ],
    "lId": "16535",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 55.885555555555555,
      "lon": 12.945
    }
  },
  {
    "name": "Aspa bruk Askersund",
    "synonyms": [
      "ASPA BRUK ASKERSUND"
    ],
    "lId": "04266",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 58.776944444444446,
      "lon": 14.797777777777778
    }
  },
  {
    "name": "Aspa Nyköping",
    "synonyms": [
      "ASPA NYKÖPING",
      "ASPA NYKØPING"
    ],
    "lId": "20909",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 58.927499999999995,
      "lon": 17.099722222222223
    }
  },
  {
    "name": "Aspedalen",
    "synonyms": [
      "ASPEDALEN",
      "ASPEDALEN STN"
    ],
    "lId": "01011",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 57.76305555555555,
      "lon": 12.258888888888889
    }
  },
  {
    "name": "Aspen",
    "synonyms": [
      "ASPEN",
      "ASPEN STN"
    ],
    "lId": "01012",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 57.754444444444445,
      "lon": 12.24111111111111
    }
  },
  {
    "name": "Asperö",
    "synonyms": [
      "ASPERÖ",
      "ASPERÖ ÖSTRA",
      "ASPERØ",
      "ASPERØ ØSTRA"
    ],
    "lId": "01202",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 57.649166666666666,
      "lon": 11.807222222222222
    }
  },
  {
    "name": "Aspudden T-bana",
    "synonyms": [
      "ASPUDDEN T-BANA"
    ],
    "lId": "21720",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.30638888888888,
      "lon": 18.00138888888889
    }
  },
  {
    "name": "Aspås",
    "synonyms": [
      "ASPÅS",
      "ASPÅS KYRKA"
    ],
    "lId": "13419",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 63.36694444444444,
      "lon": 14.484166666666665
    }
  },
  {
    "name": "Assberg",
    "synonyms": [
      "ASSBERG",
      "ASSBERG STN"
    ],
    "lId": "00286",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 57.49472222222222,
      "lon": 12.669444444444444
    }
  },
  {
    "name": "Astrid Lindgrens värld",
    "synonyms": [
      "ASTRID LINDGRENS VÄRLD",
      "ASTRID LINDGRENS VÆRLD"
    ],
    "lId": "01013",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 57.67472222222222,
      "lon": 15.842500000000001
    }
  },
  {
    "name": "Auktsjaur",
    "synonyms": [
      "AUKTSJAUR",
      "AUKTSJAUR V45"
    ],
    "lId": "04406",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 65.74305555555556,
      "lon": 19.393055555555556
    }
  },
  {
    "name": "Ausås Ausåsvägen",
    "synonyms": [
      "AUSÅS AUSÅSVÄGEN"
    ],
    "lId": "04087",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 56.16583333333333,
      "lon": 12.88861111111111
    }
  },
  {
    "name": "Avan skolan",
    "synonyms": [
      "AVAN SKOLAN"
    ],
    "lId": "14872",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 65.68,
      "lon": 21.804166666666667
    }
  },
  {
    "name": "Avaviken",
    "synonyms": [
      "AVAVIKEN",
      "AVAVIKEN STN"
    ],
    "lId": "04407",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 65.60499999999999,
      "lon": 18.65083333333333
    }
  },
  {
    "name": "Avesta centrum station",
    "synonyms": [
      "AVESTA CENTRUM STATION",
      "AVESTA CM STN"
    ],
    "lId": "01568",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 60.1475,
      "lon": 16.16638888888889
    }
  },
  {
    "name": "Avesta Krylbo",
    "synonyms": [
      "AVESTA KRYLBO"
    ],
    "lId": "00111",
    "prio": 1,
    "pId": "074",
    "pos": {
      "lat": 60.129444444444445,
      "lon": 16.215833333333332
    }
  },
  {
    "name": "Axala handel",
    "synonyms": [
      "AXALA HANDEL"
    ],
    "lId": "21539",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 58.99861111111111,
      "lon": 17.174166666666668
    }
  },
  {
    "name": "Axbergshammar",
    "synonyms": [
      "AXBERGSHAMMAR"
    ],
    "lId": "20934",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.42305555555555,
      "lon": 15.178333333333333
    }
  },
  {
    "name": "Axelsberg T-bana",
    "synonyms": [
      "AXELSBERG T-BANA"
    ],
    "lId": "21722",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.30416666666667,
      "lon": 17.975277777777777
    }
  },
  {
    "name": "Axmarby",
    "synonyms": [
      "AXMARBY"
    ],
    "lId": "10055",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 61.00083333333333,
      "lon": 17.115833333333335
    }
  },
  {
    "name": "Axvall centrum",
    "synonyms": [
      "AXVALL CENTRUM"
    ],
    "lId": "00035",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 58.388333333333335,
      "lon": 13.574444444444444
    }
  },
  {
    "name": "Axvall travbana",
    "synonyms": [
      "AXVALL TRAVBANA"
    ],
    "lId": "10056",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 58.39611111111111,
      "lon": 13.563055555555556
    }
  },
  {
    "name": "Backa Orust",
    "synonyms": [
      "BACKA ORUST"
    ],
    "lId": "21009",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 58.15861111111111,
      "lon": 11.46111111111111
    }
  },
  {
    "name": "Backaryd",
    "synonyms": [
      "BACKARYD"
    ],
    "lId": "01015",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 56.347500000000004,
      "lon": 15.153055555555556
    }
  },
  {
    "name": "Backe",
    "synonyms": [
      "BACKE",
      "BACKE BSTN"
    ],
    "lId": "00514",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 63.81055555555555,
      "lon": 16.404999999999998
    }
  },
  {
    "name": "Backlura",
    "synonyms": [
      "BACKLURA",
      "BACKLURA VÄXTHV",
      "BACKLURA VÆXTHV"
    ],
    "lId": "01023",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.385555555555555,
      "lon": 17.82472222222222
    }
  },
  {
    "name": "Bada korsväg",
    "synonyms": [
      "BADA KORSVÄG",
      "BADA KORSVÆG"
    ],
    "lId": "10061",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 60.07666666666667,
      "lon": 13.094722222222222
    }
  },
  {
    "name": "Badabruk station",
    "synonyms": [
      "BADABRUK STATION",
      "BADABRUK STN"
    ],
    "lId": "01412",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 60.06194444444444,
      "lon": 13.095833333333333
    }
  },
  {
    "name": "Badsta station",
    "synonyms": [
      "BADSTA STATION",
      "BADSTA STN"
    ],
    "lId": "23520",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.54611111111111,
      "lon": 14.291666666666666
    }
  },
  {
    "name": "Bagarmossen T-bana",
    "synonyms": [
      "BAGARMOSSEN T-BANA"
    ],
    "lId": "21692",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.27611111111111,
      "lon": 18.13138888888889
    }
  },
  {
    "name": "Baggeby",
    "synonyms": [
      "BAGGEBY"
    ],
    "lId": "23963",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.35666666666667,
      "lon": 18.13361111111111
    }
  },
  {
    "name": "Baggetorp",
    "synonyms": [
      "BAGGETORP"
    ],
    "lId": "10064",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.00861111111111,
      "lon": 16.06416666666667
    }
  },
  {
    "name": "Ballingslöv Hagagatan",
    "synonyms": [
      "BALLINGSLÖV HAG",
      "BALLINGSLÖV HAGAGATAN",
      "BALLINGSLØV HAG",
      "BALLINGSLØV HAGAGATAN"
    ],
    "lId": "22829",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 56.21388888888889,
      "lon": 13.844722222222222
    }
  },
  {
    "name": "Ballingslöv station",
    "synonyms": [
      "BALLINGSLÖV STATION",
      "BALLINGSLØV STATION"
    ],
    "lId": "01441",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 56.214444444444446,
      "lon": 13.84888888888889
    }
  },
  {
    "name": "Balsby Brommagårdsvägen",
    "synonyms": [
      "BALSBY BROMMAGV",
      "BALSBY BROMMAGÅRDSVÄGEN",
      "BALSBY BROMMAGÅRDSVÆGEN"
    ],
    "lId": "04112",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 56.077222222222225,
      "lon": 14.220555555555556
    }
  },
  {
    "name": "Bandhagen T-bana",
    "synonyms": [
      "BANDHAGEN T-BANA"
    ],
    "lId": "21711",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.27027777777778,
      "lon": 18.049444444444447
    }
  },
  {
    "name": "Bankekind affären",
    "synonyms": [
      "BANKEKIND AFFÄREN",
      "BANKEKIND AFFÆREN"
    ],
    "lId": "20263",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 58.374722222222225,
      "lon": 15.825555555555555
    }
  },
  {
    "name": "Bankeryd",
    "synonyms": [
      "BANKERYD"
    ],
    "lId": "00977",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 57.86083333333333,
      "lon": 14.12888888888889
    }
  },
  {
    "name": "Bara",
    "synonyms": [
      "BARA",
      "BARA BANVÄGEN",
      "BARA BANVÆGEN"
    ],
    "lId": "00746",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 55.57944444444445,
      "lon": 13.190833333333334
    }
  },
  {
    "name": "Barkarby handelsplats",
    "synonyms": [
      "BARKARBY HANDELSPLATS"
    ],
    "lId": "45398",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.41861111111111,
      "lon": 17.857222222222223
    }
  },
  {
    "name": "Barkarby station",
    "synonyms": [
      "BARKARBY STATION",
      "BARKARBY STN"
    ],
    "lId": "00383",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.40333333333333,
      "lon": 17.86888888888889
    }
  },
  {
    "name": "Barkarö",
    "synonyms": [
      "BARKARÖ",
      "BARKARØ"
    ],
    "lId": "10071",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.55277777777778,
      "lon": 16.508055555555554
    }
  },
  {
    "name": "Barkåkra station",
    "synonyms": [
      "BARKÅKRA STATION"
    ],
    "lId": "01613",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 56.29694444444444,
      "lon": 12.823333333333332
    }
  },
  {
    "name": "Barkåkra Valhall Park",
    "synonyms": [
      "BARKÅKRA VALHALL PARK"
    ],
    "lId": "01451",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 56.285,
      "lon": 12.840277777777779
    }
  },
  {
    "name": "Barnens ö gård",
    "synonyms": [
      "BARNENS Ö GÅRD",
      "BARNENS Ø GÅRD"
    ],
    "lId": "23503",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.919444444444444,
      "lon": 18.92138888888889
    }
  },
  {
    "name": "Barsebäck kyrka",
    "synonyms": [
      "BARSEBÄCK KYRKA",
      "BARSEBÆCK KYRKA"
    ],
    "lId": "16541",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 55.77027777777778,
      "lon": 12.956388888888888
    }
  },
  {
    "name": "Barsebäckshamn",
    "synonyms": [
      "BARSEBÄCKSHAMN",
      "BARSEBÆCKSHAMN"
    ],
    "lId": "16542",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 55.75694444444444,
      "lon": 12.909722222222223
    }
  },
  {
    "name": "Barstahamn",
    "synonyms": [
      "BARSTAHAMN"
    ],
    "lId": "29046",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 62.863055555555555,
      "lon": 18.39527777777778
    }
  },
  {
    "name": "Barum Ivövägen",
    "synonyms": [
      "BARUM IVÖVÄGEN",
      "BARUM IVØVÆGEN"
    ],
    "lId": "10077",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 56.11277777777778,
      "lon": 14.365555555555556
    }
  },
  {
    "name": "Barva kyrka",
    "synonyms": [
      "BARVA KYRKA"
    ],
    "lId": "21282",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.37138888888889,
      "lon": 16.78805555555556
    }
  },
  {
    "name": "Baskemölla",
    "synonyms": [
      "BASKEMÖLLA",
      "BASKEMÖLLA GLAD",
      "BASKEMØLLA",
      "BASKEMØLLA GLAD"
    ],
    "lId": "01002",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 55.59027777777778,
      "lon": 14.311944444444444
    }
  },
  {
    "name": "Basthagen",
    "synonyms": [
      "BASTHAGEN",
      "BASTHAGEN STN"
    ],
    "lId": "01016",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 58.205555555555556,
      "lon": 15.974166666666667
    }
  },
  {
    "name": "Bastuträsk",
    "synonyms": [
      "BASTUTRASK",
      "BASTUTRÄSK",
      "BASTUTRÄSK STN",
      "BASTUTRÆSK",
      "BASTUTRÆSK STN"
    ],
    "lId": "00294",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 64.78999999999999,
      "lon": 20.041111111111114
    }
  },
  {
    "name": "Beddingestrand",
    "synonyms": [
      "BEDDINGESTRAND"
    ],
    "lId": "01098",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 55.36388888888889,
      "lon": 13.430555555555555
    }
  },
  {
    "name": "Bengtsfors busstation",
    "synonyms": [
      "BENGTSFORS BUSSTATION"
    ],
    "lId": "12097",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.03055555555555,
      "lon": 12.223611111111111
    }
  },
  {
    "name": "Bengtsheden",
    "synonyms": [
      "BENGTSHEDEN"
    ],
    "lId": "24262",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 60.70055555555556,
      "lon": 15.873611111111112
    }
  },
  {
    "name": "Berg Hagvägen",
    "synonyms": [
      "BERG HAGVÄGEN",
      "BERG HAGVÆGEN"
    ],
    "lId": "10084",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 58.49194444444444,
      "lon": 15.528611111111111
    }
  },
  {
    "name": "Berga station",
    "synonyms": [
      "BERGA STATION",
      "BERGA STN"
    ],
    "lId": "00500",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 57.21611111111111,
      "lon": 16.0325
    }
  },
  {
    "name": "Berga Örlogsskolor",
    "synonyms": [
      "BERGA ÖRLOGSKOL",
      "BERGA ÖRLOGSSK.",
      "BERGA ÖRLOGSSKOLOR",
      "BERGA ØRLOGSKOL",
      "BERGA ØRLOGSSK.",
      "BERGA ØRLOGSSKOLOR"
    ],
    "lId": "01508",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.080000000000005,
      "lon": 18.13277777777778
    }
  },
  {
    "name": "Bergagård Ljungby skola",
    "synonyms": [
      "BERGAGÅRD LJUNGBY SKOLA",
      "BERGAGÅRD SKOLA"
    ],
    "lId": "33861",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 56.98111111111111,
      "lon": 12.578333333333333
    }
  },
  {
    "name": "Bergby",
    "synonyms": [
      "BERGBY"
    ],
    "lId": "01017",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 60.92833333333333,
      "lon": 17.039722222222224
    }
  },
  {
    "name": "Bergby gård Älmsta",
    "synonyms": [
      "BERGBY GÅRD ÄLMSTA"
    ],
    "lId": "45700",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 60.05611111111111,
      "lon": 18.75027777777778
    }
  },
  {
    "name": "Bergeforsen",
    "synonyms": [
      "BERGEFORSEN"
    ],
    "lId": "15457",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 62.52361111111111,
      "lon": 17.386666666666667
    }
  },
  {
    "name": "Bergfors",
    "synonyms": [
      "BERGFORS",
      "BERGFORS STN"
    ],
    "lId": "00354",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 68.14861111111112,
      "lon": 19.779722222222222
    }
  },
  {
    "name": "Berghem",
    "synonyms": [
      "BERGHEM",
      "BERGHEM STN"
    ],
    "lId": "00339",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 57.466944444444444,
      "lon": 12.598333333333334
    }
  },
  {
    "name": "Bergkarlås",
    "synonyms": [
      "BERGKARLÅS"
    ],
    "lId": "13091",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 61.03611111111111,
      "lon": 14.630277777777778
    }
  },
  {
    "name": "Bergkvara Gökalund",
    "synonyms": [
      "BERGKVARA GÖKALUND"
    ],
    "lId": "00572",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 56.39472222222222,
      "lon": 16.06527777777778
    }
  },
  {
    "name": "Bergkvara hamn",
    "synonyms": [
      "BERGKVARA HAMN"
    ],
    "lId": "14101",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 56.385,
      "lon": 16.090833333333332
    }
  },
  {
    "name": "Bergom",
    "synonyms": [
      "BERGOM"
    ],
    "lId": "15105",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 63.23277777777778,
      "lon": 18.574444444444445
    }
  },
  {
    "name": "Bergsbyn",
    "synonyms": [
      "BERGSBYN"
    ],
    "lId": "26315",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 64.72527777777778,
      "lon": 21.07361111111111
    }
  },
  {
    "name": "Bergshammar",
    "synonyms": [
      "BERGSHAMMAR"
    ],
    "lId": "10091",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 58.74166666666667,
      "lon": 16.911944444444444
    }
  },
  {
    "name": "Bergshamra T-bana",
    "synonyms": [
      "BERGSHAMRA T-BANA"
    ],
    "lId": "21644",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.38138888888889,
      "lon": 18.03638888888889
    }
  },
  {
    "name": "Bergsjö",
    "synonyms": [
      "BERGSJO",
      "BERGSJÖ",
      "BERGSJÖ BSTN",
      "BERGSJØ",
      "BERGSJØ BSTN"
    ],
    "lId": "00592",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 61.98527777777778,
      "lon": 17.0575
    }
  },
  {
    "name": "Bergsjön Galileis Gata",
    "synonyms": [
      "BERGSJÖN GALILEIS GATA",
      "BERGSJØN GALILEIS GATA"
    ],
    "lId": "25629",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 57.76027777777778,
      "lon": 12.051388888888889
    }
  },
  {
    "name": "Bergsjön Komettorget",
    "synonyms": [
      "BERGSJÖN KOMETTORGET",
      "BERGSJØN KOMETTORGET"
    ],
    "lId": "25646",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 57.75083333333333,
      "lon": 12.071388888888889
    }
  },
  {
    "name": "Bergsjön Rymdtorget",
    "synonyms": [
      "BERGSJÖN RYMDTORGET",
      "BERGSJØN RYMDTORGET"
    ],
    "lId": "25676",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 57.755833333333335,
      "lon": 12.066666666666666
    }
  },
  {
    "name": "Bergsjön Teleskopgatan",
    "synonyms": [
      "BERGSJÖN TELESKOPGATAN",
      "BERGSJØN TELESKOPGATAN"
    ],
    "lId": "25691",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 57.75972222222222,
      "lon": 12.06
    }
  },
  {
    "name": "Bergsunds strand",
    "synonyms": [
      "BERGSUNDS STRAND"
    ],
    "lId": "46226",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.318333333333335,
      "lon": 18.026944444444442
    }
  },
  {
    "name": "Bergsviken",
    "synonyms": [
      "BERGSVIKEN"
    ],
    "lId": "27053",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 65.3086111111111,
      "lon": 21.393055555555556
    }
  },
  {
    "name": "Bergsåker Selångergården",
    "synonyms": [
      "BERGSÅKER SELÅNGERGÅRDEN"
    ],
    "lId": "15068",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 62.41305555555555,
      "lon": 17.21944444444444
    }
  },
  {
    "name": "Bergsäng",
    "synonyms": [
      "BERGSÄNG",
      "BERGSÆNG"
    ],
    "lId": "10093",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 60.11638888888889,
      "lon": 13.5625
    }
  },
  {
    "name": "Bergvik",
    "synonyms": [
      "BERGVIK",
      "BERGVIKSBRON"
    ],
    "lId": "00707",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 61.257777777777775,
      "lon": 16.834166666666665
    }
  },
  {
    "name": "Bergvik Bergviksskolan",
    "synonyms": [
      "BERGVIK BERGVIKSSKOLAN",
      "BERGVIKSSKOLAN"
    ],
    "lId": "17975",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 61.26444444444444,
      "lon": 16.833333333333332
    }
  },
  {
    "name": "Bergåsa",
    "synonyms": [
      "BERGASA",
      "BERGÅSA",
      "BERGÅSA STN"
    ],
    "lId": "01537",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 56.1825,
      "lon": 15.601111111111111
    }
  },
  {
    "name": "Berlin Hbf",
    "synonyms": [
      "BERLIN HAUPTBAHNHOF",
      "BERLIN HBF"
    ],
    "lId": "10100",
    "prio": 1,
    "pId": "080",
    "pos": {
      "lat": 52.525555555555556,
      "lon": 13.369444444444445
    }
  },
  {
    "name": "Bernshammar affären",
    "synonyms": [
      "BERNSHAMMAR AFFÄREN",
      "BERNSHAMMAR AFFÆREN"
    ],
    "lId": "25731",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.66888888888889,
      "lon": 15.770833333333334
    }
  },
  {
    "name": "Bertilsbro",
    "synonyms": [
      "BERTILSBRO"
    ],
    "lId": "10095",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.50611111111111,
      "lon": 15.371666666666668
    }
  },
  {
    "name": "Bestorp vägskäl",
    "synonyms": [
      "BESTORP VÄGSKÄL",
      "BESTORP VÆGSKÆL"
    ],
    "lId": "23294",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 58.233333333333334,
      "lon": 15.736388888888888
    }
  },
  {
    "name": "Bettna Löta handel",
    "synonyms": [
      "BETTNA LÖTA HANDEL"
    ],
    "lId": "21310",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 58.90833333333333,
      "lon": 16.63277777777778
    }
  },
  {
    "name": "Bie",
    "synonyms": [
      "BIE",
      "BIE AFFÄREN",
      "BIE AFFÆREN"
    ],
    "lId": "10097",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.08861111111111,
      "lon": 16.21361111111111
    }
  },
  {
    "name": "Billdal",
    "synonyms": [
      "BILLDAL"
    ],
    "lId": "00835",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 57.5775,
      "lon": 11.940833333333334
    }
  },
  {
    "name": "Billeberga",
    "synonyms": [
      "BILLEBERGA",
      "BILLEBERGA STN"
    ],
    "lId": "00934",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 55.88388888888889,
      "lon": 12.995555555555555
    }
  },
  {
    "name": "Billesholm",
    "synonyms": [
      "BILLESHOLM",
      "BILLESHOLM STN"
    ],
    "lId": "00935",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 56.05638888888888,
      "lon": 12.97638888888889
    }
  },
  {
    "name": "Billinge Måns Andreas väg",
    "synonyms": [
      "BILLINGE M ANDR",
      "BILLINGE MÅNS ANDREAS VÄG"
    ],
    "lId": "16552",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 55.96416666666667,
      "lon": 13.330555555555556
    }
  },
  {
    "name": "Billingsfors",
    "synonyms": [
      "BILLINGSFORS",
      "BILLINGSFRS STN"
    ],
    "lId": "00980",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 58.98166666666667,
      "lon": 12.249722222222221
    }
  },
  {
    "name": "Billsta",
    "synonyms": [
      "BILLSTA",
      "BILLSTA Ö-VIK",
      "BILLSTA Ø-VIK"
    ],
    "lId": "26926",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 63.32222222222222,
      "lon": 18.511944444444445
    }
  },
  {
    "name": "Birsta E4",
    "synonyms": [
      "BIRSTA E4"
    ],
    "lId": "35516",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 62.44472222222222,
      "lon": 17.33833333333333
    }
  },
  {
    "name": "Bispgården",
    "synonyms": [
      "BISPGÅRDEN"
    ],
    "lId": "00489",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 63.026666666666664,
      "lon": 16.625
    }
  },
  {
    "name": "Bjurholm",
    "synonyms": [
      "BJURHOLM",
      "BJURHOLM BSTN"
    ],
    "lId": "00309",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 63.931666666666665,
      "lon": 19.216666666666665
    }
  },
  {
    "name": "Bjurhovda",
    "synonyms": [
      "BJURHOVDA"
    ],
    "lId": "70955",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.62444444444444,
      "lon": 16.621111111111112
    }
  },
  {
    "name": "Bjursås Korsvägen",
    "synonyms": [
      "BJURSÅS KORSVÄGEN",
      "BJURSÅS KORSVÆGEN"
    ],
    "lId": "00641",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 60.73444444444444,
      "lon": 15.43888888888889
    }
  },
  {
    "name": "Bjursås SkiCenter",
    "synonyms": [
      "BJURSÅS SKICENTER"
    ],
    "lId": "25306",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 60.76555555555556,
      "lon": 15.462499999999999
    }
  },
  {
    "name": "Bjurtjärns prästgård",
    "synonyms": [
      "BJURTJÄRN PRÄST",
      "BJURTJÄRNS PRÄSTGÅRD",
      "BJURTJÆRN PRÆST",
      "BJURTJÆRNS PRÆSTGÅRD"
    ],
    "lId": "04326",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.422777777777775,
      "lon": 14.353333333333333
    }
  },
  {
    "name": "Bjurträsk",
    "synonyms": [
      "BJURTRÄSK",
      "BJURTRÆSK"
    ],
    "lId": "13865",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 64.97361111111111,
      "lon": 19.721944444444443
    }
  },
  {
    "name": "Bjurvik väg 26 gränsen",
    "synonyms": [
      "BJURVIK VÄG 26 GRÄNSEN"
    ],
    "lId": "22352",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.05222222222222,
      "lon": 14.141666666666666
    }
  },
  {
    "name": "Bjuv",
    "synonyms": [
      "BJUV",
      "BJUV STN"
    ],
    "lId": "00102",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 56.08305555555556,
      "lon": 12.912222222222223
    }
  },
  {
    "name": "Bjärka-Säby slott",
    "synonyms": [
      "BJÄRKA-SÄBY SLOTT",
      "BJÄRKASÄBY SLOT",
      "BJÆRKA-SÆBY SLOTT",
      "BJÆRKASÆBY SLOT"
    ],
    "lId": "23151",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 58.26861111111111,
      "lon": 15.73861111111111
    }
  },
  {
    "name": "Bjärlöv N väg 19 P-plats",
    "synonyms": [
      "BJÄRLÖV N V 19",
      "BJÄRLÖV N VÄG 19 P-PLATS",
      "BJÆRLØV N V 19",
      "BJÆRLØV N VÆG 19 P-PLATS"
    ],
    "lId": "30761",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 56.11694444444444,
      "lon": 14.09138888888889
    }
  },
  {
    "name": "Bjärnum",
    "synonyms": [
      "BJÄRNUM",
      "BJÄRNUM BSTN",
      "BJÆRNUM",
      "BJÆRNUM BSTN"
    ],
    "lId": "00567",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 56.291666666666664,
      "lon": 13.710555555555555
    }
  },
  {
    "name": "Bjärnum station",
    "synonyms": [
      "BJÄRNUM STATION",
      "BJÆRNUM STATION"
    ],
    "lId": "01608",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 56.29138888888889,
      "lon": 13.706666666666665
    }
  },
  {
    "name": "Bjärred",
    "synonyms": [
      "BJÄRRED",
      "BJÄRRED CENTRUM",
      "BJÆRRED",
      "BJÆRRED CENTRUM"
    ],
    "lId": "00936",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 55.722500000000004,
      "lon": 13.027222222222223
    }
  },
  {
    "name": "Bjärsjölagård Syrengatan",
    "synonyms": [
      "BJÄRSJÖLAGÅRD SYRENGATAN",
      "BJÆRSJØLAGÅRD SYRENGATAN"
    ],
    "lId": "16562",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 55.723888888888894,
      "lon": 13.688055555555556
    }
  },
  {
    "name": "Bjärtrå Sahlbergs",
    "synonyms": [
      "BJÄRTRÅ SAHLBERGS",
      "BJÆRTRÅ SAHLBERGS"
    ],
    "lId": "15107",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 62.968333333333334,
      "lon": 17.893333333333334
    }
  },
  {
    "name": "Bjästa busstation",
    "synonyms": [
      "BJÄSTA BSTN",
      "BJÄSTA BUSSTATION",
      "BJÆSTA BSTN",
      "BJÆSTA BUSSTATION"
    ],
    "lId": "00400",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 63.20138888888889,
      "lon": 18.501666666666665
    }
  },
  {
    "name": "Björbo Affären",
    "synonyms": [
      "BJÖRBO AFFÄREN"
    ],
    "lId": "25020",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 60.45583333333334,
      "lon": 14.729444444444445
    }
  },
  {
    "name": "Björboholm",
    "synonyms": [
      "BJÖRBOHOLM",
      "BJØRBOHOLM"
    ],
    "lId": "15904",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 57.87416666666667,
      "lon": 12.326944444444445
    }
  },
  {
    "name": "Björke",
    "synonyms": [
      "BJÖRKE",
      "BJØRKE"
    ],
    "lId": "18420",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 60.76583333333333,
      "lon": 17.190277777777776
    }
  },
  {
    "name": "Björketorp",
    "synonyms": [
      "BJORKETORP",
      "BJÖRKETORP",
      "BJÖRKETORP STN",
      "BJØRKETORP",
      "BJØRKETORP STN"
    ],
    "lId": "00981",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 57.427499999999995,
      "lon": 12.523333333333333
    }
  },
  {
    "name": "Björkfors",
    "synonyms": [
      "BJÖRKFORS",
      "BJØRKFORS"
    ],
    "lId": "10117",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 65.92027777777778,
      "lon": 23.459444444444443
    }
  },
  {
    "name": "Björkhagen T-bana",
    "synonyms": [
      "BJÖRKHAGEN T-BANA",
      "BJØRKHAGEN T-BANA"
    ],
    "lId": "21694",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.29111111111111,
      "lon": 18.11527777777778
    }
  },
  {
    "name": "Björkhult vägskäl Vimmerby",
    "synonyms": [
      "BJÖRKHULT VSK",
      "BJÖRKHULT VÄGSKÄL VIMMERBY",
      "BJØRKHULT VSK",
      "BJØRKHULT VÆGSKÆL VIMMERBY"
    ],
    "lId": "23288",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 57.85,
      "lon": 15.664444444444445
    }
  },
  {
    "name": "Björkliden",
    "synonyms": [
      "BJORKLIDEN",
      "BJÖRKLIDEN",
      "BJÖRKLIDEN STN",
      "BJØRKLIDEN",
      "BJØRKLIDEN STN"
    ],
    "lId": "00059",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 68.4063888888889,
      "lon": 18.686666666666667
    }
  },
  {
    "name": "Björklinge",
    "synonyms": [
      "BJÖRKLINGE",
      "BJÖRKLINGE SÄTU",
      "BJØRKLINGE",
      "BJØRKLINGE SÆTU"
    ],
    "lId": "00735",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 60.031666666666666,
      "lon": 17.551944444444445
    }
  },
  {
    "name": "Björknäs",
    "synonyms": [
      "BJÖRKNÄS",
      "BJÖRKNÄS CM",
      "BJØRKNÆS",
      "BJØRKNÆS CM"
    ],
    "lId": "01169",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.31472222222222,
      "lon": 18.227777777777778
    }
  },
  {
    "name": "Björksele",
    "synonyms": [
      "BJÖRKSELE",
      "BJØRKSELE"
    ],
    "lId": "01100",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 64.98722222222223,
      "lon": 18.51527777777778
    }
  },
  {
    "name": "Björkvik",
    "synonyms": [
      "BJÖRKVIK",
      "BJØRKVIK"
    ],
    "lId": "01101",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 58.839444444444446,
      "lon": 16.514444444444443
    }
  },
  {
    "name": "Björköby",
    "synonyms": [
      "BJORKOBY",
      "BJÖRKÖBY",
      "BJØRKØBY"
    ],
    "lId": "00962",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 57.52055555555555,
      "lon": 14.917777777777777
    }
  },
  {
    "name": "Björna Centrum",
    "synonyms": [
      "BJÖRNA CENTRUM",
      "BJØRNA CENTRUM"
    ],
    "lId": "15110",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 63.55027777777777,
      "lon": 18.599166666666665
    }
  },
  {
    "name": "Björneborg Konsum",
    "synonyms": [
      "BJÖRNEBORG",
      "BJÖRNEBORG KONSUM",
      "BJØRNEBORG",
      "BJØRNEBORG KONSUM"
    ],
    "lId": "24437",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.2425,
      "lon": 14.252222222222223
    }
  },
  {
    "name": "Björnfjell",
    "synonyms": [
      "BJORNFJELL",
      "BJÖRNFJELL"
    ],
    "lId": "02406",
    "prio": 0,
    "pId": "076",
    "pos": {
      "lat": 68.44416666666667,
      "lon": 18.093055555555555
    }
  },
  {
    "name": "Björnlunda",
    "synonyms": [
      "BJÖRNLUNDA",
      "BJØRNLUNDA"
    ],
    "lId": "10124",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.064166666666665,
      "lon": 17.15888888888889
    }
  },
  {
    "name": "Björnrike centrat",
    "synonyms": [
      "BJÖRNRIKE CENTRAT",
      "BJØRNRIKE CENTRAT"
    ],
    "lId": "23990",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 62.42305555555555,
      "lon": 13.954166666666666
    }
  },
  {
    "name": "Björnrike vägskäl",
    "synonyms": [
      "BJÖRNRIKE VSK",
      "BJÖRNRIKE VÄGSKÄL",
      "BJØRNRIKE VSK",
      "BJØRNRIKE VÄGSKÄL"
    ],
    "lId": "01102",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 62.41138888888889,
      "lon": 13.919166666666666
    }
  },
  {
    "name": "Björnsholm",
    "synonyms": [
      "BJÖRNSHOLM",
      "BJØRNSHOLM"
    ],
    "lId": "01103",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 57.950833333333335,
      "lon": 16.441666666666666
    }
  },
  {
    "name": "Björnvallen",
    "synonyms": [
      "BJÖRNRIKE",
      "BJÖRNVALLEN"
    ],
    "lId": "64291",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 62.41555555555556,
      "lon": 13.949722222222222
    }
  },
  {
    "name": "Björnögården Västerås",
    "synonyms": [
      "BJÖRNÖGÅRDEN VÄSTERÅS"
    ],
    "lId": "43555",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.575833333333335,
      "lon": 16.610833333333336
    }
  },
  {
    "name": "Björsjö skola",
    "synonyms": [
      "BJÖRSJÖ SKOLA"
    ],
    "lId": "25222",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 60.032777777777774,
      "lon": 15.33
    }
  },
  {
    "name": "Björsund västra",
    "synonyms": [
      "BJÖRSUND VÄSTRA",
      "BJØRSUND VÆSTRA"
    ],
    "lId": "10125",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.45138888888889,
      "lon": 16.725277777777777
    }
  },
  {
    "name": "Björsäter kyrka",
    "synonyms": [
      "BJÖRSÄTER KYRKA",
      "BJØRSÆTER KYRKA"
    ],
    "lId": "10126",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 58.336111111111116,
      "lon": 16.02472222222222
    }
  },
  {
    "name": "Blackeberg T-bana",
    "synonyms": [
      "BLACKEBERG T-BANA"
    ],
    "lId": "21685",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.348333333333336,
      "lon": 17.88277777777778
    }
  },
  {
    "name": "Blankaholm",
    "synonyms": [
      "BLANKAHOLM",
      "BLANKAHOLM E22"
    ],
    "lId": "14099",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 57.58972222222222,
      "lon": 16.485833333333336
    }
  },
  {
    "name": "Blattnicksele väg 45",
    "synonyms": [
      "BLATTNICKSELE VÄG 45",
      "BLATTNICKSELE VÆG 45",
      "BLATTNIKSEL V45"
    ],
    "lId": "24256",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 65.34166666666667,
      "lon": 17.58611111111111
    }
  },
  {
    "name": "Bleket hamnplan",
    "synonyms": [
      "BLEKET HAMNPLAN"
    ],
    "lId": "25008",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 57.94972222222222,
      "lon": 11.566666666666666
    }
  },
  {
    "name": "Blentarp Hasselvägen",
    "synonyms": [
      "BLENTARP HASSELVÄGEN",
      "BLENTARP HASSELVÆGEN"
    ],
    "lId": "22802",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 55.58444444444444,
      "lon": 13.601944444444444
    }
  },
  {
    "name": "Blidsberg",
    "synonyms": [
      "BLIDSBERG"
    ],
    "lId": "00531",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 57.93055555555555,
      "lon": 13.494166666666667
    }
  },
  {
    "name": "Blikstorp affären",
    "synonyms": [
      "BLIKSTORP AFFÄREN",
      "BLIKSTORP AFFÆREN"
    ],
    "lId": "10128",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 58.281666666666666,
      "lon": 14.057500000000001
    }
  },
  {
    "name": "Blomberg",
    "synonyms": [
      "BLOMBERG",
      "BLOMBERG STN"
    ],
    "lId": "01022",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 58.540277777777774,
      "lon": 13.320555555555556
    }
  },
  {
    "name": "Blomstermåla",
    "synonyms": [
      "BLOMSTERMALA",
      "BLOMSTERMÅL STN",
      "BLOMSTERMÅLA"
    ],
    "lId": "01000",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 56.980555555555554,
      "lon": 16.3325
    }
  },
  {
    "name": "Blybergsvilan",
    "synonyms": [
      "BLYBERGSVILAN"
    ],
    "lId": "13151",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 61.147777777777776,
      "lon": 14.146944444444443
    }
  },
  {
    "name": "Blåsut T-bana",
    "synonyms": [
      "BLÅSUT T-BANA"
    ],
    "lId": "21703",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.29,
      "lon": 18.090833333333332
    }
  },
  {
    "name": "Blötberget",
    "synonyms": [
      "BLÖTBERGET",
      "BLÖTBERGET CM",
      "BLØTBERGET",
      "BLØTBERGET CM"
    ],
    "lId": "12963",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 60.12416666666667,
      "lon": 15.060555555555556
    }
  },
  {
    "name": "Boalt",
    "synonyms": [
      "BOALT"
    ],
    "lId": "10131",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 56.38166666666667,
      "lon": 14.157222222222222
    }
  },
  {
    "name": "Bockara centrum",
    "synonyms": [
      "BOCKARA CENTRUM",
      "BOCKARA CM"
    ],
    "lId": "14108",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 57.26138888888889,
      "lon": 16.06527777777778
    }
  },
  {
    "name": "Boda brygga",
    "synonyms": [
      "BODA BRYGGA"
    ],
    "lId": "24604",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.36972222222222,
      "lon": 18.605
    }
  },
  {
    "name": "Boda Kyrkby",
    "synonyms": [
      "BODA KYRKBY"
    ],
    "lId": "00874",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 61.01166666666666,
      "lon": 15.211666666666666
    }
  },
  {
    "name": "Bodafors",
    "synonyms": [
      "BODAFORS",
      "BODAFORS STN"
    ],
    "lId": "00963",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 57.50388888888889,
      "lon": 14.693055555555556
    }
  },
  {
    "name": "Bodal",
    "synonyms": [
      "BODAL"
    ],
    "lId": "24789",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.353611111111114,
      "lon": 18.138333333333332
    }
  },
  {
    "name": "Boden C",
    "synonyms": [
      "BODEN C"
    ],
    "lId": "00150",
    "prio": 1,
    "pId": "074",
    "pos": {
      "lat": 65.8286111111111,
      "lon": 21.7075
    }
  },
  {
    "name": "Boden Garnis",
    "synonyms": [
      "BODEN GARNIS"
    ],
    "lId": "14913",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 65.82,
      "lon": 21.660277777777775
    }
  },
  {
    "name": "Bodsjöedet",
    "synonyms": [
      "BODSJÖEDET",
      "BODSJØEDET"
    ],
    "lId": "29939",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 63.44361111111111,
      "lon": 12.693055555555556
    }
  },
  {
    "name": "Bogesund gården",
    "synonyms": [
      "BOGESUND GÅRDEN"
    ],
    "lId": "24297",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.3925,
      "lon": 18.280277777777776
    }
  },
  {
    "name": "Bograngen",
    "synonyms": [
      "BOGRANGEN"
    ],
    "lId": "00802",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 60.70305555555556,
      "lon": 12.594722222222222
    }
  },
  {
    "name": "Bohus station",
    "synonyms": [
      "BOHUS STATION"
    ],
    "lId": "01600",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 57.852222222222224,
      "lon": 12.01388888888889
    }
  },
  {
    "name": "Bohus-Malmön",
    "synonyms": [
      "BOHUS-MALMÖN",
      "BOHUS-MALMØN"
    ],
    "lId": "16225",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 58.349444444444444,
      "lon": 11.339722222222223
    }
  },
  {
    "name": "Bokenäs",
    "synonyms": [
      "BOKENÄS",
      "BOKENÄS SKOLA",
      "BOKENÆS",
      "BOKENÆS SKOLA"
    ],
    "lId": "01104",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 58.293055555555554,
      "lon": 11.580555555555556
    }
  },
  {
    "name": "Boliden",
    "synonyms": [
      "BOLIDEN",
      "BOLIDEN BSTN"
    ],
    "lId": "00310",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 64.86777777777777,
      "lon": 20.384444444444444
    }
  },
  {
    "name": "Bollebygd",
    "synonyms": [
      "BOLLEBYGD",
      "BOLLEBYGD STN"
    ],
    "lId": "00243",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 57.66722222222222,
      "lon": 12.56861111111111
    }
  },
  {
    "name": "Bollnäs",
    "synonyms": [
      "BOLLNAS",
      "BOLLNÄS",
      "BOLLNÄS STN",
      "BOLLNÆS",
      "BOLLNÆS STN"
    ],
    "lId": "00128",
    "prio": 1,
    "pId": "074",
    "pos": {
      "lat": 61.349722222222226,
      "lon": 16.391388888888887
    }
  },
  {
    "name": "Bollnäs Sjukhuset",
    "synonyms": [
      "BOLLNÄS SJUKHUSET",
      "BOLLNÆS SJUKHUSET"
    ],
    "lId": "06509",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 61.35388888888889,
      "lon": 16.36277777777778
    }
  },
  {
    "name": "Bollnäs stadszon",
    "synonyms": [
      "BOLLNÄS STADSZON",
      "BOLLNÆS STADSZON"
    ],
    "lId": "79015",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 61.349722222222226,
      "lon": 16.391388888888887
    }
  },
  {
    "name": "Bollstabruk busstation",
    "synonyms": [
      "BOLLSTABRUK BST",
      "BOLLSTABRUK BUSSTATION"
    ],
    "lId": "15112",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 62.996944444444445,
      "lon": 17.674444444444447
    }
  },
  {
    "name": "Bollstanäs",
    "synonyms": [
      "BOLLSTANÄS",
      "BOLLSTANÆS"
    ],
    "lId": "01170",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.50083333333333,
      "lon": 17.963055555555556
    }
  },
  {
    "name": "Bonäs skolan",
    "synonyms": [
      "BONÄS SKOLAN",
      "BONÆS SKOLAN"
    ],
    "lId": "13103",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 61.07194444444445,
      "lon": 14.488888888888889
    }
  },
  {
    "name": "Bonäshamn",
    "synonyms": [
      "BONÄSHAMN",
      "BONÆSHAMN"
    ],
    "lId": "13374",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 63.407222222222224,
      "lon": 13.367777777777778
    }
  },
  {
    "name": "Bor",
    "synonyms": [
      "BOR",
      "BOR STN"
    ],
    "lId": "01024",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 57.115833333333335,
      "lon": 14.169166666666666
    }
  },
  {
    "name": "Borensberg centrum",
    "synonyms": [
      "BORENSBERG CENTRUM",
      "BORENSBERG CM"
    ],
    "lId": "20264",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 58.561388888888885,
      "lon": 15.281666666666668
    }
  },
  {
    "name": "Borgafjäll",
    "synonyms": [
      "BORGAFJÄLL",
      "BORGAFJÆLL"
    ],
    "lId": "00316",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 64.83555555555554,
      "lon": 15.083055555555555
    }
  },
  {
    "name": "Borggård station",
    "synonyms": [
      "BORGGÅRD STATION",
      "BORGGÅRD STN"
    ],
    "lId": "10145",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 58.730555555555554,
      "lon": 15.547777777777778
    }
  },
  {
    "name": "Borgholm",
    "synonyms": [
      "BORGHOLM",
      "BORGHOLM BSTN"
    ],
    "lId": "00558",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 56.882222222222225,
      "lon": 16.65611111111111
    }
  },
  {
    "name": "Borgstena",
    "synonyms": [
      "BORGSTENA",
      "BORGSTENA STN"
    ],
    "lId": "00143",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 57.88305555555556,
      "lon": 13.014722222222222
    }
  },
  {
    "name": "Borgvattnet",
    "synonyms": [
      "BORGVATTNET"
    ],
    "lId": "13245",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 63.422777777777775,
      "lon": 15.825277777777778
    }
  },
  {
    "name": "Borgåsund",
    "synonyms": [
      "BORGÅSUND"
    ],
    "lId": "10148",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.50888888888889,
      "lon": 16.261666666666667
    }
  },
  {
    "name": "Borlänge C",
    "synonyms": [
      "BORLANGE C",
      "BORLÄNGE C",
      "BORLÆNGE C"
    ],
    "lId": "00160",
    "prio": 1,
    "pId": "074",
    "pos": {
      "lat": 60.483333333333334,
      "lon": 15.425833333333333
    }
  },
  {
    "name": "Borlänge centrum",
    "synonyms": [
      "BORLÄNGE CENTRUM",
      "BORLÄNGE CM",
      "BORLÆNGE CENTRUM",
      "BORLÆNGE CM"
    ],
    "lId": "12993",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 60.48555555555556,
      "lon": 15.431388888888888
    }
  },
  {
    "name": "Borlänge stadszon",
    "synonyms": [
      "BORLÄNGE STADSZON",
      "BORLÆNGE STADSZON"
    ],
    "lId": "79000",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 60.49416666666667,
      "lon": 15.425555555555555
    }
  },
  {
    "name": "Borrby",
    "synonyms": [
      "BORRBY",
      "BORRBY BSTN"
    ],
    "lId": "01026",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 55.45611111111111,
      "lon": 14.177222222222222
    }
  },
  {
    "name": "Borås C",
    "synonyms": [
      "BORAS C",
      "BORÅS C"
    ],
    "lId": "00300",
    "prio": 1,
    "pId": "074",
    "pos": {
      "lat": 57.72083333333334,
      "lon": 12.931944444444444
    }
  },
  {
    "name": "Borås sjukhus",
    "synonyms": [
      "BORÅS SJUKHUS"
    ],
    "lId": "12604",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 57.723333333333336,
      "lon": 12.961944444444443
    }
  },
  {
    "name": "Bosjökloster",
    "synonyms": [
      "BOSJÖKLOSTER",
      "BOSJØKLOSTER"
    ],
    "lId": "14454",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 55.88111111111111,
      "lon": 13.517222222222223
    }
  },
  {
    "name": "Bosön",
    "synonyms": [
      "BOSÖN",
      "BOSØN"
    ],
    "lId": "26084",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.38,
      "lon": 18.183333333333334
    }
  },
  {
    "name": "Bottnaryd",
    "synonyms": [
      "BOTTNARYD",
      "BOTTNARYD SKOLA"
    ],
    "lId": "01027",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 57.77305555555555,
      "lon": 13.825277777777778
    }
  },
  {
    "name": "Bovallstrand",
    "synonyms": [
      "BOVALLSTRAND"
    ],
    "lId": "00370",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 58.47527777777778,
      "lon": 11.322222222222223
    }
  },
  {
    "name": "Boxholm",
    "synonyms": [
      "BOXHOLM",
      "BOXHOLM STN"
    ],
    "lId": "00015",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 58.19361111111111,
      "lon": 15.05388888888889
    }
  },
  {
    "name": "Brandbergen centrum",
    "synonyms": [
      "BRANDBERGEN CENTRUM",
      "BRANDBERGEN CM"
    ],
    "lId": "01171",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.172777777777775,
      "lon": 18.16888888888889
    }
  },
  {
    "name": "Brandstorp",
    "synonyms": [
      "BRANDSTORP"
    ],
    "lId": "01028",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 58.09666666666667,
      "lon": 14.205
    }
  },
  {
    "name": "Brantevik",
    "synonyms": [
      "BRANTEVIK"
    ],
    "lId": "00750",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 55.513888888888886,
      "lon": 14.3475
    }
  },
  {
    "name": "Branäs",
    "synonyms": [
      "BRANÄS",
      "BRANÆS"
    ],
    "lId": "01029",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 60.663333333333334,
      "lon": 12.955833333333333
    }
  },
  {
    "name": "Brastad",
    "synonyms": [
      "BRASTAD",
      "BRASTAD CENTRUM"
    ],
    "lId": "00298",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 58.38194444444444,
      "lon": 11.48472222222222
    }
  },
  {
    "name": "Bratteborg",
    "synonyms": [
      "BRATTEBORG",
      "BRATTEBORG STN"
    ],
    "lId": "01030",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 57.57777777777778,
      "lon": 14.125277777777779
    }
  },
  {
    "name": "Brattland",
    "synonyms": [
      "BRATTLAND"
    ],
    "lId": "29926",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 63.341944444444444,
      "lon": 13.200833333333332
    }
  },
  {
    "name": "Braviken",
    "synonyms": [
      "BRAVIKEN"
    ],
    "lId": "10161",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 58.64,
      "lon": 16.255277777777778
    }
  },
  {
    "name": "Braås Braåsverken",
    "synonyms": [
      "BRAÅS BRAÅSVERKEN",
      "BRAÅSVERKEN"
    ],
    "lId": "24644",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 57.05555555555555,
      "lon": 15.02888888888889
    }
  },
  {
    "name": "Braås Sjösåsvägen",
    "synonyms": [
      "BRAAS SJØSASVÆGEN",
      "BRAÅS SJÖSÅSVÄGEN"
    ],
    "lId": "24645",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 57.0625,
      "lon": 15.05
    }
  },
  {
    "name": "Bredaryd",
    "synonyms": [
      "BREDARYD",
      "BREDARYD STN"
    ],
    "lId": "00465",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 57.17611111111111,
      "lon": 13.738055555555555
    }
  },
  {
    "name": "Bredbyn",
    "synonyms": [
      "BREDBYN",
      "BREDBYN BSTN"
    ],
    "lId": "00401",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 63.44888888888889,
      "lon": 18.107222222222223
    }
  },
  {
    "name": "Bredhult",
    "synonyms": [
      "BREDHULT"
    ],
    "lId": "10165",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 57.09055555555556,
      "lon": 14.640277777777778
    }
  },
  {
    "name": "Bredkälen",
    "synonyms": [
      "BREDKÄLEN",
      "BREDKÆLEN"
    ],
    "lId": "13218",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 63.84388888888889,
      "lon": 15.333333333333334
    }
  },
  {
    "name": "Bredsjö station",
    "synonyms": [
      "BREDSJÖ STATION",
      "BREDSJÖ STN",
      "BREDSJØ STATION",
      "BREDSJØ STN"
    ],
    "lId": "01533",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.83277777777778,
      "lon": 14.734166666666665
    }
  },
  {
    "name": "Bredviken",
    "synonyms": [
      "BREDVIKEN"
    ],
    "lId": "01031",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 66.12388888888889,
      "lon": 14.7425
    }
  },
  {
    "name": "Bredäng T-bana",
    "synonyms": [
      "BREDÄNG T-BANA",
      "BREDÆNG T-BANA"
    ],
    "lId": "21724",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.29472222222222,
      "lon": 17.933611111111112
    }
  },
  {
    "name": "Brevens Bruk Brevensgården",
    "synonyms": [
      "BREVENS BRUK BREVENSGÅRDEN",
      "BREVENSGÅRDEN"
    ],
    "lId": "25971",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.015,
      "lon": 15.578888888888889
    }
  },
  {
    "name": "Brevik Lidingö",
    "synonyms": [
      "BREVIK LIDINGÖ",
      "BREVIK LIDINGØ"
    ],
    "lId": "23964",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.348333333333336,
      "lon": 18.203611111111112
    }
  },
  {
    "name": "Brinellskolan",
    "synonyms": [
      "BRINELLSKOLAN"
    ],
    "lId": "01443",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 57.669444444444444,
      "lon": 14.702222222222222
    }
  },
  {
    "name": "Bro",
    "synonyms": [
      "BRO",
      "BRO STN"
    ],
    "lId": "00687",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.51138888888889,
      "lon": 17.635833333333334
    }
  },
  {
    "name": "Broakulla",
    "synonyms": [
      "BROAKULLA"
    ],
    "lId": "14111",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 56.69361111111111,
      "lon": 15.529444444444445
    }
  },
  {
    "name": "Broarna",
    "synonyms": [
      "BROARNA"
    ],
    "lId": "25969",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 60.01444444444444,
      "lon": 16.037222222222223
    }
  },
  {
    "name": "Broaryd centrum",
    "synonyms": [
      "BROARYD CENTRUM"
    ],
    "lId": "10171",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 57.12138888888889,
      "lon": 13.255555555555556
    }
  },
  {
    "name": "Brobacke Hedåker",
    "synonyms": [
      "BROBACKE HEDÅKER"
    ],
    "lId": "44131",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 60.02305555555555,
      "lon": 16.33111111111111
    }
  },
  {
    "name": "Broby",
    "synonyms": [
      "BROBY",
      "BROBY BSTN"
    ],
    "lId": "00336",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 56.25472222222222,
      "lon": 14.075555555555555
    }
  },
  {
    "name": "Broddbo",
    "synonyms": [
      "BRODDBO"
    ],
    "lId": "10174",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.98833333333334,
      "lon": 16.478888888888886
    }
  },
  {
    "name": "Broholm väg 26",
    "synonyms": [
      "BROHOLM VÄG 26"
    ],
    "lId": "10176",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 57.970555555555556,
      "lon": 13.831944444444444
    }
  },
  {
    "name": "Brohögen",
    "synonyms": [
      "BROHÖGEN",
      "BROHØGEN"
    ],
    "lId": "01444",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 58.955000000000005,
      "lon": 12.230277777777777
    }
  },
  {
    "name": "Brokind",
    "synonyms": [
      "BROKIND"
    ],
    "lId": "00587",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 58.22,
      "lon": 15.684444444444445
    }
  },
  {
    "name": "Bromma flygplats",
    "synonyms": [
      "BROMMA FLYGPLATS",
      "BROMMA FPL"
    ],
    "lId": "01105",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.35527777777778,
      "lon": 17.94638888888889
    }
  },
  {
    "name": "Brommaplan T-bana",
    "synonyms": [
      "BROMMAPLAN T",
      "BROMMAPLAN T-BANA",
      "BROMMAPLAN TBAN"
    ],
    "lId": "20581",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.33833333333334,
      "lon": 17.939166666666665
    }
  },
  {
    "name": "Bromskär brygga",
    "synonyms": [
      "BLIDÖ",
      "BLIDØ",
      "BROMSKÄR BRYGGA",
      "BROMSKÆR BRYGGA"
    ],
    "lId": "01021",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.626111111111115,
      "lon": 18.9875
    }
  },
  {
    "name": "Bromölla",
    "synonyms": [
      "BROMOLLA",
      "BROMÖLLA",
      "BROMØLLA"
    ],
    "lId": "00141",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 56.06722222222223,
      "lon": 14.479444444444445
    }
  },
  {
    "name": "Brottby",
    "synonyms": [
      "BROTTBY"
    ],
    "lId": "01106",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.56222222222222,
      "lon": 18.240833333333335
    }
  },
  {
    "name": "Bruksvallarna",
    "synonyms": [
      "BRUKSVALLARNA"
    ],
    "lId": "00475",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 62.636944444444445,
      "lon": 12.444166666666668
    }
  },
  {
    "name": "Brunflo",
    "synonyms": [
      "BRUNFLO"
    ],
    "lId": "00526",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 63.075833333333335,
      "lon": 14.831944444444444
    }
  },
  {
    "name": "Brunna Emaljstigen",
    "synonyms": [
      "BRUNNA EMALJSTIGEN"
    ],
    "lId": "24662",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.50972222222222,
      "lon": 17.74888888888889
    }
  },
  {
    "name": "Brunsberg",
    "synonyms": [
      "BRUNSBERG",
      "BRUNSBERG STN"
    ],
    "lId": "01423",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.61694444444444,
      "lon": 12.962499999999999
    }
  },
  {
    "name": "Bruzaholm",
    "synonyms": [
      "BRUZAHOLM",
      "BRUZAHOLM STN"
    ],
    "lId": "00964",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 57.64138888888889,
      "lon": 15.274722222222223
    }
  },
  {
    "name": "Brygge",
    "synonyms": [
      "BRYGGE"
    ],
    "lId": "41991",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 58.48777777777778,
      "lon": 11.366944444444444
    }
  },
  {
    "name": "Brålanda",
    "synonyms": [
      "BRÅLANDA",
      "BRÅLANDA VÄG 45",
      "BRÅLANDA VÆG 45"
    ],
    "lId": "00982",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 58.5575,
      "lon": 12.356388888888889
    }
  },
  {
    "name": "Bråvallafestivalen",
    "synonyms": [
      "BRÅVALLAFESTIVALEN"
    ],
    "lId": "65295",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 58.61638888888889,
      "lon": 16.095555555555553
    }
  },
  {
    "name": "Bråvallavägen station",
    "synonyms": [
      "BRÅVALLAV STN",
      "BRÅVALLAVÄGEN STATION",
      "BRÅVALLAVÆGEN STATION"
    ],
    "lId": "24795",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.40555555555555,
      "lon": 18.060555555555556
    }
  },
  {
    "name": "Bräcke",
    "synonyms": [
      "BRACKE",
      "BRÄCKE",
      "BRÄCKE STN",
      "BRÆCKE",
      "BRÆCKE STN"
    ],
    "lId": "00032",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 62.75,
      "lon": 15.416944444444443
    }
  },
  {
    "name": "Bräkne-Hoby",
    "synonyms": [
      "BRAKNE-HOBY",
      "BRÄKNE-HOBY",
      "BRÄKNE-HOBY STN",
      "BRÆKNE-HOBY",
      "BRÆKNE-HOBY STN"
    ],
    "lId": "00368",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 56.23083333333334,
      "lon": 15.115555555555556
    }
  },
  {
    "name": "Bränn-Ekeby",
    "synonyms": [
      "BRÄNN-EKEBY",
      "BRÆNN-EKEBY"
    ],
    "lId": "10186",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 58.705555555555556,
      "lon": 16.964444444444442
    }
  },
  {
    "name": "Brännland E12",
    "synonyms": [
      "BRÄNNLAND E12",
      "BRÆNNLAND E12"
    ],
    "lId": "20139",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 63.876111111111115,
      "lon": 20.058055555555555
    }
  },
  {
    "name": "Brännö Husvik",
    "synonyms": [
      "BRÄNNÖ HUSVIK",
      "BRÆNNØ HUSVIK"
    ],
    "lId": "01203",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 57.63527777777778,
      "lon": 11.766666666666667
    }
  },
  {
    "name": "Brännö Rödsten",
    "synonyms": [
      "BRÄNNÖ RÖDSTEN",
      "BRÆNNØ RØDSTEN"
    ],
    "lId": "24949",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 57.64833333333333,
      "lon": 11.785277777777777
    }
  },
  {
    "name": "Brömsebro",
    "synonyms": [
      "BRÖMSEBRO",
      "BRÖMSEBRO E22",
      "BRØMSEBRO",
      "BRØMSEBRO E22"
    ],
    "lId": "00597",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 56.29833333333333,
      "lon": 16.000833333333333
    }
  },
  {
    "name": "Brösarp bussterminal",
    "synonyms": [
      "BRÖSARP BUSSTERMINAL",
      "BRØSARP BUSSTERMINAL"
    ],
    "lId": "00343",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 55.72777777777778,
      "lon": 14.096666666666668
    }
  },
  {
    "name": "Bua",
    "synonyms": [
      "BUA",
      "BUA SKOLAN"
    ],
    "lId": "00767",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 57.236666666666665,
      "lon": 12.127777777777778
    }
  },
  {
    "name": "Bullandö",
    "synonyms": [
      "BULLANDÖ",
      "BULLANDØ"
    ],
    "lId": "24940",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.301944444444445,
      "lon": 18.648333333333333
    }
  },
  {
    "name": "Bunkeflostrand",
    "synonyms": [
      "BUNKEFLOSTRAND"
    ],
    "lId": "10197",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 55.547777777777775,
      "lon": 12.917499999999999
    }
  },
  {
    "name": "Bureå Torg",
    "synonyms": [
      "BUREÅ TORG"
    ],
    "lId": "00317",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 64.61749999999999,
      "lon": 21.200277777777778
    }
  },
  {
    "name": "Burgsvik",
    "synonyms": [
      "BURGSVIK",
      "BURGSVIK STNVÄG",
      "BURGSVIK STNVÆG"
    ],
    "lId": "00893",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 57.032777777777774,
      "lon": 18.274166666666666
    }
  },
  {
    "name": "Burlöv station",
    "synonyms": [
      "BURLOV",
      "BURLÖV",
      "BURLÖV STATION",
      "BURLÖV STN",
      "BURLØV",
      "BURLØV STATION",
      "BURLØV STN"
    ],
    "lId": "00937",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 55.64055555555556,
      "lon": 13.079722222222221
    }
  },
  {
    "name": "Burseryd torget",
    "synonyms": [
      "BURSERYD TORGET"
    ],
    "lId": "10201",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 57.20305555555556,
      "lon": 13.283888888888889
    }
  },
  {
    "name": "Burträsk",
    "synonyms": [
      "BURTRASK",
      "BURTRÄSK",
      "BURTRÄSK BSTN",
      "BURTRÆSK",
      "BURTRÆSK BSTN"
    ],
    "lId": "00318",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 64.52111111111111,
      "lon": 20.66
    }
  },
  {
    "name": "Buskhyttan",
    "synonyms": [
      "BUSKHYTTAN"
    ],
    "lId": "10202",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 58.66222222222222,
      "lon": 16.93861111111111
    }
  },
  {
    "name": "By Kyrkby skolan",
    "synonyms": [
      "BY KYRKBY SKOLAN"
    ],
    "lId": "12910",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 60.20388888888889,
      "lon": 16.476666666666667
    }
  },
  {
    "name": "Byarum",
    "synonyms": [
      "BYARUM",
      "BYARUM STN"
    ],
    "lId": "01033",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 57.53611111111111,
      "lon": 14.143888888888888
    }
  },
  {
    "name": "Bydalen",
    "synonyms": [
      "BYDALEN"
    ],
    "lId": "01034",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 63.1025,
      "lon": 13.800555555555556
    }
  },
  {
    "name": "Bygdeå centrum",
    "synonyms": [
      "BYGDEÅ CENTRUM"
    ],
    "lId": "00954",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 64.06388888888888,
      "lon": 20.859444444444446
    }
  },
  {
    "name": "Bygdeå E4",
    "synonyms": [
      "BYGDEÅ E4"
    ],
    "lId": "13615",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 64.0611111111111,
      "lon": 20.849166666666665
    }
  },
  {
    "name": "Bygdsiljum",
    "synonyms": [
      "BYGDSILJUM"
    ],
    "lId": "13829",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 64.34777777777778,
      "lon": 20.504166666666666
    }
  },
  {
    "name": "Bysala Skinnskatteberg",
    "synonyms": [
      "BYSALA SKINNSKATTEBERG"
    ],
    "lId": "44831",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.72166666666667,
      "lon": 15.7925
    }
  },
  {
    "name": "Byske",
    "synonyms": [
      "BYSKE",
      "BYSKE BSTN"
    ],
    "lId": "00477",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 64.95361111111112,
      "lon": 21.203055555555554
    }
  },
  {
    "name": "Byxelkrok",
    "synonyms": [
      "BYXELKROK",
      "BYXELKROK CM"
    ],
    "lId": "00525",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 57.32416666666667,
      "lon": 17.0075
    }
  },
  {
    "name": "Bålsta",
    "synonyms": [
      "BALSTA",
      "BÅLSTA",
      "BÅLSTA STN"
    ],
    "lId": "00660",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.56916666666667,
      "lon": 17.530833333333334
    }
  },
  {
    "name": "Bårslöv",
    "synonyms": [
      "BÅRSLÖV",
      "BÅRSLÖV SNÖDROP",
      "BÅRSLØV",
      "BÅRSLØV SNØDROP"
    ],
    "lId": "01035",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 56.00888888888889,
      "lon": 12.811111111111112
    }
  },
  {
    "name": "Båstad",
    "synonyms": [
      "BASTAD",
      "BÅSTAD"
    ],
    "lId": "00061",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 56.425,
      "lon": 12.869444444444445
    }
  },
  {
    "name": "Båstad nya station",
    "synonyms": [
      "BÅSTAD NYA STATION",
      "BÅSTAD NYA STN"
    ],
    "lId": "01603",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 56.431666666666665,
      "lon": 12.906944444444445
    }
  },
  {
    "name": "Bäckaskog",
    "synonyms": [
      "BÄCKASKOG",
      "BÆCKASKOG"
    ],
    "lId": "18028",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 56.04111111111111,
      "lon": 14.328888888888889
    }
  },
  {
    "name": "Bäckebo",
    "synonyms": [
      "BÄCKEBO",
      "BÆCKEBO"
    ],
    "lId": "14118",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 56.88944444444444,
      "lon": 16.065555555555555
    }
  },
  {
    "name": "Bäckebol Köpcentrum",
    "synonyms": [
      "BÄCKEBOL KÖPCENTRUM"
    ],
    "lId": "59477",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 57.76972222222222,
      "lon": 11.997499999999999
    }
  },
  {
    "name": "Bäckebron",
    "synonyms": [
      "BÄCKEBRON",
      "BÆCKEBRON"
    ],
    "lId": "00542",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.66111111111111,
      "lon": 13.166111111111112
    }
  },
  {
    "name": "Bäckebron väg 45",
    "synonyms": [
      "BÄCKEBRON V 45",
      "BÄCKEBRON VÄG 45",
      "BÆCKEBRON V 45",
      "BÆCKEBRON VÆG 45"
    ],
    "lId": "24500",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.661944444444444,
      "lon": 13.158055555555556
    }
  },
  {
    "name": "Bäckedal station",
    "synonyms": [
      "BÄCKEDAL STATION",
      "BÄCKEDAL STN",
      "BÆCKEDAL STATION",
      "BÆCKEDAL STN"
    ],
    "lId": "30005",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 62.026666666666664,
      "lon": 14.377500000000001
    }
  },
  {
    "name": "Bäckefors Terminalen",
    "synonyms": [
      "BÄCKEFORS TERMINALEN",
      "BÆCKEFORS TERMINALEN"
    ],
    "lId": "42545",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 58.805277777777775,
      "lon": 12.157777777777778
    }
  },
  {
    "name": "Bäckhammar bruket",
    "synonyms": [
      "BÄCKHAMMAR BRUKET",
      "BÆCKHAMMAR BRUKET"
    ],
    "lId": "18008",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.16027777777778,
      "lon": 14.185277777777777
    }
  },
  {
    "name": "Bäcklunda",
    "synonyms": [
      "BÄCKLUNDA",
      "BÆCKLUNDA"
    ],
    "lId": "10211",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.132777777777775,
      "lon": 14.6425
    }
  },
  {
    "name": "Bäl",
    "synonyms": [
      "BÄL",
      "BÄL BYGDEGÅRDEN",
      "BÆL",
      "BÆL BYGDEGÅRDEN"
    ],
    "lId": "01107",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 57.64361111111111,
      "lon": 18.633055555555558
    }
  },
  {
    "name": "Bälgviken",
    "synonyms": [
      "BALGVIKEN",
      "BÄLGVIKEN",
      "BÄLGVIKEN STN",
      "BÆLGVIKEN",
      "BÆLGVIKEN STN"
    ],
    "lId": "01429",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.250277777777775,
      "lon": 16.459444444444443
    }
  },
  {
    "name": "Bälinge Luleå",
    "synonyms": [
      "BÄLINGE LULEÅ"
    ],
    "lId": "23782",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 65.63277777777778,
      "lon": 21.927222222222223
    }
  },
  {
    "name": "Bälinge centrum Uppsala",
    "synonyms": [
      "BÄLINGE CENTRUM",
      "BÄLINGE CENTRUM UPPSALA"
    ],
    "lId": "12672",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.94611111111111,
      "lon": 17.535
    }
  },
  {
    "name": "Bällsta",
    "synonyms": [
      "BÄLLSTA",
      "BÄLLSTA STN",
      "BÆLLSTA",
      "BÆLLSTA STN"
    ],
    "lId": "24800",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.52388888888889,
      "lon": 18.071666666666665
    }
  },
  {
    "name": "Bällsta bro Spårv",
    "synonyms": [
      "BÄLLSTA BRO SPÅRV",
      "BÆLLSTA BRO SPÅRV"
    ],
    "lId": "64051",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.36,
      "lon": 17.960555555555555
    }
  },
  {
    "name": "Bälsunda",
    "synonyms": [
      "BÄLSUNDA",
      "BÆLSUNDA"
    ],
    "lId": "12853",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.66277777777778,
      "lon": 17.449166666666667
    }
  },
  {
    "name": "Bärby Korsväg",
    "synonyms": [
      "BÄRBY KORSVÄG"
    ],
    "lId": "59164",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 57.7925,
      "lon": 11.9125
    }
  },
  {
    "name": "Bärby station",
    "synonyms": [
      "BÄRBY STATION",
      "BÄRBY STN"
    ],
    "lId": "26059",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.8575,
      "lon": 17.8125
    }
  },
  {
    "name": "Bäsna gamla affären",
    "synonyms": [
      "BÄSNA GAMLA AFFÄREN"
    ],
    "lId": "13036",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 60.53638888888889,
      "lon": 15.202499999999999
    }
  },
  {
    "name": "Böda",
    "synonyms": [
      "BÖDA",
      "BÖDA AFFÄREN",
      "BØDA",
      "BØDA AFFÆREN"
    ],
    "lId": "00909",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 57.250277777777775,
      "lon": 17.05666666666667
    }
  },
  {
    "name": "Bönan",
    "synonyms": [
      "BÖNAN",
      "BØNAN"
    ],
    "lId": "19203",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 60.737500000000004,
      "lon": 17.30888888888889
    }
  },
  {
    "name": "Bönhamn vändplats",
    "synonyms": [
      "BÖNHAMN VÄNDPLATS",
      "BØNHAMN VÆNDPLATS"
    ],
    "lId": "29045",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 62.880833333333335,
      "lon": 18.448611111111113
    }
  },
  {
    "name": "Börjelslandet vsk Boden",
    "synonyms": [
      "BÖRJELSLANDET VSK BODEN",
      "BØRJELSLANDET VSK BODEN"
    ],
    "lId": "14865",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 65.78222222222222,
      "lon": 22.17388888888889
    }
  },
  {
    "name": "Börringe station",
    "synonyms": [
      "BÖRRINGE STATION",
      "BÖRRINGE STN",
      "BØRRINGE STATION",
      "BØRRINGE STN"
    ],
    "lId": "22781",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 55.49888888888889,
      "lon": 13.333333333333334
    }
  },
  {
    "name": "Börtnan",
    "synonyms": [
      "BÖRTNAN",
      "BØRTNAN"
    ],
    "lId": "13354",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 62.75194444444445,
      "lon": 13.843055555555557
    }
  },
  {
    "name": "Böste läge",
    "synonyms": [
      "BÖSTE LÄGE",
      "BØSTE LÆGE"
    ],
    "lId": "16582",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 55.344166666666666,
      "lon": 13.309166666666668
    }
  },
  {
    "name": "Camp Polcirkeln",
    "synonyms": [
      "CAMP POLCIRKELN"
    ],
    "lId": "20107",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 66.5475,
      "lon": 16.334444444444443
    }
  },
  {
    "name": "Charlottenberg",
    "synonyms": [
      "CHARLOTTENBERG"
    ],
    "lId": "00048",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.88388888888889,
      "lon": 12.2975
    }
  },
  {
    "name": "Copenhagen Airport",
    "synonyms": [
      "COPENHAGEN AIRPORT",
      "CPH",
      "CPH AIRPORT",
      "CPH LUFTHAVN",
      "KASTRUP CPH",
      "KBH LUFTH KASTR",
      "KOBENHAVNS LUFTHAVN",
      "KOPENHAMNS FLYGPLATS",
      "KÖBENHAVNS LUFTHAVN",
      "KÖPENHAMNS FLYGPLATS",
      "KØBENHAVNS LUFTHAVN"
    ],
    "lId": "00858",
    "prio": 1,
    "pId": "086",
    "pos": {
      "lat": 55.62416666666667,
      "lon": 12.636666666666667
    }
  },
  {
    "name": "Dala Airport",
    "synonyms": [
      "DALA AIRPORT"
    ],
    "lId": "24377",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 60.43,
      "lon": 15.5075
    }
  },
  {
    "name": "Dala-Floda ICA",
    "synonyms": [
      "DALA-FLODA ICA"
    ],
    "lId": "13044",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 60.509166666666665,
      "lon": 14.801388888888889
    }
  },
  {
    "name": "Dala-Järna",
    "synonyms": [
      "DALA-JARNA",
      "DALA-JÄRNA",
      "DALA-JÆRNA"
    ],
    "lId": "00398",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 60.547777777777775,
      "lon": 14.362222222222222
    }
  },
  {
    "name": "Dalarö",
    "synonyms": [
      "DALARÖ",
      "DALARÖ HOTELLBR",
      "DALARØ",
      "DALARØ HOTELLBR"
    ],
    "lId": "01036",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.129444444444445,
      "lon": 18.406388888888888
    }
  },
  {
    "name": "Dalby",
    "synonyms": [
      "DALBY",
      "DALBY BSTN"
    ],
    "lId": "00938",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 55.66444444444444,
      "lon": 13.346388888888889
    }
  },
  {
    "name": "Dalfors",
    "synonyms": [
      "DALFORS"
    ],
    "lId": "01446",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 61.214444444444446,
      "lon": 15.404166666666667
    }
  },
  {
    "name": "Dalhem",
    "synonyms": [
      "DALHEM",
      "DALHEM AFFÄR",
      "DALHEM AFFÆR"
    ],
    "lId": "01037",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 57.544999999999995,
      "lon": 18.532777777777778
    }
  },
  {
    "name": "Dals Långed centrum",
    "synonyms": [
      "DALS LÅNGED CENTRUM",
      "DALS LÅNGED CM"
    ],
    "lId": "12104",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 58.921388888888885,
      "lon": 12.313611111111111
    }
  },
  {
    "name": "Dals Rostock",
    "synonyms": [
      "DALS ROSTOCK"
    ],
    "lId": "12125",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 58.714444444444446,
      "lon": 12.355555555555556
    }
  },
  {
    "name": "Dalsjöfors",
    "synonyms": [
      "DALSJÖFORS",
      "DALSJÖFRS FPARK",
      "DALSJØFORS",
      "DALSJØFRS FPARK"
    ],
    "lId": "00985",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 57.7175,
      "lon": 13.11888888888889
    }
  },
  {
    "name": "Dalskog",
    "synonyms": [
      "DALSKOG"
    ],
    "lId": "12124",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 58.74805555555556,
      "lon": 12.289166666666667
    }
  },
  {
    "name": "Dalstorp torget",
    "synonyms": [
      "DALSTORP TORGET"
    ],
    "lId": "12074",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 57.605555555555554,
      "lon": 13.510555555555555
    }
  },
  {
    "name": "Dalum",
    "synonyms": [
      "DALUM"
    ],
    "lId": "65285",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 57.89833333333333,
      "lon": 13.465277777777777
    }
  },
  {
    "name": "Danderyd sjukhus",
    "synonyms": [
      "DANDERYD SJH",
      "DANDERYD SJH T",
      "DANDERYD SJUKHUS"
    ],
    "lId": "10232",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.391666666666666,
      "lon": 18.041111111111114
    }
  },
  {
    "name": "Danholn skolan",
    "synonyms": [
      "DANHOLN SKOLAN"
    ],
    "lId": "13014",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 60.62138888888889,
      "lon": 15.797777777777778
    }
  },
  {
    "name": "Danmark kyrka",
    "synonyms": [
      "DANMARK KYRKA"
    ],
    "lId": "12815",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.8325,
      "lon": 17.74361111111111
    }
  },
  {
    "name": "Dannemora värdshus",
    "synonyms": [
      "DANNEMORA VÄRDSHUS",
      "DANNEMORA VÆRDSHUS"
    ],
    "lId": "09861",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 60.19944444444444,
      "lon": 17.851944444444445
    }
  },
  {
    "name": "Dannike",
    "synonyms": [
      "DANNIKE"
    ],
    "lId": "22704",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 57.68555555555555,
      "lon": 13.22888888888889
    }
  },
  {
    "name": "Degeberga",
    "synonyms": [
      "DEGEBERGA",
      "DEGEBERGA SKADD"
    ],
    "lId": "00346",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 55.837500000000006,
      "lon": 14.09
    }
  },
  {
    "name": "Degerfors",
    "synonyms": [
      "DEGERFORS",
      "DEGERFORS STN"
    ],
    "lId": "00129",
    "prio": 1,
    "pId": "074",
    "pos": {
      "lat": 59.22888888888889,
      "lon": 14.439722222222223
    }
  },
  {
    "name": "Degerhamn",
    "synonyms": [
      "DEGERHAMN"
    ],
    "lId": "00755",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 56.35638888888889,
      "lon": 16.42
    }
  },
  {
    "name": "Deje",
    "synonyms": [
      "DEJE",
      "DEJE STN"
    ],
    "lId": "00127",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.60277777777778,
      "lon": 13.471388888888889
    }
  },
  {
    "name": "Deje Tjärnheden vändplan",
    "synonyms": [
      "DEJE TJÄRNH VPL",
      "DEJE TJÄRNHEDEN VÄNDPLAN",
      "DEJE TJÆRNH VPL",
      "DEJE TJÆRNHEDEN VÆNDPLAN"
    ],
    "lId": "04313",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.61805555555556,
      "lon": 13.449722222222222
    }
  },
  {
    "name": "Delabäcken",
    "synonyms": [
      "DELABÄCKEN",
      "DELABÆCKEN"
    ],
    "lId": "01448",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 57.81916666666667,
      "lon": 12.201666666666666
    }
  },
  {
    "name": "Delary",
    "synonyms": [
      "DELARY"
    ],
    "lId": "10239",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 56.54833333333333,
      "lon": 13.955
    }
  },
  {
    "name": "Delsbo",
    "synonyms": [
      "DELSBO",
      "DELSBO TORG"
    ],
    "lId": "00331",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 61.79944444444444,
      "lon": 16.55388888888889
    }
  },
  {
    "name": "Delsjömotet",
    "synonyms": [
      "DELSJÖMOTET"
    ],
    "lId": "22706",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 57.67666666666666,
      "lon": 12.025555555555556
    }
  },
  {
    "name": "Derome",
    "synonyms": [
      "DEROME",
      "DEROME STN"
    ],
    "lId": "00271",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 57.230000000000004,
      "lon": 12.32
    }
  },
  {
    "name": "Dikanäs",
    "synonyms": [
      "DIKANÄS",
      "DIKANÆS"
    ],
    "lId": "13912",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 65.235,
      "lon": 15.993611111111111
    }
  },
  {
    "name": "Dingle station",
    "synonyms": [
      "DINGLE STATION",
      "DINGLE STN"
    ],
    "lId": "00065",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 58.529444444444444,
      "lon": 11.578888888888889
    }
  },
  {
    "name": "Dingtuna",
    "synonyms": [
      "DINGTUNA",
      "DINGTUNA STN"
    ],
    "lId": "01333",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.57166666666667,
      "lon": 16.389722222222222
    }
  },
  {
    "name": "Diseröd",
    "synonyms": [
      "DISERÖD",
      "DISERØD"
    ],
    "lId": "24943",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 57.92472222222222,
      "lon": 12.027777777777779
    }
  },
  {
    "name": "Diö station",
    "synonyms": [
      "DIÖ STATION",
      "DIØ STATION"
    ],
    "lId": "10243",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 56.634166666666665,
      "lon": 14.215
    }
  },
  {
    "name": "Djupekås",
    "synonyms": [
      "DJUPEKÅS"
    ],
    "lId": "32667",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 56.07055555555556,
      "lon": 14.711944444444443
    }
  },
  {
    "name": "Djura Kaféet",
    "synonyms": [
      "DJURA KAFEET",
      "DJURA KAFÉET"
    ],
    "lId": "25335",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 60.611111111111114,
      "lon": 15.002222222222223
    }
  },
  {
    "name": "Djurmo E16",
    "synonyms": [
      "DJURMO E16"
    ],
    "lId": "23230",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 60.55138888888889,
      "lon": 15.192222222222222
    }
  },
  {
    "name": "Djurröd",
    "synonyms": [
      "DJURRÖD"
    ],
    "lId": "04120",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 55.99583333333334,
      "lon": 13.884722222222221
    }
  },
  {
    "name": "Djursholms Ekeby station",
    "synonyms": [
      "DJURSHOLM EKEBY",
      "DJURSHOLMS EKEBY STATION"
    ],
    "lId": "20870",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.41277777777778,
      "lon": 18.0575
    }
  },
  {
    "name": "Djursholms Ösby",
    "synonyms": [
      "DJURSHOLMS ÖSBY",
      "DJURSHOLMS ØSBY"
    ],
    "lId": "01038",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.397777777777776,
      "lon": 18.058611111111112
    }
  },
  {
    "name": "Djurås",
    "synonyms": [
      "DJURAS",
      "DJURÅS",
      "DJURÅS STN"
    ],
    "lId": "00303",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 60.559999999999995,
      "lon": 15.138333333333334
    }
  },
  {
    "name": "Djurö Byns gård",
    "synonyms": [
      "DJURÖ BYNS GÅRD",
      "DJURØ BYNS GÅRD"
    ],
    "lId": "20579",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.31305555555555,
      "lon": 18.710277777777776
    }
  },
  {
    "name": "Djuröbron",
    "synonyms": [
      "DJURÖBRON",
      "DJURØBRON"
    ],
    "lId": "21839",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.290277777777774,
      "lon": 18.66638888888889
    }
  },
  {
    "name": "Djurönäset",
    "synonyms": [
      "DJURÖNÄSET"
    ],
    "lId": "66459",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.29888888888889,
      "lon": 18.67138888888889
    }
  },
  {
    "name": "Dockmyr",
    "synonyms": [
      "DOCKMYR"
    ],
    "lId": "13255",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 62.953611111111115,
      "lon": 15.738333333333333
    }
  },
  {
    "name": "Docksta",
    "synonyms": [
      "DOCKSTA"
    ],
    "lId": "01040",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 63.05444444444444,
      "lon": 18.32638888888889
    }
  },
  {
    "name": "Docksta E4",
    "synonyms": [
      "DOCKSTA E4"
    ],
    "lId": "15125",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 63.05305555555555,
      "lon": 18.3275
    }
  },
  {
    "name": "Domsten väg 111",
    "synonyms": [
      "DOMSTEN VÄG 111",
      "DOMSTEN VÆG 111"
    ],
    "lId": "22810",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 56.126111111111115,
      "lon": 12.601666666666667
    }
  },
  {
    "name": "Donsö",
    "synonyms": [
      "DONSÖ",
      "DONSØ"
    ],
    "lId": "01109",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 57.599722222222226,
      "lon": 11.793888888888889
    }
  },
  {
    "name": "Dorotea busstation",
    "synonyms": [
      "DOROTEA BSTN",
      "DOROTEA BUSSTATION"
    ],
    "lId": "13630",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 64.25888888888889,
      "lon": 16.408055555555553
    }
  },
  {
    "name": "Drottningholm",
    "synonyms": [
      "DROTTNINGHOLM"
    ],
    "lId": "01041",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.32361111111111,
      "lon": 17.889444444444443
    }
  },
  {
    "name": "Drottningskär Madsviken",
    "synonyms": [
      "DROTTNINGSKÄR MADSVIKEN",
      "DROTTNINGSKÆR MADSVIKEN",
      "DROTTNSKÄR MADS",
      "DROTTNSKÆR MADS"
    ],
    "lId": "32191",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 56.12416666666667,
      "lon": 15.550277777777778
    }
  },
  {
    "name": "Drängsmark",
    "synonyms": [
      "DRÄNGSMARK",
      "DRÆNGSMARK"
    ],
    "lId": "13844",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 64.91805555555555,
      "lon": 20.946666666666665
    }
  },
  {
    "name": "Duvbo T-bana",
    "synonyms": [
      "DUVBO T-BANA"
    ],
    "lId": "21673",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.367777777777775,
      "lon": 17.964444444444442
    }
  },
  {
    "name": "Duved",
    "synonyms": [
      "DUVED",
      "DUVED STN"
    ],
    "lId": "00308",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 63.38972222222222,
      "lon": 12.917499999999999
    }
  },
  {
    "name": "Dvärsätt",
    "synonyms": [
      "DVÄRSÄTT",
      "DVÆRSÆTT"
    ],
    "lId": "13283",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 63.30361111111111,
      "lon": 14.470833333333333
    }
  },
  {
    "name": "Dynäs",
    "synonyms": [
      "DYNÄS",
      "DYNÆS"
    ],
    "lId": "15122",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 62.97277777777778,
      "lon": 17.71944444444444
    }
  },
  {
    "name": "Dämbol",
    "synonyms": [
      "DÄMBOL",
      "DÆMBOL"
    ],
    "lId": "10255",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 58.91277777777778,
      "lon": 16.43722222222222
    }
  },
  {
    "name": "Döda fallet",
    "synonyms": [
      "DÖDA FALLET",
      "DØDA FALLET"
    ],
    "lId": "13540",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 63.05777777777777,
      "lon": 16.52027777777778
    }
  },
  {
    "name": "Dösjebro",
    "synonyms": [
      "DOSJEBRO",
      "DÖSJEBRO",
      "DÖSJEBRO STN",
      "DØSJEBRO",
      "DØSJEBRO STN"
    ],
    "lId": "00939",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 55.82277777777778,
      "lon": 13.03138888888889
    }
  },
  {
    "name": "Ed",
    "synonyms": [
      "ED",
      "ED STN"
    ],
    "lId": "00283",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 58.913333333333334,
      "lon": 11.932777777777778
    }
  },
  {
    "name": "Eda bruk",
    "synonyms": [
      "EDA BRUK"
    ],
    "lId": "10262",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.922777777777775,
      "lon": 12.261944444444444
    }
  },
  {
    "name": "Eda kyrka",
    "synonyms": [
      "EDA KYRKA"
    ],
    "lId": "20189",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.84111111111111,
      "lon": 12.315555555555557
    }
  },
  {
    "name": "Edane",
    "synonyms": [
      "EDANE",
      "EDANE STN"
    ],
    "lId": "00410",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.626666666666665,
      "lon": 12.829166666666666
    }
  },
  {
    "name": "Ede Offerdal",
    "synonyms": [
      "EDE OFFERDAL"
    ],
    "lId": "00452",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 63.46611111111111,
      "lon": 14.013055555555555
    }
  },
  {
    "name": "Edeby Vassunda",
    "synonyms": [
      "EDEBY VASSUNDA"
    ],
    "lId": "12846",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.71388888888889,
      "lon": 17.72833333333333
    }
  },
  {
    "name": "Edebäck Högheden",
    "synonyms": [
      "EDEBÄCK HÖGHEDEN",
      "EDEBÆCK HØGHEDEN"
    ],
    "lId": "10264",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 60.0575,
      "lon": 13.55388888888889
    }
  },
  {
    "name": "Edinge",
    "synonyms": [
      "EDINGE"
    ],
    "lId": "12795",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.96055555555556,
      "lon": 18.0775
    }
  },
  {
    "name": "Edsberg",
    "synonyms": [
      "EDSBERG",
      "EDSBERG CENTRUM"
    ],
    "lId": "01173",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.44472222222222,
      "lon": 17.967499999999998
    }
  },
  {
    "name": "Edsbjörke",
    "synonyms": [
      "EDSBJÖRKE",
      "EDSBJÖRKE STN",
      "EDSBJØRKE",
      "EDSBJØRKE STN"
    ],
    "lId": "01415",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.90277777777778,
      "lon": 13.170555555555556
    }
  },
  {
    "name": "Edsbro",
    "synonyms": [
      "EDSBRO",
      "EDSBRO CENTRUM"
    ],
    "lId": "01042",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.896388888888886,
      "lon": 18.495
    }
  },
  {
    "name": "Edsbruk",
    "synonyms": [
      "EDSBRUK"
    ],
    "lId": "14133",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 58.02194444444444,
      "lon": 16.46361111111111
    }
  },
  {
    "name": "Edsbyn Centrum",
    "synonyms": [
      "EDSBYN CENTRUM"
    ],
    "lId": "00590",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 61.37583333333333,
      "lon": 15.817777777777778
    }
  },
  {
    "name": "Edsele ICA",
    "synonyms": [
      "EDSELE ICA"
    ],
    "lId": "15126",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 63.40277777777778,
      "lon": 16.544722222222223
    }
  },
  {
    "name": "Edsvalla",
    "synonyms": [
      "EDSVALLA",
      "EDSVALLA BSTN"
    ],
    "lId": "00803",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.43583333333333,
      "lon": 13.210833333333333
    }
  },
  {
    "name": "Edsåsdalen",
    "synonyms": [
      "EDSÅSDALEN"
    ],
    "lId": "00448",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 63.315555555555555,
      "lon": 13.105833333333333
    }
  },
  {
    "name": "Edö brygga",
    "synonyms": [
      "EDÖ BRYGGA",
      "EDØ BRYGGA"
    ],
    "lId": "24883",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.46666666666667,
      "lon": 18.63277777777778
    }
  },
  {
    "name": "Eggby",
    "synonyms": [
      "EGGBY"
    ],
    "lId": "10271",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 58.43222222222222,
      "lon": 13.641666666666666
    }
  },
  {
    "name": "Eke terminal",
    "synonyms": [
      "EKE TERMINAL"
    ],
    "lId": "14463",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 57.0175,
      "lon": 15.05388888888889
    }
  },
  {
    "name": "Ekeby Egna hem Kumla",
    "synonyms": [
      "EKEBY EGNA HEM KUMLA",
      "EKEBY EGNAH NÄR",
      "EKEBY EGNAH NÆR"
    ],
    "lId": "10273",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.165277777777774,
      "lon": 15.26361111111111
    }
  },
  {
    "name": "Ekeby Lillängsvägen Södertälje",
    "synonyms": [
      "EKEBY LILLÄNGSVÄGEN SÖDERTÄLJE",
      "EKEBY LILLÆNGSVÆGEN SØDERTÆLJE"
    ],
    "lId": "24780",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.2525,
      "lon": 17.515555555555554
    }
  },
  {
    "name": "Ekeby Rundelsgatan Bjuv",
    "synonyms": [
      "EKEBY RUNDELSGATAN BJUV"
    ],
    "lId": "10275",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 56.00055555555556,
      "lon": 12.972222222222223
    }
  },
  {
    "name": "Ekeby Ösmo",
    "synonyms": [
      "EKEBY ÖSMO",
      "EKEBY ÖSMÖ"
    ],
    "lId": "69629",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.01222222222222,
      "lon": 17.96388888888889
    }
  },
  {
    "name": "Ekeby-Almby",
    "synonyms": [
      "EKEBY-ALMBY",
      "EKEBY-ALMBY RÖK",
      "EKEBY-ALMBY RØK"
    ],
    "lId": "01111",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.25944444444445,
      "lon": 15.338611111111112
    }
  },
  {
    "name": "Ekedalen",
    "synonyms": [
      "EKEDALEN"
    ],
    "lId": "01449",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 58.196666666666665,
      "lon": 13.841944444444445
    }
  },
  {
    "name": "Ekenäs",
    "synonyms": [
      "EKENÄS",
      "EKENÄS SÄFFLE",
      "EKENÆS",
      "EKENÆS SÆFFLE"
    ],
    "lId": "22340",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 58.89666666666667,
      "lon": 13.233888888888888
    }
  },
  {
    "name": "Ekenässjön",
    "synonyms": [
      "EKENASSJON",
      "EKENÄSSJÖN",
      "EKENÄSSJÖN STN",
      "EKENÆSSJØN",
      "EKENÆSSJØN STN"
    ],
    "lId": "00510",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 57.489444444444445,
      "lon": 15.019166666666667
    }
  },
  {
    "name": "Ekeryd",
    "synonyms": [
      "EKERYD",
      "EKERYD STN"
    ],
    "lId": "01043",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 57.60861111111111,
      "lon": 14.10611111111111
    }
  },
  {
    "name": "Ekerö centrum",
    "synonyms": [
      "EKERÖ CENTRUM",
      "EKERØ CENTRUM"
    ],
    "lId": "00690",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.29,
      "lon": 17.810000000000002
    }
  },
  {
    "name": "Eket E4",
    "synonyms": [
      "EKET E4"
    ],
    "lId": "36037",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 56.245,
      "lon": 13.195555555555556
    }
  },
  {
    "name": "Eketorp",
    "synonyms": [
      "EKETORP",
      "EKETORP BORG"
    ],
    "lId": "14136",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 56.294999999999995,
      "lon": 16.484722222222224
    }
  },
  {
    "name": "Eklången",
    "synonyms": [
      "EKLÅNGEN"
    ],
    "lId": "10280",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.23972222222222,
      "lon": 16.745
    }
  },
  {
    "name": "Ekolsund gård",
    "synonyms": [
      "EKOLSUND GÅRD"
    ],
    "lId": "12857",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.65333333333333,
      "lon": 17.360555555555557
    }
  },
  {
    "name": "Ekshärad",
    "synonyms": [
      "EKSHÄRAD",
      "EKSHÄRAD KONSUM",
      "EKSHÆRAD",
      "EKSHÆRAD KONSUM"
    ],
    "lId": "00805",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 60.17611111111111,
      "lon": 13.495555555555555
    }
  },
  {
    "name": "Eksjö",
    "synonyms": [
      "EKSJO",
      "EKSJÖ",
      "EKSJÖ STN",
      "EKSJØ",
      "EKSJØ STN"
    ],
    "lId": "00084",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 57.66361111111111,
      "lon": 14.975555555555555
    }
  },
  {
    "name": "Eksjö Höglandssjukhuset",
    "synonyms": [
      "EKSJÖ HÖGLANDSSJUKHUSET",
      "EKSJÖ HÖGLSJUKH",
      "EKSJØ HØGLANDSSJUKHUSET",
      "EKSJØ HØGLSJUKH"
    ],
    "lId": "25017",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 57.66583333333333,
      "lon": 14.966666666666667
    }
  },
  {
    "name": "Ekskogen",
    "synonyms": [
      "EKSKOGEN",
      "EKSKOGEN STN"
    ],
    "lId": "24803",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.638888888888886,
      "lon": 18.22694444444444
    }
  },
  {
    "name": "Eksta",
    "synonyms": [
      "EKSTA",
      "EKSTA SKOLA"
    ],
    "lId": "01112",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 57.28666666666666,
      "lon": 18.205277777777777
    }
  },
  {
    "name": "Ekängen Soldanevägen",
    "synonyms": [
      "EKÄNGEN SOLDANEVÄGEN",
      "EKÄNGEN SOLDANV",
      "EKÆNGEN SOLDANEVÆGEN",
      "EKÆNGEN SOLDANV"
    ],
    "lId": "23076",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 58.47,
      "lon": 15.633888888888889
    }
  },
  {
    "name": "Eldsberga Gullbrannavägen",
    "synonyms": [
      "ELDSBERGA GULLBRANNAVÄGEN",
      "ELDSBERGA GULLBRANNAVÆGEN"
    ],
    "lId": "01044",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 56.59527777777778,
      "lon": 12.975277777777778
    }
  },
  {
    "name": "Ellös",
    "synonyms": [
      "ELLÖS",
      "ELLÖS BSTN",
      "ELLØS",
      "ELLØS BSTN"
    ],
    "lId": "00279",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 58.18277777777777,
      "lon": 11.466111111111111
    }
  },
  {
    "name": "Emmaboda",
    "synonyms": [
      "EMMABODA",
      "EMMABODA STN"
    ],
    "lId": "00096",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 56.629444444444445,
      "lon": 15.535833333333333
    }
  },
  {
    "name": "Emmabodafestivalen",
    "synonyms": [
      "EMMABODAFESTIVALEN"
    ],
    "lId": "33000",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 56.628055555555555,
      "lon": 15.555000000000001
    }
  },
  {
    "name": "Emmaljunga",
    "synonyms": [
      "EMMALJUNGA",
      "EMMALJUNGA HULT"
    ],
    "lId": "01450",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 56.39833333333333,
      "lon": 13.649166666666666
    }
  },
  {
    "name": "Emsfors",
    "synonyms": [
      "EMSFORS"
    ],
    "lId": "14137",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 57.14805555555556,
      "lon": 16.45861111111111
    }
  },
  {
    "name": "Emådalen",
    "synonyms": [
      "EMÅDALEN"
    ],
    "lId": "18303",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 61.31861111111112,
      "lon": 14.730555555555556
    }
  },
  {
    "name": "Enafors",
    "synonyms": [
      "ENAFORS",
      "ENAFORS STN"
    ],
    "lId": "00063",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 63.28972222222222,
      "lon": 12.336944444444445
    }
  },
  {
    "name": "Enebyberg",
    "synonyms": [
      "ENEBYBERG",
      "ENEBYBERG STN"
    ],
    "lId": "24372",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.425555555555555,
      "lon": 18.051111111111112
    }
  },
  {
    "name": "Eneryda Gummegatan",
    "synonyms": [
      "ENERYDA GUMMEGATAN"
    ],
    "lId": "24771",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 56.705000000000005,
      "lon": 14.336944444444445
    }
  },
  {
    "name": "Engarn",
    "synonyms": [
      "ENGARN"
    ],
    "lId": "24782",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.4175,
      "lon": 18.311111111111114
    }
  },
  {
    "name": "Engelsberg bruk",
    "synonyms": [
      "ENGELSBERG BRUK"
    ],
    "lId": "44416",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.966944444444444,
      "lon": 16.00888888888889
    }
  },
  {
    "name": "Enhagen-Ekbacken",
    "synonyms": [
      "ENHAGEN-EKBACKEN"
    ],
    "lId": "24000",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.56111111111111,
      "lon": 16.528055555555554
    }
  },
  {
    "name": "Enköping",
    "synonyms": [
      "ENKOPING",
      "ENKÖPING",
      "ENKÖPING STN",
      "ENKØPING",
      "ENKØPING STN"
    ],
    "lId": "00072",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.64472222222222,
      "lon": 17.088055555555556
    }
  },
  {
    "name": "Enskede gård T-bana",
    "synonyms": [
      "ENSKEDE GÅRD T",
      "ENSKEDE GÅRD T-BANA"
    ],
    "lId": "21707",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.28916666666667,
      "lon": 18.07027777777778
    }
  },
  {
    "name": "Ensta",
    "synonyms": [
      "ENSTA",
      "ENSTA STN"
    ],
    "lId": "24799",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.45333333333333,
      "lon": 18.06361111111111
    }
  },
  {
    "name": "Enstaberga",
    "synonyms": [
      "ENSTABERGA"
    ],
    "lId": "10293",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 58.749722222222225,
      "lon": 16.849444444444444
    }
  },
  {
    "name": "Enviken",
    "synonyms": [
      "ENVIKEN",
      "ENVIKEN BSTN"
    ],
    "lId": "01045",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 60.808055555555555,
      "lon": 15.758611111111112
    }
  },
  {
    "name": "Enånger kiosken",
    "synonyms": [
      "ENÅNGER KIOSKEN"
    ],
    "lId": "10294",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 61.54722222222222,
      "lon": 17.005
    }
  },
  {
    "name": "Erikslund",
    "synonyms": [
      "ERIKSLUND"
    ],
    "lId": "00842",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 62.52777777777778,
      "lon": 15.922777777777776
    }
  },
  {
    "name": "Eriksmåla",
    "synonyms": [
      "ERIKSMÅLA"
    ],
    "lId": "00033",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 56.73416666666667,
      "lon": 15.480555555555556
    }
  },
  {
    "name": "Eringsboda",
    "synonyms": [
      "ERINGSBODA"
    ],
    "lId": "10297",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 56.44027777777777,
      "lon": 15.363888888888889
    }
  },
  {
    "name": "Ersmark Skellefteå",
    "synonyms": [
      "ERSMARK",
      "ERSMARK SKELLEFTEÅ"
    ],
    "lId": "13840",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 64.84333333333333,
      "lon": 20.918055555555558
    }
  },
  {
    "name": "Ersnäs",
    "synonyms": [
      "ERSNÄS",
      "ERSNÄS OSTIBYV",
      "ERSNÆS",
      "ERSNÆS OSTIBYV"
    ],
    "lId": "14861",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 65.5225,
      "lon": 21.798055555555557
    }
  },
  {
    "name": "Ersnäs E4",
    "synonyms": [
      "ERSNÄS E4",
      "ERSNÆS E4"
    ],
    "lId": "20147",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 65.53138888888888,
      "lon": 21.791666666666668
    }
  },
  {
    "name": "Erstaviksbadet",
    "synonyms": [
      "ERSTAVIKSBADET"
    ],
    "lId": "24812",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.272777777777776,
      "lon": 18.285
    }
  },
  {
    "name": "Ervalla",
    "synonyms": [
      "ERVALLA",
      "ERVALLA KYRKA"
    ],
    "lId": "10298",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.43888888888888,
      "lon": 15.241666666666665
    }
  },
  {
    "name": "Eskelhem",
    "synonyms": [
      "ESKELHEM",
      "ESKELHEM FD AFF"
    ],
    "lId": "10299",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 57.486111111111114,
      "lon": 18.21527777777778
    }
  },
  {
    "name": "Eskilstuna C",
    "synonyms": [
      "ESKILSTUNA C",
      "XFJ"
    ],
    "lId": "00170",
    "prio": 1,
    "pId": "074",
    "pos": {
      "lat": 59.369166666666665,
      "lon": 16.50611111111111
    }
  },
  {
    "name": "Eskilstuna Parken Zoo",
    "synonyms": [
      "ESKILSTUNA PARKEN ZOO",
      "ESKILSTUNA ZOO"
    ],
    "lId": "21907",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.37388888888889,
      "lon": 16.486944444444447
    }
  },
  {
    "name": "Eskilstuna Sahl",
    "synonyms": [
      "ESKILSTUNA SAHL"
    ],
    "lId": "21535",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.39666666666667,
      "lon": 16.547222222222224
    }
  },
  {
    "name": "Eskilstuna Skiftingehus",
    "synonyms": [
      "ESKILSTUNA SKIFTINGEHUS"
    ],
    "lId": "21412",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.38777777777778,
      "lon": 16.539722222222224
    }
  },
  {
    "name": "Eslöv",
    "synonyms": [
      "ESLOV",
      "ESLÖV",
      "ESLÖV STN",
      "ESLØV",
      "ESLØV STN"
    ],
    "lId": "00260",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 55.837500000000006,
      "lon": 13.305277777777778
    }
  },
  {
    "name": "Espergaerde",
    "synonyms": [
      "ESPERGAERDE"
    ],
    "lId": "00667",
    "prio": 0,
    "pId": "086",
    "pos": {
      "lat": 55.99527777777778,
      "lon": 12.549444444444445
    }
  },
  {
    "name": "Essvik skola",
    "synonyms": [
      "ESSVIK SKOLA"
    ],
    "lId": "27557",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 62.308055555555555,
      "lon": 17.38861111111111
    }
  },
  {
    "name": "Evertsberg",
    "synonyms": [
      "EVERTSBERG"
    ],
    "lId": "01113",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 61.134166666666665,
      "lon": 13.955
    }
  },
  {
    "name": "Everöd Medspårsvägen",
    "synonyms": [
      "EVERÖD MEDSPÅRSVÄGEN",
      "EVERØD MEDSPÅRSVÆGEN"
    ],
    "lId": "22132",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 55.89972222222222,
      "lon": 14.0825
    }
  },
  {
    "name": "Fagerhult Habo",
    "synonyms": [
      "FAGERHULT HABO"
    ],
    "lId": "04247",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 57.99888888888889,
      "lon": 14.119722222222222
    }
  },
  {
    "name": "Fagerhult Högsby",
    "synonyms": [
      "FAGERHULT HÖGSBY",
      "FAGERHULT HØGSBY"
    ],
    "lId": "14142",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 57.14694444444444,
      "lon": 15.661944444444444
    }
  },
  {
    "name": "Fagermon",
    "synonyms": [
      "FAGERMON"
    ],
    "lId": "10308",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.075833333333335,
      "lon": 16.001666666666665
    }
  },
  {
    "name": "Fagersanna",
    "synonyms": [
      "FAGERSANNA",
      "FAGERSANNA STNV"
    ],
    "lId": "01452",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 58.468333333333334,
      "lon": 14.298055555555555
    }
  },
  {
    "name": "Fagersta C",
    "synonyms": [
      "FAGERSTA C"
    ],
    "lId": "00266",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.99055555555556,
      "lon": 15.81638888888889
    }
  },
  {
    "name": "Fagersta Fårbo industriområde",
    "synonyms": [
      "FAGERSTA FÅRBO INDUSTRIOMRÅDE"
    ],
    "lId": "44782",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.981388888888894,
      "lon": 15.79861111111111
    }
  },
  {
    "name": "Fagersta Hantverksvägen",
    "synonyms": [
      "FAGERSTA HANTVERKSVÄGEN"
    ],
    "lId": "44435",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 60.013333333333335,
      "lon": 15.787777777777778
    }
  },
  {
    "name": "Fagersta lasarett",
    "synonyms": [
      "FAGERSTA LASARETT"
    ],
    "lId": "44785",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.99611111111111,
      "lon": 15.809444444444445
    }
  },
  {
    "name": "Fagersta Norra",
    "synonyms": [
      "FAGERSTA NORRA"
    ],
    "lId": "20094",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 60.0025,
      "lon": 15.7875
    }
  },
  {
    "name": "Fagerviken",
    "synonyms": [
      "FAGERVIKEN"
    ],
    "lId": "12699",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 60.54,
      "lon": 17.74277777777778
    }
  },
  {
    "name": "Fagerås",
    "synonyms": [
      "FAGERAS",
      "FAGERÅS"
    ],
    "lId": "00426",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.51916666666666,
      "lon": 13.219722222222222
    }
  },
  {
    "name": "Falerum",
    "synonyms": [
      "FALERUM",
      "FALERUM STN"
    ],
    "lId": "00496",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 58.14333333333333,
      "lon": 16.20777777777778
    }
  },
  {
    "name": "Falkenberg busstation",
    "synonyms": [
      "FALKENBERG BSTN",
      "FALKENBERG BUSSTATION"
    ],
    "lId": "00257",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 56.901944444444446,
      "lon": 12.488055555555555
    }
  },
  {
    "name": "Falkenberg E6 McDonalds",
    "synonyms": [
      "FALKENBERG E6 MCDONALDS"
    ],
    "lId": "23256",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 56.93,
      "lon": 12.519166666666667
    }
  },
  {
    "name": "Falkenberg station",
    "synonyms": [
      "FALKENBERG STATION",
      "FALKENBERG STN"
    ],
    "lId": "01579",
    "prio": 1,
    "pId": "074",
    "pos": {
      "lat": 56.91972222222222,
      "lon": 12.5075
    }
  },
  {
    "name": "Falkenberg STCC",
    "synonyms": [
      "FALKENBERG STCC"
    ],
    "lId": "65296",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 56.97833333333333,
      "lon": 12.564722222222223
    }
  },
  {
    "name": "Falkenberg Södra Shell 7eleven",
    "synonyms": [
      "FALKENBERG SÖDRA SHELL 7ELEVEN"
    ],
    "lId": "71640",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 56.90333333333333,
      "lon": 12.580277777777777
    }
  },
  {
    "name": "Falköping C",
    "synonyms": [
      "FALKOPING C",
      "FALKÖPING C",
      "FALKØPING C"
    ],
    "lId": "00060",
    "prio": 1,
    "pId": "074",
    "pos": {
      "lat": 58.17583333333333,
      "lon": 13.553611111111111
    }
  },
  {
    "name": "Falla Tolskepps vägskäl",
    "synonyms": [
      "FALLA TOLSKEPPS VÄGSK2L",
      "FALLA TOLSKEPPS VÄGSKÄL",
      "FALLA TOLSKEPPS VÆGSK2L"
    ],
    "lId": "24843",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 58.67916666666667,
      "lon": 15.751666666666667
    }
  },
  {
    "name": "Falsterbo",
    "synonyms": [
      "FALSTERBO",
      "FALSTERBO SBAD"
    ],
    "lId": "00940",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 55.39388888888889,
      "lon": 12.851111111111111
    }
  },
  {
    "name": "Falun C",
    "synonyms": [
      "FALUN C"
    ],
    "lId": "00030",
    "prio": 1,
    "pId": "074",
    "pos": {
      "lat": 60.60305555555556,
      "lon": 15.641388888888889
    }
  },
  {
    "name": "Falun Lugnet sporthallen",
    "synonyms": [
      "FALUN LUGNET SPORTHALLEN"
    ],
    "lId": "13010",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 60.61805555555556,
      "lon": 15.658055555555556
    }
  },
  {
    "name": "Falun stadszon",
    "synonyms": [
      "FALUN STADSZON"
    ],
    "lId": "79001",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 60.60305555555556,
      "lon": 15.641388888888889
    }
  },
  {
    "name": "Fanthyttan",
    "synonyms": [
      "FANTHYTTAN"
    ],
    "lId": "10316",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.66305555555555,
      "lon": 15.098611111111111
    }
  },
  {
    "name": "Fardhem väg 141",
    "synonyms": [
      "FARDHEM VÄG 141",
      "FARDHEM VÆG 141"
    ],
    "lId": "70569",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 64.86388888888888,
      "lon": 20.83722222222222
    }
  },
  {
    "name": "Farhult Farhultsbaden",
    "synonyms": [
      "FARHULT FARHBAD",
      "FARHULT FARHULTSBADEN"
    ],
    "lId": "16613",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 56.218611111111116,
      "lon": 12.713888888888889
    }
  },
  {
    "name": "Faringe station",
    "synonyms": [
      "FARINGE STATION",
      "FARINGE STN"
    ],
    "lId": "20999",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.91972222222222,
      "lon": 18.114722222222223
    }
  },
  {
    "name": "Farsta Strand station",
    "synonyms": [
      "FARSTA STRAND",
      "FARSTA STRAND STATION"
    ],
    "lId": "00692",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.23638888888889,
      "lon": 18.10138888888889
    }
  },
  {
    "name": "Farsta T-bana",
    "synonyms": [
      "FARSTA T-BANA"
    ],
    "lId": "21697",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.24333333333333,
      "lon": 18.093055555555555
    }
  },
  {
    "name": "Fegen",
    "synonyms": [
      "FEGEN"
    ],
    "lId": "01047",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 57.105555555555554,
      "lon": 13.0375
    }
  },
  {
    "name": "Fellingsbro station",
    "synonyms": [
      "FELLINGSBRO STATION",
      "FELLINGSBRO STN"
    ],
    "lId": "00175",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.43333333333333,
      "lon": 15.591944444444445
    }
  },
  {
    "name": "Fengersfors",
    "synonyms": [
      "FENGERSFORS"
    ],
    "lId": "01453",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 58.99444444444445,
      "lon": 12.468333333333334
    }
  },
  {
    "name": "Figeholm centrum",
    "synonyms": [
      "FIGEHOLM CENTRUM",
      "FIGEHOLM CM"
    ],
    "lId": "14145",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 57.37083333333334,
      "lon": 16.55027777777778
    }
  },
  {
    "name": "Filipstad busstation",
    "synonyms": [
      "FILIPSTAD BUSSTATION"
    ],
    "lId": "10325",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.71333333333334,
      "lon": 14.173055555555555
    }
  },
  {
    "name": "Film kyrka",
    "synonyms": [
      "FILM KYRKA"
    ],
    "lId": "12748",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 60.22888888888889,
      "lon": 17.894166666666667
    }
  },
  {
    "name": "Filsbäck",
    "synonyms": [
      "FILSBÄCK",
      "FILSBÄCK STN",
      "FILSBÆCK",
      "FILSBÆCK STN"
    ],
    "lId": "01048",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 58.49305555555556,
      "lon": 13.247222222222222
    }
  },
  {
    "name": "Finja By",
    "synonyms": [
      "FINJA BY"
    ],
    "lId": "31470",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 56.16777777777777,
      "lon": 13.694166666666668
    }
  },
  {
    "name": "Finnebäck",
    "synonyms": [
      "FINNEBÄCK",
      "FINNEBÆCK"
    ],
    "lId": "10329",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.657222222222224,
      "lon": 12.94
    }
  },
  {
    "name": "Finnerödja Mobäcksvägen",
    "synonyms": [
      "FINNERÖDJA MOBÄCKSVÄGEN",
      "FINNERØDJA MOBÆCKSVÆGEN"
    ],
    "lId": "21082",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 58.92305555555555,
      "lon": 14.440277777777778
    }
  },
  {
    "name": "Finnhamn",
    "synonyms": [
      "FINNHAMN",
      "FINNHAMN BRYGGA"
    ],
    "lId": "20693",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.4825,
      "lon": 18.826666666666668
    }
  },
  {
    "name": "Finnmarken",
    "synonyms": [
      "FINNMARKEN"
    ],
    "lId": "15400",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 62.92222222222222,
      "lon": 17.595
    }
  },
  {
    "name": "Finspång Stationsvägen",
    "synonyms": [
      "FINSPÅNG STATIONSVÄGEN",
      "FINSPÅNG STNVÄG"
    ],
    "lId": "64342",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 58.7075,
      "lon": 15.776944444444446
    }
  },
  {
    "name": "Finsta station",
    "synonyms": [
      "FINSTA STATION",
      "FINSTA STN"
    ],
    "lId": "09185",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.73722222222222,
      "lon": 18.496666666666666
    }
  },
  {
    "name": "Fiskarheden",
    "synonyms": [
      "FISKARHEDEN",
      "FISKARHEDEN BST"
    ],
    "lId": "01114",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 61.07,
      "lon": 13.329722222222221
    }
  },
  {
    "name": "Fiskebäckskil",
    "synonyms": [
      "FISKEBACKSKIL",
      "FISKEBÄCKSKIL",
      "FISKEBÆCKSKIL"
    ],
    "lId": "00297",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 58.24333333333333,
      "lon": 11.458333333333332
    }
  },
  {
    "name": "Fisksätra",
    "synonyms": [
      "FISKSÄTRA",
      "FISKSÄTRA STN",
      "FISKSÆTRA",
      "FISKSÆTRA STN"
    ],
    "lId": "00693",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.29388888888889,
      "lon": 18.25638888888889
    }
  },
  {
    "name": "Fittja T-bana",
    "synonyms": [
      "FITTJA T-BANA"
    ],
    "lId": "21730",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.24722222222222,
      "lon": 17.860833333333336
    }
  },
  {
    "name": "Fivelstad kyrka",
    "synonyms": [
      "FIVELSTAD KYRKA"
    ],
    "lId": "10339",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 58.441111111111105,
      "lon": 15.00388888888889
    }
  },
  {
    "name": "Fjelie by",
    "synonyms": [
      "FJELIE BY"
    ],
    "lId": "16614",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 55.72527777777778,
      "lon": 13.10611111111111
    }
  },
  {
    "name": "Fjugesta Storgatan",
    "synonyms": [
      "FJUGESTA STORGATAN"
    ],
    "lId": "24440",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.172777777777775,
      "lon": 14.87138888888889
    }
  },
  {
    "name": "Fjälkestad",
    "synonyms": [
      "FJÄLKESTAD",
      "FJÄLKESTAD KA",
      "FJÆLKESTAD",
      "FJÆLKESTAD KA"
    ],
    "lId": "04110",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 56.10777777777778,
      "lon": 14.169444444444444
    }
  },
  {
    "name": "Fjälkinge Kumlevägen",
    "synonyms": [
      "FJÄLKINGE KUMLEVÄGEN",
      "FJÄLKINGE KUMLV",
      "FJÆLKINGE KUMLEVÆGEN",
      "FJÆLKINGE KUMLV"
    ],
    "lId": "26069",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 56.034166666666664,
      "lon": 14.2675
    }
  },
  {
    "name": "Fjälkinge station",
    "synonyms": [
      "FJÄLKINGE STATION",
      "FJÆLKINGE STATION"
    ],
    "lId": "01607",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 56.04361111111111,
      "lon": 14.280555555555557
    }
  },
  {
    "name": "Fjällbacka",
    "synonyms": [
      "FJÄLLBACKA",
      "FJÆLLBACKA"
    ],
    "lId": "00296",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 58.599722222222226,
      "lon": 11.285
    }
  },
  {
    "name": "Fjällnora Friluftsgård",
    "synonyms": [
      "FJÄLLNORA FRILUFTSGÅRD",
      "FJÆLLNORA FRILUFTSGÅRD"
    ],
    "lId": "26058",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.836111111111116,
      "lon": 17.91361111111111
    }
  },
  {
    "name": "Fjällnäs",
    "synonyms": [
      "FJÄLLNÄS",
      "FJÄLLNÄS HÖGFJÄ",
      "FJÆLLNÆS",
      "FJÆLLNÆS HØGFJÆ"
    ],
    "lId": "00481",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 62.59805555555556,
      "lon": 12.179722222222221
    }
  },
  {
    "name": "Fjällsta",
    "synonyms": [
      "FJÄLLSTA",
      "FJÆLLSTA"
    ],
    "lId": "13296",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 62.97083333333334,
      "lon": 15.168888888888889
    }
  },
  {
    "name": "Fjällåsen",
    "synonyms": [
      "FJALLASEN",
      "FJÄLLÅSEN",
      "FJÄLLÅSEN STN",
      "FJÆLLÅSEN",
      "FJÆLLÅSEN STN"
    ],
    "lId": "00414",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 67.51833333333333,
      "lon": 20.093333333333334
    }
  },
  {
    "name": "Fjärdhundra",
    "synonyms": [
      "FJÄRDHUNDRA",
      "FJÄRDHUNDRA CM",
      "FJÆRDHUNDRA",
      "FJÆRDHUNDRA CM"
    ],
    "lId": "01049",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.777499999999996,
      "lon": 16.927222222222223
    }
  },
  {
    "name": "Fjärdlång",
    "synonyms": [
      "FJÄRDLÅNG",
      "FJÆRDLÅNG"
    ],
    "lId": "20696",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.035555555555554,
      "lon": 18.511388888888888
    }
  },
  {
    "name": "Fjärdsjömåla",
    "synonyms": [
      "FJÄRDSJÖMÅLA"
    ],
    "lId": "10344",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 56.33861111111111,
      "lon": 15.740555555555554
    }
  },
  {
    "name": "Fjären",
    "synonyms": [
      "FJÄREN",
      "FJÆREN"
    ],
    "lId": "15137",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 63.04861111111111,
      "lon": 18.63861111111111
    }
  },
  {
    "name": "Fjärås Bräckaskolan",
    "synonyms": [
      "FJÄRÅS BRÄCKASKOLAN"
    ],
    "lId": "16029",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 57.45611111111111,
      "lon": 12.184166666666666
    }
  },
  {
    "name": "Fjärås centrum",
    "synonyms": [
      "FJÄRÅS CENTRUM"
    ],
    "lId": "16026",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 57.46027777777778,
      "lon": 12.17
    }
  },
  {
    "name": "Fjärås station",
    "synonyms": [
      "FJÄRÅS STATION",
      "FJÄRÅS STN",
      "FJÆRÅS STATION",
      "FJÆRÅS STN"
    ],
    "lId": "00763",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 57.43611111111111,
      "lon": 12.15388888888889
    }
  },
  {
    "name": "Flemingsberg",
    "synonyms": [
      "FLEMINGSBERG",
      "FLEMMINGSBERG",
      "XEW"
    ],
    "lId": "00031",
    "prio": 1,
    "pId": "074",
    "pos": {
      "lat": 59.217777777777776,
      "lon": 17.945555555555554
    }
  },
  {
    "name": "Flen",
    "synonyms": [
      "FLEN",
      "FLEN STN"
    ],
    "lId": "00288",
    "prio": 1,
    "pId": "074",
    "pos": {
      "lat": 59.05722222222222,
      "lon": 16.58888888888889
    }
  },
  {
    "name": "Fleninge kyrka",
    "synonyms": [
      "FLENINGE KYRKA"
    ],
    "lId": "16617",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 56.11138888888889,
      "lon": 12.793055555555556
    }
  },
  {
    "name": "Flerohopp",
    "synonyms": [
      "FLEROHOPP"
    ],
    "lId": "14149",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 56.82333333333334,
      "lon": 15.877222222222223
    }
  },
  {
    "name": "Flisby station",
    "synonyms": [
      "FLISBY STATION",
      "FLISBY STN"
    ],
    "lId": "24359",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 57.785,
      "lon": 14.800555555555556
    }
  },
  {
    "name": "Fliseryd centrum",
    "synonyms": [
      "FLISERYD CENTRUM",
      "FLISERYD CM"
    ],
    "lId": "14148",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 57.12694444444445,
      "lon": 16.261388888888888
    }
  },
  {
    "name": "Floby",
    "synonyms": [
      "FLOBY",
      "FLOBY STN"
    ],
    "lId": "00036",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 58.13916666666667,
      "lon": 13.335277777777778
    }
  },
  {
    "name": "Floda",
    "synonyms": [
      "FLODA",
      "FLODA STN"
    ],
    "lId": "00203",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 57.809999999999995,
      "lon": 12.36111111111111
    }
  },
  {
    "name": "Flygsfors Skogsvägen",
    "synonyms": [
      "FLYGSFORS SKOGSVÄGEN",
      "FLYGSFORS SKOGSVÆGEN",
      "FLYGSFORS SKOGV"
    ],
    "lId": "14158",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 56.83694444444445,
      "lon": 15.780833333333334
    }
  },
  {
    "name": "Flyinge Plantskolevägen",
    "synonyms": [
      "FLYINGE PLANTSKOLEVÄGEN",
      "FLYINGE PLANTSKOLEVÆGEN"
    ],
    "lId": "20340",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 55.751666666666665,
      "lon": 13.370555555555557
    }
  },
  {
    "name": "Flykälen",
    "synonyms": [
      "FLYKÄLEN",
      "FLYKÆLEN"
    ],
    "lId": "13219",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 63.85805555555556,
      "lon": 15.015833333333333
    }
  },
  {
    "name": "Fläckebo kyrka",
    "synonyms": [
      "FLÄCKEBO KYRKA"
    ],
    "lId": "44117",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.87555555555556,
      "lon": 16.34638888888889
    }
  },
  {
    "name": "Flädie affären",
    "synonyms": [
      "FLÄDIE AFFÄREN",
      "FLÆDIE AFFÆREN"
    ],
    "lId": "16619",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 55.72527777777778,
      "lon": 13.072777777777777
    }
  },
  {
    "name": "Flängan",
    "synonyms": [
      "FLÄNGAN"
    ],
    "lId": "72001",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 60.08888888888889,
      "lon": 15.874166666666667
    }
  },
  {
    "name": "Flärke Gideå",
    "synonyms": [
      "FLÄRKE GIDEÅ",
      "FLÆRKE GIDEÅ"
    ],
    "lId": "29094",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 63.57694444444445,
      "lon": 19.025277777777777
    }
  },
  {
    "name": "Fornåsa",
    "synonyms": [
      "FORNÅSA"
    ],
    "lId": "01050",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 58.47833333333333,
      "lon": 15.227500000000001
    }
  },
  {
    "name": "Fors station",
    "synonyms": [
      "FORS STATION",
      "FORS STN"
    ],
    "lId": "00704",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 60.20805555555556,
      "lon": 16.31416666666667
    }
  },
  {
    "name": "Forsbacka",
    "synonyms": [
      "FORSBACKA",
      "FORSBACKA KONSU"
    ],
    "lId": "10362",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 60.61388888888889,
      "lon": 16.890555555555554
    }
  },
  {
    "name": "Forserum",
    "synonyms": [
      "FORSERUM",
      "FORSERUM STN"
    ],
    "lId": "00034",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 57.69777777777777,
      "lon": 14.473888888888888
    }
  },
  {
    "name": "Forshaga",
    "synonyms": [
      "FORSHAGA",
      "FORSHAGA CM"
    ],
    "lId": "00375",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.5325,
      "lon": 13.480277777777777
    }
  },
  {
    "name": "Forsheda",
    "synonyms": [
      "FORSHEDA",
      "FORSHEDA STN"
    ],
    "lId": "00439",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 57.163333333333334,
      "lon": 13.8325
    }
  },
  {
    "name": "Forshem",
    "synonyms": [
      "FORSHEM",
      "FORSHEM STN"
    ],
    "lId": "01051",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 58.617777777777775,
      "lon": 13.491388888888888
    }
  },
  {
    "name": "Forsmark kraftverk 1-2",
    "synonyms": [
      "FORSMARK KRAFTVERK 1-2",
      "FORSMARK VERK 1"
    ],
    "lId": "12666",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 60.403055555555554,
      "lon": 18.178333333333335
    }
  },
  {
    "name": "Forsmark kraftverk 3",
    "synonyms": [
      "FORSMARK KRAFTVERK 3",
      "FORSMARK VERK 3"
    ],
    "lId": "24557",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 60.407222222222224,
      "lon": 18.16
    }
  },
  {
    "name": "Forsmark kvarnen",
    "synonyms": [
      "FORSMARK KVARN",
      "FORSMARK KVARNEN"
    ],
    "lId": "01115",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 60.368611111111115,
      "lon": 18.151944444444442
    }
  },
  {
    "name": "Forssjö skola",
    "synonyms": [
      "FORSSJÖ SKOLA",
      "FORSSJØ SKOLA"
    ],
    "lId": "09341",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 58.95444444444445,
      "lon": 16.295555555555556
    }
  },
  {
    "name": "Forsvik",
    "synonyms": [
      "FORSVIK"
    ],
    "lId": "10369",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 58.57666666666667,
      "lon": 14.434722222222222
    }
  },
  {
    "name": "Fotö färjeläge",
    "synonyms": [
      "FOTÖ FÄRJELÄGE",
      "FOTØ FÆRJELÆGE"
    ],
    "lId": "15622",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 57.672777777777775,
      "lon": 11.654722222222222
    }
  },
  {
    "name": "Framnäs City",
    "synonyms": [
      "FRAMNÄS CITY",
      "FRAMNÆS CITY"
    ],
    "lId": "01054",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 58.50833333333333,
      "lon": 13.146944444444443
    }
  },
  {
    "name": "Frankhyttan",
    "synonyms": [
      "FRANKHYTTAN"
    ],
    "lId": "10371",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 58.6625,
      "lon": 16.861111111111114
    }
  },
  {
    "name": "Fredrika",
    "synonyms": [
      "FREDRIKA"
    ],
    "lId": "01055",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 64.07527777777777,
      "lon": 18.407777777777778
    }
  },
  {
    "name": "Fredriksberg",
    "synonyms": [
      "FREDRIKSBERG",
      "FREDRIKSBRG BPL"
    ],
    "lId": "00643",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 60.13944444444444,
      "lon": 14.378055555555555
    }
  },
  {
    "name": "Fredriksdal kyrka",
    "synonyms": [
      "FREDRIKSDAL KYRKA"
    ],
    "lId": "24639",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 57.61805555555556,
      "lon": 14.599444444444446
    }
  },
  {
    "name": "Fredriksfors",
    "synonyms": [
      "FREDRIKSFORS"
    ],
    "lId": "10372",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 61.78611111111111,
      "lon": 16.616666666666667
    }
  },
  {
    "name": "Fredrikstad",
    "synonyms": [
      "FREDRIKSTAD"
    ],
    "lId": "00522",
    "prio": 0,
    "pId": "076",
    "pos": {
      "lat": 59.23111111111111,
      "lon": 10.975277777777778
    }
  },
  {
    "name": "Fridafors",
    "synonyms": [
      "FRIDAFORS",
      "FRIDAFORS KYRKH"
    ],
    "lId": "01455",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 56.407777777777774,
      "lon": 14.656666666666666
    }
  },
  {
    "name": "Fridhemsplan T-bana",
    "synonyms": [
      "FRIDHEMSPLAN T-BANA"
    ],
    "lId": "21661",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.331944444444446,
      "lon": 18.029166666666665
    }
  },
  {
    "name": "Fridlevstad",
    "synonyms": [
      "FRIDLEVSTAD"
    ],
    "lId": "10377",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 56.270833333333336,
      "lon": 15.541944444444445
    }
  },
  {
    "name": "Friggesund",
    "synonyms": [
      "FRIGGESUND"
    ],
    "lId": "10378",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 61.897777777777776,
      "lon": 16.54638888888889
    }
  },
  {
    "name": "Frillesås",
    "synonyms": [
      "FRILLESÅS",
      "FRILLESÅS SKOLA"
    ],
    "lId": "00770",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 57.31861111111112,
      "lon": 12.182222222222222
    }
  },
  {
    "name": "Frinnaryd centrum",
    "synonyms": [
      "FRINNARYD CENTRUM",
      "FRINNARYD CM"
    ],
    "lId": "10379",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 57.93388888888889,
      "lon": 14.820277777777777
    }
  },
  {
    "name": "Fristad",
    "synonyms": [
      "FRISTAD",
      "FRISTAD STN"
    ],
    "lId": "00109",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 57.82666666666667,
      "lon": 13.008055555555556
    }
  },
  {
    "name": "Fritsla",
    "synonyms": [
      "FRITSLA",
      "FRITSLA STN"
    ],
    "lId": "00353",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 57.55777777777777,
      "lon": 12.789722222222222
    }
  },
  {
    "name": "Frölunda Positivgatan",
    "synonyms": [
      "FRÖLUNDA POSITIVGATAN"
    ],
    "lId": "20480",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 57.656666666666666,
      "lon": 11.917499999999999
    }
  },
  {
    "name": "Frufällan",
    "synonyms": [
      "FRUFÄLLAN",
      "FRUFÆLLAN"
    ],
    "lId": "12351",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 57.77638888888889,
      "lon": 12.980833333333333
    }
  },
  {
    "name": "Fruängen T-bana",
    "synonyms": [
      "FRUÄNGEN T-BANA",
      "FRUÆNGEN T-BANA"
    ],
    "lId": "21719",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.28583333333333,
      "lon": 17.965
    }
  },
  {
    "name": "Fryksås vägskäl",
    "synonyms": [
      "FRYKSÅS VÄGSKÄL",
      "FRYKSÅS VÆGSKÆL"
    ],
    "lId": "01057",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 61.192499999999995,
      "lon": 14.536111111111111
    }
  },
  {
    "name": "Frykåsen",
    "synonyms": [
      "FRYKÅSEN",
      "FRYKÅSEN STN"
    ],
    "lId": "01419",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.62583333333333,
      "lon": 13.184722222222222
    }
  },
  {
    "name": "Frånö väg 90",
    "synonyms": [
      "FRÅNÖ VÄG 90",
      "FRÅNØ VÆG 90"
    ],
    "lId": "15136",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 62.902499999999996,
      "lon": 17.8325
    }
  },
  {
    "name": "Främmestad",
    "synonyms": [
      "FRÄMMESTAD",
      "FRÆMMESTAD"
    ],
    "lId": "10380",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 58.23111111111111,
      "lon": 12.662777777777778
    }
  },
  {
    "name": "Frändefors skolan",
    "synonyms": [
      "FRÄNDEFORS SKOLAN",
      "FRÆNDEFORS SKOLAN"
    ],
    "lId": "12258",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 58.49194444444444,
      "lon": 12.275277777777779
    }
  },
  {
    "name": "Fränninge affären",
    "synonyms": [
      "FRÄNNINGE AFFÄREN",
      "FRÆNNINGE AFFÆREN"
    ],
    "lId": "16620",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 55.720555555555556,
      "lon": 13.800555555555556
    }
  },
  {
    "name": "Fränsta",
    "synonyms": [
      "FRANSTA",
      "FRÄNSTA",
      "FRÆNSTA"
    ],
    "lId": "00378",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 62.49611111111111,
      "lon": 16.1675
    }
  },
  {
    "name": "Frödinge centrum",
    "synonyms": [
      "FRÖDINGE CENTRUM",
      "FRÖDINGE CM",
      "FRØDINGE CENTRUM",
      "FRØDINGE CM"
    ],
    "lId": "14155",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 57.69944444444444,
      "lon": 16.003888888888888
    }
  },
  {
    "name": "Fröjel",
    "synonyms": [
      "FRÖJEL",
      "FRÖJEL FD AFFÄR",
      "FRØJEL",
      "FRØJEL FD AFFÆR"
    ],
    "lId": "01058",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 57.331944444444446,
      "lon": 18.191388888888888
    }
  },
  {
    "name": "Fröjered kyrka",
    "synonyms": [
      "FRÖJERED KYRKA",
      "FRØJERED KYRKA"
    ],
    "lId": "10383",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 58.24611111111111,
      "lon": 14.016944444444444
    }
  },
  {
    "name": "Frölunda Musikvägen",
    "synonyms": [
      "FRÖLUNDA MUSIKVÄGEN",
      "FRØLUNDA MUSIKVÆGEN"
    ],
    "lId": "25662",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 57.659166666666664,
      "lon": 11.920833333333333
    }
  },
  {
    "name": "Frölunda torg",
    "synonyms": [
      "FRÖLUNDA TORG",
      "FRØLUNDA TORG"
    ],
    "lId": "15565",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 57.651944444444446,
      "lon": 11.909722222222223
    }
  },
  {
    "name": "Frösakull",
    "synonyms": [
      "FRÖSAKULL",
      "FRØSAKULL"
    ],
    "lId": "01457",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 56.67666666666666,
      "lon": 12.729166666666666
    }
  },
  {
    "name": "Fröseke",
    "synonyms": [
      "FRÖSEKE",
      "FRØSEKE"
    ],
    "lId": "01059",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 56.94833333333333,
      "lon": 15.79111111111111
    }
  },
  {
    "name": "Fröslida väg 26",
    "synonyms": [
      "FRÖSLIDA VÄG 26",
      "FRØSLIDA VÆG 26"
    ],
    "lId": "00965",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 56.875277777777775,
      "lon": 13.045833333333333
    }
  },
  {
    "name": "Frösunda",
    "synonyms": [
      "FRÖSUNDA"
    ],
    "lId": "66545",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.37111111111111,
      "lon": 18.01972222222222
    }
  },
  {
    "name": "Frösunda station Vallentuna",
    "synonyms": [
      "FRÖSUNDA STATION VALLENTUNA",
      "FRÖSUNDA STN",
      "FRØSUNDA FRÖSUNDA STATION VALL",
      "FRØSUNDA STN"
    ],
    "lId": "24802",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.62416666666667,
      "lon": 18.17027777777778
    }
  },
  {
    "name": "Frösundavik",
    "synonyms": [
      "FRÖSUNDAVIK"
    ],
    "lId": "46196",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.36888888888889,
      "lon": 18.029444444444444
    }
  },
  {
    "name": "Frövi",
    "synonyms": [
      "FROVI",
      "FRÖVI",
      "FRÖVI STN",
      "FRØVI",
      "FRØVI STN"
    ],
    "lId": "00293",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.4675,
      "lon": 15.36361111111111
    }
  },
  {
    "name": "Fulltofta naturcentrum",
    "synonyms": [
      "FULLTOFTA NATURCENTRUM"
    ],
    "lId": "71542",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 55.88861111111111,
      "lon": 13.640833333333333
    }
  },
  {
    "name": "Funbo kyrka",
    "synonyms": [
      "FUNBO KYRKA"
    ],
    "lId": "01116",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.85472222222222,
      "lon": 17.859444444444446
    }
  },
  {
    "name": "Funäsdalen",
    "synonyms": [
      "FUNÄSDALEN",
      "FUNÄSDALEN BSTN",
      "FUNÆSDALEN",
      "FUNÆSDALEN BSTN"
    ],
    "lId": "00491",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 62.544999999999995,
      "lon": 12.545277777777777
    }
  },
  {
    "name": "Fur sjukhus",
    "synonyms": [
      "FUR SJUKHUS"
    ],
    "lId": "24854",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 56.47555555555556,
      "lon": 15.592500000000001
    }
  },
  {
    "name": "Furuby",
    "synonyms": [
      "FURUBY"
    ],
    "lId": "10388",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 56.858333333333334,
      "lon": 15.035555555555556
    }
  },
  {
    "name": "Furudal",
    "synonyms": [
      "FURUDAL",
      "FURUDAL ISHALL"
    ],
    "lId": "00882",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 61.17055555555555,
      "lon": 15.138055555555555
    }
  },
  {
    "name": "Furulund centrum",
    "synonyms": [
      "FURULUND CENTRUM",
      "FURULUND CM"
    ],
    "lId": "30260",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 55.77611111111111,
      "lon": 13.096944444444444
    }
  },
  {
    "name": "Furusjö Strandvägen",
    "synonyms": [
      "FURUSJÖ STRANDVÄGEN",
      "FURUSJØ STRANDVÆGEN"
    ],
    "lId": "04230",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 57.92833333333333,
      "lon": 13.960555555555555
    }
  },
  {
    "name": "Furusund",
    "synonyms": [
      "FURUSUND",
      "FURUSUND FÄRJEL",
      "FURUSUND FÆRJEL"
    ],
    "lId": "01060",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.66305555555555,
      "lon": 18.92527777777778
    }
  },
  {
    "name": "Furuvik",
    "synonyms": [
      "FURUVIK",
      "FURUVIK STN"
    ],
    "lId": "01061",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 60.651111111111106,
      "lon": 17.331666666666667
    }
  },
  {
    "name": "Fyllinge",
    "synonyms": [
      "FYLLINGE"
    ],
    "lId": "33407",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 56.645833333333336,
      "lon": 12.936388888888889
    }
  },
  {
    "name": "Fågelmara",
    "synonyms": [
      "FÅGELMARA",
      "FÅGELMARA FELIX"
    ],
    "lId": "01062",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 56.26,
      "lon": 15.948611111111111
    }
  },
  {
    "name": "Fågelfors centrum",
    "synonyms": [
      "FAGELFORS CENTRUM",
      "FAGELFORS CM",
      "FÅGELFORS CENTRUM",
      "FÅGELFORS CM"
    ],
    "lId": "14164",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 57.20277777777778,
      "lon": 15.843611111111112
    }
  },
  {
    "name": "Fågelsjö vägskäl",
    "synonyms": [
      "FÅGELSJÖ VSK",
      "FÅGELSJÖ VÄGSKÄL",
      "FÅGELSJØ VSK",
      "FÅGELSJØ VÆGSKÆL"
    ],
    "lId": "29477",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 61.79361111111111,
      "lon": 14.695555555555556
    }
  },
  {
    "name": "Fågelsta skola",
    "synonyms": [
      "FÅGELSTA SKOLA"
    ],
    "lId": "25025",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 58.45722222222223,
      "lon": 15.045277777777777
    }
  },
  {
    "name": "Fåker Olle Jänsvägen",
    "synonyms": [
      "FÅKER OLLE JÄNSVÄGEN",
      "FÅKER OLLE JÆNSVÆGEN"
    ],
    "lId": "18295",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 62.99388888888889,
      "lon": 14.57611111111111
    }
  },
  {
    "name": "Fårbo",
    "synonyms": [
      "FÅRBO",
      "FÅRBO E22"
    ],
    "lId": "14166",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 57.382777777777775,
      "lon": 16.481388888888887
    }
  },
  {
    "name": "Fårhult station",
    "synonyms": [
      "FÅRHULT STATION",
      "FÅRHULT STN"
    ],
    "lId": "24958",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 57.737500000000004,
      "lon": 16.42
    }
  },
  {
    "name": "Fårö",
    "synonyms": [
      "FÅRÖ",
      "FÅRÖ KYRKA",
      "FÅRØ",
      "FÅRØ KYRKA"
    ],
    "lId": "00919",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 57.914722222222224,
      "lon": 19.13111111111111
    }
  },
  {
    "name": "Fårösund Kronhagsvägen",
    "synonyms": [
      "FÅRÖSUND KRONHAGSVÄGEN",
      "FÅRÖSUND KRONHV",
      "FÅRØSUND KRONHAGSVÆGEN",
      "FÅRØSUND KRONHV"
    ],
    "lId": "10400",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 57.86277777777778,
      "lon": 19.055
    }
  },
  {
    "name": "Fällsvik",
    "synonyms": [
      "FÄLLSVIK",
      "FÆLLSVIK"
    ],
    "lId": "29042",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 62.85916666666667,
      "lon": 18.352777777777778
    }
  },
  {
    "name": "Färentuna kyrka",
    "synonyms": [
      "FÄRENTUNA KYRKA",
      "FÆRENTUNA KYRKA"
    ],
    "lId": "01063",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.39194444444444,
      "lon": 17.654999999999998
    }
  },
  {
    "name": "Färgelanda",
    "synonyms": [
      "FÄRGELANDA",
      "FÄRGELANDA CM",
      "FÆRGELANDA",
      "FÆRGELANDA CM"
    ],
    "lId": "00986",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 58.568333333333335,
      "lon": 11.995277777777776
    }
  },
  {
    "name": "Färila",
    "synonyms": [
      "FÄRILA",
      "FÄRILA BSTN",
      "FÆRILA",
      "FÆRILA BSTN"
    ],
    "lId": "00460",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 61.79805555555556,
      "lon": 15.838611111111112
    }
  },
  {
    "name": "Färjestaden",
    "synonyms": [
      "FÄRJESTADEN",
      "FÄRJESTADEN BST",
      "FÆRJESTADEN",
      "FÆRJESTADEN BST"
    ],
    "lId": "00911",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 56.649166666666666,
      "lon": 16.46472222222222
    }
  },
  {
    "name": "Färjestaden Träffpunkt Öland",
    "synonyms": [
      "FÄRJESTADEN TRÄFFPUNKT ÖLAND",
      "FÆRJESTADEN TRÆFFPUNKT ØLAND"
    ],
    "lId": "14402",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 56.665277777777774,
      "lon": 16.484722222222224
    }
  },
  {
    "name": "Färlöv Hamiltons väg",
    "synonyms": [
      "FÄRLÖV HAMILTONS VÄG",
      "FÆRLØV HAMILTONS VÆG"
    ],
    "lId": "30288",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 56.07277777777778,
      "lon": 14.086944444444445
    }
  },
  {
    "name": "Färna",
    "synonyms": [
      "FÄRNA",
      "FÆRNA"
    ],
    "lId": "10404",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.780833333333334,
      "lon": 15.859166666666667
    }
  },
  {
    "name": "Färnäs gamla posten",
    "synonyms": [
      "FÄRNÄS GAMLA POSTEN",
      "FÄRNÄS GLA POST",
      "FÆRNÆS GAMLA POSTEN",
      "FÆRNÆS GLA POST"
    ],
    "lId": "13089",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 61.000277777777775,
      "lon": 14.63
    }
  },
  {
    "name": "Föllinge",
    "synonyms": [
      "FÖLLINGE",
      "FØLLINGE"
    ],
    "lId": "00420",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 63.669999999999995,
      "lon": 14.612777777777778
    }
  },
  {
    "name": "Förslöv",
    "synonyms": [
      "FÖRSLÖV",
      "FÖRSLÖV SANDBAC",
      "FØRSLØV",
      "FØRSLØV SANDBAC"
    ],
    "lId": "00711",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 56.34777777777778,
      "lon": 12.816666666666666
    }
  },
  {
    "name": "Förslöv station",
    "synonyms": [
      "FÖRSLÖV STATION"
    ],
    "lId": "01612",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 56.35527777777778,
      "lon": 12.801111111111112
    }
  },
  {
    "name": "Gagnef station",
    "synonyms": [
      "GAGNEF STATION",
      "GAGNEF STN"
    ],
    "lId": "00322",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 60.59861111111111,
      "lon": 15.081111111111111
    }
  },
  {
    "name": "Galoppfältet",
    "synonyms": [
      "GALOPPFÄLTET",
      "GALOPPFÆLTET"
    ],
    "lId": "24798",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.446666666666665,
      "lon": 18.083333333333332
    }
  },
  {
    "name": "Gallsäter",
    "synonyms": [
      "GALLSÄTER",
      "GALLSÆTER"
    ],
    "lId": "15140",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 62.93,
      "lon": 18.084999999999997
    }
  },
  {
    "name": "Galtström",
    "synonyms": [
      "GALTSTRÖM",
      "GALTSTRØM"
    ],
    "lId": "15141",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 62.16444444444444,
      "lon": 17.485
    }
  },
  {
    "name": "Gamla stan T-bana",
    "synonyms": [
      "GAMLA STAN T",
      "GAMLA STAN T-BANA"
    ],
    "lId": "21653",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.323055555555555,
      "lon": 18.0675
    }
  },
  {
    "name": "Gamleby",
    "synonyms": [
      "GAMLEBY",
      "GAMLEBY STN"
    ],
    "lId": "00404",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 57.89694444444444,
      "lon": 16.41
    }
  },
  {
    "name": "Gammalstorp",
    "synonyms": [
      "GAMMALSTORP"
    ],
    "lId": "10408",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 56.10388888888889,
      "lon": 14.618611111111111
    }
  },
  {
    "name": "Gammelgarn",
    "synonyms": [
      "GAMMELGARN",
      "GAMMELGARN KA"
    ],
    "lId": "01064",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 57.405,
      "lon": 18.803611111111113
    }
  },
  {
    "name": "Gammelsta",
    "synonyms": [
      "GAMMELSTA"
    ],
    "lId": "20915",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 58.7475,
      "lon": 16.619444444444444
    }
  },
  {
    "name": "Gantofta",
    "synonyms": [
      "GANTOFTA",
      "GANTOFTA STN"
    ],
    "lId": "01555",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 55.99027777777778,
      "lon": 12.805555555555557
    }
  },
  {
    "name": "Garda",
    "synonyms": [
      "GARDA",
      "GARDA AFFÄR",
      "GARDA AFFÆR"
    ],
    "lId": "01065",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 57.31472222222222,
      "lon": 18.58111111111111
    }
  },
  {
    "name": "Gargnäs",
    "synonyms": [
      "GARGNÄS",
      "GARGNÆS"
    ],
    "lId": "01117",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 65.31277777777777,
      "lon": 17.963055555555556
    }
  },
  {
    "name": "Garpenberg centrum",
    "synonyms": [
      "GARPENBERG CENTRUM"
    ],
    "lId": "46623",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 60.31666666666667,
      "lon": 16.195
    }
  },
  {
    "name": "Garpenberg Herrgården",
    "synonyms": [
      "GARPENBERG HERRGÅRDEN"
    ],
    "lId": "25177",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 60.28388888888889,
      "lon": 16.20111111111111
    }
  },
  {
    "name": "Garphyttan",
    "synonyms": [
      "GARPHYTTAN",
      "GARPHYTTAN KVAR"
    ],
    "lId": "00431",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.30777777777777,
      "lon": 14.940555555555555
    }
  },
  {
    "name": "Geijersholm",
    "synonyms": [
      "GEIJERSHOLM"
    ],
    "lId": "10420",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 60.06583333333333,
      "lon": 13.7225
    }
  },
  {
    "name": "Gemla station",
    "synonyms": [
      "GEMLA STATION",
      "GEMLA STN"
    ],
    "lId": "00388",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 56.87,
      "lon": 14.64472222222222
    }
  },
  {
    "name": "Genarp",
    "synonyms": [
      "GENARP",
      "GENARP BSTN"
    ],
    "lId": "01460",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 55.59916666666667,
      "lon": 13.4
    }
  },
  {
    "name": "Genevad",
    "synonyms": [
      "GENEVAD"
    ],
    "lId": "17049",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 56.56861111111112,
      "lon": 13.027222222222223
    }
  },
  {
    "name": "Geografiska polcirkeln",
    "synonyms": [
      "GEOGR POLCIRKEL",
      "GEOGRAFISKA POLCIRKELN"
    ],
    "lId": "25062",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 66.55638888888889,
      "lon": 19.91861111111111
    }
  },
  {
    "name": "Gesunda",
    "synonyms": [
      "GESUNDA"
    ],
    "lId": "01118",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 60.88583333333333,
      "lon": 14.545
    }
  },
  {
    "name": "Getinge",
    "synonyms": [
      "GETINGE",
      "GETINGE STN"
    ],
    "lId": "00269",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 56.818333333333335,
      "lon": 12.730555555555556
    }
  },
  {
    "name": "Gevsjön",
    "synonyms": [
      "GEVSJÖN",
      "GEVSJØN"
    ],
    "lId": "13294",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 63.36138888888889,
      "lon": 12.695277777777777
    }
  },
  {
    "name": "Gideå livs",
    "synonyms": [
      "GIDEÅ LIVS"
    ],
    "lId": "15142",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 63.48111111111111,
      "lon": 18.97138888888889
    }
  },
  {
    "name": "Gillhov",
    "synonyms": [
      "GILLHOV"
    ],
    "lId": "13302",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 62.66361111111111,
      "lon": 14.749444444444444
    }
  },
  {
    "name": "Gillstad",
    "synonyms": [
      "GILLSTAD",
      "GILLSTAD VÄG 44",
      "GILLSTAD VÆG 44"
    ],
    "lId": "20225",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 58.44166666666666,
      "lon": 12.955
    }
  },
  {
    "name": "Gimgöl",
    "synonyms": [
      "GIMGÖL",
      "GIMGØL"
    ],
    "lId": "10428",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.1675,
      "lon": 15.95611111111111
    }
  },
  {
    "name": "Gimo busstation",
    "synonyms": [
      "GIMO BSTN",
      "GIMO BUSSTATION"
    ],
    "lId": "00661",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 60.17638888888889,
      "lon": 18.188055555555557
    }
  },
  {
    "name": "Gislaved",
    "synonyms": [
      "GISLAVED",
      "GISLAVED BSTN"
    ],
    "lId": "00624",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 57.30472222222222,
      "lon": 13.543055555555556
    }
  },
  {
    "name": "Gislövs läge",
    "synonyms": [
      "GISLÖVS LÄGE",
      "GISLØVS LÆGE"
    ],
    "lId": "16631",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 55.35666666666667,
      "lon": 13.23611111111111
    }
  },
  {
    "name": "Gistad Skiffervägen",
    "synonyms": [
      "GISTAD SKIFFERVÄGEN",
      "GISTAD SKIFFERVÆGEN"
    ],
    "lId": "10432",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 58.467777777777776,
      "lon": 15.892777777777777
    }
  },
  {
    "name": "Gladsax centrum",
    "synonyms": [
      "GLADSAX CENTRUM"
    ],
    "lId": "04153",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 55.56222222222222,
      "lon": 14.287222222222223
    }
  },
  {
    "name": "Glamsta skola",
    "synonyms": [
      "GLAMSTA SKOLA"
    ],
    "lId": "19727",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 61.39555555555555,
      "lon": 16.834999999999997
    }
  },
  {
    "name": "Glanshammar",
    "synonyms": [
      "GLANSHAMMAR",
      "GLANSHAMMAR KA"
    ],
    "lId": "01067",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.318333333333335,
      "lon": 15.400277777777777
    }
  },
  {
    "name": "Glava Macken",
    "synonyms": [
      "GLAVA MACKEN"
    ],
    "lId": "10434",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.54833333333333,
      "lon": 12.56388888888889
    }
  },
  {
    "name": "Glemmingebro V",
    "synonyms": [
      "GLEMMINGEBRO V"
    ],
    "lId": "16632",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 55.44972222222222,
      "lon": 14.019722222222223
    }
  },
  {
    "name": "Glimåkra",
    "synonyms": [
      "GLIMÅKRA",
      "GLIMÅKRA BSTN"
    ],
    "lId": "01068",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 56.305,
      "lon": 14.135555555555555
    }
  },
  {
    "name": "Glissjöberg vägskäl Mosätt",
    "synonyms": [
      "GLISSJÖBERG VSK",
      "GLISSJÖBERG VÄGSKÄL MOSÄTT",
      "GLISSJØBERG VSK",
      "GLISSJØBERG VÆGSKÆL MOSÆTT"
    ],
    "lId": "29900",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 62.126111111111115,
      "lon": 14.06861111111111
    }
  },
  {
    "name": "Globen T-bana",
    "synonyms": [
      "GLOBEN T-BANA"
    ],
    "lId": "21706",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.29416666666666,
      "lon": 18.07777777777778
    }
  },
  {
    "name": "Glommen",
    "synonyms": [
      "GLOMMEN"
    ],
    "lId": "33797",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 56.930277777777775,
      "lon": 12.365
    }
  },
  {
    "name": "Glommersträsk",
    "synonyms": [
      "GLOMMERSTRÄSK",
      "GLOMMERSTRÆSK"
    ],
    "lId": "01069",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 65.26083333333334,
      "lon": 19.638055555555557
    }
  },
  {
    "name": "Glumslöv",
    "synonyms": [
      "GLUMSLÖV",
      "GLUMSLØV"
    ],
    "lId": "01558",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 55.94555555555555,
      "lon": 12.811944444444444
    }
  },
  {
    "name": "Glyxnäs",
    "synonyms": [
      "GLYXNÄS",
      "GLYXNÆS"
    ],
    "lId": "20980",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.58777777777778,
      "lon": 18.853611111111114
    }
  },
  {
    "name": "Gläborg",
    "synonyms": [
      "GLÄBORG",
      "GLÆBORG"
    ],
    "lId": "16207",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 58.48166666666667,
      "lon": 11.571666666666667
    }
  },
  {
    "name": "Glömminge",
    "synonyms": [
      "GLÖMMINGE",
      "GLØMMINGE"
    ],
    "lId": "14177",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 56.717777777777776,
      "lon": 16.53527777777778
    }
  },
  {
    "name": "Glössbo affären",
    "synonyms": [
      "GLÖSSBO AFFÄREN",
      "GLØSSBO AFFÆREN"
    ],
    "lId": "10440",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 61.350833333333334,
      "lon": 16.700555555555553
    }
  },
  {
    "name": "Glöte",
    "synonyms": [
      "GLÖTE",
      "GLØTE"
    ],
    "lId": "17767",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 62.102222222222224,
      "lon": 13.498888888888889
    }
  },
  {
    "name": "Gnarp",
    "synonyms": [
      "GNARP",
      "GNARP STN"
    ],
    "lId": "00602",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 62.05555555555555,
      "lon": 17.24416666666667
    }
  },
  {
    "name": "Gnarp Statoil",
    "synonyms": [
      "GNARP STATOIL"
    ],
    "lId": "23131",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 62.05694444444444,
      "lon": 17.266944444444444
    }
  },
  {
    "name": "Gnesta",
    "synonyms": [
      "GNESTA",
      "GNESTA STN"
    ],
    "lId": "00694",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.04861111111111,
      "lon": 17.31138888888889
    }
  },
  {
    "name": "Gnosjö",
    "synonyms": [
      "GNOSJO",
      "GNOSJÖ",
      "GNOSJÖ STN",
      "GNOSJØ",
      "GNOSJØ STN"
    ],
    "lId": "00112",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 57.35805555555556,
      "lon": 13.735277777777776
    }
  },
  {
    "name": "Godegård affären",
    "synonyms": [
      "GODEGÅRD AFFÄREN",
      "GODEGÅRD AFFÆREN"
    ],
    "lId": "10445",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 58.74861111111111,
      "lon": 15.164166666666667
    }
  },
  {
    "name": "Gonäs",
    "synonyms": [
      "GONÄS",
      "GONÆS"
    ],
    "lId": "12962",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 60.14666666666667,
      "lon": 15.09388888888889
    }
  },
  {
    "name": "Gottne vägskäl",
    "synonyms": [
      "GOTTNE VÄGSKÄL",
      "GOTTNE VÆGSKÆL"
    ],
    "lId": "15146",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 63.42972222222222,
      "lon": 18.425
    }
  },
  {
    "name": "Gottröra",
    "synonyms": [
      "GOTTRÖRA",
      "GOTTRÖRA KYRKA",
      "GOTTRØRA",
      "GOTTRØRA KYRKA"
    ],
    "lId": "01120",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.73916666666667,
      "lon": 18.15861111111111
    }
  },
  {
    "name": "Gottåsa vägskäl väg 23",
    "synonyms": [
      "GOTTÅSA VSK V23",
      "GOTTÅSA VÄGSKÄL VÄG 23"
    ],
    "lId": "23206",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 56.73305555555556,
      "lon": 14.486944444444443
    }
  },
  {
    "name": "Grangärde torget",
    "synonyms": [
      "GRANGÄRDE TORGET",
      "GRANGÆRDE TORGET"
    ],
    "lId": "01121",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 60.261944444444445,
      "lon": 14.977500000000001
    }
  },
  {
    "name": "Granhammar Kungsör",
    "synonyms": [
      "GRANHAMMAR KUNGSÖR"
    ],
    "lId": "45188",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.41027777777778,
      "lon": 16.035
    }
  },
  {
    "name": "Granhammar Livgardet",
    "synonyms": [
      "GRANHAMMAR LIVGARDET"
    ],
    "lId": "01176",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.515,
      "lon": 17.769444444444442
    }
  },
  {
    "name": "Grankullavik",
    "synonyms": [
      "GRANKULLAVIK"
    ],
    "lId": "00915",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 57.33361111111111,
      "lon": 17.097777777777775
    }
  },
  {
    "name": "Granö",
    "synonyms": [
      "GRANÖ",
      "GRANØ"
    ],
    "lId": "01071",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 64.24722222222222,
      "lon": 19.31722222222222
    }
  },
  {
    "name": "Grebbestad",
    "synonyms": [
      "GREBBESTAD",
      "GREBBESTAD BSTN"
    ],
    "lId": "00292",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 58.69194444444444,
      "lon": 11.25361111111111
    }
  },
  {
    "name": "Grebo",
    "synonyms": [
      "GREBO",
      "GREBO AFFÄREN",
      "GREBO AFFÆREN"
    ],
    "lId": "01462",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 58.305277777777775,
      "lon": 15.86888888888889
    }
  },
  {
    "name": "Grevie",
    "synonyms": [
      "GREVIE"
    ],
    "lId": "15353",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 56.39138888888889,
      "lon": 12.78277777777778
    }
  },
  {
    "name": "Gribbylund",
    "synonyms": [
      "GRIBBYLUND"
    ],
    "lId": "01177",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.462500000000006,
      "lon": 18.09111111111111
    }
  },
  {
    "name": "Grillby skola",
    "synonyms": [
      "GRILLBY SKOLA",
      "GRILLBY SKOLAN"
    ],
    "lId": "25049",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.62583333333333,
      "lon": 17.253055555555555
    }
  },
  {
    "name": "Grillom",
    "synonyms": [
      "GRILLOM"
    ],
    "lId": "15148",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 63.15138888888889,
      "lon": 17.688333333333333
    }
  },
  {
    "name": "Grimslöv Aspvägen",
    "synonyms": [
      "GRIMSLÖV ASPVÄGEN",
      "GRIMSLØV ASPVÆGEN"
    ],
    "lId": "10456",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 56.73722222222222,
      "lon": 14.538333333333334
    }
  },
  {
    "name": "Grimstorp station",
    "synonyms": [
      "GRIMSTORP STATION",
      "GRIMSTORP STN"
    ],
    "lId": "04060",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 57.55777777777777,
      "lon": 14.697777777777778
    }
  },
  {
    "name": "Grimsås",
    "synonyms": [
      "GRIMSÅS"
    ],
    "lId": "12078",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 57.48388888888889,
      "lon": 13.551944444444445
    }
  },
  {
    "name": "Grinda Norra Brygga",
    "synonyms": [
      "GRINDA N BRYGGA",
      "GRINDA NORRA BRYGGA"
    ],
    "lId": "24315",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.41888888888889,
      "lon": 18.558611111111112
    }
  },
  {
    "name": "Grinda Södra brygga",
    "synonyms": [
      "GRINDA S BRYGGA",
      "GRINDA SÖDRA BRYGGA",
      "GRINDA SØDRA BRYGGA"
    ],
    "lId": "24301",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.407222222222224,
      "lon": 18.553055555555556
    }
  },
  {
    "name": "Gripenberg station",
    "synonyms": [
      "GRIPENBERG STATION",
      "GRIPENBERG STN"
    ],
    "lId": "04050",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 57.99166666666667,
      "lon": 14.8525
    }
  },
  {
    "name": "Grisslehamn",
    "synonyms": [
      "GRISSLEHAMN",
      "GRISSLEHAMN F"
    ],
    "lId": "00695",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 60.09916666666667,
      "lon": 18.81361111111111
    }
  },
  {
    "name": "Grums station",
    "synonyms": [
      "GRUMS STATION",
      "GRUMS STN"
    ],
    "lId": "00217",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.35277777777778,
      "lon": 13.11361111111111
    }
  },
  {
    "name": "Grums Nyängen",
    "synonyms": [
      "GRUMS NYÄNGEN"
    ],
    "lId": "49131",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.3675,
      "lon": 13.143055555555556
    }
  },
  {
    "name": "Grundsund",
    "synonyms": [
      "GRUNDSUND"
    ],
    "lId": "00358",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 58.213055555555556,
      "lon": 11.421666666666667
    }
  },
  {
    "name": "Grycksbo Drottningplan",
    "synonyms": [
      "GRYCKSBO DROTTNINGPLAN",
      "GRYCKSBO DROTTP"
    ],
    "lId": "00644",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 60.6875,
      "lon": 15.48472222222222
    }
  },
  {
    "name": "Gryt Östergötland",
    "synonyms": [
      "GRYT",
      "GRYT ÖSTERGÖTLAND",
      "GRYT ÖSTERGÖTLL",
      "GRYT ØSTERGØTLAND",
      "GRYT ØSTERGØTLL"
    ],
    "lId": "00843",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 58.18583333333333,
      "lon": 16.803333333333335
    }
  },
  {
    "name": "Grytgöl centrum",
    "synonyms": [
      "GRYTGÖL CENTRUM",
      "GRYTGØL CENTRUM"
    ],
    "lId": "20347",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 58.80333333333333,
      "lon": 15.557222222222222
    }
  },
  {
    "name": "Grythyttan station",
    "synonyms": [
      "GRYTHYTTAN STATION",
      "GRYTHYTTAN STN"
    ],
    "lId": "00482",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.70416666666667,
      "lon": 14.530277777777778
    }
  },
  {
    "name": "Grythyttan Måltidens hus",
    "synonyms": [
      "GRYTHYTTAN MHUS",
      "GRYTHYTTAN MÅLTIDENS HUS"
    ],
    "lId": "21035",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.70583333333334,
      "lon": 14.544166666666667
    }
  },
  {
    "name": "Gryttjesbo",
    "synonyms": [
      "GRYTTJESBO"
    ],
    "lId": "18960",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 61.805,
      "lon": 16.27
    }
  },
  {
    "name": "Gråbo",
    "synonyms": [
      "GRÅBO",
      "GRÅBO BSTN"
    ],
    "lId": "00513",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 57.836666666666666,
      "lon": 12.298333333333334
    }
  },
  {
    "name": "Gräfsnäs",
    "synonyms": [
      "GRÄFSNÄS",
      "GRÆFSNÆS"
    ],
    "lId": "12528",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 58.08527777777778,
      "lon": 12.493611111111111
    }
  },
  {
    "name": "Grällsta",
    "synonyms": [
      "GRÄLLSTA",
      "GRÆLLSTA"
    ],
    "lId": "18029",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.856944444444444,
      "lon": 16.53666666666667
    }
  },
  {
    "name": "Gröndal",
    "synonyms": [
      "GRÖNDAL",
      "GRØNDAL"
    ],
    "lId": "24923",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.31583333333333,
      "lon": 18.011666666666667
    }
  },
  {
    "name": "Grängesberg",
    "synonyms": [
      "GRANGESBERG",
      "GRÄNGESBERG",
      "GRÄNGESBERG STN",
      "GRÆNGESBERG",
      "GRÆNGESBERG STN"
    ],
    "lId": "00162",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 60.07638888888889,
      "lon": 15.005277777777778
    }
  },
  {
    "name": "Grängshyttan",
    "synonyms": [
      "GRÄNGSHYTTAN",
      "GRÆNGSHYTTAN"
    ],
    "lId": "10465",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.72555555555556,
      "lon": 14.789166666666667
    }
  },
  {
    "name": "Gränna",
    "synonyms": [
      "GRÄNNA",
      "GRÄNNA HAMN",
      "GRÆNNA",
      "GRÆNNA HAMN"
    ],
    "lId": "00607",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 58.028888888888886,
      "lon": 14.455833333333333
    }
  },
  {
    "name": "Gränna Galgen",
    "synonyms": [
      "GRÄNNA GALGEN"
    ],
    "lId": "25491",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 58.00222222222222,
      "lon": 14.451944444444443
    }
  },
  {
    "name": "Grönskåra",
    "synonyms": [
      "GRÖNSKÅRA",
      "GRØNSKÅRA"
    ],
    "lId": "14195",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 57.075,
      "lon": 15.735555555555555
    }
  },
  {
    "name": "Gränum skola",
    "synonyms": [
      "GRÄNUM SKOLA",
      "GRÆNUM SKOLA"
    ],
    "lId": "25051",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 56.228611111111114,
      "lon": 14.604166666666666
    }
  },
  {
    "name": "Gräsmark",
    "synonyms": [
      "GRÄSMARK",
      "GRÄSMARK KYRKA",
      "GRÆSMARK",
      "GRÆSMARK KYRKA"
    ],
    "lId": "00806",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.94583333333333,
      "lon": 12.911944444444444
    }
  },
  {
    "name": "Grästorp",
    "synonyms": [
      "GRASTORP",
      "GRÄSTORP",
      "GRÄSTORP STN",
      "GRÆSTORP",
      "GRÆSTORP STN"
    ],
    "lId": "00107",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 58.334722222222226,
      "lon": 12.684722222222222
    }
  },
  {
    "name": "Gräsö färjeläge",
    "synonyms": [
      "GRÄSÖ FÄRJELÄGE",
      "GRÆSØ FÆRJELÆGE"
    ],
    "lId": "01122",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 60.34638888888889,
      "lon": 18.461666666666666
    }
  },
  {
    "name": "Grödby",
    "synonyms": [
      "GRÖDBY",
      "GRÖDBY TROLLSTA",
      "GRØDBY",
      "GRØDBY TROLLSTA"
    ],
    "lId": "01175",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.05333333333333,
      "lon": 17.86888888888889
    }
  },
  {
    "name": "Gröndalsviken",
    "synonyms": [
      "GRÖNDALSVIKEN",
      "GRØNDALSVIKEN"
    ],
    "lId": "46004",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 58.89888888888889,
      "lon": 17.93166666666667
    }
  },
  {
    "name": "Grönhögen",
    "synonyms": [
      "GRÖNHÖGEN",
      "GRØNHØGEN"
    ],
    "lId": "01072",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 56.26833333333333,
      "lon": 16.40111111111111
    }
  },
  {
    "name": "Grönklitt",
    "synonyms": [
      "GRÖNKLITT",
      "GRØNKLITT"
    ],
    "lId": "00645",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 61.2075,
      "lon": 14.539166666666667
    }
  },
  {
    "name": "Gröstorp centrum",
    "synonyms": [
      "GRÖSTORP CENTRUM",
      "GRÖSTORP CM"
    ],
    "lId": "31209",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 55.55416666666667,
      "lon": 14.314444444444446
    }
  },
  {
    "name": "Grötingen",
    "synonyms": [
      "GRÖTINGEN",
      "GRØTINGEN"
    ],
    "lId": "13257",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 62.8525,
      "lon": 15.4825
    }
  },
  {
    "name": "Grövelsjön fjällstation",
    "synonyms": [
      "GROVELSJON FJALLSTATION",
      "GROVELSJON FJST",
      "GRÖVELSJÖN FJST",
      "GRÖVELSJÖN FJÄLLSTATION",
      "GRØVELSJØN FJST",
      "GRØVELSJØN FJÆLLSTATION"
    ],
    "lId": "00574",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 62.09861111111111,
      "lon": 12.312777777777779
    }
  },
  {
    "name": "Gualöv",
    "synonyms": [
      "GUALÖV",
      "GUALØV"
    ],
    "lId": "23388",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 56.04527777777778,
      "lon": 14.427777777777777
    }
  },
  {
    "name": "Gubbo",
    "synonyms": [
      "GUBBO"
    ],
    "lId": "12941",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 60.17611111111111,
      "lon": 15.322222222222223
    }
  },
  {
    "name": "Gubbängen T-bana",
    "synonyms": [
      "GUBBÄNGEN T-BANA",
      "GUBBÆNGEN T-BANA"
    ],
    "lId": "21699",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.26277777777778,
      "lon": 18.081944444444446
    }
  },
  {
    "name": "Gudå",
    "synonyms": [
      "GUDA",
      "GUDÅ"
    ],
    "lId": "01213",
    "prio": 0,
    "pId": "076",
    "pos": {
      "lat": 63.44166666666666,
      "lon": 11.585555555555556
    }
  },
  {
    "name": "Guldsmedshyttan kiosken",
    "synonyms": [
      "GULDSMEDSHYTTAN KIOSKEN"
    ],
    "lId": "10477",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.69916666666666,
      "lon": 15.100555555555555
    }
  },
  {
    "name": "Gullabo",
    "synonyms": [
      "GULLABO"
    ],
    "lId": "14189",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 56.46472222222223,
      "lon": 15.805277777777778
    }
  },
  {
    "name": "Gullaskruv",
    "synonyms": [
      "GULLASKRUV"
    ],
    "lId": "14182",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 56.875,
      "lon": 15.677222222222222
    }
  },
  {
    "name": "Gullbrandstorp",
    "synonyms": [
      "GULLBRANDSTORP"
    ],
    "lId": "00267",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 56.70416666666667,
      "lon": 12.7325
    }
  },
  {
    "name": "Gullbranna",
    "synonyms": [
      "GULLBRANNA"
    ],
    "lId": "01073",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 56.586111111111116,
      "lon": 12.945277777777777
    }
  },
  {
    "name": "Gulleråsen Sanden",
    "synonyms": [
      "GULLERÅSEN SANDEN"
    ],
    "lId": "25409",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 61.07916666666667,
      "lon": 15.180833333333332
    }
  },
  {
    "name": "Gullholmen",
    "synonyms": [
      "GULLHOLMEN",
      "GULLHOLMEN HAMN"
    ],
    "lId": "01123",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 58.178888888888885,
      "lon": 11.40388888888889
    }
  },
  {
    "name": "Gullmarsplan T-bana",
    "synonyms": [
      "GULLMARSPLAN T",
      "GULLMARSPLAN T-BANA",
      "GULLMARSPLAN TB"
    ],
    "lId": "21705",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.29888888888889,
      "lon": 18.080555555555556
    }
  },
  {
    "name": "Gullringen",
    "synonyms": [
      "GULLRINGEN",
      "GULLRINGEN STN"
    ],
    "lId": "00543",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 57.802499999999995,
      "lon": 15.703333333333333
    }
  },
  {
    "name": "Gullspång busstation",
    "synonyms": [
      "GULLSPÅNG BSTN",
      "GULLSPÅNG BUSSTATION"
    ],
    "lId": "00223",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 58.98583333333333,
      "lon": 14.09888888888889
    }
  },
  {
    "name": "Gullspång Mariestadsvägen",
    "synonyms": [
      "GULLSPÅNG MARIESTADSVÄGEN"
    ],
    "lId": "62068",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 58.980000000000004,
      "lon": 14.084722222222222
    }
  },
  {
    "name": "Gullvalla",
    "synonyms": [
      "GULLVALLA"
    ],
    "lId": "10484",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.91555555555556,
      "lon": 16.436944444444446
    }
  },
  {
    "name": "Gunnarn",
    "synonyms": [
      "GUNNARN"
    ],
    "lId": "00969",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 65.01027777777777,
      "lon": 17.689444444444444
    }
  },
  {
    "name": "Gunnarn E12",
    "synonyms": [
      "GUNNARN E12"
    ],
    "lId": "14048",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 65.00611111111111,
      "lon": 17.67527777777778
    }
  },
  {
    "name": "Gunnarskog Stommen",
    "synonyms": [
      "GUNNARSKOG STOMMEN"
    ],
    "lId": "10489",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.81805555555556,
      "lon": 12.566666666666666
    }
  },
  {
    "name": "Gunnebo",
    "synonyms": [
      "GUNNEBO",
      "GUNNEBO CENTRUM"
    ],
    "lId": "00921",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 57.72,
      "lon": 16.531944444444445
    }
  },
  {
    "name": "Gunnesbo",
    "synonyms": [
      "GUNNESBO",
      "GUNNESBO STN"
    ],
    "lId": "00941",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 55.726111111111116,
      "lon": 13.168055555555554
    }
  },
  {
    "name": "Gunnilbo vägskäl",
    "synonyms": [
      "GUNNILBO VÄGSKÄL"
    ],
    "lId": "44819",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.80222222222222,
      "lon": 15.843333333333334
    }
  },
  {
    "name": "Gunsta",
    "synonyms": [
      "GUNSTA"
    ],
    "lId": "01189",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.85527777777778,
      "lon": 17.83222222222222
    }
  },
  {
    "name": "Gusselby skola",
    "synonyms": [
      "GUSSELBY SKOLA",
      "GUSSELBY SKOLAN"
    ],
    "lId": "21175",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.64611111111111,
      "lon": 15.220833333333333
    }
  },
  {
    "name": "Gustafs kyrka",
    "synonyms": [
      "GUSTAFS KYRKA"
    ],
    "lId": "01465",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 60.4125,
      "lon": 15.609444444444444
    }
  },
  {
    "name": "Huddinge Gustav Adolfsvägen",
    "synonyms": [
      "HUDDINGE GUSTAV ADOLFSVÄGEN"
    ],
    "lId": "68998",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.237500000000004,
      "lon": 17.912499999999998
    }
  },
  {
    "name": "Gustavsberg",
    "synonyms": [
      "GUSTAVSBERG",
      "GUSTAVSBERG CM"
    ],
    "lId": "00698",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.32638888888889,
      "lon": 18.391111111111112
    }
  },
  {
    "name": "Gustavsfors",
    "synonyms": [
      "GUSTAVSFORS",
      "GUSTAVSFORS AFF"
    ],
    "lId": "00987",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.19083333333333,
      "lon": 12.109722222222222
    }
  },
  {
    "name": "Gusum",
    "synonyms": [
      "GUSUM",
      "GUSUM CENTRUM"
    ],
    "lId": "00844",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 58.265,
      "lon": 16.497222222222224
    }
  },
  {
    "name": "Gysinge Brukshandel",
    "synonyms": [
      "GYSINGE BRUKSHANDEL",
      "GYSINGE BRUKSHL"
    ],
    "lId": "00483",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 60.28944444444444,
      "lon": 16.885277777777777
    }
  },
  {
    "name": "Gyttorp torget",
    "synonyms": [
      "GYTTORP TORGET"
    ],
    "lId": "01124",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.505833333333335,
      "lon": 14.965277777777777
    }
  },
  {
    "name": "Gålsjöbruk",
    "synonyms": [
      "GÅLSJÖBRUK",
      "GÅLSJØBRUK"
    ],
    "lId": "15154",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 63.19027777777777,
      "lon": 17.816944444444445
    }
  },
  {
    "name": "Gålö",
    "synonyms": [
      "GÅLÖ",
      "GÅLÖ SKÄLÅKER",
      "GÅLØ",
      "GÅLØ SKÆLÅKER"
    ],
    "lId": "01125",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.095,
      "lon": 18.317777777777778
    }
  },
  {
    "name": "Gånghester väg 27",
    "synonyms": [
      "GÅNGHESTER V27",
      "GÅNGHESTER VÄG 27",
      "GÅNGHESTER VÆG 27"
    ],
    "lId": "10315",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 57.69694444444444,
      "lon": 13.027222222222223
    }
  },
  {
    "name": "Gårdsjö",
    "synonyms": [
      "GARDSJO",
      "GÅRDSJÖ",
      "GÅRDSJÖ STN",
      "GÅRDSJØ",
      "GÅRDSJØ STN"
    ],
    "lId": "00071",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 58.87166666666667,
      "lon": 14.333333333333334
    }
  },
  {
    "name": "Gårdskär Kiosken",
    "synonyms": [
      "GÅRDSKÄR KIOSKEN"
    ],
    "lId": "08006",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 60.60944444444445,
      "lon": 17.57611111111111
    }
  },
  {
    "name": "Gårdskär vändslinga",
    "synonyms": [
      "GÅRDSKÄR VÄNDSLINGA",
      "GÅRDSKÆR VÆNDSLINGA"
    ],
    "lId": "12697",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 60.611111111111114,
      "lon": 17.584444444444443
    }
  },
  {
    "name": "Gårdstånga skolan",
    "synonyms": [
      "GÅRDSTÅNGA SKOLAN"
    ],
    "lId": "16639",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 55.76305555555555,
      "lon": 13.323333333333332
    }
  },
  {
    "name": "Gåshaga brygga",
    "synonyms": [
      "GÅSHAGA BRYGGA"
    ],
    "lId": "23966",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.35666666666667,
      "lon": 18.233888888888888
    }
  },
  {
    "name": "Gåshaga station",
    "synonyms": [
      "GÅSHAGA STATION"
    ],
    "lId": "20756",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.35666666666667,
      "lon": 18.228888888888886
    }
  },
  {
    "name": "Gåsvik handel",
    "synonyms": [
      "GÅSVIK HANDEL"
    ],
    "lId": "10499",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.937777777777775,
      "lon": 18.836666666666666
    }
  },
  {
    "name": "Gåvsta skolan",
    "synonyms": [
      "GÅVSTA SKOLAN"
    ],
    "lId": "21037",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.94611111111111,
      "lon": 17.878055555555555
    }
  },
  {
    "name": "Gåxsjö Föllinge vsk",
    "synonyms": [
      "GÅXSJÖ FÖLL VSK",
      "GÅXSJÖ FÖLLINGE VSK",
      "GÅXSJØ FØLL VSK",
      "GÅXSJØ FØLLINGE VSK"
    ],
    "lId": "13228",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 63.66888888888889,
      "lon": 15.100277777777777
    }
  },
  {
    "name": "Gäddede",
    "synonyms": [
      "GÄDDEDE",
      "GÄDDEDE BSTN",
      "GÆDDEDE",
      "GÆDDEDE BSTN"
    ],
    "lId": "00422",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 64.5038888888889,
      "lon": 14.145833333333332
    }
  },
  {
    "name": "Gäddeholm",
    "synonyms": [
      "GÄDDEHOLM"
    ],
    "lId": "38146",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.551111111111105,
      "lon": 16.671944444444446
    }
  },
  {
    "name": "Gällivare",
    "synonyms": [
      "GALLIVARE",
      "GÄLLIVARE",
      "GÄLLIVARE STN",
      "GÆLLIVARE",
      "GÆLLIVARE STN"
    ],
    "lId": "00254",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 67.13333333333334,
      "lon": 20.650555555555552
    }
  },
  {
    "name": "Gällnö brygga",
    "synonyms": [
      "GÄLLNÖ BRYGGA",
      "GÆLLNØ BRYGGA"
    ],
    "lId": "24302",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.390277777777776,
      "lon": 18.639166666666664
    }
  },
  {
    "name": "Gällstad",
    "synonyms": [
      "GÄLLSTAD",
      "GÆLLSTAD"
    ],
    "lId": "00697",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 57.66722222222222,
      "lon": 13.4325
    }
  },
  {
    "name": "Gällö",
    "synonyms": [
      "GALLO",
      "GÄLLÖ",
      "GÆLLØ"
    ],
    "lId": "00324",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 62.91111111111111,
      "lon": 15.229444444444445
    }
  },
  {
    "name": "Gängletorp",
    "synonyms": [
      "GÄNGLETORP",
      "GÆNGLETORP"
    ],
    "lId": "25942",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 56.1675,
      "lon": 15.746944444444443
    }
  },
  {
    "name": "Gårdby kyrka",
    "synonyms": [
      "GÅRDBY KYRKA"
    ],
    "lId": "22432",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 56.6,
      "lon": 16.639166666666664
    }
  },
  {
    "name": "Gärdala",
    "synonyms": [
      "GARDALA",
      "GÄRDALA",
      "GÄRDALA STN",
      "GÆRDALA",
      "GÆRDALA STN"
    ],
    "lId": "01074",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 58.17666666666666,
      "lon": 15.714722222222221
    }
  },
  {
    "name": "Gärdet T-bana",
    "synonyms": [
      "GÄRDET T-BANA",
      "GÆRDET T-BANA"
    ],
    "lId": "21649",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.346944444444446,
      "lon": 18.09861111111111
    }
  },
  {
    "name": "Gärds Köpinge idrottsplats",
    "synonyms": [
      "GÄRDS KÖPINGE IDROTTSPLATS",
      "GÆRDS KØPINGE IDROTTSPLATS"
    ],
    "lId": "04116",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 55.93611111111111,
      "lon": 14.152777777777779
    }
  },
  {
    "name": "Gärdshyttan",
    "synonyms": [
      "GÄRDSHYTTAN",
      "GÆRDSHYTTAN"
    ],
    "lId": "24455",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 58.782222222222224,
      "lon": 14.999166666666666
    }
  },
  {
    "name": "Gärsnäs",
    "synonyms": [
      "GARSNAS",
      "GÄRSNÄS",
      "GÆRSNÆS"
    ],
    "lId": "00742",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 55.546388888888885,
      "lon": 14.180833333333332
    }
  },
  {
    "name": "Gävle C",
    "synonyms": [
      "GAVLE C",
      "GÄVLE C",
      "GÆVLE C",
      "QYU"
    ],
    "lId": "00210",
    "prio": 1,
    "pId": "074",
    "pos": {
      "lat": 60.67611111111111,
      "lon": 17.15111111111111
    }
  },
  {
    "name": "Gävle Fjärran Höjder",
    "synonyms": [
      "GÄVLE FJÄRRAN HÖJDER",
      "GÆVLE FJÆRRAN HØJDER"
    ],
    "lId": "19338",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 60.66694444444444,
      "lon": 17.131666666666668
    }
  },
  {
    "name": "Gävle Gasklockorna",
    "synonyms": [
      "GÄVLE GASKLOCKORNA",
      "GÆVLE GASKLOCKORNA"
    ],
    "lId": "10279",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 60.67777777777778,
      "lon": 17.177222222222223
    }
  },
  {
    "name": "Gävle Gävlebro E4",
    "synonyms": [
      "GÄVLE GÄVLEBRO E4"
    ],
    "lId": "23144",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 60.64861111111111,
      "lon": 17.11861111111111
    }
  },
  {
    "name": "Gävle Högskolan",
    "synonyms": [
      "GÄVLE HÖGSKOLAN",
      "GÆVLE HØGSKOLAN"
    ],
    "lId": "19279",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 60.66916666666666,
      "lon": 17.11861111111111
    }
  },
  {
    "name": "Gävle Läkerol arena",
    "synonyms": [
      "GÄVLE LÄKEROL ARENA"
    ],
    "lId": "19242",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 60.69027777777777,
      "lon": 17.134444444444444
    }
  },
  {
    "name": "Gävle Sjukhus väg 80",
    "synonyms": [
      "GÄVLE SJUKH V80",
      "GÄVLE SJUKHUS VÄG 80",
      "GÆVLE SJUKH V80",
      "GÆVLE SJUKHUS VÆG 80"
    ],
    "lId": "19424",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 60.675555555555555,
      "lon": 17.121666666666666
    }
  },
  {
    "name": "Gävle stadszon",
    "synonyms": [
      "GÄVLE STADSZON",
      "GÆVLE STADSZON"
    ],
    "lId": "79011",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 60.67611111111111,
      "lon": 17.15111111111111
    }
  },
  {
    "name": "Göstad",
    "synonyms": [
      "GÖSTAD",
      "GØSTAD"
    ],
    "lId": "20313",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 58.59444444444445,
      "lon": 15.841111111111111
    }
  },
  {
    "name": "Göta",
    "synonyms": [
      "GÖTA",
      "GØTA"
    ],
    "lId": "12137",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 58.10722222222223,
      "lon": 12.149166666666666
    }
  },
  {
    "name": "Göteborg C",
    "synonyms": [
      "GOTEBORG C",
      "GOTHENBURG C",
      "GÖTEBORG C",
      "GØTEBORG C",
      "XWL"
    ],
    "lId": "00002",
    "prio": 400,
    "pId": "074",
    "pos": {
      "lat": 57.70888888888889,
      "lon": 11.973333333333333
    }
  },
  {
    "name": "Göteborg stadszon",
    "synonyms": [
      "GÖTEBORG STADSZON",
      "GÖTEBORG ZON",
      "GØTEBORG STADSZON"
    ],
    "lId": "01126",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 58.593333333333334,
      "lon": 13.345555555555556
    }
  },
  {
    "name": "Göteborg Almedal",
    "synonyms": [
      "GÖTEBORG ALMEDAL",
      "GØTEBORG ALMEDAL"
    ],
    "lId": "25605",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 57.68694444444444,
      "lon": 11.996944444444443
    }
  },
  {
    "name": "Göteborg Axel Dahlströms torg",
    "synonyms": [
      "GÖTEBORG AXEL DAHLSTRÖMS TOR",
      "GÖTEBORG AXEL DAHLSTRÖMS TORG",
      "GØTEBORG AXEL DAHLSTRØMS TOR",
      "GØTEBORG AXEL DAHLSTRØMS TORG"
    ],
    "lId": "25608",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 57.67222222222222,
      "lon": 11.927222222222222
    }
  },
  {
    "name": "Göteborg Bellevue",
    "synonyms": [
      "GÖTEBORG BELLEVUE",
      "GØTEBORG BELLEVUE"
    ],
    "lId": "25609",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 57.73166666666667,
      "lon": 12.0225
    }
  },
  {
    "name": "Göteborg Berzeliigatan",
    "synonyms": [
      "GÖTEBORG BERZELIIGATAN",
      "GØTEBORG BERZELIIGATAN"
    ],
    "lId": "25610",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 57.69833333333333,
      "lon": 11.981666666666667
    }
  },
  {
    "name": "Göteborg Beväringsgatan",
    "synonyms": [
      "GÖTEBORG BEVÄRINGSGATAN",
      "GØTEBORG BEVÆRINGSGATAN"
    ],
    "lId": "25611",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 57.73972222222222,
      "lon": 12.028333333333334
    }
  },
  {
    "name": "Göteborg Bokekullsgatan",
    "synonyms": [
      "GÖTEBORG BOKEKULLSGATAN",
      "GØTEBORG BOKEKULLSGATAN"
    ],
    "lId": "25612",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 57.676944444444445,
      "lon": 11.9325
    }
  },
  {
    "name": "Göteborg Botaniska Trädgård",
    "synonyms": [
      "GÖTEBORG BOTANISKA TRÄDGÅRD",
      "GØTEBORG BOTANISKA TRÆDGÅRD"
    ],
    "lId": "25689",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 57.68083333333333,
      "lon": 11.945555555555556
    }
  },
  {
    "name": "Göteborg Brunnsbotorget",
    "synonyms": [
      "GÖTEBORG BRUNNSBOTORGET"
    ],
    "lId": "59149",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 57.727222222222224,
      "lon": 11.970277777777778
    }
  },
  {
    "name": "Göteborg Brunnsgatan",
    "synonyms": [
      "GÖTEBORG BRUNNSGATAN",
      "GØTEBORG BRUNNSGATAN"
    ],
    "lId": "25614",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 57.69361111111111,
      "lon": 11.958055555555555
    }
  },
  {
    "name": "Göteborg Brunnsparken",
    "synonyms": [
      "BRUNNSPARKEN GÖTEBORG",
      "GÖTEBORG BRUNNSPARKEN",
      "GÖTEBORG BRUNSP",
      "GØTEBORG BRUNNSPARKEN",
      "GØTEBORG BRUNSP"
    ],
    "lId": "20752",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 57.706944444444446,
      "lon": 11.967777777777778
    }
  },
  {
    "name": "Göteborg Bäckeliden",
    "synonyms": [
      "GÖTEBORG BÄCKELIDEN",
      "GØTEBORG BÆCKELIDEN"
    ],
    "lId": "25615",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 57.69972222222222,
      "lon": 12.003333333333334
    }
  },
  {
    "name": "Göteborg Bögatan",
    "synonyms": [
      "GÖTEBORG BÖGATAN",
      "GØTEBORG BØGATAN"
    ],
    "lId": "25616",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 57.700833333333335,
      "lon": 12.016388888888889
    }
  },
  {
    "name": "Göteborg Chalmers",
    "synonyms": [
      "GÖTEBORG CHALMERS",
      "GØTEBORG CHALMERS"
    ],
    "lId": "25617",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 57.689722222222215,
      "lon": 11.972777777777777
    }
  },
  {
    "name": "Göteborg Chapmans Torg",
    "synonyms": [
      "GÖTEBORG CHAPMANS TORG",
      "GØTEBORG CHAPMANS TORG"
    ],
    "lId": "25618",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 57.69416666666666,
      "lon": 11.919444444444444
    }
  },
  {
    "name": "Göteborg Danmarksterminalen",
    "synonyms": [
      "GÖTEBORG DANMARKSTERMINALEN",
      "GØTEBORG DANMARKSTERMINALEN"
    ],
    "lId": "01108",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 57.70111111111111,
      "lon": 11.945555555555556
    }
  },
  {
    "name": "Göteborg Doktor Fries Torg",
    "synonyms": [
      "GÖTEBORG DOKTOR FRIES TORG",
      "GØTEBORG DOKTOR FRIES TORG"
    ],
    "lId": "25619",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 57.68416666666666,
      "lon": 11.973055555555556
    }
  },
  {
    "name": "Göteborg Doktor Sydows gata",
    "synonyms": [
      "GÖTEBORG DOKTOR SYDOWS GATA",
      "GØTEBORG DOKTOR SYDOWS GATA"
    ],
    "lId": "25620",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 57.68055555555555,
      "lon": 11.975277777777778
    }
  },
  {
    "name": "Göteborg Domkyrkan",
    "synonyms": [
      "GÖTEBORG DOMKYRKAN",
      "GØTEBORG DOMKYRKAN"
    ],
    "lId": "25621",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 57.70416666666667,
      "lon": 11.96361111111111
    }
  },
  {
    "name": "Göteborg Ejdergatan",
    "synonyms": [
      "GÖTEBORG EJDERGATAN",
      "GØTEBORG EJDERGATAN"
    ],
    "lId": "25622",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 57.72083333333334,
      "lon": 12.005833333333333
    }
  },
  {
    "name": "Göteborg Ekedal",
    "synonyms": [
      "GÖTEBORG EKEDAL",
      "GØTEBORG EKEDAL"
    ],
    "lId": "25623",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 57.68666666666666,
      "lon": 11.928055555555554
    }
  },
  {
    "name": "Göteborg Eketrägatan",
    "synonyms": [
      "GÖTEBORG EKETRÄGATAN",
      "GØTEBORG EKETRÆGATAN"
    ],
    "lId": "25624",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 57.71611111111111,
      "lon": 11.910277777777779
    }
  },
  {
    "name": "Göteborg Ekmanska",
    "synonyms": [
      "GÖTEBORG EKMANSKA",
      "GØTEBORG EKMANSKA"
    ],
    "lId": "25625",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 57.69944444444444,
      "lon": 12.009444444444444
    }
  },
  {
    "name": "Göteborg Elisedal",
    "synonyms": [
      "GÖTEBORG ELISEDAL",
      "GØTEBORG ELISEDAL"
    ],
    "lId": "25626",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 57.68388888888889,
      "lon": 12
    }
  },
  {
    "name": "Göteborg Fjällgatan",
    "synonyms": [
      "GÖTEBORG FJÄLLGATAN",
      "GØTEBORG FJÆLLGATAN"
    ],
    "lId": "25627",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 57.69444444444444,
      "lon": 11.936111111111112
    }
  },
  {
    "name": "Göteborg Frihamnsviadukten",
    "synonyms": [
      "GÖTEBORG FRIHAMNSVIADUKTEN"
    ],
    "lId": "25026",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 57.72027777777778,
      "lon": 11.959999999999999
    }
  },
  {
    "name": "Göteborg Friskväderstorget",
    "synonyms": [
      "GÖTEBORG FRISKVÄDERSTORGET",
      "GØTEBORG FRISKVÆDERSTORGET"
    ],
    "lId": "25628",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 57.723333333333336,
      "lon": 11.893333333333333
    }
  },
  {
    "name": "Göteborg Gamlestaden station",
    "synonyms": [
      "GAMLESTADEN STN",
      "GÖTEBORG GAMLESTADEN STATION"
    ],
    "lId": "01590",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 57.72888888888889,
      "lon": 12.004166666666666
    }
  },
  {
    "name": "Göteborg Gamlestadstorget",
    "synonyms": [
      "GÖTEBORG GAMLESTADSTORGET",
      "GØTEBORG GAMLESTADSTORGET"
    ],
    "lId": "25630",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 57.72833333333333,
      "lon": 12.005555555555556
    }
  },
  {
    "name": "Göteborg Getebergsäng",
    "synonyms": [
      "GÖTEBORG GETEBERGSÄNG",
      "GØTEBORG GETEBERGSÆNG"
    ],
    "lId": "25631",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 57.69166666666666,
      "lon": 11.991944444444444
    }
  },
  {
    "name": "Göteborg Godhemsgatan",
    "synonyms": [
      "GÖTEBORG GODHEMSGATAN",
      "GØTEBORG GODHEMSGATAN"
    ],
    "lId": "25632",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 57.68472222222222,
      "lon": 11.925833333333333
    }
  },
  {
    "name": "Göteborg Gropegårdsgatan",
    "synonyms": [
      "GÖTEBORG GROPEGÅRDSGATAN",
      "GØTEBORG GROPEGÅRDSGATAN"
    ],
    "lId": "25633",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 57.71805555555556,
      "lon": 11.918333333333333
    }
  },
  {
    "name": "Göteborg Grönsakstorget",
    "synonyms": [
      "GÖTEBORG GRÖNSAKSTORGET",
      "GØTEBORG GRØNSAKSTORGET"
    ],
    "lId": "15567",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 57.702222222222225,
      "lon": 11.964166666666666
    }
  },
  {
    "name": "Göteborg Hagakyrkan",
    "synonyms": [
      "GÖTEBORG HAGAKYRKAN"
    ],
    "lId": "25634",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 57.69944444444444,
      "lon": 11.961666666666666
    }
  },
  {
    "name": "Göteborg Hagen",
    "synonyms": [
      "GÖTEBORG HAGEN",
      "GØTEBORG HAGEN"
    ],
    "lId": "25635",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 57.67472222222222,
      "lon": 11.883888888888889
    }
  },
  {
    "name": "Göteborg Handelshögskolan",
    "synonyms": [
      "GÖTEBORG HANDELSHÖGSKOLAN",
      "GØTEBORG HANDELSHØGSKOLAN"
    ],
    "lId": "25653",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 57.69694444444444,
      "lon": 11.962222222222222
    }
  },
  {
    "name": "Göteborg Hinsholmen",
    "synonyms": [
      "GÖTEBORG HINSHOLMEN",
      "GØTEBORG HINSHOLMEN"
    ],
    "lId": "25637",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 57.66777777777777,
      "lon": 11.860833333333334
    }
  },
  {
    "name": "Göteborg Hjalmar Brantingspl",
    "synonyms": [
      "GÖTEBORG HJALMAR BRANTINGSPL",
      "GØTEBORG HJALMAR BRANTINGSPL"
    ],
    "lId": "15569",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 57.720555555555556,
      "lon": 11.95361111111111
    }
  },
  {
    "name": "Göteborg Härlanda",
    "synonyms": [
      "GÖTEBORG HÄRLANDA",
      "GØTEBORG HÆRLANDA"
    ],
    "lId": "25638",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 57.71805555555556,
      "lon": 12.020000000000001
    }
  },
  {
    "name": "Göteborg Högsbogatan",
    "synonyms": [
      "GÖTEBORG HÖGSBOGATAN",
      "GØTEBORG HØGSBOGATAN"
    ],
    "lId": "25639",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 57.68,
      "lon": 11.93
    }
  },
  {
    "name": "Göteborg Jaegerdorffsplatsen",
    "synonyms": [
      "GÖTEBORG JAEGERDORFFSPLATSEN",
      "GØTEBORG JAEGERDORFFSPLATSEN"
    ],
    "lId": "25640",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 57.69138888888889,
      "lon": 11.915000000000001
    }
  },
  {
    "name": "Göteborg Järntorget",
    "synonyms": [
      "GÖTEBORG JÄRNTORGET",
      "GØTEBORG JÆRNTORGET"
    ],
    "lId": "15573",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 57.7,
      "lon": 11.951944444444443
    }
  },
  {
    "name": "Göteborg Kaggeledstorget",
    "synonyms": [
      "GÖTEBORG KAGGELEDSTORGET",
      "GØTEBORG KAGGELEDSTORGET"
    ],
    "lId": "25642",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 57.723055555555554,
      "lon": 12.03361111111111
    }
  },
  {
    "name": "Göteborg Kapellplatsen",
    "synonyms": [
      "GÖTEBORG KAPELLPLATSEN",
      "GØTEBORG KAPELLPLATSEN"
    ],
    "lId": "25643",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 57.69361111111111,
      "lon": 11.973055555555556
    }
  },
  {
    "name": "Göteborg Kaptensgatan",
    "synonyms": [
      "GÖTEBORG KAPTENSGATAN",
      "GØTEBORG KAPTENSGATAN"
    ],
    "lId": "25644",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 57.69694444444444,
      "lon": 11.927222222222222
    }
  },
  {
    "name": "Göteborg Klintens Väg",
    "synonyms": [
      "GÖTEBORG KLINTENS VÄG",
      "GØTEBORG KLINTENS VÆG"
    ],
    "lId": "25645",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 57.6825,
      "lon": 11.927777777777777
    }
  },
  {
    "name": "Göteborg Korsvägen",
    "synonyms": [
      "GÖTEBORG KORSVÄGEN",
      "GØTEBORG KORSVÆGEN"
    ],
    "lId": "15578",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 57.69638888888888,
      "lon": 11.986666666666666
    }
  },
  {
    "name": "Göteborg Kungsportsplatsen",
    "synonyms": [
      "GÖTEBORG KUNGSPORTSPLATSEN",
      "GØTEBORG KUNGSPORTSPLATSEN"
    ],
    "lId": "16358",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 57.70388888888889,
      "lon": 11.969722222222222
    }
  },
  {
    "name": "Göteborg Kungssten",
    "synonyms": [
      "GÖTEBORG KUNGSSTEN",
      "GØTEBORG KUNGSSTEN"
    ],
    "lId": "25647",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 57.68055555555555,
      "lon": 11.901666666666667
    }
  },
  {
    "name": "Göteborg Kviberg",
    "synonyms": [
      "GÖTEBORG KVIBERG",
      "GØTEBORG KVIBERG"
    ],
    "lId": "25648",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 57.73638888888889,
      "lon": 12.025
    }
  },
  {
    "name": "Göteborg Kålltorp",
    "synonyms": [
      "GÖTEBORG KÅLLTORP",
      "GØTEBORG KÅLLTORP"
    ],
    "lId": "25649",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 57.71,
      "lon": 12.023055555555556
    }
  },
  {
    "name": "Göteborg Käringberget",
    "synonyms": [
      "GÖTEBORG KÄRINGBERGET",
      "GØTEBORG KÆRINGBERGET"
    ],
    "lId": "25650",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 57.66916666666666,
      "lon": 11.87138888888889
    }
  },
  {
    "name": "Göteborg Lana",
    "synonyms": [
      "GÖTEBORG LANA",
      "GØTEBORG LANA"
    ],
    "lId": "25651",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 57.67805555555555,
      "lon": 12.00388888888889
    }
  },
  {
    "name": "Göteborg Lantmilsgatan",
    "synonyms": [
      "GÖTEBORG LANTMILSGATAN",
      "GØTEBORG LANTMILSGATAN"
    ],
    "lId": "25652",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 57.66694444444444,
      "lon": 11.924444444444443
    }
  },
  {
    "name": "Göteborg Lilla Bommen",
    "synonyms": [
      "GÖTEBORG LILLA BOMMEN",
      "GØTEBORG LILLA BOMMEN"
    ],
    "lId": "16360",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 57.70944444444445,
      "lon": 11.965833333333332
    }
  },
  {
    "name": "Göteborg Linneplatsen",
    "synonyms": [
      "GÖTEBORG LINNEPLATSEN",
      "GÖTEBORG LINNÉPLATSEN",
      "GØTEBORG LINNEPLATSEN",
      "GØTEBORG LINNÉPLATSEN"
    ],
    "lId": "15581",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 57.689722222222215,
      "lon": 11.952222222222222
    }
  },
  {
    "name": "Göteborg Liseberg",
    "synonyms": [
      "GÖTEBORG LISEBERG",
      "GØTEBORG LISEBERG"
    ],
    "lId": "25654",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 57.697222222222216,
      "lon": 11.99111111111111
    }
  },
  {
    "name": "Göteborg Långedrag",
    "synonyms": [
      "GÖTEBORG LÅNGEDRAG",
      "GØTEBORG LÅNGEDRAG"
    ],
    "lId": "25027",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 57.66777777777777,
      "lon": 11.853333333333333
    }
  },
  {
    "name": "Göteborg Majvallen",
    "synonyms": [
      "GÖTEBORG MAJVALLEN",
      "GØTEBORG MAJVALLEN"
    ],
    "lId": "25655",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 57.69083333333333,
      "lon": 11.935277777777777
    }
  },
  {
    "name": "Göteborg Mariaplan",
    "synonyms": [
      "GÖTEBORG MARIAPLAN",
      "GØTEBORG MARIAPLAN"
    ],
    "lId": "25656",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 57.686388888888885,
      "lon": 11.920555555555556
    }
  },
  {
    "name": "Göteborg Marklandsgatan",
    "synonyms": [
      "GÖTEBORG MARKLANDSGATAN",
      "GØTEBORG MARKLANDSGATAN"
    ],
    "lId": "25657",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 57.674166666666665,
      "lon": 11.935833333333333
    }
  },
  {
    "name": "Göteborg Masthuggstorget",
    "synonyms": [
      "GÖTEBORG MASTHUGGSTORGET",
      "GØTEBORG MASTHUGGSTORGET"
    ],
    "lId": "25658",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 57.69944444444444,
      "lon": 11.944444444444445
    }
  },
  {
    "name": "Göteborg Medicinaregatan",
    "synonyms": [
      "GÖTEBORG MEDICINAREGATAN",
      "GØTEBORG MEDICINAREGATAN"
    ],
    "lId": "25659",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 57.68527777777778,
      "lon": 11.964166666666666
    }
  },
  {
    "name": "Göteborg Mildvädersgatan",
    "synonyms": [
      "GÖTEBORG MILDVÄDERSGATAN",
      "GØTEBORG MILDVÆDERSGATAN"
    ],
    "lId": "25660",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 57.71555555555556,
      "lon": 11.890833333333333
    }
  },
  {
    "name": "Göteborg Munkebäckstorget",
    "synonyms": [
      "GÖTEBORG MUNKEBÄCKSTORGET",
      "GØTEBORG MUNKEBÆCKSTORGET"
    ],
    "lId": "25661",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 57.718333333333334,
      "lon": 12.02638888888889
    }
  },
  {
    "name": "Göteborg Nils Ericsonterminal",
    "synonyms": [
      "GÖTEBORG NILS ERICSONTERMINAL",
      "GØTEBORG NILS ERICSONTERMINAL"
    ],
    "lId": "20483",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 57.71,
      "lon": 11.971666666666668
    }
  },
  {
    "name": "Göteborg Nordstan",
    "synonyms": [
      "GÖTEBORG NORDSTAN",
      "GØTEBORG NORDSTAN"
    ],
    "lId": "15585",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 57.70916666666667,
      "lon": 11.970555555555556
    }
  },
  {
    "name": "Göteborg Nya Varvsallén",
    "synonyms": [
      "GÖTEBORG NYA VARVSALLÉN",
      "GÖTEBORG NYA VARVSALLËN",
      "GØTEBORG NYA VARVSALLËN"
    ],
    "lId": "25663",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 57.677499999999995,
      "lon": 11.893888888888888
    }
  },
  {
    "name": "Göteborg Nymilsgatan",
    "synonyms": [
      "GÖTEBORG NYMILSGATAN",
      "GØTEBORG NYMILSGATAN"
    ],
    "lId": "25664",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 57.6625,
      "lon": 11.924166666666666
    }
  },
  {
    "name": "Göteborg Nymånegatan",
    "synonyms": [
      "GÖTEBORG NYMÅNEGATAN",
      "GØTEBORG NYMÅNEGATAN"
    ],
    "lId": "25665",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 57.74277777777778,
      "lon": 12.029722222222222
    }
  },
  {
    "name": "Göteborg Olivedalsgatan",
    "synonyms": [
      "GÖTEBORG OLIVEDALSGATAN",
      "GØTEBORG OLIVEDALSGATAN"
    ],
    "lId": "25666",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 57.69194444444444,
      "lon": 11.952777777777778
    }
  },
  {
    "name": "Göteborg Olskrokstorget",
    "synonyms": [
      "GÖTEBORG OLSKROKSTORGET",
      "GØTEBORG OLSKROKSTORGET"
    ],
    "lId": "25667",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 57.714444444444446,
      "lon": 11.998888888888889
    }
  },
  {
    "name": "Göteborg Ostindiegatan",
    "synonyms": [
      "GÖTEBORG OSTINDIEGATAN",
      "GØTEBORG OSTINDIEGATAN"
    ],
    "lId": "25670",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 57.6875,
      "lon": 11.915277777777778
    }
  },
  {
    "name": "Göteborg Pilegården",
    "synonyms": [
      "GÖTEBORG PILEGÅRDEN"
    ],
    "lId": "15589",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 57.63916666666667,
      "lon": 11.931944444444444
    }
  },
  {
    "name": "Göteborg Prinsgatan",
    "synonyms": [
      "GÖTEBORG PRINSGATAN",
      "GØTEBORG PRINSGATAN"
    ],
    "lId": "25671",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 57.696666666666665,
      "lon": 11.950833333333332
    }
  },
  {
    "name": "Göteborg Rambergsvallen",
    "synonyms": [
      "GÖTEBORG RAMBERGSVALLEN",
      "GØTEBORG RAMBERGSVALLEN"
    ],
    "lId": "25672",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 57.71944444444445,
      "lon": 11.9275
    }
  },
  {
    "name": "Göteborg Redbergsplatsen",
    "synonyms": [
      "GÖTEBORG REDBERGSPLATSEN",
      "GØTEBORG REDBERGSPLATSEN"
    ],
    "lId": "25673",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 57.71638888888889,
      "lon": 12.004722222222222
    }
  },
  {
    "name": "Göteborg Roddföreningen",
    "synonyms": [
      "GÖTEBORG RODDFÖRENINGEN",
      "GØTEBORG RODDFØRENINGEN"
    ],
    "lId": "25674",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 57.663888888888884,
      "lon": 11.851666666666667
    }
  },
  {
    "name": "Göteborg Sahlgrenska huvudentr",
    "synonyms": [
      "GÖTEBORG SAHLGRENSKA HUVUDENTR",
      "GØTEBORG SAHLGRENSKA HUVUDENTR"
    ],
    "lId": "15591",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 57.683611111111105,
      "lon": 11.960555555555555
    }
  },
  {
    "name": "Göteborg Saltholmen",
    "synonyms": [
      "GÖTEBORG SALTHOLMEN",
      "GØTEBORG SALTHOLMEN"
    ],
    "lId": "01206",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 57.66083333333333,
      "lon": 11.843055555555557
    }
  },
  {
    "name": "Göteborg Sanatoriegatan",
    "synonyms": [
      "GÖTEBORG SANATORIEGATAN",
      "GØTEBORG SANATORIEGATAN"
    ],
    "lId": "25677",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 57.71361111111111,
      "lon": 12.024166666666668
    }
  },
  {
    "name": "Göteborg Sandarna",
    "synonyms": [
      "GÖTEBORG SANDARNA",
      "GØTEBORG SANDARNA"
    ],
    "lId": "25678",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 57.68277777777777,
      "lon": 11.909444444444444
    }
  },
  {
    "name": "Göteborg Sankt Sigfrids Plan",
    "synonyms": [
      "GÖTEBORG SANKT SIGFRIDS PLAN",
      "GØTEBORG SANKT SIGFRIDS PLAN"
    ],
    "lId": "25679",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 57.698611111111106,
      "lon": 11.999166666666666
    }
  },
  {
    "name": "Göteborg Sannaplan",
    "synonyms": [
      "GÖTEBORG SANNAPLAN",
      "GØTEBORG SANNAPLAN"
    ],
    "lId": "25680",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 57.68416666666666,
      "lon": 11.91638888888889
    }
  },
  {
    "name": "Göteborg Scandinavium",
    "synonyms": [
      "GÖTEBORG SCANDINAVIUM",
      "GØTEBORG SCANDINAVIUM"
    ],
    "lId": "25681",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 57.70027777777778,
      "lon": 11.985833333333332
    }
  },
  {
    "name": "Göteborg Selma Lagerlöfs torg",
    "synonyms": [
      "GÖTEBORG SELMA LAGERLÖFS TORG"
    ],
    "lId": "59539",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 57.75083333333333,
      "lon": 11.981111111111112
    }
  },
  {
    "name": "Göteborg Seminariegatan",
    "synonyms": [
      "GÖTEBORG SEMINARIEGATAN",
      "GØTEBORG SEMINARIEGATAN"
    ],
    "lId": "25682",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 57.69222222222222,
      "lon": 11.95722222222222
    }
  },
  {
    "name": "Göteborg SKF",
    "synonyms": [
      "GÖTEBORG SKF",
      "GØTEBORG SKF"
    ],
    "lId": "25683",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 57.72916666666667,
      "lon": 12.013333333333334
    }
  },
  {
    "name": "Göteborg Solrosgatan",
    "synonyms": [
      "GÖTEBORG SOLROSGATAN",
      "GØTEBORG SOLROSGATAN"
    ],
    "lId": "25685",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 57.71638888888889,
      "lon": 12.025
    }
  },
  {
    "name": "Göteborg Stabbetorget",
    "synonyms": [
      "GÖTEBORG STABBETORGET",
      "GØTEBORG STABBETORGET"
    ],
    "lId": "59587",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 57.714444444444446,
      "lon": 12.0475
    }
  },
  {
    "name": "Göteborg Stenpiren",
    "synonyms": [
      "GÖTEBORG STENPIREN"
    ],
    "lId": "72430",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 57.70583333333334,
      "lon": 11.9575
    }
  },
  {
    "name": "Göteborg Stigbergstorget",
    "synonyms": [
      "GÖTEBORG STIGBERGSTORGET",
      "GØTEBORG STIGBERGSTORGET"
    ],
    "lId": "25686",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 57.69888888888889,
      "lon": 11.934722222222222
    }
  },
  {
    "name": "Göteborg Stockholmsgatan",
    "synonyms": [
      "GÖTEBORG STOCKHOLMSGATAN",
      "GØTEBORG STOCKHOLMSGATAN"
    ],
    "lId": "25687",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 57.716944444444444,
      "lon": 12.013333333333334
    }
  },
  {
    "name": "Göteborg Svingeln",
    "synonyms": [
      "GÖTEBORG SVINGELN",
      "GØTEBORG SVINGELN"
    ],
    "lId": "15597",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 57.71138888888889,
      "lon": 11.989999999999998
    }
  },
  {
    "name": "Göteborg Sälöfjordsgatan",
    "synonyms": [
      "GÖTEBORG SÄLÖFJORDSGATAN",
      "GØTEBORG SÆLØFJORDSGATAN"
    ],
    "lId": "25690",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 57.71361111111111,
      "lon": 11.901944444444444
    }
  },
  {
    "name": "Göteborg Temperaturgatan",
    "synonyms": [
      "GÖTEBORG TEMPERATURGATAN",
      "GØTEBORG TEMPERATURGATAN"
    ],
    "lId": "25692",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 57.73277777777778,
      "lon": 11.895277777777777
    }
  },
  {
    "name": "Göteborg Tingvallsvägen",
    "synonyms": [
      "GÖTEBORG TINGVALLSVÄGEN",
      "GØTEBORG TINGVALLSVÆGEN"
    ],
    "lId": "25693",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 57.724444444444444,
      "lon": 12.041944444444445
    }
  },
  {
    "name": "Göteborg Torp",
    "synonyms": [
      "GÖTEBORG TORP",
      "GØTEBORG TORP"
    ],
    "lId": "25734",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 57.71,
      "lon": 12.023055555555556
    }
  },
  {
    "name": "Göteborg Tranered",
    "synonyms": [
      "GOTHENBERG TRANERED",
      "GÖTEBORG TRANERED",
      "GØTEBORG TRANERED"
    ],
    "lId": "25725",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 57.6725,
      "lon": 11.879444444444445
    }
  },
  {
    "name": "Göteborg Töpelsgatan",
    "synonyms": [
      "GÖTEBORG TÖPELSGATAN",
      "GØTEBORG TØPELSGATAN"
    ],
    "lId": "25694",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 57.702222222222225,
      "lon": 12.0225
    }
  },
  {
    "name": "Göteborg Ullevi Norra",
    "synonyms": [
      "GÖTEBORG ULLEVI NORRA",
      "GØTEBORG ULLEVI NORRA"
    ],
    "lId": "25695",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 57.70777777777778,
      "lon": 11.985833333333332
    }
  },
  {
    "name": "Göteborg Ullevi Södra",
    "synonyms": [
      "GÖTEBORG ULLEVI SÖDRA",
      "GØTEBORG ULLEVI SØDRA"
    ],
    "lId": "25696",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 57.70388888888889,
      "lon": 11.985
    }
  },
  {
    "name": "Göteborg Vagnhallen Majorna",
    "synonyms": [
      "GÖTEBORG VAGNHALLEN MAJORNA",
      "GØTEBORG VAGNHALLEN MAJORNA"
    ],
    "lId": "25697",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 57.68888888888888,
      "lon": 11.912222222222223
    }
  },
  {
    "name": "Göteborg Valand",
    "synonyms": [
      "GÖTEBORG VALAND",
      "GØTEBORG VALAND"
    ],
    "lId": "25698",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 57.70027777777778,
      "lon": 11.974444444444444
    }
  },
  {
    "name": "Göteborg Varbergsgatan",
    "synonyms": [
      "GÖTEBORG VARBERGSGATAN",
      "GØTEBORG VARBERGSGATAN"
    ],
    "lId": "25699",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 57.68,
      "lon": 12.002777777777778
    }
  },
  {
    "name": "Göteborg Varmfrontsgatan",
    "synonyms": [
      "GÖTEBORG VARMFRONTSGATAN",
      "GØTEBORG VARMFRONTSGATAN"
    ],
    "lId": "25700",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 57.736666666666665,
      "lon": 11.896388888888888
    }
  },
  {
    "name": "Göteborg Vasa Viktoriagatan",
    "synonyms": [
      "GÖTEBORG VASA VIKTORIAGATAN",
      "GØTEBORG VASA VIKTORIAGATAN"
    ],
    "lId": "25702",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 57.69833333333333,
      "lon": 11.965833333333332
    }
  },
  {
    "name": "Göteborg Vasaplatsen",
    "synonyms": [
      "GÖTEBORG VASAPLATSEN",
      "GØTEBORG VASAPLATSEN"
    ],
    "lId": "25701",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 57.69888888888889,
      "lon": 11.969722222222222
    }
  },
  {
    "name": "Göteborg Vågmästareplatsen",
    "synonyms": [
      "GÖTEBORG VÅGMÄSTAREPLATSEN",
      "GØTEBORG VÅGMÆSTAREPLATSEN"
    ],
    "lId": "25706",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 57.720555555555556,
      "lon": 11.945
    }
  },
  {
    "name": "Göteborg Vårväderstorget",
    "synonyms": [
      "GÖTEBORG VÅRVÄDERSTORGET",
      "GØTEBORG VÅRVÆDERSTORGET"
    ],
    "lId": "25707",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 57.71277777777778,
      "lon": 11.893055555555556
    }
  },
  {
    "name": "Göteborg Väderilsgatan",
    "synonyms": [
      "GÖTEBORG VÄDERILSGATAN",
      "GØTEBORG VÆDERILSGATAN"
    ],
    "lId": "25708",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 57.72666666666667,
      "lon": 11.893333333333333
    }
  },
  {
    "name": "Göteborg Wavrinskys Plats",
    "synonyms": [
      "GÖTEBORG WAVRINSKYS PLATS",
      "GØTEBORG WAVRINSKYS PLATS"
    ],
    "lId": "25703",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 57.68861111111111,
      "lon": 11.968333333333334
    }
  },
  {
    "name": "Göteborg Welandergatan",
    "synonyms": [
      "GÖTEBORG WELANDERGATAN",
      "GØTEBORG WELANDERGATAN"
    ],
    "lId": "25704",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 57.70583333333334,
      "lon": 12.023888888888889
    }
  },
  {
    "name": "Göteborg Wieselgrensplatsen",
    "synonyms": [
      "GÖTEBORG WIESELGRENSPLATSEN",
      "GØTEBORG WIESELGRENSPLATSEN"
    ],
    "lId": "25705",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 57.720555555555556,
      "lon": 11.935
    }
  },
  {
    "name": "Göteborg Ättehögsgatan",
    "synonyms": [
      "GÖTEBORG ÄTTEHÖGSGATAN",
      "GØTEBORG ÆTTEHØGSGATAN"
    ],
    "lId": "25709",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 57.719722222222224,
      "lon": 12.028333333333334
    }
  },
  {
    "name": "Göteborg Önskevädersgatan",
    "synonyms": [
      "GÖTEBORG ÖNSKEVÄDERSGATAN",
      "GØTEBORG ØNSKEVÆDERSGATAN"
    ],
    "lId": "25710",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 57.719722222222224,
      "lon": 11.893611111111111
    }
  },
  {
    "name": "Göteborg Östra Sjukhuset",
    "synonyms": [
      "GÖTEBORG ÖSTRA SJUKHUSET",
      "GØTEBORG ØSTRA SJUKHUSET"
    ],
    "lId": "16368",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 57.72222222222222,
      "lon": 12.048055555555555
    }
  },
  {
    "name": "Götene busstation",
    "synonyms": [
      "GÖTENE BSTN",
      "GÖTENE BUSSTATION",
      "GØTENE",
      "GØTENE BSTN",
      "GØTENE BUSSTATION"
    ],
    "lId": "00512",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 58.52722222222222,
      "lon": 13.491388888888888
    }
  },
  {
    "name": "Götene Rasta vsk E20/väg 44",
    "synonyms": [
      "GÖTENE E20/V44",
      "GÖTENE RASTA VSK E20/VÄG 44"
    ],
    "lId": "23176",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 58.538888888888884,
      "lon": 13.5175
    }
  },
  {
    "name": "Götlunda",
    "synonyms": [
      "GÖTLUNDA",
      "GÖTLUNDA FÅRTAL",
      "GØTLUNDA",
      "GØTLUNDA FÅRTAL"
    ],
    "lId": "01127",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.35305555555556,
      "lon": 15.665277777777778
    }
  },
  {
    "name": "Hallstahammar station",
    "synonyms": [
      "HALLSTAHAMMAR STATION"
    ],
    "lId": "00673",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.614444444444445,
      "lon": 16.220555555555553
    }
  },
  {
    "name": "Hablingbo",
    "synonyms": [
      "HABLINGBO",
      "HABLINGBO AFFÄR",
      "HABLINGBO AFFÆR"
    ],
    "lId": "01128",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 57.1875,
      "lon": 18.261666666666667
    }
  },
  {
    "name": "Habo",
    "synonyms": [
      "HABO",
      "HABO STN"
    ],
    "lId": "00231",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 57.90611111111111,
      "lon": 14.076666666666666
    }
  },
  {
    "name": "Hackås",
    "synonyms": [
      "HACKÅS"
    ],
    "lId": "18294",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 62.92527777777777,
      "lon": 14.515833333333333
    }
  },
  {
    "name": "Hagfors",
    "synonyms": [
      "HAGFORS",
      "HAGFORS BSTN"
    ],
    "lId": "00376",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 60.03527777777778,
      "lon": 13.693611111111112
    }
  },
  {
    "name": "Hagsätra T-bana",
    "synonyms": [
      "HAGSÄTRA T-BANA",
      "HAGSÆTRA T-BANA"
    ],
    "lId": "21714",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.2625,
      "lon": 18.01222222222222
    }
  },
  {
    "name": "Hakkas",
    "synonyms": [
      "HAKKAS",
      "HAKKAS ICA"
    ],
    "lId": "00875",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 66.91444444444446,
      "lon": 21.563055555555557
    }
  },
  {
    "name": "Hakkas E10",
    "synonyms": [
      "HAKKAS E10"
    ],
    "lId": "20373",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 66.91194444444444,
      "lon": 21.559444444444445
    }
  },
  {
    "name": "Halden",
    "synonyms": [
      "HALDEN"
    ],
    "lId": "00546",
    "prio": 0,
    "pId": "076",
    "pos": {
      "lat": 59.12916666666667,
      "lon": 11.372777777777777
    }
  },
  {
    "name": "Hall",
    "synonyms": [
      "HALL"
    ],
    "lId": "27338",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.168055555555554,
      "lon": 17.67666666666667
    }
  },
  {
    "name": "Hallabro",
    "synonyms": [
      "HALLABRO"
    ],
    "lId": "01075",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 56.38944444444444,
      "lon": 15.1025
    }
  },
  {
    "name": "Hallen Åre",
    "synonyms": [
      "HALLEN ÅRE"
    ],
    "lId": "01076",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 63.175555555555555,
      "lon": 14.094166666666668
    }
  },
  {
    "name": "Hallinden",
    "synonyms": [
      "HALLINDEN"
    ],
    "lId": "01129",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 58.458333333333336,
      "lon": 11.5225
    }
  },
  {
    "name": "Hallonbergen T-bana",
    "synonyms": [
      "HALLONBERGEN T-BANA"
    ],
    "lId": "21675",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.375277777777775,
      "lon": 17.969166666666666
    }
  },
  {
    "name": "Hallsberg",
    "synonyms": [
      "HALLSBERG",
      "HALLSBERG STN"
    ],
    "lId": "00077",
    "prio": 1,
    "pId": "074",
    "pos": {
      "lat": 59.066944444444445,
      "lon": 15.110277777777778
    }
  },
  {
    "name": "Hallsberg station norra",
    "synonyms": [
      "HALLSBERG STATION NORRA",
      "HALLSBERG STN N"
    ],
    "lId": "21096",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.06805555555556,
      "lon": 15.110833333333334
    }
  },
  {
    "name": "Hallsta",
    "synonyms": [
      "HALLSTA",
      "HALLSTA VÄGSKÄL",
      "HALLSTA VÆGSKÆL"
    ],
    "lId": "10524",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.7675,
      "lon": 16.560000000000002
    }
  },
  {
    "name": "Hallstahammar Eriksbergsmotet",
    "synonyms": [
      "HALLSTAHAMMAR ERIKSBERGSMOTET"
    ],
    "lId": "36391",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.591944444444444,
      "lon": 16.248611111111114
    }
  },
  {
    "name": "Hallstahammar Näs Ågatan",
    "synonyms": [
      "HALLSTAHAMMAR  NÄS ÅGATAN",
      "HALLSTAHAMMAR NÄS ÅGATAN"
    ],
    "lId": "44539",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.603611111111114,
      "lon": 16.21472222222222
    }
  },
  {
    "name": "Hallstavik station",
    "synonyms": [
      "HALLSTAVIK STATION",
      "HALLSTAVIK STN"
    ],
    "lId": "00662",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 60.05083333333333,
      "lon": 18.593888888888888
    }
  },
  {
    "name": "Halltorp",
    "synonyms": [
      "HALLTORP"
    ],
    "lId": "14205",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 56.50111111111111,
      "lon": 16.102777777777778
    }
  },
  {
    "name": "Hallunda T-bana",
    "synonyms": [
      "HALLUNDA T-BANA"
    ],
    "lId": "21732",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.24305555555556,
      "lon": 17.825555555555557
    }
  },
  {
    "name": "Hallviken vägskäl",
    "synonyms": [
      "HALLVIKEN VSK",
      "HALLVIKEN VÄGSKÄL",
      "HALLVIKEN VÆGSKÆL"
    ],
    "lId": "24252",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 63.730555555555554,
      "lon": 15.486944444444443
    }
  },
  {
    "name": "Halmstad C",
    "synonyms": [
      "HALMSTAD C"
    ],
    "lId": "00080",
    "prio": 1,
    "pId": "074",
    "pos": {
      "lat": 56.66916666666666,
      "lon": 12.864444444444445
    }
  },
  {
    "name": "Halmstad flygplats",
    "synonyms": [
      "HALMSTAD FLYGPLATS"
    ],
    "lId": "17041",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 56.68055555555555,
      "lon": 12.815000000000001
    }
  },
  {
    "name": "Halmstad Frennarp",
    "synonyms": [
      "HALMSTAD FRENNARP"
    ],
    "lId": "33498",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 56.69222222222222,
      "lon": 12.887222222222222
    }
  },
  {
    "name": "Halmstad Regementet",
    "synonyms": [
      "HALMSTAD REGEMENTET"
    ],
    "lId": "23622",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 56.69,
      "lon": 12.863055555555555
    }
  },
  {
    "name": "Halmstad Sjukhuset",
    "synonyms": [
      "HALMSTAD SJUKHUSET"
    ],
    "lId": "23620",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 56.68111111111111,
      "lon": 12.845
    }
  },
  {
    "name": "Hamburgsund",
    "synonyms": [
      "HAMBURGSUND"
    ],
    "lId": "01466",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 58.55222222222222,
      "lon": 11.273055555555556
    }
  },
  {
    "name": "Hammar kyrka Askersund",
    "synonyms": [
      "HAMMAR KYRKA ASKERSUND"
    ],
    "lId": "10530",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 58.816944444444445,
      "lon": 14.959166666666667
    }
  },
  {
    "name": "Hammar Åängavägen Kristianstad",
    "synonyms": [
      "HAMMAR ÅÄNGAVÄGEN KRISTIANSTAD",
      "HAMMAR ÅÆNGAVÆGEN KRISTIANSTAD"
    ],
    "lId": "30826",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 56.02861111111111,
      "lon": 14.196666666666667
    }
  },
  {
    "name": "Hammarby",
    "synonyms": [
      "HAMMARBY"
    ],
    "lId": "10503",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 60.543055555555554,
      "lon": 16.571944444444444
    }
  },
  {
    "name": "Hammarbyhöjden T-bana",
    "synonyms": [
      "HAMMARBYHÖJDEN T-BANA",
      "HAMMARBYHØJDEN T-BANA"
    ],
    "lId": "21695",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.29472222222222,
      "lon": 18.104444444444447
    }
  },
  {
    "name": "Hammarkullen",
    "synonyms": [
      "HAMMARKULLEN"
    ],
    "lId": "25636",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 57.780277777777776,
      "lon": 12.035555555555556
    }
  },
  {
    "name": "Hammarkullen Storås",
    "synonyms": [
      "HAMMARKL STORÅS",
      "HAMMARKULLEN STORÅS"
    ],
    "lId": "25688",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 57.78472222222222,
      "lon": 12.046666666666667
    }
  },
  {
    "name": "Hammarslund Engelska Vägen",
    "synonyms": [
      "HAMMARSLUND ENGELSKA VÄGEN",
      "HAMMARSLUND ENGELSKA VÆGEN"
    ],
    "lId": "30702",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 56.019999999999996,
      "lon": 14.193333333333333
    }
  },
  {
    "name": "Hammarstrand",
    "synonyms": [
      "HAMMARSTRAND",
      "HAMMARSTRND BST"
    ],
    "lId": "00423",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 63.10777777777778,
      "lon": 16.355555555555558
    }
  },
  {
    "name": "Hammenhög torget",
    "synonyms": [
      "HAMMENHÖG TORGET",
      "HAMMENHØG TORGET"
    ],
    "lId": "10532",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 55.503055555555555,
      "lon": 14.150277777777777
    }
  },
  {
    "name": "Hammerdal",
    "synonyms": [
      "HAMMERDAL",
      "HAMMERDAL BSTN"
    ],
    "lId": "00425",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 63.5825,
      "lon": 15.350277777777777
    }
  },
  {
    "name": "Hampetorp",
    "synonyms": [
      "HAMPETORP"
    ],
    "lId": "20291",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.138888888888886,
      "lon": 15.66861111111111
    }
  },
  {
    "name": "Hamra Ljusdal",
    "synonyms": [
      "HAMRA LJUSDAL"
    ],
    "lId": "27336",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 61.658055555555556,
      "lon": 14.994444444444444
    }
  },
  {
    "name": "Hamra Rimforsa",
    "synonyms": [
      "HAMRA RIMFORSA"
    ],
    "lId": "25021",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 58.174166666666665,
      "lon": 15.675833333333333
    }
  },
  {
    "name": "Hamrafjället",
    "synonyms": [
      "HAMRAFJÄLLET",
      "HAMRAFJÆLLET"
    ],
    "lId": "13319",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 62.57416666666667,
      "lon": 12.227222222222222
    }
  },
  {
    "name": "Hamrångefjärden",
    "synonyms": [
      "HAMRÅNGEFJÄRDEN",
      "HAMRÅNGEFJÆRDEN"
    ],
    "lId": "00596",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 60.897777777777776,
      "lon": 17.069166666666668
    }
  },
  {
    "name": "Hanaskog Hantverksgatan",
    "synonyms": [
      "HANASKOG HANTVERKSGATAN"
    ],
    "lId": "10583",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 56.15361111111111,
      "lon": 14.09888888888889
    }
  },
  {
    "name": "Handen station",
    "synonyms": [
      "HANDEN STATION"
    ],
    "lId": "00699",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.1675,
      "lon": 18.134444444444444
    }
  },
  {
    "name": "Haninge Vega",
    "synonyms": [
      "HANINGE VEGA"
    ],
    "lId": "69526",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.193888888888885,
      "lon": 18.141388888888887
    }
  },
  {
    "name": "Hannäs kyrka",
    "synonyms": [
      "HANNÄS KYRKA",
      "HANNÆS KYRKA"
    ],
    "lId": "10541",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 58.15333333333333,
      "lon": 16.326944444444443
    }
  },
  {
    "name": "Haparanda/Tornio RC",
    "synonyms": [
      "HAPARANDA/TORNIO RC",
      "HAPARANDATORNIO"
    ],
    "lId": "23338",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 65.84277777777777,
      "lon": 24.138055555555557
    }
  },
  {
    "name": "Hara Östersund",
    "synonyms": [
      "HARA ÖSTERSUND",
      "HARA ØSTERSUND"
    ],
    "lId": "18486",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 63.03861111111111,
      "lon": 14.464722222222221
    }
  },
  {
    "name": "Harads Shell",
    "synonyms": [
      "HARADS SHELL"
    ],
    "lId": "14922",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 66.08416666666666,
      "lon": 20.954166666666666
    }
  },
  {
    "name": "Harbo centrum",
    "synonyms": [
      "HARBO CENTRUM"
    ],
    "lId": "11632",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 60.105000000000004,
      "lon": 17.199166666666667
    }
  },
  {
    "name": "Harg Brukshandeln",
    "synonyms": [
      "HARG BRUKSHANDELN",
      "HARG BRUKSHANDL"
    ],
    "lId": "12754",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 60.18138888888889,
      "lon": 18.399444444444445
    }
  },
  {
    "name": "Hargshamn",
    "synonyms": [
      "HARGSHAMN",
      "HARGSHAMN STNV"
    ],
    "lId": "01078",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 60.168055555555554,
      "lon": 18.471666666666664
    }
  },
  {
    "name": "Harkskär",
    "synonyms": [
      "HARKSKÄR",
      "HARKSKÆR"
    ],
    "lId": "19262",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 60.766666666666666,
      "lon": 17.32361111111111
    }
  },
  {
    "name": "Harlösa busstation",
    "synonyms": [
      "HARLÖSA BSTN",
      "HARLÖSA BUSSTATION",
      "HARLØSA BSTN",
      "HARLØSA BUSSTATION"
    ],
    "lId": "16645",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 55.715,
      "lon": 13.527500000000002
    }
  },
  {
    "name": "Harmånger",
    "synonyms": [
      "HARMÅNGER",
      "HARMÅNGER TORG"
    ],
    "lId": "00599",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 61.92805555555555,
      "lon": 17.216944444444444
    }
  },
  {
    "name": "Harplinge",
    "synonyms": [
      "HARPLINGE",
      "HARPLINGE STN"
    ],
    "lId": "00261",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 56.744166666666665,
      "lon": 12.724722222222223
    }
  },
  {
    "name": "Hassela busstation",
    "synonyms": [
      "HASSELA BUSSTATION"
    ],
    "lId": "00371",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 62.11,
      "lon": 16.70638888888889
    }
  },
  {
    "name": "Hassela Ski Resort",
    "synonyms": [
      "HASSELA SKI RESORT"
    ],
    "lId": "18946",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 62.080000000000005,
      "lon": 16.72722222222222
    }
  },
  {
    "name": "Hasselfors Torget",
    "synonyms": [
      "HASSELFORS TORGET"
    ],
    "lId": "00794",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.08555555555556,
      "lon": 14.651666666666667
    }
  },
  {
    "name": "Hasseludden",
    "synonyms": [
      "HASSELUDDEN"
    ],
    "lId": "26544",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.34722222222222,
      "lon": 18.243333333333336
    }
  },
  {
    "name": "Hasslarp torget",
    "synonyms": [
      "HASSLARP TORGET"
    ],
    "lId": "16646",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 56.13666666666666,
      "lon": 12.8125
    }
  },
  {
    "name": "Hasslerör station",
    "synonyms": [
      "HASSLERÖR STATION",
      "HASSLERÖR STN",
      "HASSLERØR STATION",
      "HASSLERØR STN"
    ],
    "lId": "01079",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 58.750277777777775,
      "lon": 13.939444444444444
    }
  },
  {
    "name": "Hasslö",
    "synonyms": [
      "HASSLÖ",
      "HASSLÖ F MÅNS V",
      "HASSLØ",
      "HASSLØ F MÅNS V"
    ],
    "lId": "00017",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 56.11277777777778,
      "lon": 15.469444444444445
    }
  },
  {
    "name": "Hasslöv",
    "synonyms": [
      "HASSLÖV",
      "HASSLØV"
    ],
    "lId": "17073",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 56.41361111111111,
      "lon": 13.005
    }
  },
  {
    "name": "Havdhem",
    "synonyms": [
      "HAVDHEM",
      "HAVDHEM FDKIOSK"
    ],
    "lId": "01080",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 57.16083333333333,
      "lon": 18.333055555555557
    }
  },
  {
    "name": "Haverdal",
    "synonyms": [
      "HAVERDAL",
      "HAVERDAL HAVERD"
    ],
    "lId": "00255",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 56.72666666666667,
      "lon": 12.665833333333333
    }
  },
  {
    "name": "Haverdalsbro",
    "synonyms": [
      "HAVERDALSBRO"
    ],
    "lId": "17076",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 56.724722222222226,
      "lon": 12.702222222222222
    }
  },
  {
    "name": "Havstenssund",
    "synonyms": [
      "HAVSTENSSUND"
    ],
    "lId": "16238",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 58.75555555555555,
      "lon": 11.181944444444444
    }
  },
  {
    "name": "Heberg",
    "synonyms": [
      "HEBERG",
      "HEBERG STN"
    ],
    "lId": "01467",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 56.87916666666667,
      "lon": 12.629722222222222
    }
  },
  {
    "name": "Heby station",
    "synonyms": [
      "HEBY STATION",
      "HEBY STN"
    ],
    "lId": "00674",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.94027777777777,
      "lon": 16.852777777777778
    }
  },
  {
    "name": "Hedared",
    "synonyms": [
      "HEDARED"
    ],
    "lId": "12368",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 57.80777777777777,
      "lon": 12.7525
    }
  },
  {
    "name": "Hede",
    "synonyms": [
      "HEDE",
      "HEDE FÄRGHANDEL",
      "HEDE FÆRGHANDEL"
    ],
    "lId": "00493",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 62.41888888888889,
      "lon": 13.515555555555556
    }
  },
  {
    "name": "Hedekas",
    "synonyms": [
      "HEDEKAS"
    ],
    "lId": "01468",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 58.644444444444446,
      "lon": 11.779722222222222
    }
  },
  {
    "name": "Hedemora",
    "synonyms": [
      "HEDEMORA",
      "HEDEMORA STN"
    ],
    "lId": "00042",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 60.27388888888889,
      "lon": 15.980277777777777
    }
  },
  {
    "name": "Hedenäset",
    "synonyms": [
      "HEDENÄSET",
      "HEDENÄSET ICA",
      "HEDENÆSET",
      "HEDENÆSET ICA"
    ],
    "lId": "01081",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 66.23361111111112,
      "lon": 23.679444444444446
    }
  },
  {
    "name": "Hedeskoga",
    "synonyms": [
      "HEDESKOGA"
    ],
    "lId": "16648",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 55.45166666666667,
      "lon": 13.801111111111112
    }
  },
  {
    "name": "Hedesunda",
    "synonyms": [
      "HEDESUNDA",
      "HEDESUNDA BSTN"
    ],
    "lId": "00631",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 60.39361111111111,
      "lon": 17.00611111111111
    }
  },
  {
    "name": "Hedkärra",
    "synonyms": [
      "HEDKÄRRA"
    ],
    "lId": "10567",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.96611111111111,
      "lon": 15.763333333333334
    }
  },
  {
    "name": "Heestrand",
    "synonyms": [
      "HEESTRAND"
    ],
    "lId": "16251",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 58.51416666666667,
      "lon": 11.280000000000001
    }
  },
  {
    "name": "Hegra",
    "synonyms": [
      "HEGRA"
    ],
    "lId": "01210",
    "prio": 0,
    "pId": "076",
    "pos": {
      "lat": 63.43333333333333,
      "lon": 11.231388888888889
    }
  },
  {
    "name": "Heimdal",
    "synonyms": [
      "HEIMDAL"
    ],
    "lId": "01122",
    "prio": 0,
    "pId": "076",
    "pos": {
      "lat": 63.30222222222222,
      "lon": 10.308333333333334
    }
  },
  {
    "name": "Hejde",
    "synonyms": [
      "HEJDE",
      "HEJDE TASS"
    ],
    "lId": "01131",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 57.41222222222222,
      "lon": 18.350555555555555
    }
  },
  {
    "name": "Helenelund",
    "synonyms": [
      "HELENELUND",
      "HELENELUND STN"
    ],
    "lId": "00701",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.409444444444446,
      "lon": 17.961388888888887
    }
  },
  {
    "name": "Helgum affären",
    "synonyms": [
      "HELGUM AFFÄREN",
      "HELGUM AFFÆREN"
    ],
    "lId": "15163",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 63.151666666666664,
      "lon": 16.953055555555554
    }
  },
  {
    "name": "Hell",
    "synonyms": [
      "HELL"
    ],
    "lId": "01208",
    "prio": 0,
    "pId": "076",
    "pos": {
      "lat": 63.446666666666665,
      "lon": 10.897777777777778
    }
  },
  {
    "name": "Hellerup",
    "synonyms": [
      "HELLERUP"
    ],
    "lId": "00655",
    "prio": 0,
    "pId": "086",
    "pos": {
      "lat": 55.73111111111111,
      "lon": 12.567222222222222
    }
  },
  {
    "name": "Helsingborg C",
    "synonyms": [
      "HELSINGBORG C"
    ],
    "lId": "00044",
    "prio": 1,
    "pId": "074",
    "pos": {
      "lat": 56.04416666666666,
      "lon": 12.694166666666668
    }
  },
  {
    "name": "Helsingborg Arena",
    "synonyms": [
      "HELSINGBORG ARENA"
    ],
    "lId": "68817",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 56.052499999999995,
      "lon": 12.705555555555556
    }
  },
  {
    "name": "Hemavan",
    "synonyms": [
      "HEMAVAN"
    ],
    "lId": "00319",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 65.81944444444444,
      "lon": 15.084166666666667
    }
  },
  {
    "name": "Hemfosa",
    "synonyms": [
      "HEMFOSA",
      "HEMFOSA STN"
    ],
    "lId": "30017",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.06861111111112,
      "lon": 17.976388888888888
    }
  },
  {
    "name": "Hemling Uno-X",
    "synonyms": [
      "HEMLING UNO-X"
    ],
    "lId": "15164",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 63.65361111111111,
      "lon": 18.54388888888889
    }
  },
  {
    "name": "Hemmesta",
    "synonyms": [
      "HEMMESTA",
      "HEMMESTA VSK"
    ],
    "lId": "01082",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.32638888888889,
      "lon": 18.503611111111113
    }
  },
  {
    "name": "Hemse",
    "synonyms": [
      "HEMSE",
      "HEMSE BSTN"
    ],
    "lId": "00998",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 57.23777777777778,
      "lon": 18.379444444444445
    }
  },
  {
    "name": "Hennan affären",
    "synonyms": [
      "HENNAN AFFÄREN",
      "HENNAN AFFÆREN"
    ],
    "lId": "22648",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 62.02361111111111,
      "lon": 15.904444444444445
    }
  },
  {
    "name": "Henriksdal",
    "synonyms": [
      "HENRIKSDAL",
      "HENRIKSDAL STN"
    ],
    "lId": "24806",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.31222222222222,
      "lon": 18.108055555555556
    }
  },
  {
    "name": "Henån",
    "synonyms": [
      "HENÅN",
      "HENÅN BSTN"
    ],
    "lId": "00515",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 58.23444444444444,
      "lon": 11.681111111111111
    }
  },
  {
    "name": "Herrljunga",
    "synonyms": [
      "HERRLJUNGA",
      "HERRLJUNGA STN"
    ],
    "lId": "00040",
    "prio": 1,
    "pId": "074",
    "pos": {
      "lat": 58.07916666666667,
      "lon": 13.021111111111113
    }
  },
  {
    "name": "Herrskogen Erikslundsv.",
    "synonyms": [
      "HERRSKOGEN ERIKSLUNDSV."
    ],
    "lId": "44535",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.52777777777778,
      "lon": 16.238055555555558
    }
  },
  {
    "name": "Herräng",
    "synonyms": [
      "HERRÄNG",
      "HERRÆNG"
    ],
    "lId": "01132",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 60.13111111111111,
      "lon": 18.64611111111111
    }
  },
  {
    "name": "Herrö",
    "synonyms": [
      "HERRÖ",
      "HERRØ"
    ],
    "lId": "13344",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 62.01611111111111,
      "lon": 14.191944444444445
    }
  },
  {
    "name": "Hestra",
    "synonyms": [
      "HESTRA",
      "HESTRA STN"
    ],
    "lId": "00089",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 57.44305555555555,
      "lon": 13.595833333333333
    }
  },
  {
    "name": "Hestra Östergötland",
    "synonyms": [
      "HESTRA ÖSTERGÖTLAND",
      "HESTRA ØSTERGØTLAND"
    ],
    "lId": "04003",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 57.95722222222223,
      "lon": 15.06861111111111
    }
  },
  {
    "name": "Hillared",
    "synonyms": [
      "HILLARED",
      "HILLARED SOLVÄG",
      "HILLARED SOLVÆG"
    ],
    "lId": "12190",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 57.63027777777778,
      "lon": 13.157777777777778
    }
  },
  {
    "name": "Hillerstorp",
    "synonyms": [
      "HILLERSTORP",
      "HILLERSTORP STN"
    ],
    "lId": "00966",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 57.31388888888888,
      "lon": 13.883055555555556
    }
  },
  {
    "name": "Himle",
    "synonyms": [
      "HIMLE"
    ],
    "lId": "10581",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 57.07166666666667,
      "lon": 12.365555555555556
    }
  },
  {
    "name": "Hindås",
    "synonyms": [
      "HINDAS",
      "HINDÅS",
      "HINDÅS STN"
    ],
    "lId": "00207",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 57.70444444444445,
      "lon": 12.45111111111111
    }
  },
  {
    "name": "Hishult",
    "synonyms": [
      "HISHULT"
    ],
    "lId": "17079",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 56.42583333333333,
      "lon": 13.316666666666666
    }
  },
  {
    "name": "Hittarp",
    "synonyms": [
      "HITTARP",
      "HITTARP SUNDSLI"
    ],
    "lId": "01083",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 56.09666666666667,
      "lon": 12.643333333333333
    }
  },
  {
    "name": "Hjo",
    "synonyms": [
      "HJO",
      "HJO BSTN"
    ],
    "lId": "00608",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 58.30555555555555,
      "lon": 14.293611111111112
    }
  },
  {
    "name": "Hjorted",
    "synonyms": [
      "HJORTED"
    ],
    "lId": "20055",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 57.62027777777778,
      "lon": 16.306944444444444
    }
  },
  {
    "name": "Hjortkvarn kiosken",
    "synonyms": [
      "HJORKVARN KIOS",
      "HJORTKVARN KIOS",
      "HJORTKVARN KIOSKEN"
    ],
    "lId": "10586",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 58.894999999999996,
      "lon": 15.432222222222222
    }
  },
  {
    "name": "Hjortsberga",
    "synonyms": [
      "HJORTSBERGA"
    ],
    "lId": "10587",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 56.91444444444444,
      "lon": 14.455277777777777
    }
  },
  {
    "name": "Hjulsjö kyrka",
    "synonyms": [
      "HJULSJÖ KYRKA",
      "HJULSJØ KYRKA"
    ],
    "lId": "10589",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.784166666666664,
      "lon": 14.777500000000002
    }
  },
  {
    "name": "Hjulsta T-bana",
    "synonyms": [
      "HJULSTA T-BANA"
    ],
    "lId": "21678",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.39611111111111,
      "lon": 17.8875
    }
  },
  {
    "name": "Hjuvik",
    "synonyms": [
      "HJUVIK"
    ],
    "lId": "21005",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 57.70472222222222,
      "lon": 11.71111111111111
    }
  },
  {
    "name": "Hjällbo",
    "synonyms": [
      "HJÄLLBO",
      "HJÆLLBO"
    ],
    "lId": "01469",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 57.76861111111111,
      "lon": 12.0225
    }
  },
  {
    "name": "Hjälmared Alle",
    "synonyms": [
      "HJÄLMARED ALLE",
      "HJÄLMARED ALLÉ",
      "HJÆLMARED ALLE",
      "HJÆLMARED ALLÉ"
    ],
    "lId": "61181",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 57.89472222222222,
      "lon": 12.549166666666666
    }
  },
  {
    "name": "Hjälmseryd Nya",
    "synonyms": [
      "HJÄLMSERYD NYA",
      "HJÆLMSERYD NYA"
    ],
    "lId": "23249",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 57.244166666666665,
      "lon": 14.51388888888889
    }
  },
  {
    "name": "Hjälmshult",
    "synonyms": [
      "HJÄLMSHULT",
      "HJÆLMSHULT"
    ],
    "lId": "16671",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 56.125277777777775,
      "lon": 12.694166666666668
    }
  },
  {
    "name": "Hjältevad",
    "synonyms": [
      "HJÄLTEVAD",
      "HJÄLTEVAD STN",
      "HJÆLTEVAD",
      "HJÆLTEVAD STN"
    ],
    "lId": "00967",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 57.62888888888889,
      "lon": 15.343611111111112
    }
  },
  {
    "name": "Hjärnarp",
    "synonyms": [
      "HJÄRNARP",
      "HJÆRNARP"
    ],
    "lId": "10595",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 56.31805555555556,
      "lon": 12.915555555555557
    }
  },
  {
    "name": "Hjärsås",
    "synonyms": [
      "HJÄRSÅS",
      "HJÄRSÅS KYRKA",
      "HJÆRSÅS",
      "HJÆRSÅS KYRKA"
    ],
    "lId": "10596",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 56.20722222222223,
      "lon": 14.149722222222222
    }
  },
  {
    "name": "Hjärup",
    "synonyms": [
      "HJÄRUP",
      "HJÄRUP STN",
      "HJÆRUP",
      "HJÆRUP STN"
    ],
    "lId": "00942",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 55.67388888888889,
      "lon": 13.136388888888888
    }
  },
  {
    "name": "Hofors centrum",
    "synonyms": [
      "HOFORS CENTRUM"
    ],
    "lId": "00350",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 60.54472222222222,
      "lon": 16.291666666666668
    }
  },
  {
    "name": "Hofors station",
    "synonyms": [
      "HOFORS STATION"
    ],
    "lId": "00218",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 60.56944444444445,
      "lon": 16.266111111111112
    }
  },
  {
    "name": "Hofterup Hänkelstorp",
    "synonyms": [
      "HOFTERUP HÄNKELSTORP",
      "HOFTERUP HÆNKELSTORP"
    ],
    "lId": "16682",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 55.80083333333333,
      "lon": 12.987499999999999
    }
  },
  {
    "name": "Hogstad",
    "synonyms": [
      "HOGSTAD"
    ],
    "lId": "10601",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 58.331388888888895,
      "lon": 15.027777777777779
    }
  },
  {
    "name": "Hok",
    "synonyms": [
      "HOK",
      "HOK STN"
    ],
    "lId": "00252",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 57.51416666666667,
      "lon": 14.275
    }
  },
  {
    "name": "Holm bygdegård",
    "synonyms": [
      "HOLM BYGDEGÅRD"
    ],
    "lId": "17080",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 56.731944444444444,
      "lon": 12.860555555555555
    }
  },
  {
    "name": "Holmeja väg 108",
    "synonyms": [
      "HOLMEJA VÄG 108",
      "HOLMEJA VÆG 108"
    ],
    "lId": "16676",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 55.556666666666665,
      "lon": 13.2575
    }
  },
  {
    "name": "Holmsjö station",
    "synonyms": [
      "HOLMSJÖ STATION",
      "HOLMSJÖ STN",
      "HOLMSJØ STATION",
      "HOLMSJØ STN"
    ],
    "lId": "00771",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 56.42027777777778,
      "lon": 15.543888888888889
    }
  },
  {
    "name": "Holmsund centrum",
    "synonyms": [
      "HOLMSUND CENTRUM",
      "HOLMSUND CM",
      "HOLMSUND HFTORG"
    ],
    "lId": "00329",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 63.7075,
      "lon": 20.36388888888889
    }
  },
  {
    "name": "Holmsund Minkvägen",
    "synonyms": [
      "HOLMSUND MINKVÄGEN",
      "HOLMSUND MINKVÆGEN"
    ],
    "lId": "25975",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 63.71333333333334,
      "lon": 20.38722222222222
    }
  },
  {
    "name": "Holmsveden",
    "synonyms": [
      "HOLMSVEDEN",
      "HOLMSVEDEN STN"
    ],
    "lId": "00632",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 61.11805555555556,
      "lon": 16.721666666666664
    }
  },
  {
    "name": "Holsbybrunn centrum",
    "synonyms": [
      "HOLSBYBRUNN CENTRUM",
      "HOLSBYBRUNN CM"
    ],
    "lId": "10609",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 57.43861111111111,
      "lon": 15.204166666666666
    }
  },
  {
    "name": "Hommelvik",
    "synonyms": [
      "HOMMELVIK"
    ],
    "lId": "01207",
    "prio": 0,
    "pId": "076",
    "pos": {
      "lat": 63.41833333333333,
      "lon": 10.828888888888889
    }
  },
  {
    "name": "Horda Järnvägsgatan",
    "synonyms": [
      "HORDA JÄRNVÄGSGATAN",
      "HORDA JÆRNVÆGSGATAN"
    ],
    "lId": "10610",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 57.03944444444444,
      "lon": 14.257222222222222
    }
  },
  {
    "name": "Horn",
    "synonyms": [
      "HORN",
      "HORN TORGET"
    ],
    "lId": "00845",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 57.89833333333333,
      "lon": 15.83888888888889
    }
  },
  {
    "name": "Horna gamla stationen",
    "synonyms": [
      "HORNA GAMLA STATIONEN",
      "HORNA GAMLA STN"
    ],
    "lId": "30693",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 55.961666666666666,
      "lon": 14.280833333333334
    }
  },
  {
    "name": "Horndal Svänghjulet",
    "synonyms": [
      "HORNDAL SVÄNGHJULET"
    ],
    "lId": "12912",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 60.29555555555555,
      "lon": 16.407777777777778
    }
  },
  {
    "name": "Horndals Bruk station",
    "synonyms": [
      "HORNDALS BRUK STATION"
    ],
    "lId": "00630",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 60.295833333333334,
      "lon": 16.413055555555555
    }
  },
  {
    "name": "Hornkullen station",
    "synonyms": [
      "HORNKULLEN STATION",
      "HORNKULLEN STN"
    ],
    "lId": "20175",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.62555555555556,
      "lon": 14.290833333333333
    }
  },
  {
    "name": "Hornstull T-bana",
    "synonyms": [
      "HORNSTULL T-BANA"
    ],
    "lId": "21658",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.31583333333333,
      "lon": 18.03388888888889
    }
  },
  {
    "name": "Hornöberget E4",
    "synonyms": [
      "HORNÖBERGET E4",
      "HORNØBERGET E4"
    ],
    "lId": "08781",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 62.80638888888888,
      "lon": 17.951666666666664
    }
  },
  {
    "name": "Horred",
    "synonyms": [
      "HORRED",
      "HORRED STN"
    ],
    "lId": "00402",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 57.35333333333333,
      "lon": 12.477222222222222
    }
  },
  {
    "name": "Hortlax skolan",
    "synonyms": [
      "HORTLAX SKOLAN"
    ],
    "lId": "14901",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 65.28305555555555,
      "lon": 21.406388888888888
    }
  },
  {
    "name": "Hoting",
    "synonyms": [
      "HOTING",
      "HOTING STN"
    ],
    "lId": "00434",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 64.11583333333333,
      "lon": 16.2
    }
  },
  {
    "name": "Hov",
    "synonyms": [
      "HOV",
      "HOV KYRKA"
    ],
    "lId": "01470",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 56.43472222222222,
      "lon": 12.729444444444445
    }
  },
  {
    "name": "Hova",
    "synonyms": [
      "HOVA"
    ],
    "lId": "00484",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 58.85444444444445,
      "lon": 14.215277777777777
    }
  },
  {
    "name": "Hova Torget",
    "synonyms": [
      "HOVA TORGET"
    ],
    "lId": "16451",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 58.85805555555556,
      "lon": 14.216666666666667
    }
  },
  {
    "name": "Hovenäset",
    "synonyms": [
      "HOVENÄSET",
      "HOVENÆSET"
    ],
    "lId": "16221",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 58.370555555555555,
      "lon": 11.296388888888888
    }
  },
  {
    "name": "Hovmantorp",
    "synonyms": [
      "HOVMANTORP",
      "HOVMANTORP STN"
    ],
    "lId": "00511",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 56.78583333333333,
      "lon": 15.140555555555554
    }
  },
  {
    "name": "Hovslätt",
    "synonyms": [
      "HOVSLÄTT",
      "HOVSLÄTT STN",
      "HOVSLÆTT",
      "HOVSLÆTT STN"
    ],
    "lId": "01084",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 57.735,
      "lon": 14.124166666666667
    }
  },
  {
    "name": "Hovsta station",
    "synonyms": [
      "HOVSTA STATION",
      "HOVSTA STN"
    ],
    "lId": "25719",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.347500000000004,
      "lon": 15.218333333333334
    }
  },
  {
    "name": "Hovås",
    "synonyms": [
      "HOVÅS",
      "HOVÅS NEDRE"
    ],
    "lId": "15572",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 57.61694444444444,
      "lon": 11.939444444444444
    }
  },
  {
    "name": "Huaröd",
    "synonyms": [
      "HUARÖD",
      "HUARØD"
    ],
    "lId": "22130",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 55.84027777777778,
      "lon": 13.969166666666666
    }
  },
  {
    "name": "Huddinge",
    "synonyms": [
      "HUDDINGE",
      "HUDDINGE STN"
    ],
    "lId": "00702",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.23722222222222,
      "lon": 17.979999999999997
    }
  },
  {
    "name": "Huddinge sjukhus",
    "synonyms": [
      "HUDDINGE SJH",
      "HUDDINGE SJUKHUS"
    ],
    "lId": "01178",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.22222222222222,
      "lon": 17.9375
    }
  },
  {
    "name": "Huddunge",
    "synonyms": [
      "HUDDUNGE"
    ],
    "lId": "18252",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 60.049166666666665,
      "lon": 16.982777777777777
    }
  },
  {
    "name": "Hudiksvall",
    "synonyms": [
      "HUDIKSVALL",
      "HUDIKSVALL STN"
    ],
    "lId": "00187",
    "prio": 1,
    "pId": "074",
    "pos": {
      "lat": 61.724444444444444,
      "lon": 17.10888888888889
    }
  },
  {
    "name": "Hudiksvall Sjukhuset",
    "synonyms": [
      "HUDIKSVALL SJUKHUSET"
    ],
    "lId": "06734",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 61.72944444444445,
      "lon": 17.100833333333334
    }
  },
  {
    "name": "Hudiksvalls stadszon",
    "synonyms": [
      "HUDIKSVALLS STADSZON"
    ],
    "lId": "79014",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 61.724444444444444,
      "lon": 17.10888888888889
    }
  },
  {
    "name": "Hult väg 40",
    "synonyms": [
      "HULT VÄG 40"
    ],
    "lId": "20753",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 57.63527777777778,
      "lon": 15.128055555555555
    }
  },
  {
    "name": "Hultsfred Festivalen",
    "synonyms": [
      "HULTSFRED FESTIVALEN"
    ],
    "lId": "25871",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 57.49611111111111,
      "lon": 15.862499999999999
    }
  },
  {
    "name": "Hultsfred station",
    "synonyms": [
      "HULTSFRED STATION",
      "HULTSFRED STN"
    ],
    "lId": "00348",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 57.486666666666665,
      "lon": 15.846666666666668
    }
  },
  {
    "name": "Hulu",
    "synonyms": [
      "HULU"
    ],
    "lId": "12453",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 57.69944444444444,
      "lon": 13.296944444444444
    }
  },
  {
    "name": "Humlebaek",
    "synonyms": [
      "HUMLEBAEK"
    ],
    "lId": "00666",
    "prio": 0,
    "pId": "086",
    "pos": {
      "lat": 55.96361111111111,
      "lon": 12.533055555555556
    }
  },
  {
    "name": "Hummelsta",
    "synonyms": [
      "HUMMELSTA",
      "HUMMELSTA CM"
    ],
    "lId": "01085",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.62583333333333,
      "lon": 16.943333333333335
    }
  },
  {
    "name": "Hunnebostrand",
    "synonyms": [
      "HUNNEBOSTRAND"
    ],
    "lId": "00357",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 58.44166666666666,
      "lon": 11.303611111111111
    }
  },
  {
    "name": "Hurva",
    "synonyms": [
      "HURVA",
      "HURVA E22"
    ],
    "lId": "01471",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 55.791666666666664,
      "lon": 13.441944444444445
    }
  },
  {
    "name": "Husarö",
    "synonyms": [
      "HUSARÖ",
      "HUSARØ"
    ],
    "lId": "20692",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.50194444444445,
      "lon": 18.843888888888888
    }
  },
  {
    "name": "Husby T-bana",
    "synonyms": [
      "HUSBY T-BANA"
    ],
    "lId": "21676",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.41,
      "lon": 17.925555555555558
    }
  },
  {
    "name": "Huskvarna",
    "synonyms": [
      "HUSKVARNA"
    ],
    "lId": "00620",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 57.782222222222224,
      "lon": 14.265277777777778
    }
  },
  {
    "name": "Husum station",
    "synonyms": [
      "HUSUM STATION",
      "HUSUM STN"
    ],
    "lId": "01584",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 63.34388888888889,
      "lon": 19.155555555555555
    }
  },
  {
    "name": "Huså",
    "synonyms": [
      "HUSÅ"
    ],
    "lId": "25925",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 63.493611111111115,
      "lon": 13.122777777777777
    }
  },
  {
    "name": "Husås",
    "synonyms": [
      "HUSÅS"
    ],
    "lId": "13426",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 63.424166666666665,
      "lon": 14.760555555555555
    }
  },
  {
    "name": "Huvudsta T-bana",
    "synonyms": [
      "HUVUDSTA T-BANA"
    ],
    "lId": "21670",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.349444444444444,
      "lon": 17.985555555555557
    }
  },
  {
    "name": "Hybo station",
    "synonyms": [
      "HYBO STATION"
    ],
    "lId": "10631",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 61.79694444444444,
      "lon": 16.191944444444445
    }
  },
  {
    "name": "Hycklinge kvarn",
    "synonyms": [
      "HYCKLINGE KVARN"
    ],
    "lId": "10632",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 57.92194444444444,
      "lon": 15.917222222222222
    }
  },
  {
    "name": "Hyllinge torget",
    "synonyms": [
      "HYLLINGE TORGET"
    ],
    "lId": "10634",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 56.10166666666667,
      "lon": 12.865555555555556
    }
  },
  {
    "name": "Hyllstofta",
    "synonyms": [
      "HYLLSTOFTA"
    ],
    "lId": "04098",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 56.1325,
      "lon": 13.296111111111111
    }
  },
  {
    "name": "Hylta",
    "synonyms": [
      "HYLTA"
    ],
    "lId": "04111",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 56.237500000000004,
      "lon": 14.206388888888888
    }
  },
  {
    "name": "Hyltebruk",
    "synonyms": [
      "HYLTEBRUK",
      "HYLTEBRUK STN"
    ],
    "lId": "00625",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 56.998333333333335,
      "lon": 13.236944444444443
    }
  },
  {
    "name": "Hyssna",
    "synonyms": [
      "HYSSNA",
      "HYSSNA HANDEL"
    ],
    "lId": "12170",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 57.54833333333333,
      "lon": 12.532222222222224
    }
  },
  {
    "name": "Håbo-Tibble kyrkby",
    "synonyms": [
      "H-TIBBLE KYRKBY",
      "HÅBO-TIBBLE KYRKBY"
    ],
    "lId": "67280",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.58638888888889,
      "lon": 17.65972222222222
    }
  },
  {
    "name": "Håby terminal",
    "synonyms": [
      "HÅBY TERMINAL"
    ],
    "lId": "25000",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 58.48861111111111,
      "lon": 11.627777777777778
    }
  },
  {
    "name": "Håkantorp",
    "synonyms": [
      "HAKANTORP",
      "HÅKANTORP",
      "HÅKANTORP STN"
    ],
    "lId": "00083",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 58.30694444444444,
      "lon": 12.907222222222222
    }
  },
  {
    "name": "Håksberg",
    "synonyms": [
      "HÅKSBERG"
    ],
    "lId": "12959",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 60.18416666666666,
      "lon": 15.207777777777777
    }
  },
  {
    "name": "Hålland E14",
    "synonyms": [
      "HÅLLAND E14"
    ],
    "lId": "13289",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 63.312777777777775,
      "lon": 13.316666666666666
    }
  },
  {
    "name": "Hållnäs kyrka",
    "synonyms": [
      "HÅLLNÄS KYRKA",
      "HÅLLNÆS KYRKA"
    ],
    "lId": "18234",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 60.534166666666664,
      "lon": 17.883333333333333
    }
  },
  {
    "name": "Hållsta",
    "synonyms": [
      "HÅLLSTA",
      "HÅLLSTA STN"
    ],
    "lId": "01428",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.29194444444444,
      "lon": 16.458333333333332
    }
  },
  {
    "name": "Hålsjö affären",
    "synonyms": [
      "HÅLSJÖ AFFÄREN",
      "HÅLSJØ AFFÆREN"
    ],
    "lId": "25930",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 61.825833333333335,
      "lon": 16.779999999999998
    }
  },
  {
    "name": "Håmojåkk",
    "synonyms": [
      "HÅMOJÅKK",
      "HÅMOJÅKK STN"
    ],
    "lId": "00305",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 67.3236111111111,
      "lon": 20.173055555555557
    }
  },
  {
    "name": "Hånger skola",
    "synonyms": [
      "HÅNGER SKOLA"
    ],
    "lId": "25973",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 57.084722222222226,
      "lon": 13.961388888888887
    }
  },
  {
    "name": "Håslöv E6",
    "synonyms": [
      "HÅSLÖV E6",
      "HÅSLØV E6"
    ],
    "lId": "44279",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 55.436388888888885,
      "lon": 13.040833333333333
    }
  },
  {
    "name": "Håverud herrgården",
    "synonyms": [
      "HÅVERUD HERRGÅRDEN"
    ],
    "lId": "25158",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 58.82166666666667,
      "lon": 12.416111111111112
    }
  },
  {
    "name": "Hägernäs",
    "synonyms": [
      "HÄGERNÄS",
      "HÄGERNÄS STN",
      "HÆGERNÆS",
      "HÆGERNÆS STN"
    ],
    "lId": "20192",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.450833333333335,
      "lon": 18.124166666666667
    }
  },
  {
    "name": "Hägerstensåsen T-bana",
    "synonyms": [
      "HÄGERSTENSÅSEN T-BANA",
      "HÆGERSTENSÅSEN T-BANA"
    ],
    "lId": "21717",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.29555555555555,
      "lon": 17.978888888888886
    }
  },
  {
    "name": "Häggdånger kyrka",
    "synonyms": [
      "HÄGGDÅNGER KYRKA",
      "HÆGGDÅNGER KYRKA"
    ],
    "lId": "15173",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 62.54138888888889,
      "lon": 17.819166666666668
    }
  },
  {
    "name": "Häggeby kyrka",
    "synonyms": [
      "HÄGGEBY KYRKA",
      "HÆGGEBY KYRKA"
    ],
    "lId": "12854",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.657777777777774,
      "lon": 17.546944444444446
    }
  },
  {
    "name": "Häggenås Häggesta",
    "synonyms": [
      "HÄGGENÅS HÄGGESTA",
      "HÄGGENÅS HÄGSTA",
      "HÆGGENÅS HÆGGESTA",
      "HÆGGENÅS HÆGSTA"
    ],
    "lId": "24251",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 63.39055555555556,
      "lon": 14.90388888888889
    }
  },
  {
    "name": "Häggsjövik",
    "synonyms": [
      "HÄGGSJÖVIK",
      "HÆGGSJØVIK"
    ],
    "lId": "13396",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 63.906666666666666,
      "lon": 14.213333333333333
    }
  },
  {
    "name": "Häggvik station",
    "synonyms": [
      "HÄGGVIK STATION",
      "HÄGGVIK STN",
      "HÆGGVIK STATION",
      "HÆGGVIK STN"
    ],
    "lId": "00703",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.44416666666666,
      "lon": 17.932222222222222
    }
  },
  {
    "name": "Häggvik Kramfors kommun",
    "synonyms": [
      "HÄGGVIK KRAMFORS KOMMUN",
      "HÆGGVIK KRAMFORS KOMMUN"
    ],
    "lId": "28998",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 62.91027777777778,
      "lon": 18.303055555555556
    }
  },
  {
    "name": "Hälglöt",
    "synonyms": [
      "HÄLGLÖT",
      "HÆLGLØT"
    ],
    "lId": "21134",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.343333333333334,
      "lon": 15.580277777777777
    }
  },
  {
    "name": "Häljarp",
    "synonyms": [
      "HÄLJARP",
      "HÄLJARP STN",
      "HÆLJARP",
      "HÆLJARP STN"
    ],
    "lId": "01547",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 55.86083333333333,
      "lon": 12.911388888888888
    }
  },
  {
    "name": "Hällabrottet Affärsgatan",
    "synonyms": [
      "HÄLLABROTTET AFFÄRSGATAN",
      "HÆLLABROTTET AFFÆRSGATAN"
    ],
    "lId": "10647",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.11638888888889,
      "lon": 15.198333333333334
    }
  },
  {
    "name": "Hällaryd vägskäl",
    "synonyms": [
      "HÄLLARYD VSK",
      "HÄLLARYD VÄGSKÄL",
      "HÆLLARYD VSK",
      "HÆLLARYD VÆGSKÆL"
    ],
    "lId": "10649",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 56.19916666666666,
      "lon": 14.944722222222222
    }
  },
  {
    "name": "Hällberga handel",
    "synonyms": [
      "HÄLLBERGA HANDEL",
      "HÄLLBERGA HANDL",
      "HÆLLBERGA HANDEL",
      "HÆLLBERGA HANDL"
    ],
    "lId": "21277",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.31777777777778,
      "lon": 16.59722222222222
    }
  },
  {
    "name": "Hällbybrunn Blåklocksvägen",
    "synonyms": [
      "HÄLLBYBRUNN BLÅKLOCKSVÄGEN",
      "HÆLLBYBRUNN BLÅKLOCKSVÆGEN"
    ],
    "lId": "24908",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.38638888888889,
      "lon": 16.420555555555556
    }
  },
  {
    "name": "Hälledal kiosken",
    "synonyms": [
      "HÄLLEDAL KIOSKEN",
      "HÆLLEDAL KIOSKEN"
    ],
    "lId": "15174",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 62.805,
      "lon": 17.866111111111113
    }
  },
  {
    "name": "Hällefors",
    "synonyms": [
      "HALLEFORS",
      "HÄLLEFORS",
      "HÆLLEFORS"
    ],
    "lId": "00419",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.7825,
      "lon": 14.518611111111111
    }
  },
  {
    "name": "Hälleforsnäs",
    "synonyms": [
      "HALLEFORSNAS",
      "HÄLLEFORSNÄS",
      "HÆLLEFORSNÆS"
    ],
    "lId": "00738",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.16222222222222,
      "lon": 16.503055555555555
    }
  },
  {
    "name": "Hällekis",
    "synonyms": [
      "HALLEKIS",
      "HÄLLEKIS",
      "HÄLLEKIS STN",
      "HÆLLEKIS",
      "HÆLLEKIS STN"
    ],
    "lId": "00427",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 58.63,
      "lon": 13.4325
    }
  },
  {
    "name": "Hällestad kyrka",
    "synonyms": [
      "HÄLLESTAD KYRKA",
      "HÆLLESTAD KYRKA"
    ],
    "lId": "10657",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 58.74194444444444,
      "lon": 15.572777777777777
    }
  },
  {
    "name": "Hällevadsholm",
    "synonyms": [
      "HALLEVADSHOLM",
      "HÄLLEVADSHOLM",
      "HÆLLEVADSHOLM"
    ],
    "lId": "00054",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 58.57972222222222,
      "lon": 11.535555555555556
    }
  },
  {
    "name": "Hällevik",
    "synonyms": [
      "HÄLLEVIK",
      "HÄLLEVIK HAMN",
      "HÆLLEVIK",
      "HÆLLEVIK HAMN"
    ],
    "lId": "00584",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 56.01222222222222,
      "lon": 14.697777777777778
    }
  },
  {
    "name": "Hälleviksstrand",
    "synonyms": [
      "HÄLLEVIKSSTRAND",
      "HÆLLEVIKSSTRAND"
    ],
    "lId": "00858",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 58.12277777777778,
      "lon": 11.443055555555556
    }
  },
  {
    "name": "Hällingsjö Källarbacken",
    "synonyms": [
      "HÄLLINGSJÖ KÄLLARBACKEN",
      "HÆLLINGSJØ KÆLLARBACKEN"
    ],
    "lId": "15987",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 57.618611111111115,
      "lon": 12.435
    }
  },
  {
    "name": "Hällnäs busstation",
    "synonyms": [
      "HÄLLNÄS BUSSTATION",
      "HÆLLNÆS BUSSTATION"
    ],
    "lId": "23488",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 64.30833333333334,
      "lon": 19.623333333333335
    }
  },
  {
    "name": "Hällnäs station",
    "synonyms": [
      "HALLNAS STATION",
      "HÄLLNÄS STATION",
      "HÆLLNÆS STATION"
    ],
    "lId": "00219",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 64.30555555555556,
      "lon": 19.625833333333333
    }
  },
  {
    "name": "Hälsö hamn",
    "synonyms": [
      "HÄLSÖ HAMN",
      "HÆLSØ HAMN"
    ],
    "lId": "15610",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 57.731944444444444,
      "lon": 11.65638888888889
    }
  },
  {
    "name": "Härad",
    "synonyms": [
      "HÄRAD",
      "HÆRAD"
    ],
    "lId": "10660",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.36055555555556,
      "lon": 16.904999999999998
    }
  },
  {
    "name": "Häradsbäck Knoxhultsvägen",
    "synonyms": [
      "HÄRADSBÄCK KNOXHULTSVÄGEN",
      "HÆRADSBÆCK KNOXHULTSVÆGEN"
    ],
    "lId": "04067",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 56.53,
      "lon": 14.450833333333332
    }
  },
  {
    "name": "Härnösand station",
    "synonyms": [
      "HARNOSAND STATION",
      "HARNOSAND STN",
      "HÄRNÖSAND STATION",
      "HÄRNÖSAND STN",
      "HÆRNØSAND STATION",
      "HÆRNØSAND STN"
    ],
    "lId": "00253",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 62.635,
      "lon": 17.928611111111113
    }
  },
  {
    "name": "Härryda kyrka",
    "synonyms": [
      "HÄRRYDA KYRKA",
      "HÆRRYDA KYRKA"
    ],
    "lId": "15981",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 57.69083333333333,
      "lon": 12.30638888888889
    }
  },
  {
    "name": "Hässelby gård T-bana",
    "synonyms": [
      "HÄSSELBY GÅRD T",
      "HÄSSELBY GÅRD T-BANA",
      "HÆSSELBY GÅRD T",
      "HÆSSELBY GÅRD T-BANA"
    ],
    "lId": "21681",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.36666666666667,
      "lon": 17.84361111111111
    }
  },
  {
    "name": "Hässelby strand T-bana",
    "synonyms": [
      "HÄSSELBY STRAND",
      "HÄSSELBY STRAND T-BANA",
      "HÆSSELBY STRAND",
      "HÆSSELBY STRAND T-BANA"
    ],
    "lId": "21680",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.361111111111114,
      "lon": 17.83222222222222
    }
  },
  {
    "name": "Hässleholm C",
    "synonyms": [
      "HASSLEHOLM C",
      "HÄSSLEHOLM C",
      "HÆSSLEHOLM C"
    ],
    "lId": "00006",
    "prio": 1,
    "pId": "074",
    "pos": {
      "lat": 56.1575,
      "lon": 13.763055555555555
    }
  },
  {
    "name": "Hästholmen Ödeshög",
    "synonyms": [
      "HÄSTHOLMEN ÖDESHÖG",
      "HÆSTHOLMEN ØDESHØG"
    ],
    "lId": "01472",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 58.27861111111111,
      "lon": 14.648888888888889
    }
  },
  {
    "name": "Hästveda Karlavägen",
    "synonyms": [
      "HÄSTVEDA KARLAVÄGEN",
      "HÆSTVEDA KARLAVÆGEN"
    ],
    "lId": "00724",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 56.28722222222222,
      "lon": 13.935555555555556
    }
  },
  {
    "name": "Hästveda station",
    "synonyms": [
      "HÄSTVEDA STATION"
    ],
    "lId": "64282",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 56.2875,
      "lon": 13.934444444444445
    }
  },
  {
    "name": "Hävla",
    "synonyms": [
      "HÄVLA",
      "HÄVLA AFFÄREN",
      "HÆVLA",
      "HÆVLA AFFÆREN"
    ],
    "lId": "20344",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 58.914722222222224,
      "lon": 15.867777777777778
    }
  },
  {
    "name": "Höganäs",
    "synonyms": [
      "HOGANAS",
      "HÖGANÄS",
      "HÖGANÄS STADSH",
      "HØGANÆS",
      "HØGANÆS STADSH"
    ],
    "lId": "00943",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 56.200833333333335,
      "lon": 12.558333333333334
    }
  },
  {
    "name": "Högberga",
    "synonyms": [
      "HÖGBERGA",
      "HØGBERGA"
    ],
    "lId": "24792",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.34388888888889,
      "lon": 18.193055555555556
    }
  },
  {
    "name": "Högbo kyrka",
    "synonyms": [
      "HÖGBO KYRKA",
      "HØGBO KYRKA"
    ],
    "lId": "17977",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 60.67055555555555,
      "lon": 16.80888888888889
    }
  },
  {
    "name": "Högboda",
    "synonyms": [
      "HOGBODA",
      "HÖGBODA",
      "HØGBODA"
    ],
    "lId": "00418",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.5575,
      "lon": 13.051388888888889
    }
  },
  {
    "name": "Högboda väg 61",
    "synonyms": [
      "HÖGBODA VÄG 61",
      "HØGBODA VÆG 61"
    ],
    "lId": "22300",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.551111111111105,
      "lon": 13.0525
    }
  },
  {
    "name": "Högdalen T-bana",
    "synonyms": [
      "HÖGDALEN T-BANA",
      "HØGDALEN T-BANA"
    ],
    "lId": "21712",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.26361111111111,
      "lon": 18.04277777777778
    }
  },
  {
    "name": "Högfors",
    "synonyms": [
      "HÖGFORS",
      "HØGFORS"
    ],
    "lId": "44755",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 60.022777777777776,
      "lon": 16.015833333333333
    }
  },
  {
    "name": "Höglandstorget",
    "synonyms": [
      "HÖGLANDSTORGET",
      "HØGLANDSTORGET"
    ],
    "lId": "24818",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.323055555555555,
      "lon": 17.94
    }
  },
  {
    "name": "Höglekardalen",
    "synonyms": [
      "HÖGLEKARDALEN",
      "HØGLEKARDALEN"
    ],
    "lId": "00429",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 63.07833333333333,
      "lon": 13.749166666666666
    }
  },
  {
    "name": "Höglunda",
    "synonyms": [
      "HÖGLUNDA",
      "HØGLUNDA"
    ],
    "lId": "13260",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 63.14861111111111,
      "lon": 15.839722222222223
    }
  },
  {
    "name": "Högsby",
    "synonyms": [
      "HOGSBY",
      "HÖGSBY",
      "HÖGSBY STN",
      "HØGSBY",
      "HØGSBY STN"
    ],
    "lId": "00923",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 57.16555555555556,
      "lon": 16.02777777777778
    }
  },
  {
    "name": "Högsjö bruk",
    "synonyms": [
      "HÖGSJÖ BRUK",
      "HØGSJØ BRUK"
    ],
    "lId": "10681",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.026666666666664,
      "lon": 15.670277777777777
    }
  },
  {
    "name": "Högsäter centrum Färgelanda",
    "synonyms": [
      "HÖGSÄTER CENTRUM",
      "HÖGSÄTER CENTRUM FÄRGELANDA",
      "HÖGSÄTER CM",
      "HØGSÆTER CENTRUM",
      "HØGSÆTER CM"
    ],
    "lId": "12038",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 58.65083333333333,
      "lon": 12.055833333333334
    }
  },
  {
    "name": "Högsäter Säffle",
    "synonyms": [
      "HÖGSÄTER SÄFFLE",
      "HØGSÆTER SÆFFLE"
    ],
    "lId": "10682",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.35111111111111,
      "lon": 12.80388888888889
    }
  },
  {
    "name": "Högvålen",
    "synonyms": [
      "HÖGVÅLEN",
      "HØGVÅLEN"
    ],
    "lId": "13330",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 62.26138888888889,
      "lon": 12.938055555555556
    }
  },
  {
    "name": "Hökarängen T-bana",
    "synonyms": [
      "HÖKARÄNGEN T-BANA",
      "HØKARÆNGEN T-BANA"
    ],
    "lId": "21698",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.257777777777775,
      "lon": 18.08222222222222
    }
  },
  {
    "name": "Hökerum affär",
    "synonyms": [
      "HÖKERUM AFFÄR",
      "HØKERUM AFFÆR"
    ],
    "lId": "12435",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 57.84111111111111,
      "lon": 13.285
    }
  },
  {
    "name": "Hökåsen",
    "synonyms": [
      "HÖKÅSEN",
      "HÖKÅSEN SKÖLDMV",
      "HØKÅSEN",
      "HØKÅSEN SKØLDMV"
    ],
    "lId": "10684",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.66083333333333,
      "lon": 16.604722222222225
    }
  },
  {
    "name": "Hökåsen Badelundavägen",
    "synonyms": [
      "HÖKÅSEN BADELUNDAVÄGEN"
    ],
    "lId": "43663",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.663333333333334,
      "lon": 16.591666666666665
    }
  },
  {
    "name": "Hökön Ljungbacken",
    "synonyms": [
      "HÖKÖN LJUNGBACKEN",
      "HØKØN LJUNGBACKEN"
    ],
    "lId": "22979",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 56.4675,
      "lon": 14.22861111111111
    }
  },
  {
    "name": "Hököpinge Sockervägen",
    "synonyms": [
      "HÖKÖPINGE SOCKERVÄGEN",
      "HØKØPINGE SOCKERVÆGEN"
    ],
    "lId": "12566",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 55.48833333333334,
      "lon": 13.008611111111112
    }
  },
  {
    "name": "Höljes",
    "synonyms": [
      "HÖLJES",
      "HÖLJES HANDEL",
      "HØLJES",
      "HØLJES HANDEL"
    ],
    "lId": "00808",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 60.89833333333333,
      "lon": 12.596944444444444
    }
  },
  {
    "name": "Höllviken",
    "synonyms": [
      "HOLLVIKEN",
      "HÖLLVIKEN",
      "HÖLLVIKEN CM",
      "HØLLVIKEN",
      "HØLLVIKEN CM"
    ],
    "lId": "00944",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 55.41861111111111,
      "lon": 12.952777777777778
    }
  },
  {
    "name": "Hölö",
    "synonyms": [
      "HÖLÖ",
      "HÖLÖ STN",
      "HØLØ",
      "HØLØ STN"
    ],
    "lId": "10689",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.025,
      "lon": 17.535
    }
  },
  {
    "name": "Hönö",
    "synonyms": [
      "HÖNÖ",
      "HÖNÖ PINAN F",
      "HØNØ",
      "HØNØ PINAN F"
    ],
    "lId": "00860",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 57.698611111111106,
      "lon": 11.666111111111112
    }
  },
  {
    "name": "Hörby",
    "synonyms": [
      "HORBY",
      "HÖRBY",
      "HÖRBY BSTN",
      "HØRBY",
      "HØRBY BSTN"
    ],
    "lId": "00591",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 55.855555555555554,
      "lon": 13.671111111111111
    }
  },
  {
    "name": "Hörja",
    "synonyms": [
      "HÖRJA",
      "HÖRJA SKOLAN",
      "HØRJA",
      "HØRJA SKOLAN"
    ],
    "lId": "01473",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 56.20638888888889,
      "lon": 13.594722222222222
    }
  },
  {
    "name": "Hörken affären",
    "synonyms": [
      "HÖRKEN AFFÄREN",
      "HØRKEN AFFÆREN"
    ],
    "lId": "21183",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 60.022777777777776,
      "lon": 14.938055555555556
    }
  },
  {
    "name": "Hörle",
    "synonyms": [
      "HÖRLE",
      "HÖRLE STN",
      "HØRLE",
      "HØRLE STN"
    ],
    "lId": "01086",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 57.259166666666665,
      "lon": 14.053611111111111
    }
  },
  {
    "name": "Hörnefors station",
    "synonyms": [
      "HÖRNEFORS STATION",
      "HÖRNEFORS STN",
      "HØRNEFORS STATION",
      "HØRNEFORS STN"
    ],
    "lId": "01582",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 63.6325,
      "lon": 19.90833333333333
    }
  },
  {
    "name": "Hörnsjöfors",
    "synonyms": [
      "HÖRNSJÖFORS",
      "HØRNSJØFORS"
    ],
    "lId": "23008",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.94888888888889,
      "lon": 16.22861111111111
    }
  },
  {
    "name": "Hörvik hamn",
    "synonyms": [
      "HÖRVIK HAMN",
      "HØRVIK HAMN"
    ],
    "lId": "10694",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 56.04138888888889,
      "lon": 14.770277777777778
    }
  },
  {
    "name": "Hötorget T-bana",
    "synonyms": [
      "HÖTORGET T-BANA",
      "HØTORGET T-BANA"
    ],
    "lId": "21667",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.33527777777778,
      "lon": 18.063333333333333
    }
  },
  {
    "name": "Höviksnäs",
    "synonyms": [
      "HÖVIKSNÄS",
      "HØVIKSNÆS"
    ],
    "lId": "15784",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 58.033055555555556,
      "lon": 11.754166666666666
    }
  },
  {
    "name": "Höör",
    "synonyms": [
      "HOOR",
      "HÖÖR",
      "HÖÖR STN",
      "HØØR",
      "HØØR STN"
    ],
    "lId": "00185",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 55.93694444444444,
      "lon": 13.54138888888889
    }
  },
  {
    "name": "Idkerberget gla affären",
    "synonyms": [
      "IDKERBERGET",
      "IDKERBERGET GLA AFFÄREN",
      "IDKERBERGET GLA AFFÆREN"
    ],
    "lId": "24781",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 60.375,
      "lon": 15.228333333333333
    }
  },
  {
    "name": "Idre Fjäll",
    "synonyms": [
      "IDRE FJÄLL"
    ],
    "lId": "00863",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 61.88972222222222,
      "lon": 12.831944444444444
    }
  },
  {
    "name": "Idre Konsum",
    "synonyms": [
      "IDRE KONSUM"
    ],
    "lId": "00647",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 61.85777777777778,
      "lon": 12.726111111111111
    }
  },
  {
    "name": "Igelboda",
    "synonyms": [
      "IGELBODA",
      "IGELBODA STN"
    ],
    "lId": "20876",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.28972222222222,
      "lon": 18.27583333333333
    }
  },
  {
    "name": "Igelfors skolan",
    "synonyms": [
      "IGELFORS SKOLAN"
    ],
    "lId": "10698",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 58.84527777777778,
      "lon": 15.69888888888889
    }
  },
  {
    "name": "Igelsta Romfartuna",
    "synonyms": [
      "IGELSTA ROMFARTUNA"
    ],
    "lId": "43826",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.72555555555556,
      "lon": 16.569166666666668
    }
  },
  {
    "name": "Igelstorp",
    "synonyms": [
      "IGELSTORP",
      "IGELSTORP V 49"
    ],
    "lId": "01474",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 58.401111111111106,
      "lon": 13.976111111111111
    }
  },
  {
    "name": "Iggesund",
    "synonyms": [
      "IGGESUND"
    ],
    "lId": "01560",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 61.64555555555555,
      "lon": 17.081666666666667
    }
  },
  {
    "name": "Iggesund nya E4",
    "synonyms": [
      "IGGESUND NYA E4"
    ],
    "lId": "59441",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 61.65416666666667,
      "lon": 17.017777777777777
    }
  },
  {
    "name": "Ilsbo skola",
    "synonyms": [
      "ILSBO SKOLA"
    ],
    "lId": "10701",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 61.86027777777778,
      "lon": 17.049722222222226
    }
  },
  {
    "name": "Immeln",
    "synonyms": [
      "IMMELN"
    ],
    "lId": "01088",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 56.20333333333333,
      "lon": 14.246388888888887
    }
  },
  {
    "name": "Indal",
    "synonyms": [
      "INDAL"
    ],
    "lId": "01089",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 62.578611111111115,
      "lon": 17.095555555555553
    }
  },
  {
    "name": "Infra city",
    "synonyms": [
      "INFRA CITY"
    ],
    "lId": "67366",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.49916666666667,
      "lon": 17.927500000000002
    }
  },
  {
    "name": "Ingared",
    "synonyms": [
      "INGARED"
    ],
    "lId": "15930",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 57.85,
      "lon": 12.459166666666667
    }
  },
  {
    "name": "Ingarö Björkvik brygga",
    "synonyms": [
      "INGARÖ BJÖRKVIK BRYGGA"
    ],
    "lId": "24969",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.22083333333334,
      "lon": 18.539722222222224
    }
  },
  {
    "name": "Ingarö Brunn",
    "synonyms": [
      "INGARÖ BRUNN",
      "INGARØ BRUNN"
    ],
    "lId": "24663",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.28138888888889,
      "lon": 18.426944444444445
    }
  },
  {
    "name": "Ingarö Eknäs brygga",
    "synonyms": [
      "INGARÖ EKNÄS BRYGGA"
    ],
    "lId": "66401",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.24055555555556,
      "lon": 18.54638888888889
    }
  },
  {
    "name": "Ingarö Idalens vändplan",
    "synonyms": [
      "INGARÖ IDALENS VÄNDPLAN"
    ],
    "lId": "66525",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.222500000000004,
      "lon": 18.509722222222223
    }
  },
  {
    "name": "Ingatorp centrum",
    "synonyms": [
      "INGATORP CENTRUM",
      "INGATORP CM"
    ],
    "lId": "10703",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 57.636944444444445,
      "lon": 15.413611111111111
    }
  },
  {
    "name": "Ingelstad centrum",
    "synonyms": [
      "INGELSTAD CENTRUM",
      "INGELSTAD CM"
    ],
    "lId": "00103",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 56.745,
      "lon": 14.921111111111111
    }
  },
  {
    "name": "Ingelstad kyrka",
    "synonyms": [
      "INGELSTAD KYRKA"
    ],
    "lId": "20363",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 56.74055555555556,
      "lon": 14.930277777777777
    }
  },
  {
    "name": "Ingelstorp kyrka",
    "synonyms": [
      "INGELSTORP KYRKA"
    ],
    "lId": "30014",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 55.43611111111111,
      "lon": 14.03277777777778
    }
  },
  {
    "name": "Ingelsträde Mandelgrensvägen",
    "synonyms": [
      "INGELSTRÄDE MANDELGRENSVÄGEN",
      "INGELSTRÆDE MANDELGRENSVÆGEN"
    ],
    "lId": "16702",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 56.18833333333333,
      "lon": 12.627777777777778
    }
  },
  {
    "name": "Ingmarsö södra",
    "synonyms": [
      "INGMARSÖ SÖDRA",
      "INGMARSØ SØDRA"
    ],
    "lId": "24873",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.46527777777778,
      "lon": 18.750833333333333
    }
  },
  {
    "name": "Ingmår",
    "synonyms": [
      "INGMÅR"
    ],
    "lId": "01414",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.87861111111111,
      "lon": 13.175277777777778
    }
  },
  {
    "name": "Innertavle",
    "synonyms": [
      "INNERTAVLE"
    ],
    "lId": "26870",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 63.815555555555555,
      "lon": 20.421666666666667
    }
  },
  {
    "name": "Innertavle västra",
    "synonyms": [
      "INNERTAVLE VÄSTRA",
      "INNERTAVLE VÆSTRA"
    ],
    "lId": "26679",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 63.811388888888885,
      "lon": 20.389722222222222
    }
  },
  {
    "name": "Insjön",
    "synonyms": [
      "INSJON",
      "INSJÖN",
      "INSJØN"
    ],
    "lId": "00202",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 60.67527777777777,
      "lon": 15.094166666666668
    }
  },
  {
    "name": "Ire",
    "synonyms": [
      "IRE"
    ],
    "lId": "01091",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 57.83166666666667,
      "lon": 18.60888888888889
    }
  },
  {
    "name": "Irsta",
    "synonyms": [
      "IRSTA"
    ],
    "lId": "43305",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.60138888888889,
      "lon": 16.699444444444445
    }
  },
  {
    "name": "Islandstorget T-bana",
    "synonyms": [
      "ISLANDSTORGET T-BANA"
    ],
    "lId": "21686",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.34583333333334,
      "lon": 17.89388888888889
    }
  },
  {
    "name": "Istaby",
    "synonyms": [
      "ISTABY"
    ],
    "lId": "10708",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 56.02222222222222,
      "lon": 14.651944444444444
    }
  },
  {
    "name": "Ivarsbjörke",
    "synonyms": [
      "IVARSBJÖRKE",
      "IVARSBJÖRKE STN",
      "IVARSBJØRKE",
      "IVARSBJØRKE STN"
    ],
    "lId": "01413",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.959722222222226,
      "lon": 13.143611111111111
    }
  },
  {
    "name": "Jakobsberg",
    "synonyms": [
      "JAKOBSBERG",
      "JAKOBSBERG STN"
    ],
    "lId": "00705",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.42333333333333,
      "lon": 17.83277777777778
    }
  },
  {
    "name": "Jarlaberg",
    "synonyms": [
      "JARLABERG"
    ],
    "lId": "24853",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.315555555555555,
      "lon": 18.169444444444444
    }
  },
  {
    "name": "Jenny",
    "synonyms": [
      "JENNY"
    ],
    "lId": "14226",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 57.76833333333333,
      "lon": 16.579166666666666
    }
  },
  {
    "name": "Johannelund T-bana",
    "synonyms": [
      "JOHANNELUND T-BANA"
    ],
    "lId": "21682",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.367777777777775,
      "lon": 17.857222222222223
    }
  },
  {
    "name": "Johannesfred Spårv",
    "synonyms": [
      "JOHANNESFRED SPÅRV"
    ],
    "lId": "71178",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.342222222222226,
      "lon": 17.97
    }
  },
  {
    "name": "Johannishus station",
    "synonyms": [
      "JOHANNISHUS STATION",
      "JOHANNISHUS STN"
    ],
    "lId": "10712",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 56.22666666666667,
      "lon": 15.42
    }
  },
  {
    "name": "Jokkmokk busstation",
    "synonyms": [
      "JOKKMOKK BSTN",
      "JOKKMOKK BUSSTATION"
    ],
    "lId": "14701",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 66.60777777777777,
      "lon": 19.829166666666666
    }
  },
  {
    "name": "Jonsbol Bytespunkten",
    "synonyms": [
      "JONSBOL BYTESPUNKTEN"
    ],
    "lId": "72181",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.34305555555556,
      "lon": 13.502777777777778
    }
  },
  {
    "name": "Jonsered",
    "synonyms": [
      "JONSERED",
      "JONSERED STN"
    ],
    "lId": "15675",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 57.749722222222225,
      "lon": 12.17361111111111
    }
  },
  {
    "name": "Jonstorp",
    "synonyms": [
      "JONSTORP",
      "JONSTORP CM"
    ],
    "lId": "00723",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 56.22694444444445,
      "lon": 12.673888888888888
    }
  },
  {
    "name": "Jordbro",
    "synonyms": [
      "JORDBRO",
      "JORDBRO STN"
    ],
    "lId": "00706",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.14138888888889,
      "lon": 18.125555555555557
    }
  },
  {
    "name": "Jormvattnet",
    "synonyms": [
      "JORMVATTNET"
    ],
    "lId": "13493",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 64.72277777777778,
      "lon": 14.036944444444444
    }
  },
  {
    "name": "Jugansbo",
    "synonyms": [
      "JUGANSBO"
    ],
    "lId": "18251",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 60.00527777777778,
      "lon": 16.70111111111111
    }
  },
  {
    "name": "Jukkasjärvi",
    "synonyms": [
      "JUKKASJÄRVI",
      "JUKKASJÄRVI KA",
      "JUKKASJÆRVI",
      "JUKKASJÆRVI KA"
    ],
    "lId": "00876",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 67.84666666666666,
      "lon": 20.61916666666667
    }
  },
  {
    "name": "Julita",
    "synonyms": [
      "JULITA"
    ],
    "lId": "10719",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.151944444444446,
      "lon": 16.040555555555557
    }
  },
  {
    "name": "Jumkilsmacken",
    "synonyms": [
      "JUMKILSMACKEN"
    ],
    "lId": "12798",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.961111111111116,
      "lon": 17.392777777777777
    }
  },
  {
    "name": "Jung busstation",
    "synonyms": [
      "JUNG BSTN",
      "JUNG BUSSTATION"
    ],
    "lId": "20122",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 58.33305555555556,
      "lon": 13.123055555555556
    }
  },
  {
    "name": "Juniskär",
    "synonyms": [
      "JUNISKÄR",
      "JUNISKÆR"
    ],
    "lId": "15183",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 62.296388888888885,
      "lon": 17.46472222222222
    }
  },
  {
    "name": "Junosuando",
    "synonyms": [
      "JUNOSUANDO",
      "JUNOSUANDO BSTN"
    ],
    "lId": "14809",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 67.42805555555556,
      "lon": 22.51638888888889
    }
  },
  {
    "name": "Junsele",
    "synonyms": [
      "JUNSELE",
      "JUNSELE BSTN"
    ],
    "lId": "00538",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 63.69583333333333,
      "lon": 16.878888888888888
    }
  },
  {
    "name": "Juoksengi",
    "synonyms": [
      "JUOKSENGI"
    ],
    "lId": "14778",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 66.56444444444445,
      "lon": 23.840833333333332
    }
  },
  {
    "name": "Jursla Lillsjövägen",
    "synonyms": [
      "JURSLA LILLSJÖVÄGEN",
      "JURSLA LILLSJØVÆGEN"
    ],
    "lId": "10721",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 58.653888888888886,
      "lon": 16.161666666666665
    }
  },
  {
    "name": "Jutsajaure",
    "synonyms": [
      "JUTSAJAURE",
      "JUTSAJAURE STN"
    ],
    "lId": "04420",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 67.06472222222222,
      "lon": 19.921111111111113
    }
  },
  {
    "name": "Jäderfors Nyvägen",
    "synonyms": [
      "JÄDERFORS NYVÄGEN",
      "JÆDERFORS NYVÆGEN"
    ],
    "lId": "19754",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 60.6675,
      "lon": 16.683888888888887
    }
  },
  {
    "name": "Jädraås torg",
    "synonyms": [
      "JÄDRAÅS AFFÄREN",
      "JÄDRAÅS TORG",
      "JÆDRAÅS AFFÆREN",
      "JÆDRAÅS TORG"
    ],
    "lId": "10722",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 60.8425,
      "lon": 16.46861111111111
    }
  },
  {
    "name": "Jäkkvik",
    "synonyms": [
      "JÄKKVIK",
      "JÄKKVIK AFFÄREN",
      "JÆKKVIK",
      "JÆKKVIK AFFÆREN"
    ],
    "lId": "00726",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 66.38722222222223,
      "lon": 16.96638888888889
    }
  },
  {
    "name": "Jämjö",
    "synonyms": [
      "JÄMJÖ",
      "JÄMJÖ CM JÄMJÖH",
      "JÆMJØ",
      "JÆMJØ CM JÆMJØH"
    ],
    "lId": "00333",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 56.19194444444444,
      "lon": 15.835
    }
  },
  {
    "name": "Jämshög",
    "synonyms": [
      "JÄMSHÖG",
      "JÄMSHÖG BYGATAN",
      "JÆMSHØG",
      "JÆMSHØG BYGATAN"
    ],
    "lId": "00488",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 56.24055555555556,
      "lon": 14.530555555555557
    }
  },
  {
    "name": "Jämtlands Nyby",
    "synonyms": [
      "JÄMTLANDS NYBY",
      "JÆMTLANDS NYBY"
    ],
    "lId": "13239",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 63.32805555555556,
      "lon": 15.178055555555554
    }
  },
  {
    "name": "Jämtön",
    "synonyms": [
      "JÄMTÖN",
      "JÄMTÖN ICA",
      "JÆMTØN",
      "JÆMTØN ICA"
    ],
    "lId": "14876",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 65.85583333333332,
      "lon": 22.499722222222225
    }
  },
  {
    "name": "Jämtön E4",
    "synonyms": [
      "JÄMTÖN E4",
      "JÆMTØN E4"
    ],
    "lId": "20375",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 65.87388888888889,
      "lon": 22.490555555555556
    }
  },
  {
    "name": "Järbo",
    "synonyms": [
      "JÄRBO",
      "JÄRBO BSTN",
      "JÆRBO",
      "JÆRBO BSTN"
    ],
    "lId": "00633",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 60.71555555555556,
      "lon": 16.59583333333333
    }
  },
  {
    "name": "Järkvissle",
    "synonyms": [
      "JÄRKVISSLE",
      "JÆRKVISSLE"
    ],
    "lId": "15185",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 62.808611111111105,
      "lon": 16.671944444444446
    }
  },
  {
    "name": "Järna",
    "synonyms": [
      "JÄRNA",
      "JÄRNA STN",
      "JÆRNA",
      "JÆRNA STN"
    ],
    "lId": "00709",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.093333333333334,
      "lon": 17.56722222222222
    }
  },
  {
    "name": "Järnboås",
    "synonyms": [
      "JÄRNBOÅS",
      "JÆRNBOÅS"
    ],
    "lId": "10728",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.655277777777776,
      "lon": 14.865277777777777
    }
  },
  {
    "name": "Järnforsen",
    "synonyms": [
      "JÄRNFORSEN",
      "JÄRNFORSEN STN",
      "JÆRNFORSEN",
      "JÆRNFORSEN STN"
    ],
    "lId": "01093",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 57.407777777777774,
      "lon": 15.620000000000001
    }
  },
  {
    "name": "Järpen",
    "synonyms": [
      "JARPEN",
      "JÄRPEN",
      "JÄRPEN STN",
      "JÆRPEN",
      "JÆRPEN STN"
    ],
    "lId": "00126",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 63.342222222222226,
      "lon": 13.471666666666668
    }
  },
  {
    "name": "Järpås",
    "synonyms": [
      "JARPAS",
      "JÄRPÅS",
      "JÄRPÅS STN",
      "JÆRPÅS",
      "JÆRPÅS STN"
    ],
    "lId": "00442",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 58.37916666666667,
      "lon": 12.969722222222222
    }
  },
  {
    "name": "Järrestad Näckebo",
    "synonyms": [
      "JÄRRESTAD NÄCKEBO",
      "JÆRRESTAD NÆCKEBO"
    ],
    "lId": "24987",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 55.535555555555554,
      "lon": 14.286666666666667
    }
  },
  {
    "name": "Järvsö",
    "synonyms": [
      "JARVSO",
      "JÄRVSÖ",
      "JÄRVSÖ STN",
      "JÆRVSØ",
      "JÆRVSØ STN"
    ],
    "lId": "00146",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 61.715833333333336,
      "lon": 16.172222222222224
    }
  },
  {
    "name": "Jättendal",
    "synonyms": [
      "JÄTTENDAL",
      "JÆTTENDAL"
    ],
    "lId": "10736",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 61.977222222222224,
      "lon": 17.245555555555555
    }
  },
  {
    "name": "Jävre E4",
    "synonyms": [
      "JÄVRE E4",
      "JÆVRE E4"
    ],
    "lId": "14887",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 65.15722222222223,
      "lon": 21.49277777777778
    }
  },
  {
    "name": "Jönköping C",
    "synonyms": [
      "JONKOPING C",
      "JÖNKÖPING C",
      "JØNKØPING C"
    ],
    "lId": "00090",
    "prio": 1,
    "pId": "074",
    "pos": {
      "lat": 57.78444444444444,
      "lon": 14.163055555555555
    }
  },
  {
    "name": "Jönköping Elmia",
    "synonyms": [
      "JÖNKÖPING ELMIA",
      "JØNKØPING ELMIA"
    ],
    "lId": "21191",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 57.78527777777778,
      "lon": 14.230555555555556
    }
  },
  {
    "name": "Jönköping Kinnarps Arena",
    "synonyms": [
      "JÖNKÖPING KINNARPS ARENA"
    ],
    "lId": "68809",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 57.786944444444444,
      "lon": 14.230833333333333
    }
  },
  {
    "name": "Jönköping länssjukhuset Ryh",
    "synonyms": [
      "JÖNKÖPING LÄNSSJUKHUSET RYH",
      "JÖNKÖPING RYHOV",
      "JØNKØPING LÆNSSJUKHUSET RYH",
      "JØNKØPING RYHOV"
    ],
    "lId": "24008",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 57.76638888888889,
      "lon": 14.193888888888889
    }
  },
  {
    "name": "Jönköping Råslätt centrum",
    "synonyms": [
      "JÖNKÖPING RÅSLÄTT CENTRUM"
    ],
    "lId": "39686",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 57.73916666666667,
      "lon": 14.151666666666667
    }
  },
  {
    "name": "Jönåker",
    "synonyms": [
      "JÖNÅKER",
      "JØNÅKER"
    ],
    "lId": "10738",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 58.74444444444445,
      "lon": 16.721666666666664
    }
  },
  {
    "name": "Jörlanda",
    "synonyms": [
      "JÖRLANDA",
      "JØRLANDA"
    ],
    "lId": "00349",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 57.98694444444445,
      "lon": 11.83
    }
  },
  {
    "name": "Jörn",
    "synonyms": [
      "JORN",
      "JÖRN",
      "JÖRN STN",
      "JØRN",
      "JØRN STN"
    ],
    "lId": "00282",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 65.05416666666666,
      "lon": 20.030277777777776
    }
  },
  {
    "name": "Jörn busstation",
    "synonyms": [
      "JÖRN BSTN",
      "JÖRN BUSSTATION",
      "JØRN BSTN",
      "JØRN BUSSTATION"
    ],
    "lId": "13726",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 65.0586111111111,
      "lon": 20.040277777777778
    }
  },
  {
    "name": "Jössefors",
    "synonyms": [
      "JÖSSEFORS",
      "JØSSEFORS"
    ],
    "lId": "58601",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.67472222222222,
      "lon": 12.501388888888888
    }
  },
  {
    "name": "Kaggeholm slott",
    "synonyms": [
      "KAGGEHOLM SLOTT"
    ],
    "lId": "24531",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.282777777777774,
      "lon": 17.664166666666667
    }
  },
  {
    "name": "Kaitum",
    "synonyms": [
      "KAITUM",
      "KAITUM STN"
    ],
    "lId": "00326",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 67.5436111111111,
      "lon": 20.10777777777778
    }
  },
  {
    "name": "Kalix",
    "synonyms": [
      "KALIX",
      "KALIX BSTN"
    ],
    "lId": "00877",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 65.85416666666666,
      "lon": 23.141944444444444
    }
  },
  {
    "name": "Kalkbrottsvillorna",
    "synonyms": [
      "KALKBROTTSVILLORNA"
    ],
    "lId": "21297",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.16027777777778,
      "lon": 15.934444444444445
    }
  },
  {
    "name": "Kall",
    "synonyms": [
      "KALL"
    ],
    "lId": "00445",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 63.47361111111111,
      "lon": 13.23
    }
  },
  {
    "name": "Kallhäll",
    "synonyms": [
      "KALLHÄLL",
      "KALLHÄLL STN",
      "KALLHÆLL",
      "KALLHÆLL STN"
    ],
    "lId": "00710",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.45305555555556,
      "lon": 17.805555555555557
    }
  },
  {
    "name": "Kallhäll Stäket Kajsas Hof",
    "synonyms": [
      "KALLHÄLL STÄKET KAJSAS HOF"
    ],
    "lId": "66994",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.473333333333336,
      "lon": 17.79361111111111
    }
  },
  {
    "name": "Kallinge torget",
    "synonyms": [
      "KALLINGE TORGET"
    ],
    "lId": "00104",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 56.245,
      "lon": 15.285555555555556
    }
  },
  {
    "name": "Kallrör",
    "synonyms": [
      "KALLRÖR",
      "KALLRØR"
    ],
    "lId": "13376",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 63.558611111111105,
      "lon": 13.028333333333334
    }
  },
  {
    "name": "Kallsedet",
    "synonyms": [
      "KALLSEDET"
    ],
    "lId": "01134",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 63.70138888888889,
      "lon": 12.956944444444444
    }
  },
  {
    "name": "Kallviken",
    "synonyms": [
      "KALLVIKEN"
    ],
    "lId": "10743",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.66777777777777,
      "lon": 12.796944444444444
    }
  },
  {
    "name": "Kalmar C",
    "synonyms": [
      "KALMAR C"
    ],
    "lId": "00020",
    "prio": 1,
    "pId": "074",
    "pos": {
      "lat": 56.66111111111111,
      "lon": 16.360000000000003
    }
  },
  {
    "name": "Kalmar Hansa City",
    "synonyms": [
      "KALMAR HANSA CITY"
    ],
    "lId": "52182",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 56.68444444444444,
      "lon": 16.31833333333333
    }
  },
  {
    "name": "Kalmar Malmen",
    "synonyms": [
      "KALMAR MALMEN"
    ],
    "lId": "72135",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 56.6675,
      "lon": 16.353055555555557
    }
  },
  {
    "name": "Kalmar Norrlidens Centrum",
    "synonyms": [
      "KALMAR NORRLIDENS CENTRUM"
    ],
    "lId": "52058",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 56.70277777777778,
      "lon": 16.359444444444446
    }
  },
  {
    "name": "Kalmar Öland Airport",
    "synonyms": [
      "KALMAR AIRPORT",
      "KALMAR ÖLAND AIRPORT"
    ],
    "lId": "22960",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 56.67722222222222,
      "lon": 16.286944444444448
    }
  },
  {
    "name": "Kapellskär",
    "synonyms": [
      "KAPELLSKÄR",
      "KAPELLSKÆR"
    ],
    "lId": "01136",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.721111111111114,
      "lon": 19.063055555555557
    }
  },
  {
    "name": "Kappelshamn",
    "synonyms": [
      "KAPPELSHAMN",
      "KAPPELSHAMN AFF"
    ],
    "lId": "01135",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 57.8525,
      "lon": 18.782777777777778
    }
  },
  {
    "name": "Karbenning",
    "synonyms": [
      "KARBENNING",
      "KARBENNING STN"
    ],
    "lId": "00903",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 60.03638888888889,
      "lon": 16.072777777777777
    }
  },
  {
    "name": "Karby",
    "synonyms": [
      "KARBY",
      "KARBY STORA"
    ],
    "lId": "01137",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.559444444444445,
      "lon": 18.221666666666664
    }
  },
  {
    "name": "Karesuando",
    "synonyms": [
      "KARESUANDO",
      "KARESUANDO BSTN"
    ],
    "lId": "00878",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 68.44111111111111,
      "lon": 22.478888888888886
    }
  },
  {
    "name": "Karlaplan T-bana",
    "synonyms": [
      "KARLAPLAN T-BANA"
    ],
    "lId": "21650",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.33861111111111,
      "lon": 18.090833333333332
    }
  },
  {
    "name": "Karlberg",
    "synonyms": [
      "KARLBERG",
      "KARLBERG STN"
    ],
    "lId": "00712",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.33972222222222,
      "lon": 18.029722222222222
    }
  },
  {
    "name": "Karlholmsbruk",
    "synonyms": [
      "KARLHOLM KARLIT",
      "KARLHOLMSBRUK"
    ],
    "lId": "00270",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 60.519999999999996,
      "lon": 17.628888888888888
    }
  },
  {
    "name": "Karlsbodavägen Spårv",
    "synonyms": [
      "KARLSBODAVÄGEN SPÅRV",
      "KARLSBODAVÆGEN SPÅRV"
    ],
    "lId": "64044",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.35638888888889,
      "lon": 17.961111111111112
    }
  },
  {
    "name": "Karlsborg busstation",
    "synonyms": [
      "KARLSBORG BSTN",
      "KARLSBORG BUSSTATION"
    ],
    "lId": "00256",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 58.53055555555555,
      "lon": 14.509444444444444
    }
  },
  {
    "name": "Karlsborg ICA Kalix",
    "synonyms": [
      "KARLSBORG ICA KALIX"
    ],
    "lId": "14753",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 65.80305555555556,
      "lon": 23.293055555555558
    }
  },
  {
    "name": "Karlshamn",
    "synonyms": [
      "KARLSHAMN",
      "KARLSHAMN STN"
    ],
    "lId": "00073",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 56.17638888888889,
      "lon": 14.867777777777778
    }
  },
  {
    "name": "Karlshamn Statoil",
    "synonyms": [
      "KARLSHAMN STATOIL"
    ],
    "lId": "71576",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 56.19,
      "lon": 14.846388888888889
    }
  },
  {
    "name": "Karlskoga busstation",
    "synonyms": [
      "KARLSKOGA BUSSTATION"
    ],
    "lId": "00176",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.32666666666667,
      "lon": 14.511666666666667
    }
  },
  {
    "name": "Karlskrona C",
    "synonyms": [
      "KARLSKRONA C"
    ],
    "lId": "00230",
    "prio": 1,
    "pId": "074",
    "pos": {
      "lat": 56.16611111111111,
      "lon": 15.585277777777778
    }
  },
  {
    "name": "Karlskrona Amiralen",
    "synonyms": [
      "KARLSKRONA AMIRALEN"
    ],
    "lId": "31800",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 56.197222222222216,
      "lon": 15.644444444444444
    }
  },
  {
    "name": "Karlskrona Amiralitetstorget",
    "synonyms": [
      "KARLSKRONA AMIRALITETSTORGET"
    ],
    "lId": "40917",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 56.159166666666664,
      "lon": 15.585277777777778
    }
  },
  {
    "name": "Karlskrona E22 McDonalds",
    "synonyms": [
      "KARLSKR E22 MCD",
      "KARLSKRONA E22 MCDONALDS",
      "KARLSKRONA E22MCDONALDS"
    ],
    "lId": "43896",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 56.203611111111115,
      "lon": 15.641666666666666
    }
  },
  {
    "name": "Karlskrona Verkö färjeterminal",
    "synonyms": [
      "KARLSKRONA VERKÖ FÄRJETERMINAL"
    ],
    "lId": "22976",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 56.164722222222224,
      "lon": 15.630555555555556
    }
  },
  {
    "name": "Karlstad C",
    "synonyms": [
      "KARLSTAD C"
    ],
    "lId": "00070",
    "prio": 1,
    "pId": "074",
    "pos": {
      "lat": 59.378055555555555,
      "lon": 13.498888888888889
    }
  },
  {
    "name": "Karlstad Bergvik Köpcenter",
    "synonyms": [
      "KARLSTAD BERGVIK K3PCENTER",
      "KARLSTAD BERGVIK KÖPCENTER"
    ],
    "lId": "57556",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.37722222222222,
      "lon": 13.42861111111111
    }
  },
  {
    "name": "Karlstad Campus Futurum",
    "synonyms": [
      "KARLSTAD CAMPUS FUTURUM"
    ],
    "lId": "57700",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.411944444444444,
      "lon": 13.571388888888889
    }
  },
  {
    "name": "Karlstad Carlstads Conference",
    "synonyms": [
      "KARLSTAD CARLSTADS CONFERENCE"
    ],
    "lId": "57602",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.382777777777775,
      "lon": 13.509444444444444
    }
  },
  {
    "name": "Karlstad Centralsjukhuset",
    "synonyms": [
      "KARLSTAD CENTRALSJUKHUSET"
    ],
    "lId": "24623",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.37416666666667,
      "lon": 13.481666666666667
    }
  },
  {
    "name": "Karlstad Färjestad Trav&Arena",
    "synonyms": [
      "KARLSTAD F2RJESTAD TRAV&ARENA",
      "KARLSTAD FÄRJESTAD TRAV&ARENA"
    ],
    "lId": "57955",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.40861111111111,
      "lon": 13.499722222222221
    }
  },
  {
    "name": "Karlstad Karolinen",
    "synonyms": [
      "KARLSTAD KAROLINEN"
    ],
    "lId": "23578",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.382222222222225,
      "lon": 13.488333333333333
    }
  },
  {
    "name": "Karlstad Länsstyrelsen",
    "synonyms": [
      "KARLSTAD L2NSSTYRELSEN",
      "KARLSTAD LÄNSSTYRELSEN"
    ],
    "lId": "23579",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.38194444444444,
      "lon": 13.493333333333332
    }
  },
  {
    "name": "Karlstad Mariebergsskogen",
    "synonyms": [
      "KARLSTAD MARIEBERGSSKOGEN"
    ],
    "lId": "57750",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.370555555555555,
      "lon": 13.486666666666666
    }
  },
  {
    "name": "Karlstad Universitetet",
    "synonyms": [
      "KARLSTAD UNIVERSITETET"
    ],
    "lId": "23232",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.405833333333334,
      "lon": 13.579166666666666
    }
  },
  {
    "name": "Karmansbo",
    "synonyms": [
      "KARMANSBO"
    ],
    "lId": "10762",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.69305555555555,
      "lon": 15.752222222222223
    }
  },
  {
    "name": "Karolinska sjukhuset",
    "synonyms": [
      "KAROLINSKA SJH",
      "KAROLINSKA SJUKHUSET"
    ],
    "lId": "01179",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.35277777777778,
      "lon": 18.031944444444445
    }
  },
  {
    "name": "Karpalund",
    "synonyms": [
      "KARPALUND",
      "KARPALUND LAGER"
    ],
    "lId": "10763",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 56.03861111111111,
      "lon": 14.093055555555557
    }
  },
  {
    "name": "Karsjö Ljusdal",
    "synonyms": [
      "KARSJÖ LJUSDAL",
      "KARSJØ LJUSDAL"
    ],
    "lId": "19069",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 61.63944444444444,
      "lon": 16.258333333333333
    }
  },
  {
    "name": "Karsudden",
    "synonyms": [
      "KARSUDDEN"
    ],
    "lId": "26081",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.01277777777778,
      "lon": 16.21333333333333
    }
  },
  {
    "name": "Karungi ICA",
    "synonyms": [
      "KARUNGI ICA"
    ],
    "lId": "14975",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 66.04305555555555,
      "lon": 23.959722222222222
    }
  },
  {
    "name": "Karups Nygård",
    "synonyms": [
      "KARUPS NYGÅRD"
    ],
    "lId": "14018",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 55.588055555555556,
      "lon": 13.637777777777778
    }
  },
  {
    "name": "Kastlösa",
    "synonyms": [
      "KASTLOSA",
      "KASTLÖSA",
      "KASTLØSA"
    ],
    "lId": "14238",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 56.456944444444446,
      "lon": 16.429722222222225
    }
  },
  {
    "name": "Katrineberg",
    "synonyms": [
      "KATRINEBERG",
      "KATRINEBERG FSK"
    ],
    "lId": "01475",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 56.972500000000004,
      "lon": 12.634722222222221
    }
  },
  {
    "name": "Katrineholm C",
    "synonyms": [
      "KATRINEHOLM C"
    ],
    "lId": "00166",
    "prio": 1,
    "pId": "074",
    "pos": {
      "lat": 58.99638888888889,
      "lon": 16.208055555555553
    }
  },
  {
    "name": "Kattarp",
    "synonyms": [
      "KATTARP",
      "KATTARP STN"
    ],
    "lId": "01544",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 56.14416666666666,
      "lon": 12.778333333333334
    }
  },
  {
    "name": "Katterat",
    "synonyms": [
      "KATTERAT"
    ],
    "lId": "02405",
    "prio": 0,
    "pId": "076",
    "pos": {
      "lat": 68.4063888888889,
      "lon": 17.915
    }
  },
  {
    "name": "Katterjåkk",
    "synonyms": [
      "KATTERJAKK",
      "KATTERJÅKK",
      "KATTERJÅKK STN"
    ],
    "lId": "01432",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 68.41916666666667,
      "lon": 18.163055555555555
    }
  },
  {
    "name": "Katthammarsvik",
    "synonyms": [
      "KATTHAMMARSVIK"
    ],
    "lId": "01138",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 57.43388888888889,
      "lon": 18.851111111111113
    }
  },
  {
    "name": "Kaxholmen",
    "synonyms": [
      "KAXHOLMEN",
      "KAXHOLMEN AFFÄR",
      "KAXHOLMEN AFFÆR"
    ],
    "lId": "01139",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 57.85138888888889,
      "lon": 14.305833333333334
    }
  },
  {
    "name": "Kaxås",
    "synonyms": [
      "KAXÅS"
    ],
    "lId": "13412",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 63.49444444444445,
      "lon": 13.899166666666666
    }
  },
  {
    "name": "KA2",
    "synonyms": [
      "KA2"
    ],
    "lId": "32108",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 56.212500000000006,
      "lon": 15.601111111111111
    }
  },
  {
    "name": "Kebnats/Saltoluokta",
    "synonyms": [
      "KEBNATS/SALTOLUOKTA"
    ],
    "lId": "00689",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 67.4175,
      "lon": 18.549444444444447
    }
  },
  {
    "name": "Kerstinbo",
    "synonyms": [
      "KERSTINBO"
    ],
    "lId": "17976",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 60.24055555555556,
      "lon": 16.959166666666665
    }
  },
  {
    "name": "Kiaby affären",
    "synonyms": [
      "KIABY AFFÄREN"
    ],
    "lId": "04128",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 56.06666666666667,
      "lon": 14.330833333333333
    }
  },
  {
    "name": "Kil",
    "synonyms": [
      "KIL",
      "KIL STN"
    ],
    "lId": "00206",
    "prio": 1,
    "pId": "074",
    "pos": {
      "lat": 59.505,
      "lon": 13.316111111111113
    }
  },
  {
    "name": "Kila kyrka",
    "synonyms": [
      "KILA KYRKA"
    ],
    "lId": "04048",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 58.74472222222222,
      "lon": 16.54888888888889
    }
  },
  {
    "name": "Kila Sala",
    "synonyms": [
      "KILA SALA"
    ],
    "lId": "44183",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.87305555555555,
      "lon": 16.543055555555558
    }
  },
  {
    "name": "Kilafors",
    "synonyms": [
      "KILAFORS",
      "KILAFORS STN"
    ],
    "lId": "00345",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 61.23083333333334,
      "lon": 16.57027777777778
    }
  },
  {
    "name": "Killeberg station",
    "synonyms": [
      "KILLEBERG STATION"
    ],
    "lId": "01605",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 56.474722222222226,
      "lon": 14.098333333333334
    }
  },
  {
    "name": "Killeberg Torget",
    "synonyms": [
      "KILLEBERG TORG",
      "KILLEBERG TORGET"
    ],
    "lId": "22098",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 56.475833333333334,
      "lon": 14.097777777777779
    }
  },
  {
    "name": "Killinge",
    "synonyms": [
      "KILLINGE"
    ],
    "lId": "67291",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.60111111111111,
      "lon": 17.610833333333336
    }
  },
  {
    "name": "Kilsmo Gästgivarvägen",
    "synonyms": [
      "KILSMO GÄSTGIVARVÄGEN",
      "KILSMO GÄSTGIVV",
      "KILSMO GÆSTGIVARVÆGEN",
      "KILSMO GÆSTGIVV"
    ],
    "lId": "21116",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.066944444444445,
      "lon": 15.538333333333334
    }
  },
  {
    "name": "Kimstad station",
    "synonyms": [
      "KIMSTAD STATION"
    ],
    "lId": "68883",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 58.545833333333334,
      "lon": 15.971666666666668
    }
  },
  {
    "name": "Kinna",
    "synonyms": [
      "KINNA",
      "KINNA STN"
    ],
    "lId": "00553",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 57.505833333333335,
      "lon": 12.698055555555555
    }
  },
  {
    "name": "Kinnared",
    "synonyms": [
      "KINNARED",
      "KINNARED STN"
    ],
    "lId": "00021",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 57.02611111111111,
      "lon": 13.105277777777777
    }
  },
  {
    "name": "Kinnarp",
    "synonyms": [
      "KINNARP"
    ],
    "lId": "00832",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 58.07416666666667,
      "lon": 13.520555555555557
    }
  },
  {
    "name": "Kiruna station",
    "synonyms": [
      "KIRUNA STATION"
    ],
    "lId": "01602",
    "prio": 1,
    "pId": "074",
    "pos": {
      "lat": 67.86722222222221,
      "lon": 20.200277777777778
    }
  },
  {
    "name": "Kisa",
    "synonyms": [
      "KISA",
      "KISA STN"
    ],
    "lId": "00344",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 57.98527777777778,
      "lon": 15.63361111111111
    }
  },
  {
    "name": "Kista T-bana",
    "synonyms": [
      "KISTA T-BANA"
    ],
    "lId": "12883",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.40277777777778,
      "lon": 17.942222222222224
    }
  },
  {
    "name": "Kitajaur station",
    "synonyms": [
      "KITAJAUR STATION",
      "KITAJAUR STN"
    ],
    "lId": "14726",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 66.17888888888889,
      "lon": 19.947222222222223
    }
  },
  {
    "name": "Kittelfjäll",
    "synonyms": [
      "KITTELFJÄLL",
      "KITTELFJÆLL"
    ],
    "lId": "00374",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 65.25055555555555,
      "lon": 15.500277777777777
    }
  },
  {
    "name": "Kivik",
    "synonyms": [
      "KIVIK",
      "KIVIK TORGET"
    ],
    "lId": "00341",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 55.684999999999995,
      "lon": 14.225555555555555
    }
  },
  {
    "name": "Kjula",
    "synonyms": [
      "KJULA",
      "KJULA KIOSKEN"
    ],
    "lId": "10788",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.38305555555556,
      "lon": 16.67638888888889
    }
  },
  {
    "name": "Klacka",
    "synonyms": [
      "KLACKA"
    ],
    "lId": "21547",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 58.837500000000006,
      "lon": 17.375833333333333
    }
  },
  {
    "name": "Klackberg",
    "synonyms": [
      "KLACKBERG"
    ],
    "lId": "71781",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 60.07666666666667,
      "lon": 15.89611111111111
    }
  },
  {
    "name": "Klagshamn",
    "synonyms": [
      "KLAGSHAMN"
    ],
    "lId": "16093",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 55.52361111111111,
      "lon": 12.931944444444444
    }
  },
  {
    "name": "Klagstorp Skola",
    "synonyms": [
      "KLAGSTORP SKOLA"
    ],
    "lId": "21810",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 55.393055555555556,
      "lon": 13.374444444444444
    }
  },
  {
    "name": "Klampenborg",
    "synonyms": [
      "KLAMPENBORG"
    ],
    "lId": "00659",
    "prio": 0,
    "pId": "086",
    "pos": {
      "lat": 55.777499999999996,
      "lon": 12.587777777777779
    }
  },
  {
    "name": "Klaråsen",
    "synonyms": [
      "KLARÅSEN"
    ],
    "lId": "10791",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 60.970555555555556,
      "lon": 12.489444444444443
    }
  },
  {
    "name": "Klasaröd",
    "synonyms": [
      "KLASARÖD"
    ],
    "lId": "14078",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 55.68333333333333,
      "lon": 13.838055555555556
    }
  },
  {
    "name": "Klavreström Majorsgatan",
    "synonyms": [
      "KLAVRESTRÖM MAJORSGATAN",
      "KLAVRESTRØM MAJORSGATAN"
    ],
    "lId": "05882",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 57.140277777777776,
      "lon": 15.134444444444444
    }
  },
  {
    "name": "Klenshyttan",
    "synonyms": [
      "KLENSHYTTAN"
    ],
    "lId": "12964",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 60.1025,
      "lon": 15.098611111111111
    }
  },
  {
    "name": "Klevshult",
    "synonyms": [
      "KLEVSHULT",
      "KLEVSHULT STN"
    ],
    "lId": "00490",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 57.3525,
      "lon": 14.097222222222223
    }
  },
  {
    "name": "Klimpfjäll",
    "synonyms": [
      "KLIMPFJÄLL",
      "KLIMPFJÆLL"
    ],
    "lId": "00436",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 65.06027777777777,
      "lon": 14.79138888888889
    }
  },
  {
    "name": "Klintehamn",
    "synonyms": [
      "KLINTEHAMN",
      "KLINTEHAMN KONS"
    ],
    "lId": "00917",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 57.38722222222222,
      "lon": 18.204722222222223
    }
  },
  {
    "name": "Klintehamn hamn",
    "synonyms": [
      "KLINTEHAMN HAMN"
    ],
    "lId": "10793",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 57.388888888888886,
      "lon": 18.18638888888889
    }
  },
  {
    "name": "Klippan",
    "synonyms": [
      "KLIPPAN",
      "KLIPPAN STN"
    ],
    "lId": "00121",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 56.130833333333335,
      "lon": 13.128333333333334
    }
  },
  {
    "name": "Klockestrand kiosk",
    "synonyms": [
      "KLOCKESTRAND KIOSK"
    ],
    "lId": "15187",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 62.88444444444444,
      "lon": 17.90583333333333
    }
  },
  {
    "name": "Klockhammar",
    "synonyms": [
      "KLOCKHAMMAR"
    ],
    "lId": "10797",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.382777777777775,
      "lon": 15.029722222222222
    }
  },
  {
    "name": "Klockrike",
    "synonyms": [
      "KLOCKRIKE"
    ],
    "lId": "10798",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 58.49722222222222,
      "lon": 15.336388888888889
    }
  },
  {
    "name": "Klågerup",
    "synonyms": [
      "KLÅGERUP",
      "KLÅGERUP BSTN"
    ],
    "lId": "00474",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 55.597500000000004,
      "lon": 13.26
    }
  },
  {
    "name": "Klädesholmen östra",
    "synonyms": [
      "KLÄDESHOLMEN ÖSTRA",
      "KLÆDESHOLMEN ØSTRA"
    ],
    "lId": "25009",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 57.94888888888889,
      "lon": 11.548055555555555
    }
  },
  {
    "name": "Kläppen",
    "synonyms": [
      "KLÄPPEN",
      "KLÆPPEN"
    ],
    "lId": "20862",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 61.03138888888889,
      "lon": 13.339166666666667
    }
  },
  {
    "name": "Klässbol Klädesvägen",
    "synonyms": [
      "KLÄSSBOL KLÄDESVÄGEN",
      "KLÄSSBOL KLÄDEV",
      "KLÆSSBOL KLÆDESVÆGEN",
      "KLÆSSBOL KLÆDEV"
    ],
    "lId": "10801",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.53944444444444,
      "lon": 12.74472222222222
    }
  },
  {
    "name": "Klövervägen",
    "synonyms": [
      "KLÖVERVÄGEN",
      "KLØVERVÆGEN"
    ],
    "lId": "24815",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.325,
      "lon": 17.973611111111108
    }
  },
  {
    "name": "Klövsjö by",
    "synonyms": [
      "KLÖVSJÖ BY",
      "KLØVSJØ  BY"
    ],
    "lId": "29816",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 62.528055555555554,
      "lon": 14.194166666666668
    }
  },
  {
    "name": "Klövsjö skidområde",
    "synonyms": [
      "KLÖVSJÖ SKIDOMRÅDE",
      "KLØVSJØ SKIDOMRÅDE"
    ],
    "lId": "62751",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 62.50277777777778,
      "lon": 14.179166666666665
    }
  },
  {
    "name": "Knalleland",
    "synonyms": [
      "KNALLELAND",
      "KNALLELAND STN"
    ],
    "lId": "01426",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 57.73361111111111,
      "lon": 12.9425
    }
  },
  {
    "name": "Knislinge",
    "synonyms": [
      "KNISLINGE",
      "KNISLINGE MTORG"
    ],
    "lId": "00337",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 56.19277777777778,
      "lon": 14.087222222222223
    }
  },
  {
    "name": "Knivsta Ar-terminalen",
    "synonyms": [
      "KNIVSTA AR-TERMINALEN"
    ],
    "lId": "20496",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.74,
      "lon": 17.809444444444445
    }
  },
  {
    "name": "Knivsta station",
    "synonyms": [
      "KNIVSTA STATION",
      "KNIVSTA STN"
    ],
    "lId": "00559",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.72555555555556,
      "lon": 17.78666666666667
    }
  },
  {
    "name": "Knutby",
    "synonyms": [
      "KNUTBY",
      "KNUTBY SKOLAN"
    ],
    "lId": "01003",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.91166666666666,
      "lon": 18.267777777777777
    }
  },
  {
    "name": "Knäckepilsgränd",
    "synonyms": [
      "KNÄCKEPILSGRÄND"
    ],
    "lId": "67303",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.38944444444444,
      "lon": 17.81638888888889
    }
  },
  {
    "name": "Knäred",
    "synonyms": [
      "KNÄRED",
      "KNÄRED STN",
      "KNÆRED STN"
    ],
    "lId": "00247",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 56.51444444444444,
      "lon": 13.315000000000001
    }
  },
  {
    "name": "Knäred Västralt",
    "synonyms": [
      "KNÄRED VÄSTRALT",
      "KNÆRED VÆSTRALT"
    ],
    "lId": "22981",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 56.515277777777776,
      "lon": 13.310555555555556
    }
  },
  {
    "name": "Knöstad bytespunkt",
    "synonyms": [
      "KNÖSTAD BYTESPU",
      "KNÖSTAD BYTESPUNKT"
    ],
    "lId": "24999",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.248333333333335,
      "lon": 12.832777777777778
    }
  },
  {
    "name": "Kode",
    "synonyms": [
      "KODE",
      "KODE STN"
    ],
    "lId": "00456",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 57.94416666666666,
      "lon": 11.850833333333332
    }
  },
  {
    "name": "Kokkedal",
    "synonyms": [
      "KOKKEDAL"
    ],
    "lId": "00664",
    "prio": 0,
    "pId": "086",
    "pos": {
      "lat": 55.90277777777778,
      "lon": 12.5025
    }
  },
  {
    "name": "Kolbäck",
    "synonyms": [
      "KOLBACK",
      "KOLBÄCK",
      "KOLBÄCK STN",
      "KOLBÆCK",
      "KOLBÆCK STN"
    ],
    "lId": "00321",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.56361111111111,
      "lon": 16.23222222222222
    }
  },
  {
    "name": "Kolmården station",
    "synonyms": [
      "KOLMARDEN STATION",
      "KOLMÅRDEN STATION",
      "KOLMÅRDEN STN"
    ],
    "lId": "01545",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 58.67527777777777,
      "lon": 16.3625
    }
  },
  {
    "name": "Kolmården Vildmarkshotell",
    "synonyms": [
      "KOLMÅRDEN VILDMARKSHOTELL"
    ],
    "lId": "10868",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 58.65861111111111,
      "lon": 16.4525
    }
  },
  {
    "name": "Kolmårdens Djurpark",
    "synonyms": [
      "KOLMARDENS DJURPARK",
      "KOLMÅRDEN DJURP",
      "KOLMÅRDENS DJURPARK"
    ],
    "lId": "00847",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 58.665,
      "lon": 16.46638888888889
    }
  },
  {
    "name": "Kolsnäs",
    "synonyms": [
      "KOLSNÄS",
      "KOLSNÄS STN",
      "KOLSNÆS",
      "KOLSNÆS STN"
    ],
    "lId": "01209",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.82555555555556,
      "lon": 13.140833333333333
    }
  },
  {
    "name": "Kolsva",
    "synonyms": [
      "KOLSVA",
      "KOLSVA CENTRUM"
    ],
    "lId": "00675",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.6,
      "lon": 15.842222222222222
    }
  },
  {
    "name": "Kolsätt",
    "synonyms": [
      "KOLSÄTT",
      "KOLSÆTT"
    ],
    "lId": "13342",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 62.03388888888889,
      "lon": 14.774166666666668
    }
  },
  {
    "name": "Konga",
    "synonyms": [
      "KONGA",
      "KONGA KONSUM"
    ],
    "lId": "01477",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 56.49472222222222,
      "lon": 15.119166666666667
    }
  },
  {
    "name": "Kongsvinger",
    "synonyms": [
      "KONGSVINGER"
    ],
    "lId": "00318",
    "prio": 0,
    "pId": "076",
    "pos": {
      "lat": 60.19027777777777,
      "lon": 12.036666666666667
    }
  },
  {
    "name": "Kopparberg",
    "synonyms": [
      "KOPPARBERG",
      "KOPPARBERG STN"
    ],
    "lId": "00280",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.8725,
      "lon": 14.986666666666666
    }
  },
  {
    "name": "Kopparmora",
    "synonyms": [
      "KOPPARMORA"
    ],
    "lId": "24941",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.339444444444446,
      "lon": 18.583333333333332
    }
  },
  {
    "name": "Kopperå",
    "synonyms": [
      "KOPPERA",
      "KOPPERÅ"
    ],
    "lId": "01215",
    "prio": 0,
    "pId": "076",
    "pos": {
      "lat": 63.425,
      "lon": 11.8925
    }
  },
  {
    "name": "Koppom Konsum",
    "synonyms": [
      "KOPPOM KONSUM",
      "KOPPOM TORGET"
    ],
    "lId": "00811",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.706944444444446,
      "lon": 12.150277777777777
    }
  },
  {
    "name": "Koppom skolan",
    "synonyms": [
      "KOPPOM SKOLAN"
    ],
    "lId": "20186",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.70055555555556,
      "lon": 12.148888888888889
    }
  },
  {
    "name": "Korpilombolo",
    "synonyms": [
      "KORPILOMBOLO"
    ],
    "lId": "00880",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 66.84888888888888,
      "lon": 23.06222222222222
    }
  },
  {
    "name": "Korrö",
    "synonyms": [
      "KORRÖ",
      "KORRØ"
    ],
    "lId": "01478",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 56.62555555555556,
      "lon": 15.195
    }
  },
  {
    "name": "Korsberga affär Västergötla",
    "synonyms": [
      "KORSBERGA AFFÄR VÄSTERGÖTLA",
      "KORSBERGA AFFÆR VÆSTERGØTLA"
    ],
    "lId": "10821",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 58.30361111111111,
      "lon": 14.09888888888889
    }
  },
  {
    "name": "Korsberga station Småland",
    "synonyms": [
      "KORSBERGA STATION SMÅLAND",
      "KORSBERGA STN"
    ],
    "lId": "00524",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 57.301111111111105,
      "lon": 15.125
    }
  },
  {
    "name": "Korskrogen",
    "synonyms": [
      "KORSKROGEN"
    ],
    "lId": "13512",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 61.81055555555555,
      "lon": 15.75388888888889
    }
  },
  {
    "name": "Kortedala Allhelgonakyrkan",
    "synonyms": [
      "KORTEDALA ALLHELGONAKYRKAN"
    ],
    "lId": "25604",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 57.757222222222225,
      "lon": 12.036666666666667
    }
  },
  {
    "name": "Kortedala Aprilgatan",
    "synonyms": [
      "KORTEDALA APRILGATAN"
    ],
    "lId": "25607",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 57.76111111111111,
      "lon": 12.04111111111111
    }
  },
  {
    "name": "Kortedala Januarigatan",
    "synonyms": [
      "KORTEDALA JANUARIGATAN"
    ],
    "lId": "25641",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 57.76027777777778,
      "lon": 12.04111111111111
    }
  },
  {
    "name": "Kortedala Runstavsgatan",
    "synonyms": [
      "KORTEDALA RUNSTAVSGATAN"
    ],
    "lId": "25675",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 57.7475,
      "lon": 12.030000000000001
    }
  },
  {
    "name": "Kortedala torg",
    "synonyms": [
      "KORTEDALA TORG"
    ],
    "lId": "15579",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 57.75277777777778,
      "lon": 12.03277777777778
    }
  },
  {
    "name": "Kosta Glasbruk",
    "synonyms": [
      "KOSTA GLASBRUK"
    ],
    "lId": "22470",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 56.84916666666667,
      "lon": 15.395
    }
  },
  {
    "name": "Kosteröarna",
    "synonyms": [
      "KOSTERÖARNA",
      "KOSTERØARNA"
    ],
    "lId": "01200",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 58.893055555555556,
      "lon": 11.009722222222223
    }
  },
  {
    "name": "Kottla",
    "synonyms": [
      "KOTTLA"
    ],
    "lId": "24791",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.344166666666666,
      "lon": 18.179722222222225
    }
  },
  {
    "name": "Kovland",
    "synonyms": [
      "KOVLAND"
    ],
    "lId": "15190",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 62.47,
      "lon": 17.15361111111111
    }
  },
  {
    "name": "Kragenäs vägskäl",
    "synonyms": [
      "KRAGENÄS VSK",
      "KRAGENÄS VÄGSKÄL",
      "KRAGENÆS VSK",
      "KRAGENÆS VÆGSKÆL"
    ],
    "lId": "16263",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 58.80138888888889,
      "lon": 11.257777777777777
    }
  },
  {
    "name": "Kragstalund station",
    "synonyms": [
      "KRAGSTALUND STATION",
      "KRAGSTALUND STN"
    ],
    "lId": "20873",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.51,
      "lon": 18.075277777777778
    }
  },
  {
    "name": "Kramfors station",
    "synonyms": [
      "KRAMFORS STATION",
      "KRAMFORS STN"
    ],
    "lId": "00220",
    "prio": 1,
    "pId": "074",
    "pos": {
      "lat": 62.928888888888885,
      "lon": 17.778055555555554
    }
  },
  {
    "name": "Krigslida",
    "synonyms": [
      "KRIGSLIDA",
      "KRIGSLIDA STN"
    ],
    "lId": "30026",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.10944444444445,
      "lon": 18.0675
    }
  },
  {
    "name": "Kristdala",
    "synonyms": [
      "KRISTDALA"
    ],
    "lId": "01142",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 57.400555555555556,
      "lon": 16.1975
    }
  },
  {
    "name": "Kristianopel",
    "synonyms": [
      "KRISTIANOPEL"
    ],
    "lId": "10826",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 56.257777777777775,
      "lon": 16.041111111111114
    }
  },
  {
    "name": "Kristianstad C",
    "synonyms": [
      "KRISTIANSTAD C"
    ],
    "lId": "00200",
    "prio": 1,
    "pId": "074",
    "pos": {
      "lat": 56.031666666666666,
      "lon": 14.151111111111112
    }
  },
  {
    "name": "Kristianstad busstation",
    "synonyms": [
      "KRISTIANSTAD BUSSTATION",
      "KRISTIANSTD BST"
    ],
    "lId": "10827",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 56.029444444444444,
      "lon": 14.16
    }
  },
  {
    "name": "Kristianstad Statoil",
    "synonyms": [
      "KRISTIANSTAD STATOIL"
    ],
    "lId": "71575",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 56.02333333333333,
      "lon": 14.173888888888888
    }
  },
  {
    "name": "Kristianstad Österlen Airport",
    "synonyms": [
      "EVERÖD AIRPORT",
      "KRISTIANST AIRP",
      "KRISTIANSTAD ÖSTERLEN AIRPORT"
    ],
    "lId": "08368",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 55.92388888888889,
      "lon": 14.073888888888888
    }
  },
  {
    "name": "Kristineberg",
    "synonyms": [
      "KRISTINEBERG"
    ],
    "lId": "00074",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 65.06027777777777,
      "lon": 18.57361111111111
    }
  },
  {
    "name": "Kristineberg Syd",
    "synonyms": [
      "KRISTINEBERG SYD"
    ],
    "lId": "16424",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 55.538888888888884,
      "lon": 13.075
    }
  },
  {
    "name": "Kristineberg T-bana",
    "synonyms": [
      "KRISTINEBERG T-BANA"
    ],
    "lId": "21663",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.33277777777778,
      "lon": 18.003055555555555
    }
  },
  {
    "name": "Kristinehamn",
    "synonyms": [
      "KRISTINEHAMN",
      "KRISTINEHMN STN"
    ],
    "lId": "00222",
    "prio": 1,
    "pId": "074",
    "pos": {
      "lat": 59.31638888888889,
      "lon": 14.108055555555556
    }
  },
  {
    "name": "Kristvallabrunn",
    "synonyms": [
      "KRISTVALLABRUNN"
    ],
    "lId": "14249",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 56.77611111111111,
      "lon": 16.053055555555556
    }
  },
  {
    "name": "Krokek Sandviken",
    "synonyms": [
      "KROKEK SANDVIKEN"
    ],
    "lId": "00848",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 58.66083333333333,
      "lon": 16.401944444444442
    }
  },
  {
    "name": "Krokom",
    "synonyms": [
      "KROKOM",
      "KROKOM STN"
    ],
    "lId": "00228",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 63.325833333333335,
      "lon": 14.448333333333334
    }
  },
  {
    "name": "Krokvik",
    "synonyms": [
      "KROKVIK",
      "KROKVIK STN"
    ],
    "lId": "00174",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 67.93222222222222,
      "lon": 20.066111111111113
    }
  },
  {
    "name": "Kråksjö",
    "synonyms": [
      "KRÅKSJÖ",
      "KRÅKSJØ"
    ],
    "lId": "10835",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 56.64277777777778,
      "lon": 15.351944444444444
    }
  },
  {
    "name": "Krägga herrgård",
    "synonyms": [
      "KRÄGGA HERRGÅRD",
      "KRÆGGA HERRGÅRD"
    ],
    "lId": "12865",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.60444444444445,
      "lon": 17.406388888888888
    }
  },
  {
    "name": "Kräklingbo",
    "synonyms": [
      "KRÄKLINGBO",
      "KRÄKLINGBO AFFÄ",
      "KRÆKLINGBO",
      "KRÆKLINGBO AFFÆ"
    ],
    "lId": "01143",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 57.44583333333333,
      "lon": 18.710277777777776
    }
  },
  {
    "name": "Kubbe",
    "synonyms": [
      "KUBBE"
    ],
    "lId": "29095",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 63.520833333333336,
      "lon": 18.060833333333335
    }
  },
  {
    "name": "Kullavik",
    "synonyms": [
      "KULLAVIK",
      "KULLAVIK HAMN"
    ],
    "lId": "16008",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 57.545833333333334,
      "lon": 11.924722222222222
    }
  },
  {
    "name": "Kulltorp skolan",
    "synonyms": [
      "KULLTORP SKOLAN"
    ],
    "lId": "22860",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 57.26027777777778,
      "lon": 13.787222222222223
    }
  },
  {
    "name": "Kumla",
    "synonyms": [
      "KUMLA",
      "KUMLA STN"
    ],
    "lId": "00192",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.12638888888889,
      "lon": 15.140555555555554
    }
  },
  {
    "name": "Kumla kyrkby Västmanland",
    "synonyms": [
      "KUMLA KYRKBY VÄSTMANLAND",
      "KUMLA KYRKBY VÆSTMANLAND"
    ],
    "lId": "20839",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.843611111111116,
      "lon": 16.63722222222222
    }
  },
  {
    "name": "Kummelnäs",
    "synonyms": [
      "KUMMELNÄS",
      "KUMMELNÆS"
    ],
    "lId": "26545",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.352222222222224,
      "lon": 18.27361111111111
    }
  },
  {
    "name": "Kungens Kurva IKEA södra",
    "synonyms": [
      "KUNGENS KURVA IKEA SÖDRA",
      "KUNGENS KURVA IKEA SØDRA"
    ],
    "lId": "45557",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.27027777777778,
      "lon": 17.9175
    }
  },
  {
    "name": "Kungs Barkarö kyrka",
    "synonyms": [
      "KUNGS BARKARÖ KYRKA",
      "KUNGS BARKARØ KYRKA"
    ],
    "lId": "09046",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.45027777777778,
      "lon": 16.03611111111111
    }
  },
  {
    "name": "Kungsbacka",
    "synonyms": [
      "KUNGSBACKA",
      "KUNGSBACKA STN"
    ],
    "lId": "00161",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 57.489444444444445,
      "lon": 12.08
    }
  },
  {
    "name": "Kungsbacka Basunvägen",
    "synonyms": [
      "KUNGSBACKA BASUNVÄGEN"
    ],
    "lId": "61357",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 57.492222222222225,
      "lon": 12.104166666666666
    }
  },
  {
    "name": "Kungsbacka Hede",
    "synonyms": [
      "KUNGSBACKA HEDE"
    ],
    "lId": "01144",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 57.51305555555555,
      "lon": 12.083333333333334
    }
  },
  {
    "name": "Kungsberg",
    "synonyms": [
      "KUNGSBERG"
    ],
    "lId": "01151",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 60.76138888888889,
      "lon": 16.454722222222223
    }
  },
  {
    "name": "Kungsberga Konsum",
    "synonyms": [
      "KUNGSBERGA KONSUM"
    ],
    "lId": "25944",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.404444444444444,
      "lon": 17.631944444444446
    }
  },
  {
    "name": "Kungsberget",
    "synonyms": [
      "KUNGSBERGET"
    ],
    "lId": "19793",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 60.761944444444445,
      "lon": 16.500833333333333
    }
  },
  {
    "name": "Kungsgården klockargården",
    "synonyms": [
      "KUNGSGÅRDEN KLO",
      "KUNGSGÅRDEN KLOCKARGÅRDEN"
    ],
    "lId": "10847",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 60.60611111111111,
      "lon": 16.61277777777778
    }
  },
  {
    "name": "Kungshamn",
    "synonyms": [
      "KUNGSHAMN",
      "KUNGSHAMN BSTN"
    ],
    "lId": "00356",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 58.36138888888889,
      "lon": 11.249166666666666
    }
  },
  {
    "name": "Kungshult väg 17",
    "synonyms": [
      "KUNGSHULT VÄG 17",
      "KUNGSHULT VÄG17",
      "KUNGSHULT VÆG 17",
      "KUNGSHULT VÆG17"
    ],
    "lId": "16727",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 55.85111111111111,
      "lon": 13.412222222222223
    }
  },
  {
    "name": "Kungsträdgården T-bana",
    "synonyms": [
      "KUNGSTRÄDGÅRDEN T-BANA",
      "KUNGSTRÆDGÅRDEN T-BANA"
    ],
    "lId": "21659",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.330555555555556,
      "lon": 18.073055555555555
    }
  },
  {
    "name": "Kungsängen",
    "synonyms": [
      "KUNGSANGEN",
      "KUNGSÄNGEN",
      "KUNGSÄNGEN STN",
      "KUNGSÆNGEN",
      "KUNGSÆNGEN STN"
    ],
    "lId": "00284",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.47777777777778,
      "lon": 17.7525
    }
  },
  {
    "name": "Kungsängen Tammsvik",
    "synonyms": [
      "KUNGSÄNGEN TAMMSVIK"
    ],
    "lId": "66892",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.50083333333333,
      "lon": 17.58861111111111
    }
  },
  {
    "name": "Kungsäter kyrka",
    "synonyms": [
      "KUNGSÄTER KYRKA",
      "KUNGSÆTER KYRKA"
    ],
    "lId": "10849",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 57.30722222222222,
      "lon": 12.571111111111112
    }
  },
  {
    "name": "Kungsör station",
    "synonyms": [
      "KUNGSOR  STATION",
      "KUNGSOR STN",
      "KUNGSÖR STATION",
      "KUNGSÖR STN",
      "KUNGSØR STATION",
      "KUNGSØR STN"
    ],
    "lId": "00676",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.427499999999995,
      "lon": 16.099722222222223
    }
  },
  {
    "name": "Kungsör Torpa kyrka",
    "synonyms": [
      "KUNGSÖR TORPA KYRKA"
    ],
    "lId": "21968",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.42194444444444,
      "lon": 16.186944444444446
    }
  },
  {
    "name": "Kungälv",
    "synonyms": [
      "KUNGÄLV",
      "KUNGÄLV BSTN",
      "KUNGÆLV",
      "KUNGÆLV BSTN"
    ],
    "lId": "00580",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 57.8725,
      "lon": 11.979444444444445
    }
  },
  {
    "name": "Kungälv Eriksdal",
    "synonyms": [
      "KUNGÄLV ERIKSDAL"
    ],
    "lId": "15561",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 57.85777777777778,
      "lon": 11.99861111111111
    }
  },
  {
    "name": "Kusmark",
    "synonyms": [
      "KUSMARK"
    ],
    "lId": "13841",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 64.8775,
      "lon": 20.80027777777778
    }
  },
  {
    "name": "Kvarn Stridsskolan",
    "synonyms": [
      "KVARN STRIDSSKOLAN"
    ],
    "lId": "23461",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 58.63333333333333,
      "lon": 15.316666666666666
    }
  },
  {
    "name": "Kvarnholmen",
    "synonyms": [
      "KVARNHOLMEN"
    ],
    "lId": "18250",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.31583333333333,
      "lon": 18.139444444444443
    }
  },
  {
    "name": "Kvarnsjö station",
    "synonyms": [
      "KVARNSJÖ STATION",
      "KVARNSJÖ STN",
      "KVARNSJØ STATION",
      "KVARNSJØ STN"
    ],
    "lId": "04426",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 62.56583333333333,
      "lon": 14.372222222222224
    }
  },
  {
    "name": "Kvarntorp Gejrots väg",
    "synonyms": [
      "KVARNTORP GEJRO",
      "KVARNTORP GEJROTS VÄG",
      "KVARNTORP GEJROTS VÆG"
    ],
    "lId": "04277",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.13027777777778,
      "lon": 15.270555555555557
    }
  },
  {
    "name": "Kvarsebo",
    "synonyms": [
      "KVARSEBO"
    ],
    "lId": "10855",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 58.64138888888889,
      "lon": 16.63
    }
  },
  {
    "name": "Kvibille",
    "synonyms": [
      "KVIBILLE",
      "KVIBILLE GÄSTIS",
      "KVIBILLE GÆSTIS"
    ],
    "lId": "01479",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 56.782777777777774,
      "lon": 12.831944444444444
    }
  },
  {
    "name": "Kvicksund station",
    "synonyms": [
      "KVICKSUND STATION",
      "KVICKSUND STN"
    ],
    "lId": "00677",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.450833333333335,
      "lon": 16.32027777777778
    }
  },
  {
    "name": "Kvidinge",
    "synonyms": [
      "KVIDINGE"
    ],
    "lId": "16728",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 56.13444444444444,
      "lon": 13.046111111111111
    }
  },
  {
    "name": "Kvidinge station",
    "synonyms": [
      "KVIDINGE STATION"
    ],
    "lId": "01610",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 56.13722222222222,
      "lon": 13.046666666666667
    }
  },
  {
    "name": "Kvikkjokk",
    "synonyms": [
      "KVIKKJOKK",
      "KVIKKJOKK KYRKA"
    ],
    "lId": "00881",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 66.95166666666667,
      "lon": 17.72083333333333
    }
  },
  {
    "name": "Kvillsfors",
    "synonyms": [
      "KVILLSFORS",
      "KVILLSFORS STN"
    ],
    "lId": "01145",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 57.403888888888886,
      "lon": 15.496666666666666
    }
  },
  {
    "name": "Kvinnerstaskolan",
    "synonyms": [
      "KVINNERSTASKOLAN"
    ],
    "lId": "21154",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.35583333333334,
      "lon": 15.237777777777778
    }
  },
  {
    "name": "Kvissleby centrum",
    "synonyms": [
      "KVISSLEBY CENTRUM",
      "KVISSLEBY CM"
    ],
    "lId": "15194",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 62.300555555555555,
      "lon": 17.377222222222223
    }
  },
  {
    "name": "Kvistofta kyrka",
    "synonyms": [
      "KVISTOFTA KYRKA"
    ],
    "lId": "16729",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 55.968333333333334,
      "lon": 12.828888888888889
    }
  },
  {
    "name": "Kvänum",
    "synonyms": [
      "KVÄNUM",
      "KVÄNUM BSTN",
      "KVÆNUM",
      "KVÆNUM BSTN"
    ],
    "lId": "01146",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 58.29972222222222,
      "lon": 13.186944444444444
    }
  },
  {
    "name": "Kvärlöv",
    "synonyms": [
      "KVÄRLÖV"
    ],
    "lId": "23585",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 55.83833333333334,
      "lon": 12.987777777777778
    }
  },
  {
    "name": "Kymmendö brygga",
    "synonyms": [
      "KYMMENDÖ BRYGGA",
      "KYMMENDØ BRYGGA"
    ],
    "lId": "18277",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.11083333333333,
      "lon": 18.489444444444445
    }
  },
  {
    "name": "Kyrkekvarn väg 26",
    "synonyms": [
      "KYRKEKVARN VÄG 26"
    ],
    "lId": "71680",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 57.9925,
      "lon": 13.83
    }
  },
  {
    "name": "Kyrkheddinge väg 11",
    "synonyms": [
      "KYRKHEDDING V11",
      "KYRKHEDDINGE VÄG 11",
      "KYRKHEDDINGE VÆG 11"
    ],
    "lId": "12495",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 55.64527777777778,
      "lon": 13.272222222222224
    }
  },
  {
    "name": "Kyrkhult",
    "synonyms": [
      "KYRKHULT"
    ],
    "lId": "00548",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 56.356944444444444,
      "lon": 14.586944444444445
    }
  },
  {
    "name": "Kyrktåsjö",
    "synonyms": [
      "KYRKTÅSJÖ",
      "KYRKTÅSJØ",
      "TÅSJÖ",
      "TÅSJØ"
    ],
    "lId": "01147",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 64.2225,
      "lon": 15.903333333333334
    }
  },
  {
    "name": "Kåbdalis affär",
    "synonyms": [
      "KÅBDALIS AFFÄR",
      "KÅBDALIS AFFÆR"
    ],
    "lId": "04421",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 66.14416666666668,
      "lon": 19.99388888888889
    }
  },
  {
    "name": "Kåge",
    "synonyms": [
      "KÅGE",
      "KÅGE BYN"
    ],
    "lId": "00377",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 64.83194444444445,
      "lon": 20.989722222222223
    }
  },
  {
    "name": "Kågeröd Lunnaskolan",
    "synonyms": [
      "KÅGERÖD LUNNASKOLAN",
      "KÅGERØD LUNNASKOLAN"
    ],
    "lId": "35364",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 55.999722222222225,
      "lon": 13.09
    }
  },
  {
    "name": "Kållekärr",
    "synonyms": [
      "KÅLLEKÄRR",
      "KÅLLEKÆRR"
    ],
    "lId": "15802",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 58.02444444444444,
      "lon": 11.657222222222222
    }
  },
  {
    "name": "Kållered",
    "synonyms": [
      "KÅLLERED",
      "KÅLLERED STN"
    ],
    "lId": "00335",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 57.609722222222224,
      "lon": 12.04861111111111
    }
  },
  {
    "name": "Kålshester",
    "synonyms": [
      "KÅLSHESTER"
    ],
    "lId": "10870",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 57.73444444444444,
      "lon": 15.055000000000001
    }
  },
  {
    "name": "Kånna",
    "synonyms": [
      "KÅNNA"
    ],
    "lId": "24648",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 56.782777777777774,
      "lon": 13.895833333333332
    }
  },
  {
    "name": "Kårböle",
    "synonyms": [
      "KÅRBÖLE",
      "KÅRBÖLE PILGRIM",
      "KÅRBØLE",
      "KÅRBØLE PILGRIM"
    ],
    "lId": "00463",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 61.98694444444445,
      "lon": 15.29861111111111
    }
  },
  {
    "name": "Kåremo E22",
    "synonyms": [
      "KÅREMO E22"
    ],
    "lId": "14485",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 56.85,
      "lon": 16.376944444444444
    }
  },
  {
    "name": "Kårsta",
    "synonyms": [
      "KÅRSTA",
      "KÅRSTA STN"
    ],
    "lId": "00713",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.656666666666666,
      "lon": 18.26722222222222
    }
  },
  {
    "name": "Kåseberga",
    "synonyms": [
      "ALE STENAR",
      "ALES STENAR",
      "KÅSEBERGA",
      "KÅSEBERGA S"
    ],
    "lId": "01149",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 55.38666666666666,
      "lon": 14.064722222222223
    }
  },
  {
    "name": "Kälarne",
    "synonyms": [
      "KÄLARNE",
      "KÄLARNE PARKEN",
      "KÆLARNE",
      "KÆLARNE PARKEN"
    ],
    "lId": "01216",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 62.98027777777778,
      "lon": 16.085277777777776
    }
  },
  {
    "name": "Källbrink Källbrinksskolan",
    "synonyms": [
      "KÄLLBRINK KÄLLBRINKSSKOLAN",
      "KÄLLBRINKSSKOLA",
      "KÆLLBRINK KÆLLBRINKSSKOLAN",
      "KÆLLBRINKSSKOLA"
    ],
    "lId": "45558",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.249722222222225,
      "lon": 17.96222222222222
    }
  },
  {
    "name": "Källby",
    "synonyms": [
      "KALLBY",
      "KÄLLBY",
      "KÄLLBY STN",
      "KÆLLBY",
      "KÆLLBY STN"
    ],
    "lId": "00478",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 58.510555555555555,
      "lon": 13.302222222222223
    }
  },
  {
    "name": "Källfallet Skinnskatteberg",
    "synonyms": [
      "KÄLLFALLET SKINNSKATTEBERG"
    ],
    "lId": "44852",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.82194444444445,
      "lon": 15.532222222222224
    }
  },
  {
    "name": "Kämpinge skolan",
    "synonyms": [
      "KÄMPINGE SKOLAN",
      "KÆMPINGE SKOLAN"
    ],
    "lId": "12585",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 55.403888888888886,
      "lon": 12.995833333333332
    }
  },
  {
    "name": "Köping Hökartorget",
    "synonyms": [
      "KÖPING HÖKARTORGET"
    ],
    "lId": "45073",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.51305555555555,
      "lon": 15.996944444444443
    }
  },
  {
    "name": "Käppala",
    "synonyms": [
      "KÄPPALA",
      "KÆPPALA"
    ],
    "lId": "24793",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.3525,
      "lon": 18.217777777777776
    }
  },
  {
    "name": "Kärda väg 27",
    "synonyms": [
      "KÄRDA VÄG 27",
      "KÆRDA VÆG 27"
    ],
    "lId": "22855",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 57.17666666666666,
      "lon": 13.92
    }
  },
  {
    "name": "Käringön",
    "synonyms": [
      "KÄRINGÖN",
      "KÆRINGØN"
    ],
    "lId": "01218",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 58.11277777777778,
      "lon": 11.365833333333333
    }
  },
  {
    "name": "Kärra Klareberg",
    "synonyms": [
      "KÄRRA KLAREBERG"
    ],
    "lId": "15575",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 57.8,
      "lon": 11.991666666666665
    }
  },
  {
    "name": "Kärrgruvan",
    "synonyms": [
      "KÄRRGRUVAN",
      "KÆRRGRUVAN"
    ],
    "lId": "10882",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 60.10166666666667,
      "lon": 15.928055555555554
    }
  },
  {
    "name": "Kärrtorp T-bana",
    "synonyms": [
      "KÄRRTORP T-BANA",
      "KÆRRTORP T-BANA"
    ],
    "lId": "21693",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.28444444444444,
      "lon": 18.114444444444445
    }
  },
  {
    "name": "Kättbo",
    "synonyms": [
      "KÄTTBO",
      "KÄTTBO PARKERIN",
      "KÆTTBO",
      "KÆTTBO PARKERIN"
    ],
    "lId": "13078",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 60.844166666666666,
      "lon": 14.199722222222222
    }
  },
  {
    "name": "Kättilsmåla",
    "synonyms": [
      "KÄTTILSMÅLA",
      "KÆTTILSMÅLA"
    ],
    "lId": "10884",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 56.27638888888889,
      "lon": 15.73611111111111
    }
  },
  {
    "name": "Kättilstorp",
    "synonyms": [
      "KÄTTILSTORP",
      "KÆTTILSTORP"
    ],
    "lId": "04240",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 58.04083333333333,
      "lon": 13.709444444444443
    }
  },
  {
    "name": "Kävlinge",
    "synonyms": [
      "KAVLINGE",
      "KÄVLINGE",
      "KÄVLINGE STN",
      "KÆVLINGE",
      "KÆVLINGE STN"
    ],
    "lId": "00945",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 55.79416666666666,
      "lon": 13.111388888888888
    }
  },
  {
    "name": "Köbenhavn H",
    "synonyms": [
      "COPENHAGEN CENTRAL STATION",
      "COPENHAGEN H",
      "KOBENHAVN H",
      "KOEBENHAVN H",
      "KOPENHAMN",
      "KÖBENHAVN H",
      "KÖPENHAMN H",
      "KØBENHAVN H",
      "ZGH"
    ],
    "lId": "00626",
    "prio": 1,
    "pId": "086",
    "pos": {
      "lat": 55.67305555555555,
      "lon": 12.565277777777778
    }
  },
  {
    "name": "Köbenhavn Österport",
    "synonyms": [
      "COPENHAGEN ÖSTERPORT",
      "KÖBENHAVN ÖSTERPORT",
      "KÖPENHAMN ÖSTERPORT",
      "OESTERPORT"
    ],
    "lId": "00650",
    "prio": 0,
    "pId": "086",
    "pos": {
      "lat": 55.692499999999995,
      "lon": 12.587777777777779
    }
  },
  {
    "name": "Kölsillre",
    "synonyms": [
      "KÖLSILLRE",
      "KØLSILLRE"
    ],
    "lId": "15197",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 62.3975,
      "lon": 15.209999999999999
    }
  },
  {
    "name": "Köping station",
    "synonyms": [
      "KOPING",
      "KÖPING STATION",
      "KÖPING STN",
      "KØPING",
      "KØPING STN"
    ],
    "lId": "00167",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.50666666666667,
      "lon": 16.004166666666666
    }
  },
  {
    "name": "Köpingebro",
    "synonyms": [
      "KOPINGEBRO",
      "KÖPINGEBRO",
      "KÖPINGEBRO STN",
      "KØPINGEBRO",
      "KØPINGEBRO STN"
    ],
    "lId": "00946",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 55.45722222222223,
      "lon": 13.935555555555556
    }
  },
  {
    "name": "Köpingsvik",
    "synonyms": [
      "KÖPINGSVIK",
      "KÖPINGSVIK KA",
      "KØPINGSVIK",
      "KØPINGSVIK KA"
    ],
    "lId": "01219",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 56.87916666666667,
      "lon": 16.71833333333333
    }
  },
  {
    "name": "Köpmanholmen",
    "synonyms": [
      "KÖPMANHOLMEN",
      "KÖPMANHOLMENKAJ",
      "KØPMANHOLMEN",
      "KØPMANHOLMENKAJ"
    ],
    "lId": "01220",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 63.16972222222222,
      "lon": 18.590277777777775
    }
  },
  {
    "name": "Köpstadsö",
    "synonyms": [
      "KÖPSTADSÖ",
      "KØPSTADSØ"
    ],
    "lId": "01204",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 57.625,
      "lon": 11.809444444444445
    }
  },
  {
    "name": "Lagan",
    "synonyms": [
      "LAGAN",
      "LAGAN TORGGATAN"
    ],
    "lId": "00519",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 56.91611111111111,
      "lon": 13.987222222222222
    }
  },
  {
    "name": "Lagga skola",
    "synonyms": [
      "LAGGA SKOLA"
    ],
    "lId": "21040",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.79666666666667,
      "lon": 17.83722222222222
    }
  },
  {
    "name": "Lagnö",
    "synonyms": [
      "LAGNÖ",
      "LAGNÖ VÄNDPL",
      "LAGNØ",
      "LAGNØ VÆNDPL"
    ],
    "lId": "01152",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 58.3525,
      "lon": 16.816111111111113
    }
  },
  {
    "name": "Laholm",
    "synonyms": [
      "LAHOLM",
      "LAHOLM STN"
    ],
    "lId": "00058",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 56.501666666666665,
      "lon": 12.999444444444444
    }
  },
  {
    "name": "Laholm busstation",
    "synonyms": [
      "LAHOLM BSTN",
      "LAHOLM BUSSTATION"
    ],
    "lId": "10896",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 56.51138888888889,
      "lon": 13.046944444444444
    }
  },
  {
    "name": "Lahäll station",
    "synonyms": [
      "LAHÄLL STATION",
      "LAHÄLL STN",
      "LAHÆLL STATION",
      "LAHÆLL STN"
    ],
    "lId": "24371",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.42388888888889,
      "lon": 18.073888888888888
    }
  },
  {
    "name": "Laisvall",
    "synonyms": [
      "LAISVALL"
    ],
    "lId": "01221",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 66.13083333333333,
      "lon": 17.16472222222222
    }
  },
  {
    "name": "Lammhult station",
    "synonyms": [
      "LAMMHULT STATION",
      "LAMMHULT STN"
    ],
    "lId": "37092",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 57.170833333333334,
      "lon": 14.585277777777778
    }
  },
  {
    "name": "Landeryd",
    "synonyms": [
      "LANDERYD",
      "LANDERYD STN"
    ],
    "lId": "00116",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 57.07666666666667,
      "lon": 13.266111111111112
    }
  },
  {
    "name": "Landfjärden norra",
    "synonyms": [
      "LANDFJÄRDEN NORRA"
    ],
    "lId": "69626",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.035,
      "lon": 17.991111111111113
    }
  },
  {
    "name": "Landsbro",
    "synonyms": [
      "LANDSBRO",
      "LANDSBRO BSTN"
    ],
    "lId": "01222",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 57.369166666666665,
      "lon": 14.900277777777777
    }
  },
  {
    "name": "Landskrona Drottninggatan",
    "synonyms": [
      "LANDSKRONA DROTTNINGGATAN"
    ],
    "lId": "00211",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 55.867777777777775,
      "lon": 12.830833333333333
    }
  },
  {
    "name": "Landskrona Skeppsbron",
    "synonyms": [
      "LANDSKRONA SKEPPSBRON"
    ],
    "lId": "17342",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 55.86555555555556,
      "lon": 12.826666666666666
    }
  },
  {
    "name": "Landskrona station",
    "synonyms": [
      "LANDSKRONA STATION"
    ],
    "lId": "01554",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 55.87888888888889,
      "lon": 12.857222222222221
    }
  },
  {
    "name": "Landsort brygga",
    "synonyms": [
      "LANDSORT BRYGGA"
    ],
    "lId": "24878",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 58.74444444444445,
      "lon": 17.865000000000002
    }
  },
  {
    "name": "Landvetter centrum",
    "synonyms": [
      "LANDVETTER CENTRUM",
      "LANDVETTER CM"
    ],
    "lId": "00865",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 57.68611111111111,
      "lon": 12.213333333333333
    }
  },
  {
    "name": "Landvetter flygplats",
    "synonyms": [
      "LANDVETTER FLYGPLATS",
      "LANDVETTER FPL"
    ],
    "lId": "00554",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 57.66777777777777,
      "lon": 12.295833333333333
    }
  },
  {
    "name": "Landvettermotet",
    "synonyms": [
      "LANDVETTERMOTET"
    ],
    "lId": "35841",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 57.684999999999995,
      "lon": 12.21111111111111
    }
  },
  {
    "name": "Landön",
    "synonyms": [
      "LANDÖN",
      "LANDØN"
    ],
    "lId": "13399",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 63.56638888888889,
      "lon": 14.270833333333334
    }
  },
  {
    "name": "Lanna",
    "synonyms": [
      "LANNA"
    ],
    "lId": "22861",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 57.22083333333334,
      "lon": 13.783055555555556
    }
  },
  {
    "name": "Lansjärv",
    "synonyms": [
      "LANSJÄRV",
      "LANSJÄRV G AFFÄ",
      "LANSJÆRV",
      "LANSJÆRV G AFFÆ"
    ],
    "lId": "01223",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 66.6563888888889,
      "lon": 22.191944444444445
    }
  },
  {
    "name": "Lansjärv E10",
    "synonyms": [
      "LANSJÄRV E10",
      "LANSJÄRV E10 N",
      "LANSJÆRV E10",
      "LANSJÆRV E10 N"
    ],
    "lId": "20374",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 66.65833333333335,
      "lon": 22.17361111111111
    }
  },
  {
    "name": "Lappberg station",
    "synonyms": [
      "LAPPBERG STATION",
      "LAPPBERG STN"
    ],
    "lId": "00199",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 67.59194444444444,
      "lon": 20.195
    }
  },
  {
    "name": "Lappträsk Lantmännen",
    "synonyms": [
      "LAPPTRÄSK LANTMÄNNEN",
      "LAPPTRÆSK LANTMÆNNEN"
    ],
    "lId": "23339",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 66.01055555555556,
      "lon": 23.485277777777778
    }
  },
  {
    "name": "Larsberg",
    "synonyms": [
      "LARSBERG"
    ],
    "lId": "24790",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.35027777777778,
      "lon": 18.14611111111111
    }
  },
  {
    "name": "Latikberg",
    "synonyms": [
      "LATIKBERG"
    ],
    "lId": "13883",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 64.64194444444445,
      "lon": 17.05777777777778
    }
  },
  {
    "name": "Latorp skola",
    "synonyms": [
      "LATORP SKOLA"
    ],
    "lId": "10905",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.27638888888889,
      "lon": 14.987222222222222
    }
  },
  {
    "name": "Laxne",
    "synonyms": [
      "LAXNE"
    ],
    "lId": "18255",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.17027777777778,
      "lon": 17.184722222222224
    }
  },
  {
    "name": "Laxsjö",
    "synonyms": [
      "LAXSJÖ",
      "LAXSJØ"
    ],
    "lId": "13220",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 63.81222222222222,
      "lon": 14.796944444444444
    }
  },
  {
    "name": "Laxvik",
    "synonyms": [
      "LAXVIK"
    ],
    "lId": "17106",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 56.59805555555556,
      "lon": 12.922777777777776
    }
  },
  {
    "name": "Laxå station",
    "synonyms": [
      "LAXA",
      "LAXÅ STATION",
      "LAXÅ STN"
    ],
    "lId": "00194",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 58.98916666666667,
      "lon": 14.616388888888888
    }
  },
  {
    "name": "Leipojärvi E10",
    "synonyms": [
      "LEIPOJÄRVI E10",
      "LEIPOJÆRVI E10"
    ],
    "lId": "23768",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 67.05166666666666,
      "lon": 21.193055555555556
    }
  },
  {
    "name": "Lekeryd",
    "synonyms": [
      "LEKERYD",
      "LEKERYD AFFÄREN",
      "LEKERYD AFFÆREN"
    ],
    "lId": "01225",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 57.77388888888889,
      "lon": 14.41861111111111
    }
  },
  {
    "name": "Leksand",
    "synonyms": [
      "LEKSAND",
      "LEKSAND STN"
    ],
    "lId": "00019",
    "prio": 1,
    "pId": "074",
    "pos": {
      "lat": 60.73388888888889,
      "lon": 15.003055555555555
    }
  },
  {
    "name": "Lekvattnet",
    "synonyms": [
      "LEKVATTNET"
    ],
    "lId": "10912",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 60.190555555555555,
      "lon": 12.67361111111111
    }
  },
  {
    "name": "Lekåsa E20",
    "synonyms": [
      "LEKÅSA E20"
    ],
    "lId": "12530",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 58.14361111111111,
      "lon": 12.86361111111111
    }
  },
  {
    "name": "Lene",
    "synonyms": [
      "LENE",
      "LENE STN"
    ],
    "lId": "01422",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.54388888888889,
      "lon": 13.1225
    }
  },
  {
    "name": "Lenhovda Terminal",
    "synonyms": [
      "LENHOVDA TERM",
      "LENHOVDA TERMINAL"
    ],
    "lId": "24756",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 56.99722222222222,
      "lon": 15.287777777777778
    }
  },
  {
    "name": "Lenna station",
    "synonyms": [
      "LENNA STATION",
      "LENNA STN",
      "LÄNNA STATION"
    ],
    "lId": "20998",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.87277777777778,
      "lon": 17.960833333333333
    }
  },
  {
    "name": "Lennartsfors",
    "synonyms": [
      "LENNARTSFORS"
    ],
    "lId": "10915",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.31638888888889,
      "lon": 11.9
    }
  },
  {
    "name": "Lerbäck Lerbäcksvägen",
    "synonyms": [
      "LERBÄCK LERBÄCKSVÄGEN",
      "LERBÄCK VSK",
      "LERBÆCK LERBÆCKSVÆGEN",
      "LERBÆCK VSK"
    ],
    "lId": "21969",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 58.95138888888889,
      "lon": 15.043055555555556
    }
  },
  {
    "name": "Lerdala Kyrka",
    "synonyms": [
      "LERDALA KYRKA"
    ],
    "lId": "20239",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 58.47777777777778,
      "lon": 13.715
    }
  },
  {
    "name": "Lernbo",
    "synonyms": [
      "LERNBO",
      "LERNBO SKOLA"
    ],
    "lId": "12942",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 60.13916666666667,
      "lon": 15.311111111111112
    }
  },
  {
    "name": "Lerot",
    "synonyms": [
      "LEROT",
      "LEROT STN"
    ],
    "lId": "01424",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.82611111111112,
      "lon": 12.362777777777778
    }
  },
  {
    "name": "Lerum",
    "synonyms": [
      "LERUM",
      "LERUM STN"
    ],
    "lId": "00540",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 57.76916666666666,
      "lon": 12.272222222222224
    }
  },
  {
    "name": "Lesjöfors",
    "synonyms": [
      "LESJÖFORS",
      "LESJÖFORS POST",
      "LESJØFORS",
      "LESJØFORS POST"
    ],
    "lId": "00814",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.977222222222224,
      "lon": 14.18388888888889
    }
  },
  {
    "name": "Lessebo",
    "synonyms": [
      "LESSEBO",
      "LESSEBO STN"
    ],
    "lId": "00235",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 56.74944444444444,
      "lon": 15.258888888888889
    }
  },
  {
    "name": "Liatorp station",
    "synonyms": [
      "LIATORP STATION",
      "LIATORP STN"
    ],
    "lId": "10927",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 56.66277777777778,
      "lon": 14.269722222222223
    }
  },
  {
    "name": "Lickershamn",
    "synonyms": [
      "LICKERSHAMN"
    ],
    "lId": "21603",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 57.82472222222223,
      "lon": 18.51388888888889
    }
  },
  {
    "name": "Liden",
    "synonyms": [
      "LIDEN"
    ],
    "lId": "01226",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 62.7,
      "lon": 16.80138888888889
    }
  },
  {
    "name": "Lidhult",
    "synonyms": [
      "LIDHULT",
      "LIDHULT TORGG"
    ],
    "lId": "01481",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 56.82805555555556,
      "lon": 13.436666666666667
    }
  },
  {
    "name": "Lidingö centrum",
    "synonyms": [
      "LIDINGÖ CENTRUM",
      "LIDINGØ CENTRUM"
    ],
    "lId": "00714",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.365,
      "lon": 18.13277777777778
    }
  },
  {
    "name": "Lidköping",
    "synonyms": [
      "LIDKOPING",
      "LIDKÖPING",
      "LIDKÖPING STN",
      "LIDKØPING"
    ],
    "lId": "00148",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 58.504444444444445,
      "lon": 13.16388888888889
    }
  },
  {
    "name": "Lidsjöberg",
    "synonyms": [
      "LIDSJÖBERG",
      "LIDSJÖBERG VSK",
      "LIDSJØBERG",
      "LIDSJØBERG VSK"
    ],
    "lId": "13184",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 64.30777777777777,
      "lon": 15.23361111111111
    }
  },
  {
    "name": "Likenäs Allköp ICA",
    "synonyms": [
      "LIKENÄS ALLKÖP ICA",
      "LIKENÆS ALLKØP ICA"
    ],
    "lId": "10936",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 60.61555555555556,
      "lon": 13.040833333333333
    }
  },
  {
    "name": "Liljeholmen T-bana",
    "synonyms": [
      "LILJEHOLMEN T-BANA"
    ],
    "lId": "04046",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.31055555555555,
      "lon": 18.023055555555555
    }
  },
  {
    "name": "Lilla Edet",
    "synonyms": [
      "LILLA EDET",
      "LILLA EDET BSTN"
    ],
    "lId": "00995",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 58.134166666666665,
      "lon": 12.125277777777779
    }
  },
  {
    "name": "Lilla Harrie Skolhusvägen",
    "synonyms": [
      "L HARRIE SKOLHU",
      "LILLA HARRIE SKOLHUSVÄGEN",
      "LILLA HARRIE SKOLHUSVÆGEN"
    ],
    "lId": "16740",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 55.79361111111111,
      "lon": 13.203888888888889
    }
  },
  {
    "name": "Lilla Tjärby Fridhemsgården",
    "synonyms": [
      "L TJÄRBY FRIDHE",
      "L TJÆRBY FRIDHE",
      "LILLA TJÄRBY FRIDHEMSGÅRDEN",
      "LILLA TJÆRBY FRIDHEMSGÅRDEN"
    ],
    "lId": "17110",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 56.52583333333333,
      "lon": 13.055277777777778
    }
  },
  {
    "name": "Lilla Varholmen",
    "synonyms": [
      "LILLA VARHOLMEN"
    ],
    "lId": "01205",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 57.70861111111111,
      "lon": 11.703333333333333
    }
  },
  {
    "name": "Lilleström",
    "synonyms": [
      "LILLESTROM",
      "LILLESTRÖM"
    ],
    "lId": "00207",
    "prio": 0,
    "pId": "076",
    "pos": {
      "lat": 59.96361111111111,
      "lon": 11.072777777777777
    }
  },
  {
    "name": "Lillholmsjö",
    "synonyms": [
      "LILLHOLMSJÖ",
      "LILLHOLMSJØ"
    ],
    "lId": "22961",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 63.640277777777776,
      "lon": 14.389166666666666
    }
  },
  {
    "name": "Lillhärdal",
    "synonyms": [
      "LILLHÄRDAL",
      "LILLHÆRDAL"
    ],
    "lId": "13340",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 61.85,
      "lon": 14.070833333333333
    }
  },
  {
    "name": "Lillkyrka",
    "synonyms": [
      "LILLKYRKA",
      "LILLKYRKA TRÖGD",
      "LILLKYRKA TRØGD"
    ],
    "lId": "12869",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.56027777777778,
      "lon": 17.245833333333334
    }
  },
  {
    "name": "Lillsjöhögen östra",
    "synonyms": [
      "LILLSJÖHÖGEN ÖSTRA",
      "LILLSJØHØGEN ØSTRA"
    ],
    "lId": "13252",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 63.19138888888889,
      "lon": 15.20111111111111
    }
  },
  {
    "name": "Lillsved Värmdö",
    "synonyms": [
      "LILLSVED VÄRMDÖ",
      "LILLSVED VÆRMDØ"
    ],
    "lId": "24603",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.41138888888889,
      "lon": 18.49416666666667
    }
  },
  {
    "name": "Lillängen",
    "synonyms": [
      "LILLÄNGEN",
      "LILLÄNGEN STN",
      "LILLÆNGEN",
      "LILLÆNGEN STN"
    ],
    "lId": "24808",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.305,
      "lon": 18.161388888888887
    }
  },
  {
    "name": "Lima",
    "synonyms": [
      "LIMA",
      "LIMA UNGÄRDE",
      "LIMA UNGÆRDE"
    ],
    "lId": "00838",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 60.93666666666666,
      "lon": 13.360277777777778
    }
  },
  {
    "name": "Limedsforsen",
    "synonyms": [
      "LIMEDSFORS KONS",
      "LIMEDSFORSEN"
    ],
    "lId": "20379",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 60.90333333333333,
      "lon": 13.382777777777779
    }
  },
  {
    "name": "Limmared",
    "synonyms": [
      "LIMMARED",
      "LIMMARED STN"
    ],
    "lId": "00100",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 57.53611111111111,
      "lon": 13.3525
    }
  },
  {
    "name": "Linanäs brygga",
    "synonyms": [
      "LINANÄS BRYGGA",
      "LINANÆS BRYGGA"
    ],
    "lId": "20577",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.472500000000004,
      "lon": 18.511666666666667
    }
  },
  {
    "name": "Linderöd",
    "synonyms": [
      "LINDERÖD",
      "LINDERÖD E22",
      "LINDERØD",
      "LINDERØD E22"
    ],
    "lId": "01228",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 55.93138888888889,
      "lon": 13.8225
    }
  },
  {
    "name": "Lindesberg",
    "synonyms": [
      "LINDESBERG",
      "LINDESBERG STN"
    ],
    "lId": "00093",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.59444444444445,
      "lon": 15.22861111111111
    }
  },
  {
    "name": "Lindfors",
    "synonyms": [
      "LINDFORS"
    ],
    "lId": "10268",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.60611111111111,
      "lon": 13.826666666666666
    }
  },
  {
    "name": "Lindholmen",
    "synonyms": [
      "LINDHOLMEN",
      "LINDHOLMEN STN"
    ],
    "lId": "01154",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.58388888888889,
      "lon": 18.109166666666667
    }
  },
  {
    "name": "Lindome",
    "synonyms": [
      "LINDOME",
      "LINDOME STN"
    ],
    "lId": "00557",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 57.575833333333335,
      "lon": 12.078333333333333
    }
  },
  {
    "name": "Lindsdal centrum",
    "synonyms": [
      "LINDSDAL CENTRUM",
      "LINDSDAL CM"
    ],
    "lId": "24363",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 56.73527777777778,
      "lon": 16.297222222222224
    }
  },
  {
    "name": "Lindshammar Smultronstället",
    "synonyms": [
      "LINDSHAMMAR SMULTRONSTÄLLET",
      "LINDSHAMMAR SMULTRONSTÆLLET"
    ],
    "lId": "04066",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 57.221111111111114,
      "lon": 15.143888888888888
    }
  },
  {
    "name": "Lindvallen Snöcentret",
    "synonyms": [
      "LINDVALLEN SNÖCENTRET",
      "LINDVALLEN SNØCENTRET",
      "SÄLEN LINDVALLEN SNÖCENTRUM",
      "SÆLEN LINDVALLEN SNØCENTRUM"
    ],
    "lId": "00648",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 61.155,
      "lon": 13.205277777777777
    }
  },
  {
    "name": "Lingbo",
    "synonyms": [
      "LINGBO",
      "LINGBO STN"
    ],
    "lId": "00635",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 61.04472222222222,
      "lon": 16.672777777777778
    }
  },
  {
    "name": "Linghed affären",
    "synonyms": [
      "LINGHED AFFÄREN",
      "LINGHED AFFÆREN"
    ],
    "lId": "13029",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 60.7825,
      "lon": 15.86
    }
  },
  {
    "name": "Linghem",
    "synonyms": [
      "LINGHEM",
      "LINGHEM STN"
    ],
    "lId": "00849",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 58.43666666666666,
      "lon": 15.786944444444444
    }
  },
  {
    "name": "Linköping C",
    "synonyms": [
      "LINKOPING C",
      "LINKÖPING C",
      "LINKØPING C"
    ],
    "lId": "00009",
    "prio": 350,
    "pId": "074",
    "pos": {
      "lat": 58.41638888888889,
      "lon": 15.624722222222223
    }
  },
  {
    "name": "Linköping Universitet",
    "synonyms": [
      "LINKÖPING UNIVERSITET",
      "LINKØPING UNIVERSITET"
    ],
    "lId": "20328",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 58.400277777777774,
      "lon": 15.572777777777777
    }
  },
  {
    "name": "Linneryd",
    "synonyms": [
      "LINNERYD"
    ],
    "lId": "01482",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 56.659166666666664,
      "lon": 15.129444444444445
    }
  },
  {
    "name": "Linnes Hammarby",
    "synonyms": [
      "LINNES HAMMARBY",
      "LINNÉS HAMMARBY"
    ],
    "lId": "12817",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.81666666666667,
      "lon": 17.77611111111111
    }
  },
  {
    "name": "Linsell",
    "synonyms": [
      "LINSELL"
    ],
    "lId": "13325",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 62.157222222222224,
      "lon": 13.889999999999999
    }
  },
  {
    "name": "Liseberg station",
    "synonyms": [
      "LISEBERG STATION"
    ],
    "lId": "01230",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 57.698055555555555,
      "lon": 11.995
    }
  },
  {
    "name": "Lista gård",
    "synonyms": [
      "LISTA GÅRD"
    ],
    "lId": "20892",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.31388888888888,
      "lon": 16.270833333333332
    }
  },
  {
    "name": "Listerby Shell",
    "synonyms": [
      "LISTERBY SHELL"
    ],
    "lId": "10964",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 56.198055555555555,
      "lon": 15.402777777777779
    }
  },
  {
    "name": "Lisö",
    "synonyms": [
      "LISÖ",
      "LISÖ LINDHOLMEN",
      "LISØ",
      "LISØ LINDHOLMEN"
    ],
    "lId": "01182",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 58.874722222222225,
      "lon": 17.791666666666668
    }
  },
  {
    "name": "Lit centrum",
    "synonyms": [
      "LIT CENTRUM"
    ],
    "lId": "13583",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 63.31583333333333,
      "lon": 14.845277777777778
    }
  },
  {
    "name": "Ljugarn",
    "synonyms": [
      "LJUGARN",
      "LJUGARN HAMN"
    ],
    "lId": "00901",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 57.32361111111111,
      "lon": 18.712777777777777
    }
  },
  {
    "name": "Ljung",
    "synonyms": [
      "LJUNG",
      "LJUNG STN"
    ],
    "lId": "00245",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 57.98638888888889,
      "lon": 13.053055555555556
    }
  },
  {
    "name": "Ljunga Lövbergsvägen",
    "synonyms": [
      "LJUNGA LÖVBERGSV",
      "LJUNGA LÖVBERGSV2GEN",
      "LJUNGA LÖVBERGSVÄGEN",
      "LJUNGA LÖVBERGV",
      "LJUNGA LØVBERGSV",
      "LJUNGA LØVBERGSV2GEN",
      "LJUNGA LØVBERGV"
    ],
    "lId": "10966",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 58.57472222222223,
      "lon": 16.308611111111112
    }
  },
  {
    "name": "Ljungaverk",
    "synonyms": [
      "LJUNGAVERK"
    ],
    "lId": "00325",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 62.49583333333334,
      "lon": 16.05888888888889
    }
  },
  {
    "name": "Ljungby",
    "synonyms": [
      "LJUNGBY",
      "LJUNGBY BSTN"
    ],
    "lId": "00555",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 56.831944444444446,
      "lon": 13.935833333333333
    }
  },
  {
    "name": "Ljungbyhed",
    "synonyms": [
      "LJUNGBYHED",
      "LJUNGBYHED BSTN"
    ],
    "lId": "00435",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 56.07527777777778,
      "lon": 13.233333333333333
    }
  },
  {
    "name": "Ljungbyholm",
    "synonyms": [
      "LJUNGBYHOLM",
      "LJUNGBYHOLM KIO"
    ],
    "lId": "00756",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 56.63305555555556,
      "lon": 16.173333333333336
    }
  },
  {
    "name": "Ljungdalen",
    "synonyms": [
      "LJUNGDALEN"
    ],
    "lId": "00449",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 62.85194444444445,
      "lon": 12.796111111111111
    }
  },
  {
    "name": "Ljunghusen",
    "synonyms": [
      "LJUNGHUSEN",
      "LJUNGHUSEN STOR"
    ],
    "lId": "01231",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 55.405277777777776,
      "lon": 12.920833333333333
    }
  },
  {
    "name": "Ljungsbro",
    "synonyms": [
      "LJUNGSBRO",
      "LJUNGSBRO BSTN"
    ],
    "lId": "00850",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 58.50861111111111,
      "lon": 15.501944444444444
    }
  },
  {
    "name": "Ljungskile",
    "synonyms": [
      "LJUNGSKILE",
      "LJUNGSKILE STN"
    ],
    "lId": "00098",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 58.224444444444444,
      "lon": 11.921111111111111
    }
  },
  {
    "name": "Ljungstorp Ljungstorpsgården",
    "synonyms": [
      "LJUNGSTORP GÅRD",
      "LJUNGSTORP LJUNGSTORPSGÅRDEN"
    ],
    "lId": "14417",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 55.90861111111111,
      "lon": 13.574444444444444
    }
  },
  {
    "name": "Ljusdal",
    "synonyms": [
      "LJUSDAL",
      "LJUSDAL STN"
    ],
    "lId": "00198",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 61.82666666666667,
      "lon": 16.096944444444443
    }
  },
  {
    "name": "Ljusfallshammar skolan",
    "synonyms": [
      "LJUSFALLSHAMMAR SKOLAN"
    ],
    "lId": "10974",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 58.78722222222222,
      "lon": 15.495
    }
  },
  {
    "name": "Ljusne station",
    "synonyms": [
      "LJUSNE STATION"
    ],
    "lId": "01559",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 61.21277777777778,
      "lon": 17.111666666666668
    }
  },
  {
    "name": "Ljusterö skola",
    "synonyms": [
      "LJUSTERÖ SKOLA",
      "LJUSTERØ SKOLA"
    ],
    "lId": "68652",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.52583333333333,
      "lon": 18.621944444444445
    }
  },
  {
    "name": "Ljustorp",
    "synonyms": [
      "LJUSTORP"
    ],
    "lId": "26924",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 62.62305555555555,
      "lon": 17.335277777777776
    }
  },
  {
    "name": "Lockryd busstation",
    "synonyms": [
      "LOCKRYD BSTN",
      "LOCKRYD BUSSTATION"
    ],
    "lId": "12189",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 57.61472222222223,
      "lon": 13.115
    }
  },
  {
    "name": "Lofsdalen",
    "synonyms": [
      "LOFSDALEN"
    ],
    "lId": "00497",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 62.11222222222222,
      "lon": 13.272222222222224
    }
  },
  {
    "name": "Loftahammar",
    "synonyms": [
      "LOFTAHAMMAR"
    ],
    "lId": "00926",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 57.906388888888884,
      "lon": 16.696944444444444
    }
  },
  {
    "name": "Loka brunn",
    "synonyms": [
      "LOKA BRUNN"
    ],
    "lId": "20284",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.60527777777778,
      "lon": 14.476666666666667
    }
  },
  {
    "name": "Loka station",
    "synonyms": [
      "LOKA STATION",
      "LOKA STN"
    ],
    "lId": "01531",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.63638888888889,
      "lon": 14.469722222222222
    }
  },
  {
    "name": "Lomma",
    "synonyms": [
      "LOMMA",
      "LOMMA BSTN"
    ],
    "lId": "00947",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 55.67361111111111,
      "lon": 13.068888888888889
    }
  },
  {
    "name": "Los Gruvbyn",
    "synonyms": [
      "LOS GRUVBYN"
    ],
    "lId": "10982",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 61.74444444444445,
      "lon": 15.155277777777778
    }
  },
  {
    "name": "Loshult Kyrkan",
    "synonyms": [
      "LOSHULT KYRKAN"
    ],
    "lId": "14744",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 56.50111111111111,
      "lon": 14.115555555555556
    }
  },
  {
    "name": "Lotorp Torgvägen",
    "synonyms": [
      "LOTORP TORGVÄGEN",
      "LOTORP TORGVÆGEN"
    ],
    "lId": "24777",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 58.736111111111114,
      "lon": 15.827222222222222
    }
  },
  {
    "name": "Lottefors",
    "synonyms": [
      "LOTTEFORS"
    ],
    "lId": "18421",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 61.420833333333334,
      "lon": 16.408055555555553
    }
  },
  {
    "name": "Lovene",
    "synonyms": [
      "LOVENE",
      "LOVENE STN"
    ],
    "lId": "01233",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 58.44,
      "lon": 13.046666666666667
    }
  },
  {
    "name": "Lovikka väg 395",
    "synonyms": [
      "LOVIKKA VÄG 395",
      "LOVIKKA VÆG 395"
    ],
    "lId": "14810",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 67.33333333333333,
      "lon": 22.581666666666667
    }
  },
  {
    "name": "Lucksta",
    "synonyms": [
      "LUCKSTA"
    ],
    "lId": "27579",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 62.297777777777775,
      "lon": 17.05
    }
  },
  {
    "name": "Ludvigsborg Kvarndammsgatan",
    "synonyms": [
      "LUDVIGSBORG KVARNDAMMSGATAN"
    ],
    "lId": "21813",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 55.904444444444444,
      "lon": 13.6075
    }
  },
  {
    "name": "Ludvika station",
    "synonyms": [
      "LUDVIKA STATION",
      "LUDVIKA STN"
    ],
    "lId": "00291",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 60.14972222222222,
      "lon": 15.183055555555555
    }
  },
  {
    "name": "Ludvika stadszon",
    "synonyms": [
      "LUDVIKA STADSZON",
      "LUDVIKA ZON"
    ],
    "lId": "79002",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 60.14972222222222,
      "lon": 15.1825
    }
  },
  {
    "name": "Lugnvik busstation",
    "synonyms": [
      "LUGNVIK BSTN",
      "LUGNVIK BUSSTATION"
    ],
    "lId": "15208",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 62.92916666666667,
      "lon": 17.910833333333333
    }
  },
  {
    "name": "Lugnås",
    "synonyms": [
      "LUGNÅS",
      "LUGNÅS STN"
    ],
    "lId": "00466",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 58.644444444444446,
      "lon": 13.701944444444443
    }
  },
  {
    "name": "Luleå C",
    "synonyms": [
      "LULEA",
      "LULEA C",
      "LULEÅ C"
    ],
    "lId": "00144",
    "prio": 1,
    "pId": "074",
    "pos": {
      "lat": 65.58388888888888,
      "lon": 22.16472222222222
    }
  },
  {
    "name": "Luleå Universitet",
    "synonyms": [
      "LULEÅ UNIVERSITET"
    ],
    "lId": "23785",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 65.61805555555554,
      "lon": 22.130277777777778
    }
  },
  {
    "name": "Luma",
    "synonyms": [
      "LUMA"
    ],
    "lId": "24929",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.30416666666667,
      "lon": 18.09583333333333
    }
  },
  {
    "name": "Lummelunda",
    "synonyms": [
      "LUMMELUNDA",
      "LUMMELUNDA SKAR"
    ],
    "lId": "01155",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 57.64527777777778,
      "lon": 18.30638888888889
    }
  },
  {
    "name": "Lund C",
    "synonyms": [
      "LUND C",
      "XGC"
    ],
    "lId": "00120",
    "prio": 1,
    "pId": "074",
    "pos": {
      "lat": 55.70805555555556,
      "lon": 13.186666666666667
    }
  },
  {
    "name": "Lund Råby trafikplats",
    "synonyms": [
      "LUND RÅBY TRAFIKPLATS"
    ],
    "lId": "34533",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 55.68611111111111,
      "lon": 13.197222222222223
    }
  },
  {
    "name": "Lunde",
    "synonyms": [
      "LUNDE"
    ],
    "lId": "50747",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 62.876111111111115,
      "lon": 17.857222222222223
    }
  },
  {
    "name": "Lundsberg",
    "synonyms": [
      "LUNDSBERG"
    ],
    "lId": "22324",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.495555555555555,
      "lon": 14.173888888888888
    }
  },
  {
    "name": "Lundsbrunn Lundagården",
    "synonyms": [
      "LUNDSBRUNN LGD",
      "LUNDSBRUNN LUNDAGÅRDEN"
    ],
    "lId": "24054",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 58.467777777777776,
      "lon": 13.448055555555555
    }
  },
  {
    "name": "Lunger",
    "synonyms": [
      "LUNGER"
    ],
    "lId": "21079",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.32666666666667,
      "lon": 15.68
    }
  },
  {
    "name": "Lungsund",
    "synonyms": [
      "LUNGSUND",
      "LUNGSUND KYRKA"
    ],
    "lId": "22323",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.52166666666667,
      "lon": 14.19138888888889
    }
  },
  {
    "name": "Lunnarp station",
    "synonyms": [
      "LUNNARP STATION",
      "LUNNARP STN"
    ],
    "lId": "01234",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 55.54111111111111,
      "lon": 14.041666666666666
    }
  },
  {
    "name": "Lyckeby",
    "synonyms": [
      "LYCKEBY"
    ],
    "lId": "00663",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 56.198611111111106,
      "lon": 15.654722222222222
    }
  },
  {
    "name": "Lycksele station",
    "synonyms": [
      "LYCKSELE STATION",
      "LYCKSELE STN"
    ],
    "lId": "00360",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 64.59527777777777,
      "lon": 18.66777777777778
    }
  },
  {
    "name": "Lyngby Gård",
    "synonyms": [
      "LYNGBY GÅRD"
    ],
    "lId": "30879",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 55.88666666666666,
      "lon": 14.121111111111112
    }
  },
  {
    "name": "Lyrestad station",
    "synonyms": [
      "LYRESTAD STATION",
      "LYRESTAD STN"
    ],
    "lId": "00468",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 58.805,
      "lon": 14.056944444444445
    }
  },
  {
    "name": "Lysekil station",
    "synonyms": [
      "LYSEKIL STATION"
    ],
    "lId": "16176",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 58.27611111111111,
      "lon": 11.440833333333334
    }
  },
  {
    "name": "Lysekil Södra hamnen",
    "synonyms": [
      "LYSEKIL S HAMN",
      "LYSEKIL SÖDRA HAMNEN",
      "LYSEKIL SØDRA HAMNEN"
    ],
    "lId": "00118",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 58.27305555555555,
      "lon": 11.437777777777779
    }
  },
  {
    "name": "Lysvik",
    "synonyms": [
      "LYSVIK"
    ],
    "lId": "00433",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 60.01583333333333,
      "lon": 13.1375
    }
  },
  {
    "name": "Låktatjåkka",
    "synonyms": [
      "LAKTATJAKKA",
      "LÅKTATJÅKKA",
      "LÅKTATJÅKKA STN"
    ],
    "lId": "01433",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 68.42333333333333,
      "lon": 18.32638888888889
    }
  },
  {
    "name": "Långalma skola",
    "synonyms": [
      "LÅNGALMA SKOLA"
    ],
    "lId": "09715",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 60.264722222222225,
      "lon": 18.472777777777775
    }
  },
  {
    "name": "Långasjö",
    "synonyms": [
      "LÅNGASJÖ",
      "LÅNGASJÖ ALLÉGD",
      "LÅNGASJØ",
      "LÅNGASJØ ALLÉGD"
    ],
    "lId": "01235",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 56.5775,
      "lon": 15.448611111111111
    }
  },
  {
    "name": "Långban",
    "synonyms": [
      "LÅNGBAN"
    ],
    "lId": "24592",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.853611111111114,
      "lon": 14.263055555555555
    }
  },
  {
    "name": "Långbron station",
    "synonyms": [
      "LÅNGBRON STATION",
      "LÅNGBRON STN"
    ],
    "lId": "30065",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 58.936388888888885,
      "lon": 12.279444444444445
    }
  },
  {
    "name": "Långed",
    "synonyms": [
      "LÅNGED"
    ],
    "lId": "01156",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 63.60388888888889,
      "lon": 19.671111111111113
    }
  },
  {
    "name": "Långflon",
    "synonyms": [
      "LÅNGFLON"
    ],
    "lId": "01236",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 61.04611111111111,
      "lon": 12.595833333333333
    }
  },
  {
    "name": "Långhundra Åby vägskäl",
    "synonyms": [
      "LÅNGHUND ÅBYVSK",
      "LÅNGHUNDRA ÅBY VÄGSKÄL",
      "LÅNGHUNDRA ÅBY VÆGSKÆL"
    ],
    "lId": "12832",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.75138888888889,
      "lon": 18.04361111111111
    }
  },
  {
    "name": "Långsele",
    "synonyms": [
      "LANGSELE",
      "LÅNGSELE",
      "LÅNGSELE STN"
    ],
    "lId": "00278",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 63.17638888888889,
      "lon": 17.066944444444445
    }
  },
  {
    "name": "Långshyttan centrum",
    "synonyms": [
      "LÅNGSHYTTAN CENTRUM"
    ],
    "lId": "01484",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 60.45277777777778,
      "lon": 16.033611111111114
    }
  },
  {
    "name": "Långshyttan Långsbro skola",
    "synonyms": [
      "LÅNGSHYTTAN LÅNGSBRO SKOLA"
    ],
    "lId": "25184",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 60.45611111111111,
      "lon": 16.053055555555556
    }
  },
  {
    "name": "Långträsk",
    "synonyms": [
      "LÅNGTRÄSK",
      "LÅNGTRÄSK POST",
      "LÅNGTRÆSK",
      "LÅNGTRÆSK POST"
    ],
    "lId": "14889",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 65.38361111111112,
      "lon": 20.33138888888889
    }
  },
  {
    "name": "Långvik",
    "synonyms": [
      "LÅNGVIK"
    ],
    "lId": "25721",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.24166666666667,
      "lon": 18.511388888888888
    }
  },
  {
    "name": "Långviksmon Jollen",
    "synonyms": [
      "LÅNGVIKSMON JOLLEN"
    ],
    "lId": "15211",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 63.62972222222222,
      "lon": 18.69472222222222
    }
  },
  {
    "name": "Långå vägskäl",
    "synonyms": [
      "LÅNGÅ VÄGSKÄL",
      "LÅNGÅ VÆGSKÆL"
    ],
    "lId": "29385",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 62.434999999999995,
      "lon": 13.265277777777778
    }
  },
  {
    "name": "Långås",
    "synonyms": [
      "LÅNGÅS"
    ],
    "lId": "01485",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 56.976111111111116,
      "lon": 12.45
    }
  },
  {
    "name": "Läby",
    "synonyms": [
      "LÄBY",
      "LÄBY BJÖRKLINGE",
      "LÆBY",
      "LÆBY BJØRKLINGE"
    ],
    "lId": "01190",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 60.086666666666666,
      "lon": 17.551111111111112
    }
  },
  {
    "name": "Läckeby",
    "synonyms": [
      "LÄCKEBY",
      "LÆCKEBY"
    ],
    "lId": "17998",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 56.782777777777774,
      "lon": 16.294722222222223
    }
  },
  {
    "name": "Läggesta",
    "synonyms": [
      "LAGGESTA",
      "LÄGGESTA",
      "LÄGGESTA STN",
      "LÆGGESTA",
      "LÆGGESTA STN"
    ],
    "lId": "00067",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.248333333333335,
      "lon": 17.16722222222222
    }
  },
  {
    "name": "Länghem",
    "synonyms": [
      "LÄNGHEM",
      "LÆNGHEM"
    ],
    "lId": "00996",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 57.602222222222224,
      "lon": 13.244166666666667
    }
  },
  {
    "name": "Länna macken",
    "synonyms": [
      "LÄNNA MACKEN",
      "LÆNNA MACKEN"
    ],
    "lId": "01237",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.87694444444445,
      "lon": 17.964444444444442
    }
  },
  {
    "name": "Lännersta",
    "synonyms": [
      "LÄNNERSTA",
      "LÄNNERSTA ÅNGBV",
      "LÆNNERSTA",
      "LÆNNERSTA ÅNGBV"
    ],
    "lId": "01180",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.30555555555555,
      "lon": 18.255277777777778
    }
  },
  {
    "name": "Läppe",
    "synonyms": [
      "LÄPPE",
      "LÆPPE"
    ],
    "lId": "04044",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.12972222222222,
      "lon": 15.80888888888889
    }
  },
  {
    "name": "Lärbro",
    "synonyms": [
      "LÄRBRO",
      "LÆRBRO"
    ],
    "lId": "00922",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 57.78472222222222,
      "lon": 18.789722222222224
    }
  },
  {
    "name": "Lästringe",
    "synonyms": [
      "LÄSTRINGE",
      "LÆSTRINGE"
    ],
    "lId": "20768",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 58.87583333333333,
      "lon": 17.320555555555554
    }
  },
  {
    "name": "Lästringe trafikplats",
    "synonyms": [
      "LÄSTRINGE TRAFIKPLATS",
      "LÄSTRINGE TRPL",
      "LÆSTRINGE TRPL"
    ],
    "lId": "20770",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 58.90861111111111,
      "lon": 17.328888888888887
    }
  },
  {
    "name": "Löa bron",
    "synonyms": [
      "LÖA BRON",
      "LØA BRON"
    ],
    "lId": "11011",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.799166666666665,
      "lon": 15.152777777777779
    }
  },
  {
    "name": "Löberöd torget",
    "synonyms": [
      "LÖBERÖD TORGET",
      "LØBERØD TORGET"
    ],
    "lId": "16769",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 55.775,
      "lon": 13.5125
    }
  },
  {
    "name": "Löddeköpinge centrum",
    "synonyms": [
      "LÖDDEKÖPINGE CENTRUM",
      "LÖDDEKÖPINGE CM",
      "LØDDEKØPINGE CENTRUM",
      "LØDDEKØPINGE CM"
    ],
    "lId": "16771",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 55.75805555555556,
      "lon": 13.00611111111111
    }
  },
  {
    "name": "Löderup",
    "synonyms": [
      "LÖDERUP",
      "LÖDERUP CENTRUM",
      "LØDERUP",
      "LØDERUP CENTRUM"
    ],
    "lId": "01238",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 55.43805555555555,
      "lon": 14.113055555555555
    }
  },
  {
    "name": "Lödöse",
    "synonyms": [
      "LÖDÖSE",
      "LÖDÖSE S INFART",
      "LØDØSE",
      "LØDØSE S INFART"
    ],
    "lId": "00997",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 58.028888888888886,
      "lon": 12.152777777777779
    }
  },
  {
    "name": "Lödöse Södra station",
    "synonyms": [
      "LÖDÖSE SÖDRA STATION"
    ],
    "lId": "01591",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 58.015,
      "lon": 12.163333333333334
    }
  },
  {
    "name": "Lönneberga affären",
    "synonyms": [
      "LÖNNEBERGA AFFÄREN"
    ],
    "lId": "14275",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 57.550555555555555,
      "lon": 15.721944444444444
    }
  },
  {
    "name": "Lönsboda",
    "synonyms": [
      "LÖNSBODA",
      "LÖNSBODA BSTN",
      "LØNSBODA",
      "LØNSBODA BSTN"
    ],
    "lId": "00029",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 56.396388888888886,
      "lon": 14.320277777777777
    }
  },
  {
    "name": "Lörby",
    "synonyms": [
      "LÖRBY",
      "LØRBY"
    ],
    "lId": "26079",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 56.06638888888889,
      "lon": 14.695
    }
  },
  {
    "name": "Löttorp",
    "synonyms": [
      "LÖTTORP",
      "LÖTTORP CENTRUM",
      "LØTTORP",
      "LØTTORP CENTRUM"
    ],
    "lId": "00927",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 57.166666666666664,
      "lon": 16.993055555555557
    }
  },
  {
    "name": "Lövberga väg 45",
    "synonyms": [
      "LÖVBERGA VÄG 45",
      "LØVBERGA VÆG 45"
    ],
    "lId": "13187",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 63.96611111111111,
      "lon": 15.8525
    }
  },
  {
    "name": "Lövestad",
    "synonyms": [
      "LÖVESTAD",
      "LÖVESTAD STN",
      "LØVESTAD",
      "LØVESTAD STN"
    ],
    "lId": "01239",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 55.65333333333333,
      "lon": 13.891388888888889
    }
  },
  {
    "name": "Lövsta handel",
    "synonyms": [
      "LÖVSTA HANDEL"
    ],
    "lId": "38724",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 58.70666666666667,
      "lon": 16.96833333333333
    }
  },
  {
    "name": "Lövstabruk",
    "synonyms": [
      "LÖVSTABRUK",
      "LÖVSTABRUK HERR",
      "LØVSTABRUK",
      "LØVSTABRUK HERR"
    ],
    "lId": "00664",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 60.408055555555556,
      "lon": 17.879166666666666
    }
  },
  {
    "name": "Lövstalöt norra",
    "synonyms": [
      "LÖVSTALÖT NORRA",
      "LØVSTALØT NORRA"
    ],
    "lId": "21908",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.95888888888889,
      "lon": 17.583888888888886
    }
  },
  {
    "name": "Lövånger busstation",
    "synonyms": [
      "LÖVÅNGER BSTN",
      "LÖVÅNGER BUSSTATION",
      "LØVÅNGER BSTN",
      "LØVÅNGER BUSSTATION"
    ],
    "lId": "00498",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 64.3711111111111,
      "lon": 21.30611111111111
    }
  },
  {
    "name": "Lövåsen väg 26",
    "synonyms": [
      "LÖVÅSEN VÄG 26"
    ],
    "lId": "16456",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 58.526944444444446,
      "lon": 13.820277777777777
    }
  },
  {
    "name": "Madängsholm",
    "synonyms": [
      "MADÄNGSHOLM",
      "MADÆNGSHOLM"
    ],
    "lId": "11024",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 58.141666666666666,
      "lon": 13.916111111111112
    }
  },
  {
    "name": "Maglehem Lillehemsvägen",
    "synonyms": [
      "MAGLEHEM LILLEHEMSVÄGEN",
      "MAGLEHEM LILLEHEMSVÆGEN"
    ],
    "lId": "30715",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 55.77166666666667,
      "lon": 14.140833333333333
    }
  },
  {
    "name": "Mala Stationsvägen",
    "synonyms": [
      "MALA STATIONSVÄGEN",
      "MALA STATIONSVÆGEN"
    ],
    "lId": "31566",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 56.24111111111111,
      "lon": 13.71361111111111
    }
  },
  {
    "name": "Malingsbo bro",
    "synonyms": [
      "MALINGSBO BRO"
    ],
    "lId": "25237",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.92861111111111,
      "lon": 15.436944444444444
    }
  },
  {
    "name": "Malmberget",
    "synonyms": [
      "MALMBERGET",
      "MALMBERGET BSTN"
    ],
    "lId": "00883",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 67.17527777777778,
      "lon": 20.65694444444444
    }
  },
  {
    "name": "Malmby",
    "synonyms": [
      "MALMBY"
    ],
    "lId": "20900",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.337500000000006,
      "lon": 17.058333333333334
    }
  },
  {
    "name": "Malmbäck",
    "synonyms": [
      "MALMBACK",
      "MALMBÄCK",
      "MALMBÄCK STN",
      "MALMBÆCK",
      "MALMBÆCK STN"
    ],
    "lId": "00311",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 57.57777777777778,
      "lon": 14.460277777777778
    }
  },
  {
    "name": "Malmköping",
    "synonyms": [
      "MALMKÖPING",
      "MALMKÖPING BSTN",
      "MALMKØPING",
      "MALMKØPING BSTN"
    ],
    "lId": "00833",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.13472222222222,
      "lon": 16.724444444444444
    }
  },
  {
    "name": "Malmslätt Kärna kors",
    "synonyms": [
      "MALMSLÄTT KÄRNA KORS",
      "MALMSLÆTT KÆRNA KORS"
    ],
    "lId": "11029",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 58.41416666666667,
      "lon": 15.519444444444446
    }
  },
  {
    "name": "Malmö C",
    "synonyms": [
      "MALMO C",
      "MALMÖ C",
      "MALMØ C",
      "XFP"
    ],
    "lId": "00003",
    "prio": 300,
    "pId": "074",
    "pos": {
      "lat": 55.60944444444445,
      "lon": 13.000833333333333
    }
  },
  {
    "name": "Malmö stadszon",
    "synonyms": [
      "MALMÖ STADSZON",
      "MALMÖ ZON",
      "MALMØ STADSZON"
    ],
    "lId": "01529",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 55.60611111111111,
      "lon": 12.999722222222221
    }
  },
  {
    "name": "Malmö Airport Sturup flygplats",
    "synonyms": [
      "MALMÖ AIRPORT STURUP FLYGPLATS"
    ],
    "lId": "00953",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 55.540277777777774,
      "lon": 13.365833333333333
    }
  },
  {
    "name": "Malmö Hyllie station",
    "synonyms": [
      "HYLLIE STN",
      "MALMÖ HYLLIE STATION"
    ],
    "lId": "01586",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 55.56305555555555,
      "lon": 12.976666666666667
    }
  },
  {
    "name": "Malmö Norra Vallgatan",
    "synonyms": [
      "MALMÖ NORRA VALLGATAN"
    ],
    "lId": "72050",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 0,
      "lon": 0
    }
  },
  {
    "name": "Malmö Persborg",
    "synonyms": [
      "MALMÖ PERSBORG",
      "MALMØ PERSBORG"
    ],
    "lId": "01486",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 55.58027777777778,
      "lon": 13.02888888888889
    }
  },
  {
    "name": "Malmö Shell Holma",
    "synonyms": [
      "MALMÖ SHELL HOLMA",
      "MALMØ SHELL HOLMA"
    ],
    "lId": "59034",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 55.575,
      "lon": 12.989444444444443
    }
  },
  {
    "name": "Malmö Syd/Svågertorp",
    "synonyms": [
      "MALMO SYD/SVAGERTORP",
      "MALMÖ SYD/SVÅGERTORP",
      "MALMØ SYD/SVÅGERTORP",
      "SVÅGERTORP",
      "XFR"
    ],
    "lId": "01546",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 55.54694444444444,
      "lon": 12.990277777777777
    }
  },
  {
    "name": "Malmö Triangeln station",
    "synonyms": [
      "MALMÖ TRIANGELN STATION",
      "TRIANGELN STN"
    ],
    "lId": "01587",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 55.59305555555556,
      "lon": 13.001388888888888
    }
  },
  {
    "name": "Malung centrum",
    "synonyms": [
      "MALUNG CENTRUM"
    ],
    "lId": "00367",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 60.683611111111105,
      "lon": 13.709722222222222
    }
  },
  {
    "name": "Malung Folkhögskolan",
    "synonyms": [
      "MALUNG FOLKHÖGSKOLAN",
      "MALUNG FOLKHØGSKOLAN"
    ],
    "lId": "48761",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 60.67027777777778,
      "lon": 13.736666666666666
    }
  },
  {
    "name": "Malungsfors Boa",
    "synonyms": [
      "MALUNGSFORS BOA"
    ],
    "lId": "13112",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 60.73444444444444,
      "lon": 13.556944444444445
    }
  },
  {
    "name": "Malå",
    "synonyms": [
      "MALÅ",
      "MALÅ BSTN"
    ],
    "lId": "00387",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 65.18388888888889,
      "lon": 18.746666666666666
    }
  },
  {
    "name": "Mantorp",
    "synonyms": [
      "MANTORP",
      "MANTORP STN"
    ],
    "lId": "00616",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 58.34861111111111,
      "lon": 15.290555555555555
    }
  },
  {
    "name": "Marbäck affären",
    "synonyms": [
      "MARBÄCK AFFÄR",
      "MARBÄCK AFFÄREN",
      "MARBÆCK AFFÆR"
    ],
    "lId": "12456",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 57.73833333333334,
      "lon": 13.421388888888888
    }
  },
  {
    "name": "Margretetorp Gästis",
    "synonyms": [
      "MARGRETETORP GÄSTIS",
      "MARGRETETORP GÆSTIS"
    ],
    "lId": "04079",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 56.33583333333333,
      "lon": 12.891388888888889
    }
  },
  {
    "name": "Maria",
    "synonyms": [
      "MARIA",
      "MARIA STN"
    ],
    "lId": "01542",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 56.075833333333335,
      "lon": 12.710833333333333
    }
  },
  {
    "name": "Mariannelund torget",
    "synonyms": [
      "MARIANNELUND TG",
      "MARIANNELUND TORGET"
    ],
    "lId": "21788",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 57.61666666666667,
      "lon": 15.571388888888889
    }
  },
  {
    "name": "Mariatorget T-bana",
    "synonyms": [
      "MARIATORGET T-BANA"
    ],
    "lId": "21656",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.316944444444445,
      "lon": 18.063055555555557
    }
  },
  {
    "name": "Marieby kyrka",
    "synonyms": [
      "MARIEBY KYRKA"
    ],
    "lId": "13390",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 63.11055555555556,
      "lon": 14.730833333333333
    }
  },
  {
    "name": "Mariefred busstation",
    "synonyms": [
      "MARIEFRED BSTN",
      "MARIEFRED BUSSTATION"
    ],
    "lId": "00276",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.26361111111111,
      "lon": 17.230277777777776
    }
  },
  {
    "name": "Mariefred Museijärnväg station",
    "synonyms": [
      "MARIEFRED MUSEIJÄRNVÄG STATION"
    ],
    "lId": "21001",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.25861111111111,
      "lon": 17.21833333333333
    }
  },
  {
    "name": "Marieholm",
    "synonyms": [
      "MARIEHOLM",
      "MARIEHOLM CM"
    ],
    "lId": "01487",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 55.86333333333334,
      "lon": 13.15388888888889
    }
  },
  {
    "name": "Marielund station Sörmland",
    "synonyms": [
      "MARIELUND STATION SÖRMLAND",
      "MARIELUND SÖRMLAND"
    ],
    "lId": "67287",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.253055555555555,
      "lon": 17.18722222222222
    }
  },
  {
    "name": "Marielund station Uppland",
    "synonyms": [
      "MARIELUND STATION UPPLAND",
      "MARIELUND UPPL"
    ],
    "lId": "12812",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.8425,
      "lon": 17.875555555555557
    }
  },
  {
    "name": "Marienborg/Sykehuset",
    "synonyms": [
      "MARIENBORG/SYKEHUSE",
      "MARIENBORG/SYKEHUSET"
    ],
    "lId": "90015",
    "prio": 0,
    "pId": "076",
    "pos": {
      "lat": 0,
      "lon": 0
    }
  },
  {
    "name": "Mariestad Karleby väg 26",
    "synonyms": [
      "MARIESTAD KARLEBY VÄG 26"
    ],
    "lId": "24017",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 58.66777777777777,
      "lon": 13.819444444444445
    }
  },
  {
    "name": "Mariestad station",
    "synonyms": [
      "MARIESTAD STATION",
      "MARIESTAD STN"
    ],
    "lId": "00216",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 58.71194444444445,
      "lon": 13.824444444444444
    }
  },
  {
    "name": "Marka kyrka",
    "synonyms": [
      "MARKA KYRKA"
    ],
    "lId": "04244",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 58.15861111111111,
      "lon": 13.478333333333333
    }
  },
  {
    "name": "Markaryd",
    "synonyms": [
      "MARKARYD",
      "MARKARYD STN"
    ],
    "lId": "00258",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 56.45888888888889,
      "lon": 13.593333333333334
    }
  },
  {
    "name": "Marma station",
    "synonyms": [
      "MARMA STATION",
      "MARMA STN"
    ],
    "lId": "00627",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 60.490833333333335,
      "lon": 17.430555555555557
    }
  },
  {
    "name": "Marmaverken",
    "synonyms": [
      "MARMAVERKEN"
    ],
    "lId": "11045",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 61.271388888888886,
      "lon": 16.86777777777778
    }
  },
  {
    "name": "Marmorbyn",
    "synonyms": [
      "MARMORBYN"
    ],
    "lId": "11046",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.0475,
      "lon": 16.06416666666667
    }
  },
  {
    "name": "Marstrand",
    "synonyms": [
      "MARSTRAND"
    ],
    "lId": "00038",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 57.88666666666666,
      "lon": 11.58888888888889
    }
  },
  {
    "name": "Marum brygga",
    "synonyms": [
      "MARUM BRYGGA"
    ],
    "lId": "11047",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.85027777777778,
      "lon": 18.995
    }
  },
  {
    "name": "Masmo T-bana",
    "synonyms": [
      "MASMO T-BANA"
    ],
    "lId": "21729",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.24944444444444,
      "lon": 17.880277777777778
    }
  },
  {
    "name": "Masugnsbyn affären",
    "synonyms": [
      "MASUGNSBYN AFFÄREN",
      "MASUGNSBYN AFFÆREN"
    ],
    "lId": "15005",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 67.4588888888889,
      "lon": 22.038333333333334
    }
  },
  {
    "name": "Matfors",
    "synonyms": [
      "MATFORS",
      "MATFORS BSTN"
    ],
    "lId": "00407",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 62.344166666666666,
      "lon": 17.01833333333333
    }
  },
  {
    "name": "Mattmar busstation",
    "synonyms": [
      "MATTMAR BSTN",
      "MATTMAR BUSSTATION"
    ],
    "lId": "13285",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 63.30416666666667,
      "lon": 13.829444444444444
    }
  },
  {
    "name": "Medborgarplatsen T-bana",
    "synonyms": [
      "MEDBORGARPLATSEN T-BANA"
    ],
    "lId": "21654",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.314166666666665,
      "lon": 18.073333333333334
    }
  },
  {
    "name": "Medevi brunn",
    "synonyms": [
      "MEDEVI BRUNN"
    ],
    "lId": "01240",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 58.67388888888889,
      "lon": 14.958055555555555
    }
  },
  {
    "name": "Medle",
    "synonyms": [
      "MEDLE"
    ],
    "lId": "14037",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 64.745,
      "lon": 20.759444444444444
    }
  },
  {
    "name": "Medstugan",
    "synonyms": [
      "MEDSTUGAN"
    ],
    "lId": "29455",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 63.525555555555556,
      "lon": 12.399722222222222
    }
  },
  {
    "name": "Medåker",
    "synonyms": [
      "MEDÅKER",
      "MEDÅKER KYRKA"
    ],
    "lId": "21076",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.45194444444445,
      "lon": 15.757777777777777
    }
  },
  {
    "name": "Mehedeby station",
    "synonyms": [
      "MEHEDEBY STATION",
      "MEHEDEBY STN"
    ],
    "lId": "01573",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 60.45,
      "lon": 17.400277777777777
    }
  },
  {
    "name": "Mellansel",
    "synonyms": [
      "MELLANSEL",
      "MELLANSEL STN"
    ],
    "lId": "00263",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 63.42833333333333,
      "lon": 18.3075
    }
  },
  {
    "name": "Mellbystrand",
    "synonyms": [
      "MELLBYSTRAND"
    ],
    "lId": "01242",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 56.51416666666667,
      "lon": 12.949722222222222
    }
  },
  {
    "name": "Mellerud",
    "synonyms": [
      "MELLERUD",
      "MELLERUD STN"
    ],
    "lId": "00039",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 58.70166666666667,
      "lon": 12.464722222222221
    }
  },
  {
    "name": "Mellösa Konsum",
    "synonyms": [
      "MELLÖSA KONSUM",
      "MELLØSA KONSUM"
    ],
    "lId": "21921",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.100833333333334,
      "lon": 16.561666666666667
    }
  },
  {
    "name": "Merlänna Länna kyrka",
    "synonyms": [
      "MERLÄNNA KYRKA",
      "MERLÄNNA LÄNNA KYRKA",
      "MERLÆNNA KYRKA",
      "MERLÆNNA LÆNNA KYRKA"
    ],
    "lId": "20903",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.28194444444444,
      "lon": 16.982499999999998
    }
  },
  {
    "name": "Meråker",
    "synonyms": [
      "MERAKER",
      "MERÅKER"
    ],
    "lId": "01214",
    "prio": 0,
    "pId": "076",
    "pos": {
      "lat": 63.44583333333333,
      "lon": 11.780555555555557
    }
  },
  {
    "name": "Meselefors",
    "synonyms": [
      "MESELEFORS"
    ],
    "lId": "26101",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 64.44083333333333,
      "lon": 16.816666666666666
    }
  },
  {
    "name": "Messlingen",
    "synonyms": [
      "MESSLINGEN"
    ],
    "lId": "01243",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 62.66305555555555,
      "lon": 12.861388888888888
    }
  },
  {
    "name": "Midsommarkransen T-bana",
    "synonyms": [
      "MIDSOMMARKRANSEN T-BANA"
    ],
    "lId": "21715",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.30166666666666,
      "lon": 18.011944444444445
    }
  },
  {
    "name": "Misterhult",
    "synonyms": [
      "MISTERHULT",
      "MISTERHULT E22"
    ],
    "lId": "14286",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 57.47694444444445,
      "lon": 16.5175
    }
  },
  {
    "name": "Mittådalen",
    "synonyms": [
      "MITTÅDALEN"
    ],
    "lId": "01157",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 62.69194444444444,
      "lon": 12.672222222222222
    }
  },
  {
    "name": "Mjällby Centrumvägen",
    "synonyms": [
      "MJÄLLBY CENTRUMVÄGEN",
      "MJÄLLBY CENTRUV",
      "MJÆLLBY CENTRUMVÆGEN",
      "MJÆLLBY CENTRUV"
    ],
    "lId": "00588",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 56.04555555555555,
      "lon": 14.677777777777777
    }
  },
  {
    "name": "Mjällom",
    "synonyms": [
      "MJÄLLOM",
      "MJÆLLOM"
    ],
    "lId": "15223",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 62.98555555555556,
      "lon": 18.43138888888889
    }
  },
  {
    "name": "Mjällomslandet",
    "synonyms": [
      "MJÄLLOMSLANDET",
      "MJÆLLOMSLANDET"
    ],
    "lId": "29048",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 63.00416666666667,
      "lon": 18.39611111111111
    }
  },
  {
    "name": "Mjöbäck",
    "synonyms": [
      "MJÖBÄCK",
      "MJØBÆCK"
    ],
    "lId": "12198",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 57.314166666666665,
      "lon": 12.876111111111111
    }
  },
  {
    "name": "Mjöhult järnvägen",
    "synonyms": [
      "MJÖHULT JÄRNVÄGEN",
      "MJØHULT JÄRNVÄGEN"
    ],
    "lId": "16787",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 56.17666666666666,
      "lon": 12.67861111111111
    }
  },
  {
    "name": "Mjölby",
    "synonyms": [
      "MJOLBY",
      "MJÖLBY",
      "MJÖLBY STN",
      "MJØLBY",
      "MJØLBY STN"
    ],
    "lId": "00180",
    "prio": 1,
    "pId": "074",
    "pos": {
      "lat": 58.32277777777778,
      "lon": 15.131944444444445
    }
  },
  {
    "name": "Mjölkö brygga",
    "synonyms": [
      "MJÖLKÖ BRYGGA",
      "MJØLKØ BRYGGA"
    ],
    "lId": "24871",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.465,
      "lon": 18.418333333333333
    }
  },
  {
    "name": "Mockfjärd E16",
    "synonyms": [
      "MOCKFJÄRD E16"
    ],
    "lId": "13043",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 60.5075,
      "lon": 14.96111111111111
    }
  },
  {
    "name": "Mogata kyrka",
    "synonyms": [
      "MOGATA KYRKA"
    ],
    "lId": "11063",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 58.45166666666667,
      "lon": 16.45111111111111
    }
  },
  {
    "name": "Mohed",
    "synonyms": [
      "MOHED",
      "MOHED BSTN"
    ],
    "lId": "20845",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 61.294444444444444,
      "lon": 16.830833333333334
    }
  },
  {
    "name": "Mohed väg 50",
    "synonyms": [
      "MOHED VÄG 50"
    ],
    "lId": "06322",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 61.297777777777775,
      "lon": 16.834999999999997
    }
  },
  {
    "name": "Moheda station",
    "synonyms": [
      "MOHEDA STATION",
      "MOHEDA STN"
    ],
    "lId": "00122",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 57.003055555555555,
      "lon": 14.576666666666666
    }
  },
  {
    "name": "Moholm",
    "synonyms": [
      "MOHOLM"
    ],
    "lId": "22844",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 58.6075,
      "lon": 14.035555555555556
    }
  },
  {
    "name": "Moliden posten",
    "synonyms": [
      "MOLIDEN POSTEN"
    ],
    "lId": "26927",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 63.37861111111111,
      "lon": 18.455555555555556
    }
  },
  {
    "name": "Molkom Graninge",
    "synonyms": [
      "MOLKOM GRANINGE"
    ],
    "lId": "20075",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.59805555555556,
      "lon": 13.71888888888889
    }
  },
  {
    "name": "Mollaryd",
    "synonyms": [
      "MOLLARYD",
      "MOLLARYD STN"
    ],
    "lId": "00546",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 57.905833333333334,
      "lon": 13.0225
    }
  },
  {
    "name": "Mollösund",
    "synonyms": [
      "MOLLÖSUND",
      "MOLLÖSUND ÖSTRA",
      "MOLLØSUND",
      "MOLLØSUND ØSTRA"
    ],
    "lId": "00857",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 58.073888888888895,
      "lon": 11.477222222222222
    }
  },
  {
    "name": "Molnby",
    "synonyms": [
      "MOLNBY",
      "MOLNBY STN"
    ],
    "lId": "24801",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.55638888888888,
      "lon": 18.084722222222222
    }
  },
  {
    "name": "Mora busstation",
    "synonyms": [
      "MORA BUSSTATION"
    ],
    "lId": "13079",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 61.00333333333333,
      "lon": 14.53888888888889
    }
  },
  {
    "name": "Mora station",
    "synonyms": [
      "MORA STATION",
      "MORA STN"
    ],
    "lId": "00302",
    "prio": 1,
    "pId": "074",
    "pos": {
      "lat": 61.00861111111111,
      "lon": 14.558611111111112
    }
  },
  {
    "name": "Mora stadszon",
    "synonyms": [
      "MORA STADSZON",
      "MORA ZON"
    ],
    "lId": "79003",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 61.00333333333333,
      "lon": 14.53888888888889
    }
  },
  {
    "name": "Morastrand",
    "synonyms": [
      "MORASTRAND",
      "MORASTRAND STN"
    ],
    "lId": "20170",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 61.00472222222222,
      "lon": 14.542777777777777
    }
  },
  {
    "name": "Morgongåva",
    "synonyms": [
      "MORGONGAVA",
      "MORGONGÅVA",
      "MORGONGÅVA STN"
    ],
    "lId": "00736",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.93277777777777,
      "lon": 16.961388888888887
    }
  },
  {
    "name": "Morjärv Smedjan",
    "synonyms": [
      "MORJÄRV SMEDJAN",
      "MORJÆRV SMEDJAN"
    ],
    "lId": "24598",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 66.06666666666666,
      "lon": 22.704444444444444
    }
  },
  {
    "name": "Morshyttan södra",
    "synonyms": [
      "MORSHYTTAN SODRA",
      "MORSHYTTAN SÖDRA"
    ],
    "lId": "10248",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 60.259166666666665,
      "lon": 16.366944444444446
    }
  },
  {
    "name": "Morup",
    "synonyms": [
      "MORUP"
    ],
    "lId": "17127",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 56.97944444444445,
      "lon": 12.393055555555556
    }
  },
  {
    "name": "Moskosel affär",
    "synonyms": [
      "MOSKOSEL AFFÄR",
      "MOSKOSEL AFFÆR"
    ],
    "lId": "17257",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 65.875,
      "lon": 19.45
    }
  },
  {
    "name": "Moss",
    "synonyms": [
      "MOSS"
    ],
    "lId": "00516",
    "prio": 0,
    "pId": "076",
    "pos": {
      "lat": 59.43388888888889,
      "lon": 10.699722222222222
    }
  },
  {
    "name": "Mosås Landins väg",
    "synonyms": [
      "MOSÅS LANDINS VÄG",
      "MOSÅS LANDINS VÆG"
    ],
    "lId": "11076",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.19916666666666,
      "lon": 15.158888888888889
    }
  },
  {
    "name": "Motala",
    "synonyms": [
      "MOTALA"
    ],
    "lId": "00172",
    "prio": 1,
    "pId": "074",
    "pos": {
      "lat": 58.53722222222222,
      "lon": 15.048055555555555
    }
  },
  {
    "name": "Mullhyttan",
    "synonyms": [
      "MULLHYTTAN"
    ],
    "lId": "01158",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.15138888888889,
      "lon": 14.684444444444445
    }
  },
  {
    "name": "Mullsjö",
    "synonyms": [
      "MULLSJO",
      "MULLSJÖ",
      "MULLSJÖ STN",
      "MULLSJØ",
      "MULLSJØ STN"
    ],
    "lId": "00215",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 57.914722222222224,
      "lon": 13.881666666666668
    }
  },
  {
    "name": "Munka Ljungby väg 13",
    "synonyms": [
      "MUNKA LJUNGBY VÄG 13",
      "MUNKA LJUNGBY VÆG 13"
    ],
    "lId": "52237",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 56.254444444444445,
      "lon": 12.970833333333333
    }
  },
  {
    "name": "Munka-Ljungby Nygatan",
    "synonyms": [
      "M-LJUNGBY NYG",
      "MUNKA-LJUNGBY NYGATAN"
    ],
    "lId": "24390",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 56.25888888888889,
      "lon": 12.969166666666666
    }
  },
  {
    "name": "Munkedal",
    "synonyms": [
      "MUNKEDAL",
      "MUNKEDAL STN"
    ],
    "lId": "00087",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 58.46472222222223,
      "lon": 11.678055555555554
    }
  },
  {
    "name": "Munkflohögen affären",
    "synonyms": [
      "MUNKFLOHÖGEN AFFÄREN",
      "MUNKFLOHØGEN AFFÆREN"
    ],
    "lId": "18301",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 63.56083333333333,
      "lon": 14.949166666666667
    }
  },
  {
    "name": "Munkfors",
    "synonyms": [
      "MUNKFORS",
      "MUNKFORS BSTN"
    ],
    "lId": "00381",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.83416666666667,
      "lon": 13.545833333333333
    }
  },
  {
    "name": "Munktorp",
    "synonyms": [
      "MUNKTORP"
    ],
    "lId": "11085",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.5325,
      "lon": 16.133055555555558
    }
  },
  {
    "name": "Munsön",
    "synonyms": [
      "MUNSÖ SJÖÄNGEN",
      "MUNSÖN",
      "MUNSØ SJØÆNGEN",
      "MUNSØN"
    ],
    "lId": "01247",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.39138888888889,
      "lon": 17.53611111111111
    }
  },
  {
    "name": "Muodoslompolo",
    "synonyms": [
      "MUODOSLOMPOLO"
    ],
    "lId": "14804",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 67.94500000000001,
      "lon": 23.423333333333336
    }
  },
  {
    "name": "Murjek",
    "synonyms": [
      "MURJEK",
      "MURJEK STN"
    ],
    "lId": "00268",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 66.48388888888888,
      "lon": 20.880555555555556
    }
  },
  {
    "name": "Muskö",
    "synonyms": [
      "MUSKÖ",
      "MUSKÖ HYTTAN",
      "MUSKØ",
      "MUSKØ HYTTAN"
    ],
    "lId": "01248",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.02027777777778,
      "lon": 18.185277777777777
    }
  },
  {
    "name": "Myckelgensjö",
    "synonyms": [
      "MYCKELGENSJÖ",
      "MYCKELGENSJØ"
    ],
    "lId": "15227",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 63.578611111111115,
      "lon": 17.594166666666666
    }
  },
  {
    "name": "Myggenäs",
    "synonyms": [
      "MYGGENÄS",
      "MYGGENÄS KORSVÄ",
      "MYGGENÆS",
      "MYGGENÆS KORSVÆ"
    ],
    "lId": "01249",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 58.056666666666665,
      "lon": 11.760833333333334
    }
  },
  {
    "name": "Myresjö",
    "synonyms": [
      "MYRESJÖ",
      "MYRESJÖ BSTN",
      "MYRESJØ",
      "MYRESJØ BSTN"
    ],
    "lId": "01250",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 57.382222222222225,
      "lon": 14.959999999999999
    }
  },
  {
    "name": "Myrviken",
    "synonyms": [
      "MYRVIKEN"
    ],
    "lId": "01251",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 62.998333333333335,
      "lon": 14.338611111111112
    }
  },
  {
    "name": "Målerås",
    "synonyms": [
      "MÅLERÅS"
    ],
    "lId": "14301",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 56.91416666666667,
      "lon": 15.568888888888889
    }
  },
  {
    "name": "Målilla terminalen",
    "synonyms": [
      "MÅLILLA TERMINALEN"
    ],
    "lId": "71268",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 57.38722222222222,
      "lon": 15.805000000000001
    }
  },
  {
    "name": "Målsryd",
    "synonyms": [
      "MÅLSRYD",
      "MÅLSRYD CENTRUM"
    ],
    "lId": "01252",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 57.6825,
      "lon": 13.052777777777779
    }
  },
  {
    "name": "Månkarbo",
    "synonyms": [
      "MÅNKARBO",
      "MÅNKARBO GÅNGTU"
    ],
    "lId": "01253",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 60.22638888888889,
      "lon": 17.46472222222222
    }
  },
  {
    "name": "Månsarp",
    "synonyms": [
      "MÅNSARP",
      "MÅNSARP STN"
    ],
    "lId": "01254",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 57.654444444444444,
      "lon": 14.070277777777777
    }
  },
  {
    "name": "Månsåsen",
    "synonyms": [
      "MÅNSÅSEN"
    ],
    "lId": "13360",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 63.07,
      "lon": 14.315277777777778
    }
  },
  {
    "name": "Mårbacka",
    "synonyms": [
      "MÅRBACKA"
    ],
    "lId": "11094",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.780833333333334,
      "lon": 13.23611111111111
    }
  },
  {
    "name": "Mårtensdal",
    "synonyms": [
      "MÅRTENSDAL"
    ],
    "lId": "24928",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.302499999999995,
      "lon": 18.088055555555556
    }
  },
  {
    "name": "Måttsund Kallaxvägen",
    "synonyms": [
      "MÅTTSUND KALLAXVÄGEN",
      "MÅTTSUND KALLAXVÆGEN"
    ],
    "lId": "26984",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 65.53138888888888,
      "lon": 21.919722222222223
    }
  },
  {
    "name": "Mälarhöjden T-bana",
    "synonyms": [
      "MÄLARHÖJDEN T-BANA",
      "MÆLARHØJDEN T-BANA"
    ],
    "lId": "21723",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.30083333333333,
      "lon": 17.95722222222222
    }
  },
  {
    "name": "Märsta station",
    "synonyms": [
      "MARSTA STATION",
      "MÄRSTA STATION",
      "MÄRSTA STN",
      "MÆRSTA STATION",
      "MÆRSTA STN"
    ],
    "lId": "00027",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.628055555555555,
      "lon": 17.86138888888889
    }
  },
  {
    "name": "Möja Berg brygga",
    "synonyms": [
      "MÖJA BERG BRYGGA",
      "MØJA BERG BRYGGA"
    ],
    "lId": "24316",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.405833333333334,
      "lon": 18.88888888888889
    }
  },
  {
    "name": "Möklinta",
    "synonyms": [
      "MÖKLINTA",
      "MØKLINTA"
    ],
    "lId": "11097",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 60.08277777777778,
      "lon": 16.545
    }
  },
  {
    "name": "Mölle",
    "synonyms": [
      "MOLLE",
      "MÖLLE",
      "MÖLLE BSTN",
      "MØLLE",
      "MØLLE BSTN"
    ],
    "lId": "00948",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 56.28194444444444,
      "lon": 12.498888888888889
    }
  },
  {
    "name": "Mölltorp",
    "synonyms": [
      "MÖLLTORP",
      "MÖLLTORP CM",
      "MØLLTORP",
      "MØLLTORP CM"
    ],
    "lId": "00177",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 58.49333333333333,
      "lon": 14.415000000000001
    }
  },
  {
    "name": "Mölltorp väg 49",
    "synonyms": [
      "MÖLLTORP VÄG 49",
      "MØLLTORP VÆG 49"
    ],
    "lId": "11102",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 58.49027777777778,
      "lon": 14.420555555555556
    }
  },
  {
    "name": "Mölnbo",
    "synonyms": [
      "MÖLNBO",
      "MÖLNBO STN",
      "MØLNBO",
      "MØLNBO STN"
    ],
    "lId": "00715",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.0475,
      "lon": 17.418055555555558
    }
  },
  {
    "name": "Mölndal Krokslätts fabriker",
    "synonyms": [
      "MÖLNDAL KROKSLÄTTS FABRIKER",
      "MØLNDAL KROKSLÆTTS FABRIKER"
    ],
    "lId": "25720",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 57.671388888888885,
      "lon": 12.01
    }
  },
  {
    "name": "Mölndal Krokslätts torg",
    "synonyms": [
      "MÖLNDAL KROKSLÄTTS TORG",
      "MØLNDAL KROKSLÆTTS TORG"
    ],
    "lId": "15640",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 57.67527777777777,
      "lon": 12.007777777777777
    }
  },
  {
    "name": "Mölndal Lackarebäck",
    "synonyms": [
      "MÖLNDAL LACKAREBÄCK",
      "MØLNDAL LACKAREBÆCK"
    ],
    "lId": "25715",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 57.66583333333333,
      "lon": 12.011111111111111
    }
  },
  {
    "name": "Mölndal sjukhus",
    "synonyms": [
      "MÖLNDAL SJUKHUS",
      "MØLNDAL SJUKHUS"
    ],
    "lId": "15635",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 57.66138888888889,
      "lon": 12.013333333333334
    }
  },
  {
    "name": "Mölndal station",
    "synonyms": [
      "MÖLNDAL STATION",
      "MÖLNDAL STN",
      "MØLNDAL STN"
    ],
    "lId": "00315",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 57.655833333333334,
      "lon": 12.018611111111111
    }
  },
  {
    "name": "Mölndal Åby Fritidscentrum",
    "synonyms": [
      "MÖLNDAL ÅBY FRITIDSCENTRUM"
    ],
    "lId": "15645",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 57.64666666666667,
      "lon": 11.998333333333333
    }
  },
  {
    "name": "Mölnlycke station",
    "synonyms": [
      "MOLNLYCKE STATION",
      "MÖLNLYCKE STATION",
      "MØLNLYCKE STATION"
    ],
    "lId": "00205",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 57.656666666666666,
      "lon": 12.117222222222223
    }
  },
  {
    "name": "Mölntorp",
    "synonyms": [
      "MÖLNTORP"
    ],
    "lId": "44534",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.549166666666665,
      "lon": 16.25722222222222
    }
  },
  {
    "name": "Mönsterås busstation",
    "synonyms": [
      "MONSTERAS BUS STATION",
      "MÖNSTERÅS BSTN",
      "MÖNSTERÅS BUSSTATION",
      "MØNSTERÅS BSTN",
      "MØNSTERÅS BUSSTATION"
    ],
    "lId": "00561",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 57.04083333333333,
      "lon": 16.447222222222223
    }
  },
  {
    "name": "Mönsterås norra",
    "synonyms": [
      "MÖNSTERÅS NORRA"
    ],
    "lId": "14150",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 57.05138888888889,
      "lon": 16.43888888888889
    }
  },
  {
    "name": "Mörarp",
    "synonyms": [
      "MORARP",
      "MÖRARP",
      "MÖRARP STN",
      "MØRARP",
      "MØRARP STN"
    ],
    "lId": "01255",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 56.05555555555555,
      "lon": 12.873055555555556
    }
  },
  {
    "name": "Mörby centrum T-bana",
    "synonyms": [
      "MÖRBY CENTRUM T-BANA",
      "MØRBY CENTRUM T-BANA"
    ],
    "lId": "00716",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.39861111111111,
      "lon": 18.03611111111111
    }
  },
  {
    "name": "Mörby station",
    "synonyms": [
      "MÖRBY STATION",
      "MÖRBY STN",
      "MØRBY STATION",
      "MØRBY STN"
    ],
    "lId": "20867",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.391666666666666,
      "lon": 18.046666666666667
    }
  },
  {
    "name": "Mörbylånga",
    "synonyms": [
      "MÖRBYLÅNGA",
      "MÖRBYLÅNGA BSTN",
      "MØRBYLÅNGA",
      "MØRBYLÅNGA BSTN"
    ],
    "lId": "00928",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 56.52777777777778,
      "lon": 16.37611111111111
    }
  },
  {
    "name": "Mörkö",
    "synonyms": [
      "MÖRKÖ",
      "MÖRKÖ HÖRNINGSH",
      "MØRKØ",
      "MØRKØ HØRNINGSH"
    ],
    "lId": "01184",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.044999999999995,
      "lon": 17.67388888888889
    }
  },
  {
    "name": "Mörlunda station",
    "synonyms": [
      "MÖRLUNDA STATION",
      "MÖRLUNDA STN",
      "MØRLUNDA STATION",
      "MØRLUNDA STN"
    ],
    "lId": "00209",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 57.32222222222222,
      "lon": 15.875555555555556
    }
  },
  {
    "name": "Mörrum station",
    "synonyms": [
      "MÖRRUM STATION",
      "MÖRRUM STN",
      "MØRRUM STATION",
      "MØRRUM STN"
    ],
    "lId": "00366",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 56.18666666666666,
      "lon": 14.744444444444444
    }
  },
  {
    "name": "Mörsil station",
    "synonyms": [
      "MÖRSIL STATION",
      "MÖRSIL STN",
      "MØRSIL STN"
    ],
    "lId": "00153",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 63.30833333333333,
      "lon": 13.657222222222222
    }
  },
  {
    "name": "Mörtnäs Ålstäket",
    "synonyms": [
      "MÖRTNÄS ÅLSTÄKET",
      "MØRTNÆS ÅLSTÆKET"
    ],
    "lId": "26591",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.31305555555555,
      "lon": 18.45611111111111
    }
  },
  {
    "name": "Mörtsal E4",
    "synonyms": [
      "MÖRTSAL E4",
      "MØRTSAL E4"
    ],
    "lId": "53531",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 62.78055555555555,
      "lon": 17.91916666666667
    }
  },
  {
    "name": "Nabbelund",
    "synonyms": [
      "NABBELUND"
    ],
    "lId": "14302",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 57.34777777777778,
      "lon": 17.080555555555556
    }
  },
  {
    "name": "Nacka station",
    "synonyms": [
      "NACKA STATION",
      "NACKA STN"
    ],
    "lId": "00717",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.30638888888888,
      "lon": 18.13
    }
  },
  {
    "name": "Nacka strand",
    "synonyms": [
      "NACKA STRAND"
    ],
    "lId": "24852",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.31638888888889,
      "lon": 18.16
    }
  },
  {
    "name": "Narvik stn",
    "synonyms": [
      "NARVIK STN"
    ],
    "lId": "02402",
    "prio": 1,
    "pId": "076",
    "pos": {
      "lat": 68.44166666666668,
      "lon": 17.441388888888888
    }
  },
  {
    "name": "Nattavaara",
    "synonyms": [
      "NATTAVAARA",
      "NATTAVAARA STN"
    ],
    "lId": "00265",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 66.7538888888889,
      "lon": 20.950833333333332
    }
  },
  {
    "name": "Nedansjö",
    "synonyms": [
      "NEDANSJÖ",
      "NEDANSJÖ BYSTUG",
      "NEDANSJØ",
      "NEDANSJØ BYSTUG"
    ],
    "lId": "15232",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 62.37722222222222,
      "lon": 16.83111111111111
    }
  },
  {
    "name": "Nederhögen station",
    "synonyms": [
      "NEDERHÖGEN STATION",
      "NEDERHÖGEN STN",
      "NEDERHØGEN STATION",
      "NEDERHØGEN STN"
    ],
    "lId": "04438",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 62.41083333333333,
      "lon": 14.428333333333333
    }
  },
  {
    "name": "Nedre Soppero",
    "synonyms": [
      "NEDRE SOPPERO"
    ],
    "lId": "01256",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 68.04722222222222,
      "lon": 21.7625
    }
  },
  {
    "name": "Neglinge station",
    "synonyms": [
      "NEGLINGE STATION",
      "NEGLINGE STN"
    ],
    "lId": "20877",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.288333333333334,
      "lon": 18.291944444444447
    }
  },
  {
    "name": "Nikkala E4",
    "synonyms": [
      "NIKKALA E4"
    ],
    "lId": "14967",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 65.8111111111111,
      "lon": 23.911944444444444
    }
  },
  {
    "name": "Nikkaluokta",
    "synonyms": [
      "NIKKALUOKTA"
    ],
    "lId": "00884",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 67.85055555555554,
      "lon": 19.015
    }
  },
  {
    "name": "Nissafors affären",
    "synonyms": [
      "NISSAFORS AFFÄREN",
      "NISSAFORS AFFÆREN"
    ],
    "lId": "23498",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 57.40861111111111,
      "lon": 13.635833333333332
    }
  },
  {
    "name": "Nitta affär",
    "synonyms": [
      "NITTA AFFÄR",
      "NITTA AFFÆR"
    ],
    "lId": "12433",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 57.827222222222225,
      "lon": 13.19
    }
  },
  {
    "name": "Nivå",
    "synonyms": [
      "NIVA",
      "NIVÅ"
    ],
    "lId": "00665",
    "prio": 0,
    "pId": "086",
    "pos": {
      "lat": 55.93333333333333,
      "lon": 12.50611111111111
    }
  },
  {
    "name": "Njurundabommen",
    "synonyms": [
      "NJURUNDABOMMEN"
    ],
    "lId": "15233",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 62.269444444444446,
      "lon": 17.371666666666666
    }
  },
  {
    "name": "Njutånger Backa",
    "synonyms": [
      "NJUTÅNGER BACKA"
    ],
    "lId": "11117",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 61.60638888888889,
      "lon": 17.054722222222225
    }
  },
  {
    "name": "Nockeby",
    "synonyms": [
      "NOCKEBY"
    ],
    "lId": "01181",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.328611111111115,
      "lon": 17.91861111111111
    }
  },
  {
    "name": "Nockeby torg",
    "synonyms": [
      "NOCKEBY TORG"
    ],
    "lId": "24820",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.32888888888889,
      "lon": 17.928055555555556
    }
  },
  {
    "name": "Nogersund",
    "synonyms": [
      "NOGERSUND",
      "NOGERSUND HAMN"
    ],
    "lId": "01257",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 56.00527777777778,
      "lon": 14.738055555555555
    }
  },
  {
    "name": "Nol station",
    "synonyms": [
      "NOL STATION",
      "NOL STN"
    ],
    "lId": "00066",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 57.91833333333333,
      "lon": 12.061944444444444
    }
  },
  {
    "name": "Noppikoski OKQ8",
    "synonyms": [
      "NOPPIKOSKI OKQ8"
    ],
    "lId": "20095",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 61.494166666666665,
      "lon": 14.8475
    }
  },
  {
    "name": "Nora Hitorp Övre",
    "synonyms": [
      "NORA HITORP ÖVRE",
      "NORA HITORP ØVRE"
    ],
    "lId": "20928",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.505,
      "lon": 15.040277777777778
    }
  },
  {
    "name": "Nora station",
    "synonyms": [
      "NORA STATION"
    ],
    "lId": "67101",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.51722222222222,
      "lon": 15.04138888888889
    }
  },
  {
    "name": "Norberg",
    "synonyms": [
      "NORBERG",
      "NORBERG BSTN"
    ],
    "lId": "00678",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 60.06472222222222,
      "lon": 15.925277777777778
    }
  },
  {
    "name": "Norberg Fågelvägen",
    "synonyms": [
      "NORBERG FÅGELVÄGEN"
    ],
    "lId": "71779",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 60.05888888888889,
      "lon": 15.94138888888889
    }
  },
  {
    "name": "Nordanö",
    "synonyms": [
      "NORDANÖ",
      "NORDANØ"
    ],
    "lId": "25136",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 60.14888888888889,
      "lon": 16.235
    }
  },
  {
    "name": "Norderåsen",
    "synonyms": [
      "NORDERÅSEN"
    ],
    "lId": "25947",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 63.4375,
      "lon": 14.851111111111111
    }
  },
  {
    "name": "Nordingrå",
    "synonyms": [
      "NORDINGRÅ",
      "NORDINGRÅ VALLE"
    ],
    "lId": "01258",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 62.93055555555555,
      "lon": 18.295
    }
  },
  {
    "name": "Nordmaling station",
    "synonyms": [
      "NORDMALING STATION",
      "NORDMALING STN"
    ],
    "lId": "01583",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 63.57833333333333,
      "lon": 19.485833333333336
    }
  },
  {
    "name": "Nordmark Kruthuset",
    "synonyms": [
      "NORDMARK KRUTHUSET"
    ],
    "lId": "25005",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.83861111111111,
      "lon": 14.130555555555556
    }
  },
  {
    "name": "Norje Bro",
    "synonyms": [
      "NORJE BRO"
    ],
    "lId": "11123",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 56.117222222222225,
      "lon": 14.671944444444444
    }
  },
  {
    "name": "Norra Bro Lilla Ässkogsvägen",
    "synonyms": [
      "N BRO L ÄSKOGSV",
      "N BRO L ÆSKOGSV",
      "NORRA BRO LILLA ÄSSKOGSVÄGEN",
      "NORRA BRO LILLA ÆSSKOGSVÆGEN"
    ],
    "lId": "22014",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.224444444444444,
      "lon": 15.250833333333333
    }
  },
  {
    "name": "Norra Häljaröd Rönnen",
    "synonyms": [
      "N HÄLJARÖD RÖNN",
      "NORRA HÄLJARÖD RÖNNEN"
    ],
    "lId": "20724",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 56.222500000000004,
      "lon": 12.743611111111111
    }
  },
  {
    "name": "Norra Lagnö",
    "synonyms": [
      "NORRA LAGNÖ",
      "NORRA LAGNØ"
    ],
    "lId": "18274",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.352222222222224,
      "lon": 18.40972222222222
    }
  },
  {
    "name": "Norra Möckleby kyrka",
    "synonyms": [
      "N MÖCKLEBY KA",
      "N MØCKLEBY KA",
      "NORRA MÖCKLEBY KYRKA",
      "NORRA MØCKLEBY KYRKA"
    ],
    "lId": "14290",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 56.6475,
      "lon": 16.678611111111113
    }
  },
  {
    "name": "Norra Råsen",
    "synonyms": [
      "NORRA RÅSEN"
    ],
    "lId": "20386",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 56.90611111111111,
      "lon": 14.465277777777777
    }
  },
  {
    "name": "Norra Rörum affären",
    "synonyms": [
      "N RÖRUM AFFÄREN",
      "N RØRUM AFFÆREN",
      "NORRA RÖRUM AFFÄREN",
      "NORRA RØRUM AFFÆREN"
    ],
    "lId": "26066",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 56.01694444444444,
      "lon": 13.508333333333333
    }
  },
  {
    "name": "Norra Sandby kyrka",
    "synonyms": [
      "N SANDBY KYRKA",
      "NORRA SANDBY KYRKA"
    ],
    "lId": "22087",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 56.19972222222222,
      "lon": 13.923055555555555
    }
  },
  {
    "name": "Norra Ulvsunda Spårv",
    "synonyms": [
      "NORRA ULVSUNDA SPÅRV"
    ],
    "lId": "64041",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.35055555555556,
      "lon": 17.9625
    }
  },
  {
    "name": "Norra Unnaryd",
    "synonyms": [
      "N UNNARYD V 26",
      "NORRA UNNARYD"
    ],
    "lId": "00578",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 57.60138888888889,
      "lon": 13.746944444444443
    }
  },
  {
    "name": "Norra Vram kyrka",
    "synonyms": [
      "N VRAM KYRKA",
      "NORRA VRAM KYRKA"
    ],
    "lId": "16795",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 56.088055555555556,
      "lon": 12.973888888888888
    }
  },
  {
    "name": "Norra Åsum Wendeskolan",
    "synonyms": [
      "N ÅSUM WENDESKO",
      "NORRA ÅSUM WENDESKOLAN"
    ],
    "lId": "10488",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 55.99,
      "lon": 14.145833333333332
    }
  },
  {
    "name": "Norra Älvsborgs Lasarett",
    "synonyms": [
      "NORRA ÄLVSBORGS LASARETT",
      "NÄL"
    ],
    "lId": "12297",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 58.31722222222223,
      "lon": 12.266944444444444
    }
  },
  {
    "name": "Norrahammar station",
    "synonyms": [
      "NORRAHAMMAR STATION"
    ],
    "lId": "00533",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 57.70444444444445,
      "lon": 14.115277777777777
    }
  },
  {
    "name": "Norrboda Gräsö",
    "synonyms": [
      "GRÄSÖ NORRBODA",
      "GRÆSØ NORRBODA",
      "NORRBODA",
      "NORRBODA GRÄSÖ",
      "NORRBODA GRÆSØ",
      "NORRBODA ÖSTHAM",
      "NORRBODA ØSTHAM"
    ],
    "lId": "12705",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 60.469722222222224,
      "lon": 18.41111111111111
    }
  },
  {
    "name": "Norrbyås kyrka",
    "synonyms": [
      "NORRBYÅS KYRKA"
    ],
    "lId": "11128",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.19472222222222,
      "lon": 15.389999999999999
    }
  },
  {
    "name": "Norrfjärden Gnarp",
    "synonyms": [
      "NORRFJÄRDEN GNARP",
      "NORRFJÆRDEN GNARP"
    ],
    "lId": "18947",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 62.06083333333333,
      "lon": 17.425833333333333
    }
  },
  {
    "name": "Norrfjärden kyrka Piteå",
    "synonyms": [
      "NORRFJÄRDEN KYRKA PITEÅ",
      "NORRFJÆRDEN KYRKA PITEÅ"
    ],
    "lId": "14906",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 65.42166666666667,
      "lon": 21.493333333333336
    }
  },
  {
    "name": "Norrfjärden Umeå",
    "synonyms": [
      "NORRFJÄRDEN UMEÅ",
      "NORRFJÆRDEN UMEÅ"
    ],
    "lId": "20389",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 63.86222222222222,
      "lon": 20.73777777777778
    }
  },
  {
    "name": "Norrfällsviken",
    "synonyms": [
      "NORRFÄLLSVIKEN",
      "NORRFÆLLSVIKEN"
    ],
    "lId": "15373",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 62.97277777777778,
      "lon": 18.523333333333333
    }
  },
  {
    "name": "Norrhult",
    "synonyms": [
      "NORRHULT",
      "NORRHULT Q8"
    ],
    "lId": "00124",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 57.12388888888889,
      "lon": 15.16861111111111
    }
  },
  {
    "name": "Norrköping C",
    "synonyms": [
      "NORRKOPING C",
      "NORRKÖPING C",
      "NORRKØPING C"
    ],
    "lId": "00007",
    "prio": 1,
    "pId": "074",
    "pos": {
      "lat": 58.59638888888889,
      "lon": 16.183333333333334
    }
  },
  {
    "name": "Norrköping Albrektsvägen",
    "synonyms": [
      "NORRKÖPING ALBREKTSVÄGEN",
      "NORRKØPING ALBREKTSVÆGEN"
    ],
    "lId": "25987",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 58.58083333333334,
      "lon": 16.189444444444444
    }
  },
  {
    "name": "Norrköping Atriumhusen",
    "synonyms": [
      "NORRKÖPING ATRIUMHUSEN"
    ],
    "lId": "54016",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 58.56333333333333,
      "lon": 16.22111111111111
    }
  },
  {
    "name": "Norrköping Bastuban",
    "synonyms": [
      "NORRKÖPING BASTUBAN",
      "NORRKØPING BASTUBAN"
    ],
    "lId": "26015",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 58.57805555555556,
      "lon": 16.138055555555557
    }
  },
  {
    "name": "Norrköping Blommmelundsgatan",
    "synonyms": [
      "NORRKÖPING BLOMMMELUNDSGATAN",
      "NORRKØPING BLOMMMELUNDSGATAN"
    ],
    "lId": "26005",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 58.60138888888889,
      "lon": 16.161944444444444
    }
  },
  {
    "name": "Norrköping Breda vägen",
    "synonyms": [
      "NORRKÖPING BREDA VÄGEN",
      "NORRKØPING BREDA VÆGEN"
    ],
    "lId": "26004",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 58.60305555555556,
      "lon": 16.16333333333333
    }
  },
  {
    "name": "Norrköping Broocmans Plan",
    "synonyms": [
      "NORRKÖPING BROOCMANS PLAN",
      "NORRKØPING BROOCMANS PLAN"
    ],
    "lId": "25986",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 58.58277777777778,
      "lon": 16.186666666666667
    }
  },
  {
    "name": "Norrköping Cederborgsvägen",
    "synonyms": [
      "NORRKÖPING CEDERBORGSVÄGEN",
      "NORRKØPING CEDERBORGSVÆGEN"
    ],
    "lId": "25993",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 58.60055555555556,
      "lon": 16.15722222222222
    }
  },
  {
    "name": "Norrköping Centralbadet",
    "synonyms": [
      "NORRKÖPING CENTRALBADET",
      "NORRKØPING CENTRALBADET"
    ],
    "lId": "25978",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 58.58638888888889,
      "lon": 16.199444444444445
    }
  },
  {
    "name": "Norrköping De Geersgatan",
    "synonyms": [
      "NORRKÖPING DE GEERSGATAN",
      "NORRKØPING DE GEERSGATAN"
    ],
    "lId": "25990",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 58.60527777777778,
      "lon": 16.139166666666664
    }
  },
  {
    "name": "Norrköping Djäkneparksskolan",
    "synonyms": [
      "NORRKÖPING DJÄKNEPARKSSKOLAN",
      "NORRKØPING DJÆKNEPARKSSKOLAN"
    ],
    "lId": "25976",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 58.58972222222222,
      "lon": 16.198611111111113
    }
  },
  {
    "name": "Norrköping Eneby centrum",
    "synonyms": [
      "NORRKÖPING ENEBY CENTRUM",
      "NORRKØPING ENEBY CENTRUM"
    ],
    "lId": "25985",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 58.60277777777778,
      "lon": 16.14361111111111
    }
  },
  {
    "name": "Norrköping Folkets Park",
    "synonyms": [
      "NORRKÖPING FOLKETS PARK",
      "NORRKØPING FOLKETS PARK"
    ],
    "lId": "26013",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 58.57777777777778,
      "lon": 16.149722222222223
    }
  },
  {
    "name": "Norrköping Fridvalla",
    "synonyms": [
      "NORRKÖPING FRIDVALLA",
      "NORRKØPING FRIDVALLA"
    ],
    "lId": "25980",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 58.61138888888889,
      "lon": 16.133888888888887
    }
  },
  {
    "name": "Norrköping Gymnastikgatan",
    "synonyms": [
      "NORRKÖPING GYMNASTIKGATAN",
      "NORRKØPING GYMNASTIKGATAN"
    ],
    "lId": "26007",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 58.58555555555556,
      "lon": 16.183611111111112
    }
  },
  {
    "name": "Norrköping Hagaskolan",
    "synonyms": [
      "NORRKÖPING HAGASKOLAN",
      "NORRKØPING HAGASKOLAN"
    ],
    "lId": "25994",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 58.599444444444444,
      "lon": 16.160833333333333
    }
  },
  {
    "name": "Norrköping Hageby centrum",
    "synonyms": [
      "NORRKÖPING HAGEBY CENTRUM"
    ],
    "lId": "53800",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 58.57194444444445,
      "lon": 16.206944444444442
    }
  },
  {
    "name": "Norrköping Hageby vårdcentral",
    "synonyms": [
      "NORRKÖPING HAGEBY VÅRDCENTRAL"
    ],
    "lId": "54012",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 58.57472222222223,
      "lon": 16.2025
    }
  },
  {
    "name": "Norrköping Heleneborgsgatan",
    "synonyms": [
      "NORRKÖPING HELENEBORGSGATAN",
      "NORRKØPING HELENEBORGSGATAN"
    ],
    "lId": "25989",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 58.60805555555556,
      "lon": 16.136944444444445
    }
  },
  {
    "name": "Norrköping Himmelstalundsvägen",
    "synonyms": [
      "NORRKÖPING HIMMELSTALUNDSVÄGEN",
      "NORRKØPING HIMMELSTALUNDSVÆGEN"
    ],
    "lId": "25995",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 58.598333333333336,
      "lon": 16.164166666666667
    }
  },
  {
    "name": "Norrköping Holmstaskolan",
    "synonyms": [
      "NORRKÖPING HOLMSTASKOLAN",
      "NORRKØPING HOLMSTASKOLAN"
    ],
    "lId": "26001",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 58.57833333333333,
      "lon": 16.192777777777778
    }
  },
  {
    "name": "Norrköping Hospitalsgatan",
    "synonyms": [
      "NORRKÖPING HOSPITALSGATAN",
      "NORRKØPING HOSPITALSGATAN"
    ],
    "lId": "26006",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 58.59055555555556,
      "lon": 16.186944444444446
    }
  },
  {
    "name": "Norrköping Hörsalsparken",
    "synonyms": [
      "NORRKÖPING HÖRSALSPARKEN",
      "NORRKØPING HØRSALSPARKEN"
    ],
    "lId": "25982",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 58.58833333333334,
      "lon": 16.188333333333333
    }
  },
  {
    "name": "Norrköping Karlshovsskolan",
    "synonyms": [
      "NORRKÖPING KARLSHOVSSKOLAN",
      "NORRKØPING KARLSHOVSSKOLAN"
    ],
    "lId": "25992",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 58.60305555555556,
      "lon": 16.1525
    }
  },
  {
    "name": "Norrköping Klingsberg",
    "synonyms": [
      "NORRKÖPING KLINGSBERG",
      "NORRKØPING KLINGSBERG"
    ],
    "lId": "25977",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 58.57666666666667,
      "lon": 16.18888888888889
    }
  },
  {
    "name": "Norrköping Klingsbergsparken",
    "synonyms": [
      "NORRKÖPING KLINGSBERGSPARKEN",
      "NORRKØPING KLINGSBERGSPARKEN"
    ],
    "lId": "25988",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 58.57888888888889,
      "lon": 16.18638888888889
    }
  },
  {
    "name": "Norrköping Klockaretorpet",
    "synonyms": [
      "NORRKÖPING KLOCKARETORPET",
      "NORRKØPING KLOCKARETORPET"
    ],
    "lId": "25983",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 58.57527777777778,
      "lon": 16.125555555555557
    }
  },
  {
    "name": "Norrköping Kv. Niten",
    "synonyms": [
      "KV. NITEN",
      "NORRKÖPING KV. NITEN"
    ],
    "lId": "54013",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 58.56888888888889,
      "lon": 16.211111111111112
    }
  },
  {
    "name": "Norrköping Kvarnberget",
    "synonyms": [
      "NORRKÖPING KVARNBERGET"
    ],
    "lId": "53802",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 58.55472222222222,
      "lon": 16.2275
    }
  },
  {
    "name": "Norrköping Ljura",
    "synonyms": [
      "NORRKÖPING LJURA"
    ],
    "lId": "54046",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 58.580000000000005,
      "lon": 16.197222222222223
    }
  },
  {
    "name": "Norrköping Ljura södra",
    "synonyms": [
      "NORRKÖPING LJURA SÖDRA"
    ],
    "lId": "54047",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 58.57805555555556,
      "lon": 16.2
    }
  },
  {
    "name": "Norrköping Lokegatan",
    "synonyms": [
      "NORRKÖPING LOKEGATAN",
      "NORRKØPING LOKEGATAN"
    ],
    "lId": "26011",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 58.58111111111111,
      "lon": 16.16
    }
  },
  {
    "name": "Norrköping Marielund",
    "synonyms": [
      "NORRKÖPING MARIELUND",
      "NORRKØPING MARIELUND"
    ],
    "lId": "25996",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 58.59666666666667,
      "lon": 16.16638888888889
    }
  },
  {
    "name": "Norrköping Matteusskolan",
    "synonyms": [
      "NORRKÖPING MATTEUSSKOLAN",
      "NORRKØPING MATTEUSSKOLAN"
    ],
    "lId": "25997",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 58.59388888888889,
      "lon": 16.16916666666667
    }
  },
  {
    "name": "Norrköping Norr Tull",
    "synonyms": [
      "NORRKÖPING NORR TULL",
      "NORRKØPING NORR TULL"
    ],
    "lId": "20345",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 58.594722222222224,
      "lon": 16.17666666666667
    }
  },
  {
    "name": "Norrköping Nya Torget",
    "synonyms": [
      "NORRKÖPING NYA TORGET",
      "NORRKØPING NYA TORGET"
    ],
    "lId": "25999",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 58.592222222222226,
      "lon": 16.191944444444445
    }
  },
  {
    "name": "Norrköping Ringdansens centrum",
    "synonyms": [
      "NORRKÖPING RINGDANSENS CENTRUM"
    ],
    "lId": "53801",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 58.558611111111105,
      "lon": 16.225555555555555
    }
  },
  {
    "name": "Norrköping Rådhuset",
    "synonyms": [
      "NORRKÖPING RÅDHUSET",
      "NORRKØPING RÅDHUSET"
    ],
    "lId": "25998",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 58.592222222222226,
      "lon": 16.18611111111111
    }
  },
  {
    "name": "Norrköping Rågången",
    "synonyms": [
      "NORRKÖPING RÅGÅNGEN"
    ],
    "lId": "26002",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 58.60638888888889,
      "lon": 16.154444444444444
    }
  },
  {
    "name": "Norrköping Sandbyhov",
    "synonyms": [
      "NORRKÖPING SANDBYHOV",
      "NORRKØPING SANDBYHOV"
    ],
    "lId": "26003",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 58.60444444444445,
      "lon": 16.15833333333333
    }
  },
  {
    "name": "Norrköping Skarphagsgatan",
    "synonyms": [
      "NORRKÖPING SKARPHAGSGATAN",
      "NORRKØPING SKARPHAGSGATAN"
    ],
    "lId": "26012",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 58.57944444444445,
      "lon": 16.154722222222222
    }
  },
  {
    "name": "Norrköping Slåttergatan",
    "synonyms": [
      "NORRKÖPING SLÅTTERGATAN",
      "NORRKØPING SLÅTTERGATAN"
    ],
    "lId": "25991",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 58.60472222222222,
      "lon": 16.149166666666666
    }
  },
  {
    "name": "Norrköping SMHI",
    "synonyms": [
      "NORRKÖPING SMHI",
      "NORRKØPING SMHI"
    ],
    "lId": "26014",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 58.57944444444445,
      "lon": 16.14611111111111
    }
  },
  {
    "name": "Norrköping Stortorget",
    "synonyms": [
      "NORRKÖPING STORTORGET",
      "NORRKØPING STORTORGET"
    ],
    "lId": "25979",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 58.58583333333333,
      "lon": 16.196666666666665
    }
  },
  {
    "name": "Norrköping Strömbacken",
    "synonyms": [
      "NORRKÖPING STRÖMBACKEN",
      "NORRKØPING STRØMBACKEN"
    ],
    "lId": "26009",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 58.58638888888889,
      "lon": 16.17
    }
  },
  {
    "name": "Norrköping Styrmansgatan",
    "synonyms": [
      "NORRKÖPING STYRMANSGATAN",
      "NORRKØPING STYRMANSGATAN"
    ],
    "lId": "26000",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 58.59277777777778,
      "lon": 16.19611111111111
    }
  },
  {
    "name": "Norrköping Söder Tull",
    "synonyms": [
      "NORRKÖPING SÖDER TULL",
      "NORRKØPING SØDER TULL"
    ],
    "lId": "11132",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 58.585,
      "lon": 16.189722222222223
    }
  },
  {
    "name": "Norrköping Torsten Fogelqvistg",
    "synonyms": [
      "NORRKÖPING TORSTEN FOGELQVISTG",
      "NORRKØPING TORSTEN FOGELQVISTG"
    ],
    "lId": "26016",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 58.57694444444445,
      "lon": 16.13138888888889
    }
  },
  {
    "name": "Norrköping Trumpetaregatan",
    "synonyms": [
      "NORRKÖPING TRUMPETAREGATAN",
      "TRUMPETAREGATAN"
    ],
    "lId": "54015",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 58.56527777777777,
      "lon": 16.217777777777776
    }
  },
  {
    "name": "Norrköping Vidablick",
    "synonyms": [
      "NORRKÖPING VIDABLICK",
      "NORRKØPING VIDABLICK"
    ],
    "lId": "25981",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 58.60861111111111,
      "lon": 16.15111111111111
    }
  },
  {
    "name": "Norrköping Vägträffen",
    "synonyms": [
      "NORRKÖPING VÄGTRÄFFEN",
      "NORRKØPING VÆGTRÆFFEN"
    ],
    "lId": "26010",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 58.585,
      "lon": 16.16333333333333
    }
  },
  {
    "name": "Norrköping Väster Tull",
    "synonyms": [
      "NORRKÖPING VÄSTER TULL",
      "NORRKØPING VÆSTER TULL"
    ],
    "lId": "26008",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 58.586111111111116,
      "lon": 16.17666666666667
    }
  },
  {
    "name": "Norrköping Östra Eneby kyrka",
    "synonyms": [
      "NORRKÖPING ÖSTRA ENEBY KYRKA",
      "NORRKØPING ØSTRA ENEBY KYRKA"
    ],
    "lId": "25984",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 58.60944444444445,
      "lon": 16.135277777777777
    }
  },
  {
    "name": "Norrskedika norra",
    "synonyms": [
      "NORRSKEDIKA NORRA"
    ],
    "lId": "01259",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 60.28805555555555,
      "lon": 18.28611111111111
    }
  },
  {
    "name": "Norrsundet",
    "synonyms": [
      "NORRSUNDET",
      "NORRSUNDET FABR"
    ],
    "lId": "00637",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 60.937777777777775,
      "lon": 17.140555555555554
    }
  },
  {
    "name": "Norrtälje busstation",
    "synonyms": [
      "NORRTÄLJE BSTN",
      "NORRTÄLJE BUSSTATION",
      "NORRTÆLJE BSTN",
      "NORRTÆLJE BUSSTATION"
    ],
    "lId": "00665",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.75944444444445,
      "lon": 18.699166666666667
    }
  },
  {
    "name": "Norrtälje Campus Roslagen",
    "synonyms": [
      "NORRTÄLJE CAMPUS ROSLAGEN"
    ],
    "lId": "49263",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.74805555555556,
      "lon": 18.685555555555556
    }
  },
  {
    "name": "Norrviken",
    "synonyms": [
      "NORRVIKEN",
      "NORRVIKEN STN"
    ],
    "lId": "00718",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.45805555555556,
      "lon": 17.924166666666668
    }
  },
  {
    "name": "Norråker",
    "synonyms": [
      "NORRÅKER"
    ],
    "lId": "01260",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 64.43527777777778,
      "lon": 15.593055555555557
    }
  },
  {
    "name": "Norsborg T-bana",
    "synonyms": [
      "NORSBORG T-BANA"
    ],
    "lId": "21733",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.243611111111115,
      "lon": 17.814444444444444
    }
  },
  {
    "name": "Norsesund",
    "synonyms": [
      "NORSESUND",
      "NORSESUND STN"
    ],
    "lId": "01261",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 57.86138888888889,
      "lon": 12.43888888888889
    }
  },
  {
    "name": "Norsholm",
    "synonyms": [
      "NORSHOLM",
      "NORSHOLM CM"
    ],
    "lId": "00853",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 58.50611111111111,
      "lon": 15.972777777777777
    }
  },
  {
    "name": "Norsjö",
    "synonyms": [
      "NORSJÖ",
      "NORSJÖ BSTN",
      "NORSJØ",
      "NORSJØ BSTN"
    ],
    "lId": "00389",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 64.9113888888889,
      "lon": 19.483888888888888
    }
  },
  {
    "name": "Nossebro",
    "synonyms": [
      "NOSSEBRO",
      "NOSSEBRO BSTN"
    ],
    "lId": "00594",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 58.18722222222222,
      "lon": 12.71888888888889
    }
  },
  {
    "name": "Nottebäck terminalen",
    "synonyms": [
      "NOTTEBÄCK TERMINALEN",
      "NOTTEBÆCK TERMINALEN"
    ],
    "lId": "14474",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 57.08777777777778,
      "lon": 15.183333333333334
    }
  },
  {
    "name": "Notviken station",
    "synonyms": [
      "NOTVIKEN STATION"
    ],
    "lId": "02953",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 65.61194444444443,
      "lon": 22.114722222222223
    }
  },
  {
    "name": "Nusnäs gamla affären",
    "synonyms": [
      "NUSNÄS GAMLA AFFÄREN"
    ],
    "lId": "24263",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 60.961666666666666,
      "lon": 14.642777777777777
    }
  },
  {
    "name": "Nyadal",
    "synonyms": [
      "NYADAL"
    ],
    "lId": "27906",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 62.8125,
      "lon": 17.952777777777776
    }
  },
  {
    "name": "Nybble Macken",
    "synonyms": [
      "NYBBLE MACKEN"
    ],
    "lId": "58192",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.100833333333334,
      "lon": 14.167222222222222
    }
  },
  {
    "name": "Nyborg Kalix",
    "synonyms": [
      "NYBORG KALIX"
    ],
    "lId": "14756",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 65.7875,
      "lon": 23.174722222222222
    }
  },
  {
    "name": "Nybro",
    "synonyms": [
      "NYBRO",
      "NYBRO STN"
    ],
    "lId": "00189",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 56.742222222222225,
      "lon": 15.909166666666668
    }
  },
  {
    "name": "Nybrostrand",
    "synonyms": [
      "NYBROSTRAND",
      "NYBROSTRAND BAD"
    ],
    "lId": "01198",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 55.43194444444444,
      "lon": 13.947222222222223
    }
  },
  {
    "name": "Nye",
    "synonyms": [
      "NYE"
    ],
    "lId": "11144",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 57.34277777777778,
      "lon": 15.278611111111111
    }
  },
  {
    "name": "Nyhammar torget",
    "synonyms": [
      "NYHAMMAR TORGET"
    ],
    "lId": "00649",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 60.29194444444444,
      "lon": 14.969722222222222
    }
  },
  {
    "name": "Nyhamnsläge centrum",
    "synonyms": [
      "NYHAMNSLÄGE CENTRUM",
      "NYHAMNSLÄGE CM",
      "NYHAMNSLÆGE CENTRUM",
      "NYHAMNSLÆGE CM"
    ],
    "lId": "16799",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 56.24166666666667,
      "lon": 12.539722222222222
    }
  },
  {
    "name": "Nyhem",
    "synonyms": [
      "NYHEM"
    ],
    "lId": "13256",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 62.888333333333335,
      "lon": 15.61
    }
  },
  {
    "name": "Nyhyttan bron",
    "synonyms": [
      "NYHYTTAN BRON"
    ],
    "lId": "24424",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.67527777777777,
      "lon": 14.815833333333334
    }
  },
  {
    "name": "Nykil kyrka",
    "synonyms": [
      "NYKIL KYRKA"
    ],
    "lId": "11148",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 58.28805555555555,
      "lon": 15.448611111111111
    }
  },
  {
    "name": "Nykroppa station",
    "synonyms": [
      "NYKROPPA STATION",
      "NYKROPPA STN"
    ],
    "lId": "00816",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.62361111111111,
      "lon": 14.307222222222222
    }
  },
  {
    "name": "Nykvarn",
    "synonyms": [
      "NYKVARN",
      "NYKVARN STN"
    ],
    "lId": "00149",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.17916666666667,
      "lon": 17.430833333333336
    }
  },
  {
    "name": "Nykyrka skolan",
    "synonyms": [
      "NYKYRKA SKOLAN"
    ],
    "lId": "11150",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 58.62361111111111,
      "lon": 14.970833333333333
    }
  },
  {
    "name": "Nyköping C",
    "synonyms": [
      "NYKOPING C",
      "NYKÖPING C",
      "NYKØPING C"
    ],
    "lId": "00050",
    "prio": 1,
    "pId": "074",
    "pos": {
      "lat": 58.75555555555555,
      "lon": 16.994722222222222
    }
  },
  {
    "name": "Nyland station",
    "synonyms": [
      "NYLAND STATION",
      "NYLAND STN"
    ],
    "lId": "00275",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 63.005833333333335,
      "lon": 17.761666666666667
    }
  },
  {
    "name": "Nymölla centrumhuset",
    "synonyms": [
      "NYMÖLLA CENTRUMHUSET",
      "NYMÖLLA CM-HUS",
      "NYMØLLA CENTRUMHUSET",
      "NYMØLLA CM-HUS"
    ],
    "lId": "11152",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 56.040277777777774,
      "lon": 14.465277777777777
    }
  },
  {
    "name": "Nynäs Havsbad",
    "synonyms": [
      "NYNÄS HAVSBAD",
      "NYNÆS HAVSBAD"
    ],
    "lId": "30035",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 58.89666666666667,
      "lon": 17.941944444444445
    }
  },
  {
    "name": "Nynäsgård",
    "synonyms": [
      "NYNÄSGÅRD",
      "NYNÄSGÅRD STN",
      "NYNÆSGÅRD",
      "NYNÆSGÅRD STN"
    ],
    "lId": "30036",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 58.913333333333334,
      "lon": 17.9425
    }
  },
  {
    "name": "Nynäshamn",
    "synonyms": [
      "NYNÄSHAMN",
      "NYNÄSHAMN STN",
      "NYNÆSHAMN",
      "NYNÆSHAMN STN"
    ],
    "lId": "00727",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 58.901111111111106,
      "lon": 17.95111111111111
    }
  },
  {
    "name": "Nysäter",
    "synonyms": [
      "NYSÄTER",
      "NYSÄTER BSTN",
      "NYSÆTER",
      "NYSÆTER BSTN"
    ],
    "lId": "00818",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.2825,
      "lon": 12.774166666666668
    }
  },
  {
    "name": "Nysättra",
    "synonyms": [
      "NYSÄTTRA",
      "NYSÄTTRA BYLVSK",
      "NYSÆTTRA",
      "NYSÆTTRA BYLVSK"
    ],
    "lId": "20571",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.82027777777778,
      "lon": 18.903055555555554
    }
  },
  {
    "name": "Nyåker Affären",
    "synonyms": [
      "NYÅKER AFFÄREN",
      "NYÅKER AFFÆREN"
    ],
    "lId": "00248",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 63.76694444444444,
      "lon": 19.309444444444445
    }
  },
  {
    "name": "Nås Centrum",
    "synonyms": [
      "NÅS CENTRUM"
    ],
    "lId": "34323",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 60.45388888888889,
      "lon": 14.496388888888887
    }
  },
  {
    "name": "Nåttarö brygga",
    "synonyms": [
      "NÅTTARÖ BRYGGA",
      "NÅTTARØ BRYGGA"
    ],
    "lId": "24875",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 58.88111111111111,
      "lon": 18.110555555555557
    }
  },
  {
    "name": "Näckrosen T-bana",
    "synonyms": [
      "NÄCKROSEN T-BANA",
      "NÆCKROSEN T-BANA"
    ],
    "lId": "21668",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.36666666666667,
      "lon": 17.983055555555556
    }
  },
  {
    "name": "Nälden ICA",
    "synonyms": [
      "NÄLDEN ICA",
      "NÆLDEN ICA"
    ],
    "lId": "13423",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 63.34777777777778,
      "lon": 14.253333333333334
    }
  },
  {
    "name": "Näsby Allé",
    "synonyms": [
      "NÄSBY ALLE",
      "NÄSBY ALLÉ",
      "NÄSBY ALLÉ STN",
      "NÆSBY ALLE",
      "NÆSBY ALLÉ",
      "NÆSBY ALLÉ STN"
    ],
    "lId": "20869",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.42722222222222,
      "lon": 18.085277777777776
    }
  },
  {
    "name": "Näsbypark",
    "synonyms": [
      "NÄSBYPARK",
      "NÄSBYPARK STN",
      "NÆSBYPARK",
      "NÆSBYPARK STN"
    ],
    "lId": "01052",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.43055555555555,
      "lon": 18.09611111111111
    }
  },
  {
    "name": "Nässjö C",
    "synonyms": [
      "NASSJO C",
      "NÄSSJÖ C",
      "NÆSSJØ C"
    ],
    "lId": "00140",
    "prio": 1,
    "pId": "074",
    "pos": {
      "lat": 57.65222222222222,
      "lon": 14.693888888888889
    }
  },
  {
    "name": "Näsum kyrka",
    "synonyms": [
      "NÄSUM KYRKA",
      "NÆSUM KYRKA"
    ],
    "lId": "24868",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 56.17055555555555,
      "lon": 14.498333333333333
    }
  },
  {
    "name": "Näsviken centrum",
    "synonyms": [
      "NÄSVIKEN CENTRUM",
      "NÄSVIKEN CM",
      "NÆSVIKEN",
      "NÆSVIKEN CM"
    ],
    "lId": "00485",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 61.756388888888885,
      "lon": 16.866666666666667
    }
  },
  {
    "name": "Näsåker",
    "synonyms": [
      "NÄSÅKER",
      "NÄSÅKER BSTN",
      "NÆSÅKER",
      "NÆSÅKER BSTN"
    ],
    "lId": "00535",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 63.440555555555555,
      "lon": 16.90694444444444
    }
  },
  {
    "name": "Näsänget",
    "synonyms": [
      "NÄSÄNGET",
      "NÆSÆNGET"
    ],
    "lId": "15250",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 62.88361111111111,
      "lon": 18.396666666666665
    }
  },
  {
    "name": "Nättraby",
    "synonyms": [
      "NÄTTRABY",
      "NÄTTRABY HÖRNET",
      "NÆTTRABY",
      "NÆTTRABY HØRNET"
    ],
    "lId": "00564",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 56.20666666666667,
      "lon": 15.530555555555557
    }
  },
  {
    "name": "Nävekvarn",
    "synonyms": [
      "NÄVEKVARN",
      "NÆVEKVARN"
    ],
    "lId": "11167",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 58.63055555555555,
      "lon": 16.800555555555555
    }
  },
  {
    "name": "Nävragöl",
    "synonyms": [
      "NÄVRAGÖL",
      "NÆVRAGØL"
    ],
    "lId": "11168",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 56.37416666666667,
      "lon": 15.567499999999999
    }
  },
  {
    "name": "Nöbbele",
    "synonyms": [
      "NÖBBELE",
      "NÖBBELE SOLVALL",
      "NØBBELE",
      "NØBBELE SOLVALL"
    ],
    "lId": "01489",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 56.684999999999995,
      "lon": 15.036388888888888
    }
  },
  {
    "name": "Nödinge station",
    "synonyms": [
      "NÖDINGE STATION",
      "NÖDINGE STN",
      "NØDINGE",
      "NØDINGE STN"
    ],
    "lId": "00081",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 57.893055555555556,
      "lon": 12.044444444444444
    }
  },
  {
    "name": "Nörreport",
    "synonyms": [
      "NOERREPORT",
      "NÖRREPORT",
      "NØRREPORT"
    ],
    "lId": "00646",
    "prio": 0,
    "pId": "086",
    "pos": {
      "lat": 55.68277777777777,
      "lon": 12.571111111111112
    }
  },
  {
    "name": "Nässundet",
    "synonyms": [
      "NÄSSUNDET",
      "NÄSSUNDET STN",
      "NÆSSUNDET",
      "NÆSSUNDET STN"
    ],
    "lId": "11161",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.43833333333333,
      "lon": 14.234166666666665
    }
  },
  {
    "name": "Obbola centralhållplats",
    "synonyms": [
      "OBBOLA CENTRALHÅLLPLATS",
      "OBBOLA CENTRUM"
    ],
    "lId": "00390",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 63.70138888888889,
      "lon": 20.319166666666668
    }
  },
  {
    "name": "Ockelbo",
    "synonyms": [
      "OCKELBO",
      "OCKELBO STN"
    ],
    "lId": "00277",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 60.89111111111111,
      "lon": 16.72083333333333
    }
  },
  {
    "name": "Odenplan T-bana",
    "synonyms": [
      "ODENPLAN T-BANA"
    ],
    "lId": "21013",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.34277777777778,
      "lon": 18.049444444444447
    }
  },
  {
    "name": "Odensbacken",
    "synonyms": [
      "ODENSBACKEN",
      "ODENSBACKN SKOL"
    ],
    "lId": "00795",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.157777777777774,
      "lon": 15.526666666666667
    }
  },
  {
    "name": "Olberga Surahammar",
    "synonyms": [
      "OLBERGA SURAHAMMAR"
    ],
    "lId": "04340",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.684999999999995,
      "lon": 16.20638888888889
    }
  },
  {
    "name": "Olberga Tumba",
    "synonyms": [
      "OLBERGA TUMBA"
    ],
    "lId": "69124",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.11138888888889,
      "lon": 17.74138888888889
    }
  },
  {
    "name": "Oleby",
    "synonyms": [
      "OLEBY"
    ],
    "lId": "01411",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 60.12972222222222,
      "lon": 13.038333333333334
    }
  },
  {
    "name": "Olofstorp",
    "synonyms": [
      "OLOFSTORP"
    ],
    "lId": "15587",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 57.805277777777775,
      "lon": 12.169444444444444
    }
  },
  {
    "name": "Olofström Bussterminal",
    "synonyms": [
      "OLOFSTRÖM BUSSTERMINAL",
      "OLOFSTRØM BUSSTERMINAL"
    ],
    "lId": "11176",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 56.276666666666664,
      "lon": 14.53277777777778
    }
  },
  {
    "name": "Olovslund",
    "synonyms": [
      "OLOVSLUND"
    ],
    "lId": "24819",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.32777777777778,
      "lon": 17.935
    }
  },
  {
    "name": "Olseröd Olserödsvägen",
    "synonyms": [
      "OLSERÖD OLSERDV",
      "OLSERÖD OLSERÖDSVÄGEN",
      "OLSERØD OLSERØDSVÆGEN"
    ],
    "lId": "30767",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 55.797777777777775,
      "lon": 14.147777777777778
    }
  },
  {
    "name": "Olsfors",
    "synonyms": [
      "OLSFORS"
    ],
    "lId": "12384",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 57.69083333333333,
      "lon": 12.70111111111111
    }
  },
  {
    "name": "Olshammar",
    "synonyms": [
      "OLSHAMMAR",
      "OLSHAMMAR BOCKS"
    ],
    "lId": "01262",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 58.756388888888885,
      "lon": 14.7975
    }
  },
  {
    "name": "Ombenning norra",
    "synonyms": [
      "OMBENNING NORRA"
    ],
    "lId": "11179",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.98083333333334,
      "lon": 15.954166666666666
    }
  },
  {
    "name": "Omne",
    "synonyms": [
      "OMNE"
    ],
    "lId": "15401",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 62.94888888888889,
      "lon": 18.362222222222222
    }
  },
  {
    "name": "Onsala kyrka",
    "synonyms": [
      "ONSALA",
      "ONSALA KYRKA"
    ],
    "lId": "00092",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 57.41305555555555,
      "lon": 12.020555555555557
    }
  },
  {
    "name": "Onslunda busstation",
    "synonyms": [
      "ONSLUNDA BSTN",
      "ONSLUNDA BUSSTATION"
    ],
    "lId": "11180",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 55.59861111111111,
      "lon": 14.052777777777779
    }
  },
  {
    "name": "Ope skola",
    "synonyms": [
      "OPE SKOLA"
    ],
    "lId": "25926",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 63.13027777777778,
      "lon": 14.766388888888889
    }
  },
  {
    "name": "Opphem",
    "synonyms": [
      "OPPHEM",
      "OPPHEM STN"
    ],
    "lId": "01263",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 58.14694444444444,
      "lon": 15.726666666666667
    }
  },
  {
    "name": "Oppmanna Kyrkväg",
    "synonyms": [
      "OPPMANNA KYRKVÄG",
      "OPPMANNA KYRKVÆG"
    ],
    "lId": "04129",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 56.15222222222222,
      "lon": 14.305833333333334
    }
  },
  {
    "name": "Ormaryd",
    "synonyms": [
      "ORMARYD",
      "ORMARYD STN"
    ],
    "lId": "00547",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 57.664722222222224,
      "lon": 14.833055555555555
    }
  },
  {
    "name": "Orminge",
    "synonyms": [
      "ORMINGE",
      "ORMINGE CENTRUM"
    ],
    "lId": "00730",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.32611111111112,
      "lon": 18.258333333333333
    }
  },
  {
    "name": "Ormsta",
    "synonyms": [
      "ORMSTA",
      "ORMSTA STN"
    ],
    "lId": "20112",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.545833333333334,
      "lon": 18.079444444444444
    }
  },
  {
    "name": "Ornäs",
    "synonyms": [
      "ORNÄS",
      "ORNÄS KIOSKEN",
      "ORNÆS",
      "ORNÆS KIOSKEN"
    ],
    "lId": "01264",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 60.51,
      "lon": 15.540833333333333
    }
  },
  {
    "name": "Orrefors",
    "synonyms": [
      "ORREFORS",
      "ORREFORS CM"
    ],
    "lId": "00929",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 56.83833333333334,
      "lon": 15.749444444444444
    }
  },
  {
    "name": "Orresta",
    "synonyms": [
      "ORRESTA"
    ],
    "lId": "11183",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.66111111111111,
      "lon": 16.834444444444443
    }
  },
  {
    "name": "Orrviken",
    "synonyms": [
      "ORRVIKEN"
    ],
    "lId": "13368",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 63.10638888888889,
      "lon": 14.438055555555556
    }
  },
  {
    "name": "Orsa busstation",
    "synonyms": [
      "ORSA BSTN",
      "ORSA BUSSTATION"
    ],
    "lId": "24261",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 61.117777777777775,
      "lon": 14.619722222222222
    }
  },
  {
    "name": "Orsta",
    "synonyms": [
      "ORSTA"
    ],
    "lId": "29041",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 62.92527777777777,
      "lon": 18.351944444444445
    }
  },
  {
    "name": "Osby",
    "synonyms": [
      "OSBY",
      "OSBY STN"
    ],
    "lId": "00295",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 56.37972222222222,
      "lon": 13.994166666666667
    }
  },
  {
    "name": "Osbyholm",
    "synonyms": [
      "OSBYHOLM"
    ],
    "lId": "16803",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 55.848888888888894,
      "lon": 13.606666666666666
    }
  },
  {
    "name": "Oskar-Fredriksborg",
    "synonyms": [
      "OSKAR FREDRIKSB",
      "OSKAR-FREDRIKSB",
      "OSKAR-FREDRIKSBORG"
    ],
    "lId": "18088",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.395833333333336,
      "lon": 18.44
    }
  },
  {
    "name": "Oskarshamn busstation",
    "synonyms": [
      "OSKARSHAMN BSTN",
      "OSKARSHAMN BUSSTATION"
    ],
    "lId": "14315",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 57.26361111111111,
      "lon": 16.445555555555554
    }
  },
  {
    "name": "Oskarshamn Gotlandsterminalen",
    "synonyms": [
      "OSKARSHAMN GOTL",
      "OSKARSHAMN GOTLANDSTERMINALEN"
    ],
    "lId": "20392",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 57.26305555555555,
      "lon": 16.45888888888889
    }
  },
  {
    "name": "Oskarshamn station",
    "synonyms": [
      "OSKARSHAMN STATION",
      "OSKARSHAMN STN"
    ],
    "lId": "00213",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 57.26305555555555,
      "lon": 16.4575
    }
  },
  {
    "name": "Oskarström station",
    "synonyms": [
      "OSKARSTRÖM STATION",
      "OSKARSTRÖM STN",
      "OSKARSTRØM STATION",
      "OSKARSTRØM STN"
    ],
    "lId": "00313",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 56.80638888888888,
      "lon": 12.971944444444444
    }
  },
  {
    "name": "Oslo S",
    "synonyms": [
      "OSLO S",
      "XZO"
    ],
    "lId": "00100",
    "prio": 1,
    "pId": "076",
    "pos": {
      "lat": 59.91027777777778,
      "lon": 10.755277777777778
    }
  },
  {
    "name": "Oslo Bussterminal",
    "synonyms": [
      "OSLO BUSSTERMINAL"
    ],
    "lId": "90001",
    "prio": 0,
    "pId": "076",
    "pos": {
      "lat": 0,
      "lon": 0
    }
  },
  {
    "name": "Ottebol",
    "synonyms": [
      "OTTEBOL",
      "OTTEBOL STN"
    ],
    "lId": "00359",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.69583333333333,
      "lon": 12.469722222222222
    }
  },
  {
    "name": "Ottenby",
    "synonyms": [
      "OTTENBY"
    ],
    "lId": "01004",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 56.23444444444444,
      "lon": 16.41583333333333
    }
  },
  {
    "name": "Otterbäcken Badängen",
    "synonyms": [
      "OTTERBÄCKEN BADÄNGEN",
      "OTTERBÆCKEN BADÆNGEN"
    ],
    "lId": "11191",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 58.94416666666666,
      "lon": 14.039722222222222
    }
  },
  {
    "name": "Otterbäcken väg 26",
    "synonyms": [
      "OTTERBÄCKEN VÄG 26"
    ],
    "lId": "16443",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 58.95638888888889,
      "lon": 14.056944444444445
    }
  },
  {
    "name": "Otterstad",
    "synonyms": [
      "OTTERSTAD"
    ],
    "lId": "01208",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 58.654444444444444,
      "lon": 13.165277777777778
    }
  },
  {
    "name": "Ottsjö",
    "synonyms": [
      "OTTSJÖ",
      "OTTSJØ"
    ],
    "lId": "01266",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 63.21555555555556,
      "lon": 13.06027777777778
    }
  },
  {
    "name": "Ottsjö vägskäl",
    "synonyms": [
      "OTTSJÖ VÄGSKÄL"
    ],
    "lId": "17661",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 63.22805555555556,
      "lon": 13.159444444444444
    }
  },
  {
    "name": "Ovanåker",
    "synonyms": [
      "OVANÅKER"
    ],
    "lId": "25943",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 61.362500000000004,
      "lon": 15.895833333333332
    }
  },
  {
    "name": "Ovesholm",
    "synonyms": [
      "OVESHOLM"
    ],
    "lId": "04119",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 55.99333333333333,
      "lon": 14.036388888888888
    }
  },
  {
    "name": "Oviken",
    "synonyms": [
      "OVIKEN"
    ],
    "lId": "13373",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 62.99638888888889,
      "lon": 14.394444444444444
    }
  },
  {
    "name": "Oxberg",
    "synonyms": [
      "OXBERG"
    ],
    "lId": "01267",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 61.11638888888889,
      "lon": 14.173333333333332
    }
  },
  {
    "name": "Oxelösund",
    "synonyms": [
      "OXELOSUND",
      "OXELÖSUND",
      "OXELÖSUND CM",
      "OXELØSUND",
      "OXELØSUND CM"
    ],
    "lId": "00249",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 58.66916666666666,
      "lon": 17.103611111111114
    }
  },
  {
    "name": "Oxie",
    "synonyms": [
      "OXIE",
      "OXIE STN"
    ],
    "lId": "20760",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 55.54138888888889,
      "lon": 13.096111111111112
    }
  },
  {
    "name": "Pajala",
    "synonyms": [
      "PAJALA",
      "PAJALA BSTN"
    ],
    "lId": "00885",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 67.21083333333334,
      "lon": 23.365555555555556
    }
  },
  {
    "name": "Partille",
    "synonyms": [
      "PARTILLE",
      "PARTILLE STN"
    ],
    "lId": "00132",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 57.740833333333335,
      "lon": 12.102777777777778
    }
  },
  {
    "name": "Pauliström",
    "synonyms": [
      "PAULISTRÖM",
      "PAULISTRØM"
    ],
    "lId": "11195",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 57.467222222222226,
      "lon": 15.507777777777777
    }
  },
  {
    "name": "Pello",
    "synonyms": [
      "PELLO",
      "PELLO PELLOHALL"
    ],
    "lId": "00749",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 66.80277777777778,
      "lon": 23.978888888888886
    }
  },
  {
    "name": "Penningby slott",
    "synonyms": [
      "PENNINGBY SLOTT"
    ],
    "lId": "11196",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.680277777777775,
      "lon": 18.68277777777778
    }
  },
  {
    "name": "Persberg",
    "synonyms": [
      "PERSBERG",
      "PERSBERG STN"
    ],
    "lId": "01268",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.74888888888889,
      "lon": 14.237499999999999
    }
  },
  {
    "name": "Pershagen",
    "synonyms": [
      "PERSHAGEN",
      "PERSHAGEN HAGKV"
    ],
    "lId": "01186",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.15277777777778,
      "lon": 17.65694444444444
    }
  },
  {
    "name": "Perstorp",
    "synonyms": [
      "PERSTORP",
      "PERSTORP STN"
    ],
    "lId": "00022",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 56.13611111111111,
      "lon": 13.396944444444443
    }
  },
  {
    "name": "Persön",
    "synonyms": [
      "PERSÖN",
      "PERSÖN KAFFE E4",
      "PERSØN",
      "PERSØN KAFFE E4"
    ],
    "lId": "14864",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 65.74694444444445,
      "lon": 22.17
    }
  },
  {
    "name": "Petersburg",
    "synonyms": [
      "PETERSBURG"
    ],
    "lId": "11201",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 56.751666666666665,
      "lon": 13.595833333333333
    }
  },
  {
    "name": "Pilgrimstad",
    "synonyms": [
      "PILGRIMSTAD"
    ],
    "lId": "00653",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 62.955000000000005,
      "lon": 15.04
    }
  },
  {
    "name": "Piteå",
    "synonyms": [
      "PITEA",
      "PITEÅ",
      "PITEÅ BSTN"
    ],
    "lId": "00571",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 65.31972222222223,
      "lon": 21.473333333333333
    }
  },
  {
    "name": "Porjus E45 ICA",
    "synonyms": [
      "PORJUS E45 ICA"
    ],
    "lId": "14704",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 66.96000000000001,
      "lon": 19.82111111111111
    }
  },
  {
    "name": "Prästmon Korsningen",
    "synonyms": [
      "PRÄSTMON KORSNINGEN",
      "PRÆSTMON KORSNINGEN"
    ],
    "lId": "15260",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 63.07805555555556,
      "lon": 17.753055555555555
    }
  },
  {
    "name": "Pukavik",
    "synonyms": [
      "PUKAVIK"
    ],
    "lId": "11205",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 56.163333333333334,
      "lon": 14.680277777777777
    }
  },
  {
    "name": "Påarp",
    "synonyms": [
      "PAARP",
      "PÅARP",
      "PÅARP STN"
    ],
    "lId": "00520",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 56.02916666666667,
      "lon": 12.816944444444443
    }
  },
  {
    "name": "Pålsboda",
    "synonyms": [
      "PÅLSBODA",
      "PÅLSBODA N BANG"
    ],
    "lId": "00796",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.06444444444444,
      "lon": 15.340555555555556
    }
  },
  {
    "name": "Påryd",
    "synonyms": [
      "PÅRYD"
    ],
    "lId": "14328",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 56.566944444444445,
      "lon": 15.920833333333333
    }
  },
  {
    "name": "Påskallavik",
    "synonyms": [
      "PÅSKALLAVIK",
      "PÅSKALLAVIK CM"
    ],
    "lId": "00930",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 57.16611111111111,
      "lon": 16.45888888888889
    }
  },
  {
    "name": "Raade",
    "synonyms": [
      "RAADE",
      "RÅDE"
    ],
    "lId": "00519",
    "prio": 0,
    "pId": "076",
    "pos": {
      "lat": 59.33083333333334,
      "lon": 10.905000000000001
    }
  },
  {
    "name": "Rabbalshede",
    "synonyms": [
      "RABBALSHEDE",
      "RABBALSHEDE STN"
    ],
    "lId": "00299",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 58.61,
      "lon": 11.470555555555556
    }
  },
  {
    "name": "Rabo",
    "synonyms": [
      "RABO"
    ],
    "lId": "21447",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.29361111111111,
      "lon": 16.04527777777778
    }
  },
  {
    "name": "Raggarön",
    "synonyms": [
      "RAGGARÖN",
      "RAGGARØN"
    ],
    "lId": "12752",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 60.19972222222222,
      "lon": 18.58861111111111
    }
  },
  {
    "name": "Ragunda vägskäl",
    "synonyms": [
      "RAGUNDA VÄGSKÄL",
      "RAGUNDA VÆGSKÆL"
    ],
    "lId": "28014",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 63.06027777777778,
      "lon": 16.398611111111112
    }
  },
  {
    "name": "Ramdala Tornbyvägen",
    "synonyms": [
      "RAMDALA TORNBYVÄGEN",
      "RAMDALA TORNBYVÆGEN"
    ],
    "lId": "11210",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 56.184999999999995,
      "lon": 15.76361111111111
    }
  },
  {
    "name": "Ramkvilla",
    "synonyms": [
      "RAMKVILLA"
    ],
    "lId": "01269",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 57.20388888888889,
      "lon": 14.952777777777778
    }
  },
  {
    "name": "Ramlösa",
    "synonyms": [
      "RAMLOSA",
      "RAMLÖSA",
      "RAMLÖSA STN",
      "RAMLØSA",
      "RAMLØSA STN"
    ],
    "lId": "01270",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 56.0225,
      "lon": 12.72861111111111
    }
  },
  {
    "name": "Ramnäs",
    "synonyms": [
      "RAMNAS",
      "RAMNÄS",
      "RAMNÄS STN",
      "RAMNÆS",
      "RAMNÆS STN"
    ],
    "lId": "00046",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.76972222222222,
      "lon": 16.208055555555553
    }
  },
  {
    "name": "Ramnäs Centrum",
    "synonyms": [
      "RAMNÄS CENTRUM"
    ],
    "lId": "44884",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.775277777777774,
      "lon": 16.19361111111111
    }
  },
  {
    "name": "Ramsberg Bruket",
    "synonyms": [
      "RAMSBERG BRUKET"
    ],
    "lId": "21086",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.76833333333333,
      "lon": 15.312222222222223
    }
  },
  {
    "name": "Ramsele",
    "synonyms": [
      "RAMSELE",
      "RAMSELE BSTN"
    ],
    "lId": "00411",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 63.536944444444444,
      "lon": 16.46944444444444
    }
  },
  {
    "name": "Ramsjö affären",
    "synonyms": [
      "RAMSJÖ AFFÄREN",
      "RAMSJØ AFFÆREN"
    ],
    "lId": "11219",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 62.183055555555555,
      "lon": 15.649166666666666
    }
  },
  {
    "name": "Ramsta kyrka",
    "synonyms": [
      "RAMSTA KYRKA"
    ],
    "lId": "12824",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.7925,
      "lon": 17.438333333333333
    }
  },
  {
    "name": "Ramundberget",
    "synonyms": [
      "RAMUNDBERGET"
    ],
    "lId": "00506",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 62.700833333333335,
      "lon": 12.38861111111111
    }
  },
  {
    "name": "Ramvik",
    "synonyms": [
      "RAMVIK"
    ],
    "lId": "00413",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 62.81861111111112,
      "lon": 17.854444444444447
    }
  },
  {
    "name": "Ransby",
    "synonyms": [
      "RANSBY",
      "RANSBY HANDEL"
    ],
    "lId": "01272",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 60.67583333333333,
      "lon": 12.946666666666667
    }
  },
  {
    "name": "Ransta",
    "synonyms": [
      "RANSTA",
      "RANSTA STN"
    ],
    "lId": "00679",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.809999999999995,
      "lon": 16.64
    }
  },
  {
    "name": "Ransäter",
    "synonyms": [
      "RANSÄTER",
      "RANSÄTER KYRKA",
      "RANSÆTER",
      "RANSÆTER KYRKA"
    ],
    "lId": "01273",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.77055555555555,
      "lon": 13.449722222222222
    }
  },
  {
    "name": "Rasbo kyrka",
    "synonyms": [
      "RASBO KYRKA"
    ],
    "lId": "12813",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.950833333333335,
      "lon": 17.878055555555555
    }
  },
  {
    "name": "Rautas",
    "synonyms": [
      "RAUTAS",
      "RAUTAS STN"
    ],
    "lId": "00193",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 67.99361111111111,
      "lon": 19.895833333333332
    }
  },
  {
    "name": "Ravlunda kyrkan",
    "synonyms": [
      "RAVLUNDA KYRKAN"
    ],
    "lId": "31154",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 55.715,
      "lon": 14.153055555555556
    }
  },
  {
    "name": "Reftele",
    "synonyms": [
      "REFTELE",
      "REFTELE STN"
    ],
    "lId": "00212",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 57.17611111111111,
      "lon": 13.593055555555557
    }
  },
  {
    "name": "Reimersholme",
    "synonyms": [
      "REIMERSHOLME"
    ],
    "lId": "46222",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.31777777777778,
      "lon": 18.020833333333332
    }
  },
  {
    "name": "Rejmyre",
    "synonyms": [
      "REJMYRE",
      "REJMYRE VÄNDPL",
      "REJMYRE VÆNDPL"
    ],
    "lId": "00855",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 58.831944444444446,
      "lon": 15.924999999999999
    }
  },
  {
    "name": "Rengsjö Ringshög",
    "synonyms": [
      "RENGSJÖ RINGSHÖG",
      "RENGSJØ RINGSHØG"
    ],
    "lId": "25934",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 61.36416666666667,
      "lon": 16.61777777777778
    }
  },
  {
    "name": "Rensbyn",
    "synonyms": [
      "RENSBYN"
    ],
    "lId": "25301",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 60.49527777777778,
      "lon": 15.70111111111111
    }
  },
  {
    "name": "Rensjön",
    "synonyms": [
      "RENSJON",
      "RENSJÖN",
      "RENSJÖN STN",
      "RENSJØN",
      "RENSJØN STN"
    ],
    "lId": "00137",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 68.07194444444444,
      "lon": 19.826944444444443
    }
  },
  {
    "name": "Resarö",
    "synonyms": [
      "RESARÖ",
      "RESARÖ YTTERBY",
      "RESARØ",
      "RESARØ YTTERBY"
    ],
    "lId": "01275",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.428888888888885,
      "lon": 18.335833333333333
    }
  },
  {
    "name": "Reutersberg",
    "synonyms": [
      "REUTERSBERG"
    ],
    "lId": "45184",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.405833333333334,
      "lon": 15.983333333333333
    }
  },
  {
    "name": "Revingeby station",
    "synonyms": [
      "REVINGEBY STATION",
      "REVINGEBY STN"
    ],
    "lId": "11228",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 55.723333333333336,
      "lon": 13.461666666666666
    }
  },
  {
    "name": "Revsudden",
    "synonyms": [
      "REVSUDDEN"
    ],
    "lId": "14475",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 56.776666666666664,
      "lon": 16.47861111111111
    }
  },
  {
    "name": "Riala kyrka",
    "synonyms": [
      "RIALA KYRKA"
    ],
    "lId": "11230",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.63055555555555,
      "lon": 18.51972222222222
    }
  },
  {
    "name": "Rickarum skolan",
    "synonyms": [
      "RICKARUM SKOLAN"
    ],
    "lId": "04121",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 55.994166666666665,
      "lon": 13.8225
    }
  },
  {
    "name": "Riddarhyttan",
    "synonyms": [
      "RIDDARHYTTAN",
      "RIDDARHYTTAN IP"
    ],
    "lId": "11232",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.81055555555555,
      "lon": 15.558611111111112
    }
  },
  {
    "name": "Riksgränsen",
    "synonyms": [
      "RIKSGRANSEN",
      "RIKSGRÄNSEN",
      "RIKSGRÄNSEN STN",
      "RIKSGRÆNSEN",
      "RIKSGRÆNSEN STN"
    ],
    "lId": "00229",
    "prio": 1,
    "pId": "074",
    "pos": {
      "lat": 68.42555555555556,
      "lon": 18.127222222222223
    }
  },
  {
    "name": "Rimbo",
    "synonyms": [
      "RIMBO",
      "RIMBO BSTN"
    ],
    "lId": "00666",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.743611111111115,
      "lon": 18.36861111111111
    }
  },
  {
    "name": "Rimforsa",
    "synonyms": [
      "RIMFORSA",
      "RIMFORSA STN"
    ],
    "lId": "00365",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 58.13527777777778,
      "lon": 15.681666666666667
    }
  },
  {
    "name": "Rindö",
    "synonyms": [
      "RINDÖ",
      "RINDÖ SMEDJA",
      "RINDØ",
      "RINDØ SMEDJA"
    ],
    "lId": "01276",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.40361111111111,
      "lon": 18.365000000000002
    }
  },
  {
    "name": "Ringarum",
    "synonyms": [
      "RINGARUM",
      "RINGARUM CM"
    ],
    "lId": "00551",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 58.333333333333336,
      "lon": 16.44472222222222
    }
  },
  {
    "name": "Ringhals",
    "synonyms": [
      "RINGHALS"
    ],
    "lId": "17144",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 57.25694444444444,
      "lon": 12.1175
    }
  },
  {
    "name": "Ringsegård",
    "synonyms": [
      "RINGSEGÅRD"
    ],
    "lId": "17145",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 56.87,
      "lon": 12.54861111111111
    }
  },
  {
    "name": "Ringvägen station",
    "synonyms": [
      "RINGVÄGEN STATION",
      "RINGVÄGEN STN",
      "RINGVÆGEN STATION",
      "RINGVÆGEN STN"
    ],
    "lId": "24811",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.283055555555556,
      "lon": 18.301944444444445
    }
  },
  {
    "name": "Rinkaby Skjutfältsvägen",
    "synonyms": [
      "RINKABY SKJUTFV",
      "RINKABY SKJUTFÄLTSVÄGEN",
      "RINKABY SKJUTFÆLTSVÆGEN"
    ],
    "lId": "27544",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 55.98027777777778,
      "lon": 14.271944444444445
    }
  },
  {
    "name": "Rinkabyholm E22",
    "synonyms": [
      "RINKABYHOLM E22"
    ],
    "lId": "14333",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 56.651111111111106,
      "lon": 16.258055555555554
    }
  },
  {
    "name": "Rinkeby T-bana",
    "synonyms": [
      "RINKEBY T-BANA"
    ],
    "lId": "21679",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.38805555555555,
      "lon": 17.928611111111113
    }
  },
  {
    "name": "Rissna",
    "synonyms": [
      "RISSNA"
    ],
    "lId": "13297",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 63.05833333333333,
      "lon": 15.338055555555556
    }
  },
  {
    "name": "Rissne T-bana",
    "synonyms": [
      "RISSNE T-BANA"
    ],
    "lId": "21674",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.37583333333333,
      "lon": 17.939722222222223
    }
  },
  {
    "name": "Risögrund",
    "synonyms": [
      "RISÖGRUND",
      "RISØGRUND"
    ],
    "lId": "26990",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 65.8111111111111,
      "lon": 23.24277777777778
    }
  },
  {
    "name": "Ritsem",
    "synonyms": [
      "RITSEM",
      "RITSEM FJÄLLSTN",
      "RITSEM FJÆLLSTN"
    ],
    "lId": "00886",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 67.71888888888888,
      "lon": 17.47861111111111
    }
  },
  {
    "name": "Ronneby station",
    "synonyms": [
      "RONNEBY STATION",
      "RONNEBY STN"
    ],
    "lId": "00069",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 56.206944444444446,
      "lon": 15.28277777777778
    }
  },
  {
    "name": "Robertsfors",
    "synonyms": [
      "ROBERTSFORS",
      "ROBERTSFORS BST"
    ],
    "lId": "00391",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 64.19222222222223,
      "lon": 20.846944444444443
    }
  },
  {
    "name": "Rockhammar",
    "synonyms": [
      "ROCKHAMMAR"
    ],
    "lId": "11247",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.528055555555554,
      "lon": 15.449444444444445
    }
  },
  {
    "name": "Rockneby E22",
    "synonyms": [
      "ROCKNEBY E22"
    ],
    "lId": "14510",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 56.79666666666667,
      "lon": 16.355
    }
  },
  {
    "name": "Rocksjön",
    "synonyms": [
      "ROCKSJON",
      "ROCKSJÖN",
      "ROCKSJÖN STN",
      "ROCKSJØN",
      "ROCKSJØN STN"
    ],
    "lId": "01277",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 57.775277777777774,
      "lon": 14.198333333333334
    }
  },
  {
    "name": "Roknäs affär",
    "synonyms": [
      "ROKNÄS AFFÄR",
      "ROKNÆS AFFÆR"
    ],
    "lId": "23795",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 65.34638888888888,
      "lon": 21.17
    }
  },
  {
    "name": "Rolfstorp",
    "synonyms": [
      "ROLFSTORP"
    ],
    "lId": "11248",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 57.14472222222222,
      "lon": 12.452777777777778
    }
  },
  {
    "name": "Roma",
    "synonyms": [
      "ROMA",
      "ROMA PRESSBYRÅN"
    ],
    "lId": "00918",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 57.50527777777778,
      "lon": 18.454444444444444
    }
  },
  {
    "name": "Rombak",
    "synonyms": [
      "ROMBAK"
    ],
    "lId": "02404",
    "prio": 0,
    "pId": "076",
    "pos": {
      "lat": 68.4175,
      "lon": 17.779722222222222
    }
  },
  {
    "name": "Romme Alpin",
    "synonyms": [
      "ROMME ALPIN"
    ],
    "lId": "25265",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 60.38944444444444,
      "lon": 15.37888888888889
    }
  },
  {
    "name": "Ronneby flygplats",
    "synonyms": [
      "RONNEBY FLYGPLATS"
    ],
    "lId": "26045",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 56.25416666666667,
      "lon": 15.267222222222223
    }
  },
  {
    "name": "Ronnebyhamn",
    "synonyms": [
      "RONNEBYHAMN"
    ],
    "lId": "11252",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 56.17638888888889,
      "lon": 15.29861111111111
    }
  },
  {
    "name": "Ropsten T-bana",
    "synonyms": [
      "ROPSTEN T-BANA"
    ],
    "lId": "20757",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.35722222222223,
      "lon": 18.101944444444445
    }
  },
  {
    "name": "Rosersberg",
    "synonyms": [
      "ROSERSBERG",
      "ROSERSBERG STN"
    ],
    "lId": "00739",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.583333333333336,
      "lon": 17.879722222222224
    }
  },
  {
    "name": "Roslags Näsby",
    "synonyms": [
      "ROSLAGS NÄSBY",
      "ROSLAGS NÆSBY"
    ],
    "lId": "00740",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.434999999999995,
      "lon": 18.057222222222222
    }
  },
  {
    "name": "Roslagskulla",
    "synonyms": [
      "ROSLAGSKULLA",
      "ROSLAGSKULLA KA"
    ],
    "lId": "01325",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.55916666666666,
      "lon": 18.55888888888889
    }
  },
  {
    "name": "Rosshyttan",
    "synonyms": [
      "ROSSHYTTAN"
    ],
    "lId": "11256",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 60.06916666666667,
      "lon": 16.354166666666668
    }
  },
  {
    "name": "Rossön",
    "synonyms": [
      "ROSSÖN",
      "ROSSØN"
    ],
    "lId": "00527",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 63.92638888888889,
      "lon": 16.326944444444443
    }
  },
  {
    "name": "Rosvik",
    "synonyms": [
      "ROSVIK",
      "ROSVIK BYN OK"
    ],
    "lId": "01278",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 65.43583333333333,
      "lon": 21.690277777777776
    }
  },
  {
    "name": "Rosvik E4",
    "synonyms": [
      "ROSVIK E4",
      "ROSVIK E4 N VSK"
    ],
    "lId": "20148",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 65.45083333333334,
      "lon": 21.674444444444447
    }
  },
  {
    "name": "Rot",
    "synonyms": [
      "ROT"
    ],
    "lId": "13143",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 61.25555555555555,
      "lon": 14.034722222222221
    }
  },
  {
    "name": "Rotebro",
    "synonyms": [
      "ROTEBRO",
      "ROTEBRO STN"
    ],
    "lId": "00623",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.47638888888889,
      "lon": 17.914166666666667
    }
  },
  {
    "name": "Rottne Gullebovägen",
    "synonyms": [
      "ROTTNE GULLEBOVÄGEN"
    ],
    "lId": "00131",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 57.02111111111111,
      "lon": 14.892777777777777
    }
  },
  {
    "name": "Rottneros",
    "synonyms": [
      "ROTTNEROS"
    ],
    "lId": "00501",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.794999999999995,
      "lon": 13.12888888888889
    }
  },
  {
    "name": "Rottneros väg 45",
    "synonyms": [
      "ROTTNEROS V 45",
      "ROTTNEROS VÄG 45",
      "ROTTNEROS VÆG 45"
    ],
    "lId": "24498",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.79388888888889,
      "lon": 13.110555555555555
    }
  },
  {
    "name": "Ruda centrum",
    "synonyms": [
      "RUDA CENTRUM"
    ],
    "lId": "22547",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 57.108333333333334,
      "lon": 16.114722222222223
    }
  },
  {
    "name": "Rudboda torg",
    "synonyms": [
      "RUDBODA TORG"
    ],
    "lId": "24784",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.374722222222225,
      "lon": 18.17638888888889
    }
  },
  {
    "name": "Rudolf Steinerseminariet",
    "synonyms": [
      "RUDOLF STEINERSEMINARIET"
    ],
    "lId": "70054",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.06888888888889,
      "lon": 17.61722222222222
    }
  },
  {
    "name": "Rumskulla",
    "synonyms": [
      "RUMSKULLA"
    ],
    "lId": "14339",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 57.67333333333333,
      "lon": 15.592222222222222
    }
  },
  {
    "name": "Runemo",
    "synonyms": [
      "RUNEMO"
    ],
    "lId": "25937",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 61.35583333333334,
      "lon": 16.136388888888888
    }
  },
  {
    "name": "Rungsted Kyst",
    "synonyms": [
      "RUNGSTED KYST"
    ],
    "lId": "00663",
    "prio": 0,
    "pId": "086",
    "pos": {
      "lat": 55.882222222222225,
      "lon": 12.530833333333334
    }
  },
  {
    "name": "Runhällen",
    "synonyms": [
      "RUNHÄLLEN",
      "RUNHÆLLEN"
    ],
    "lId": "22073",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 60.025,
      "lon": 16.822777777777777
    }
  },
  {
    "name": "Runtuna Oskarshäll",
    "synonyms": [
      "RUNTUNA OSKARSHÄLL",
      "RUNTUNA OSKARSHÆLL"
    ],
    "lId": "25948",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 58.86805555555556,
      "lon": 17.068055555555556
    }
  },
  {
    "name": "Rutvik",
    "synonyms": [
      "RUTVIK",
      "RUTVIK BYAVÄGEN",
      "RUTVIK BYAVÆGEN"
    ],
    "lId": "20106",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 65.67,
      "lon": 22.083055555555557
    }
  },
  {
    "name": "Rutvik vägskäl E4",
    "synonyms": [
      "RUTVIK VSK E4",
      "RUTVIK VÄGSKÄL E4",
      "RUTVIK VÆGSKÆL E4"
    ],
    "lId": "20376",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 65.65833333333335,
      "lon": 22.104166666666668
    }
  },
  {
    "name": "Ryd",
    "synonyms": [
      "RYD",
      "RYD BSTN"
    ],
    "lId": "00134",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 56.46194444444445,
      "lon": 14.692777777777778
    }
  },
  {
    "name": "Rydaholm",
    "synonyms": [
      "RYDAHOLM",
      "RYDAHOLM STN"
    ],
    "lId": "00342",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 56.986111111111114,
      "lon": 14.311388888888889
    }
  },
  {
    "name": "Rydbo",
    "synonyms": [
      "RYDBO",
      "RYDBO STN"
    ],
    "lId": "20871",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.46527777777778,
      "lon": 18.18305555555556
    }
  },
  {
    "name": "Rydbo Kulla vägskäl",
    "synonyms": [
      "RYDBO KULLA VSK",
      "RYDBO KULLA VÄGSKÄL"
    ],
    "lId": "24350",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.44972222222222,
      "lon": 18.215555555555554
    }
  },
  {
    "name": "Rydboholm Ängsjöparken",
    "synonyms": [
      "RYDBOHOLM ÄNGSJÖPARKEN",
      "RYDBOHOLM ÄNGSP",
      "RYDBOHOLM ÆNGSJØPARKEN",
      "RYDBOHOLM ÆNGSP"
    ],
    "lId": "25946",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 57.65472222222222,
      "lon": 12.884166666666665
    }
  },
  {
    "name": "Rydebäck",
    "synonyms": [
      "RYDEBÄCK",
      "RYDEBÆCK"
    ],
    "lId": "01557",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 55.965833333333336,
      "lon": 12.783333333333333
    }
  },
  {
    "name": "Rydsgård",
    "synonyms": [
      "RYDSGÅRD",
      "RYDSGÅRD STN"
    ],
    "lId": "00415",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 55.47416666666667,
      "lon": 13.587222222222223
    }
  },
  {
    "name": "Rydsnäs Rydbergsgatan",
    "synonyms": [
      "RYDNÄS RYDBG",
      "RYDNÆS RYDBG",
      "RYDSNÄS RYDBERGSGATAN",
      "RYDSNÄS RYDBG",
      "RYDSNÆS RYDBERGSGATAN"
    ],
    "lId": "25733",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 57.79694444444444,
      "lon": 15.156944444444445
    }
  },
  {
    "name": "Rydöbruk",
    "synonyms": [
      "RYDÖBRUK",
      "RYDÖBRUK STN",
      "RYDØBRUK",
      "RYDØBRUK STN"
    ],
    "lId": "00246",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 56.95944444444445,
      "lon": 13.136111111111111
    }
  },
  {
    "name": "Rygge",
    "synonyms": [
      "RYGGE"
    ],
    "lId": "00518",
    "prio": 0,
    "pId": "076",
    "pos": {
      "lat": 59.358333333333334,
      "lon": 10.81027777777778
    }
  },
  {
    "name": "Rynge station",
    "synonyms": [
      "RYNGE STATION",
      "RYNGE STN"
    ],
    "lId": "16831",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 55.47,
      "lon": 13.663333333333334
    }
  },
  {
    "name": "Ryssby",
    "synonyms": [
      "RYSSBY",
      "RYSSBY STORG"
    ],
    "lId": "01279",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 56.86472222222223,
      "lon": 14.165555555555557
    }
  },
  {
    "name": "Rytterne",
    "synonyms": [
      "RYTTERNE",
      "RYTTERNE KYRKA"
    ],
    "lId": "11282",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.49583333333334,
      "lon": 16.349166666666665
    }
  },
  {
    "name": "Råby Bastuvägen Bromölla",
    "synonyms": [
      "RÅBY BASTUVÄGEN BROMÖLLA"
    ],
    "lId": "14627",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 56.10944444444445,
      "lon": 14.510277777777778
    }
  },
  {
    "name": "Råby handel Nyköping",
    "synonyms": [
      "RÅBY HANDEL",
      "RÅBY HANDEL NYKÖPING",
      "RÅBY HANDEL NYKØPING"
    ],
    "lId": "23510",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 58.873333333333335,
      "lon": 16.885555555555555
    }
  },
  {
    "name": "Råbäck",
    "synonyms": [
      "RÅBÄCK",
      "RÅBÄCK STN",
      "RÅBÆCK",
      "RÅBÆCK STN"
    ],
    "lId": "01280",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 58.61055555555556,
      "lon": 13.376111111111111
    }
  },
  {
    "name": "Råda",
    "synonyms": [
      "RÅDA"
    ],
    "lId": "11285",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 60.005833333333335,
      "lon": 13.595555555555556
    }
  },
  {
    "name": "Rådhuset T-bana",
    "synonyms": [
      "RÅDHUSET T-BANA"
    ],
    "lId": "21660",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.33027777777778,
      "lon": 18.041944444444447
    }
  },
  {
    "name": "Rådmanby by",
    "synonyms": [
      "RÅDMANBY BY"
    ],
    "lId": "18089",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.75972222222222,
      "lon": 18.967499999999998
    }
  },
  {
    "name": "Rådmansgatan T-bana",
    "synonyms": [
      "RÅDMANSGATAN T-BANA"
    ],
    "lId": "21666",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.34055555555556,
      "lon": 18.058611111111112
    }
  },
  {
    "name": "Rågsved T-bana",
    "synonyms": [
      "RÅGSVED T-BANA"
    ],
    "lId": "21713",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.256388888888885,
      "lon": 18.028055555555554
    }
  },
  {
    "name": "Rågsveden E16",
    "synonyms": [
      "RÅGSVEDEN E16"
    ],
    "lId": "25850",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 60.47916666666667,
      "lon": 14.062777777777779
    }
  },
  {
    "name": "Råneå",
    "synonyms": [
      "RÅNEÅ",
      "RÅNEÅ BSTN"
    ],
    "lId": "00887",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 65.8561111111111,
      "lon": 22.290000000000003
    }
  },
  {
    "name": "Råneå E4",
    "synonyms": [
      "RÅNEÅ E4"
    ],
    "lId": "20143",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 65.84944444444444,
      "lon": 22.31527777777778
    }
  },
  {
    "name": "Rångedala bygdegård",
    "synonyms": [
      "RÅNGEDALA BYGDE",
      "RÅNGEDALA BYGDEGÅRD"
    ],
    "lId": "12396",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 57.796388888888885,
      "lon": 13.1375
    }
  },
  {
    "name": "Rånnaväg",
    "synonyms": [
      "RÅNNAVÄG",
      "RÅNNAVÆG"
    ],
    "lId": "12459",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 57.67666666666666,
      "lon": 13.465555555555556
    }
  },
  {
    "name": "Rånäs Långsjö torg",
    "synonyms": [
      "RÅNÄS",
      "RÅNÄS LÅNGSJÖ TORG",
      "RÅNÆS",
      "RÅNÆS LÅNGSJØ TORG"
    ],
    "lId": "01282",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.80416666666667,
      "lon": 18.299722222222226
    }
  },
  {
    "name": "Rånö brygga",
    "synonyms": [
      "RÅNÖ BRYGGA",
      "RÅNØ BRYGGA"
    ],
    "lId": "24876",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 58.91888888888889,
      "lon": 18.17777777777778
    }
  },
  {
    "name": "Råå",
    "synonyms": [
      "RÅÅ",
      "RÅÅ LYBECKSGATA"
    ],
    "lId": "16834",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 56.000277777777775,
      "lon": 12.743055555555555
    }
  },
  {
    "name": "Råcksta T-bana",
    "synonyms": [
      "RÅCKSTA T-BANA"
    ],
    "lId": "21684",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.35472222222222,
      "lon": 17.881666666666668
    }
  },
  {
    "name": "Räfsnäs brygga",
    "synonyms": [
      "RÄFSNÄS BRYGGA",
      "RÆFSNÆS BRYGGA"
    ],
    "lId": "18090",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.75194444444445,
      "lon": 19.080555555555556
    }
  },
  {
    "name": "Rälla",
    "synonyms": [
      "RÄLLA",
      "RÄLLA VÄGSKÄL",
      "RÆLLA",
      "RÆLLA VÆGSKÆL"
    ],
    "lId": "14343",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 56.77361111111111,
      "lon": 16.56972222222222
    }
  },
  {
    "name": "Rämshyttan",
    "synonyms": [
      "RÄMSHYTTAN",
      "RÄMSHYTTAN TURI",
      "RÆMSHYTTAN",
      "RÆMSHYTTAN TURI"
    ],
    "lId": "01283",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 60.3175,
      "lon": 15.206388888888888
    }
  },
  {
    "name": "Ränneslöv",
    "synonyms": [
      "RÄNNESLÖV",
      "RÆNNESLØV"
    ],
    "lId": "01493",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 56.45305555555556,
      "lon": 13.07611111111111
    }
  },
  {
    "name": "Rätan",
    "synonyms": [
      "RÄTAN",
      "RÆTAN"
    ],
    "lId": "20381",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 62.46222222222222,
      "lon": 14.535833333333333
    }
  },
  {
    "name": "Rättvik",
    "synonyms": [
      "RATTVIK",
      "RÄTTVIK",
      "RÄTTVIK STN",
      "RÆTTVIK",
      "RÆTTVIK STN"
    ],
    "lId": "00158",
    "prio": 1,
    "pId": "074",
    "pos": {
      "lat": 60.885,
      "lon": 15.115555555555556
    }
  },
  {
    "name": "Rävemåla",
    "synonyms": [
      "RÄVEMÅLA",
      "RÄVEMÅLA ICA",
      "RÆVEMÅLA",
      "RÆVEMÅLA ICA"
    ],
    "lId": "01494",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 56.55472222222222,
      "lon": 15.266666666666667
    }
  },
  {
    "name": "Rävlanda",
    "synonyms": [
      "RAVLANDA",
      "RÄVLANDA",
      "RÄVLANDA STN",
      "RÆVLANDA",
      "RÆVLANDA STN"
    ],
    "lId": "00238",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 57.654444444444444,
      "lon": 12.500277777777777
    }
  },
  {
    "name": "Rödeby",
    "synonyms": [
      "RÖDEBY",
      "RØDEBY"
    ],
    "lId": "00521",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 56.260555555555555,
      "lon": 15.618055555555555
    }
  },
  {
    "name": "Rödlöga brygga",
    "synonyms": [
      "RÖDLÖGA BRYGGA",
      "RØDLØGA BRYGGA"
    ],
    "lId": "24879",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.594166666666666,
      "lon": 19.172222222222224
    }
  },
  {
    "name": "Röfors",
    "synonyms": [
      "RÖFORS",
      "RØFORS"
    ],
    "lId": "11294",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 58.940555555555555,
      "lon": 14.620277777777778
    }
  },
  {
    "name": "Röjan station",
    "synonyms": [
      "RÖJAN STATION",
      "RÖJAN STN",
      "RØJAN STN"
    ],
    "lId": "30041",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 62.47916666666667,
      "lon": 14.359166666666667
    }
  },
  {
    "name": "Röke kyrka",
    "synonyms": [
      "RÖKE KYRKA",
      "RØKE KYRKA"
    ],
    "lId": "01495",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 56.23444444444444,
      "lon": 13.52138888888889
    }
  },
  {
    "name": "Rönninge",
    "synonyms": [
      "RÖNNINGE",
      "RÖNNINGE STN",
      "RØNNINGE",
      "RØNNINGE STN"
    ],
    "lId": "00748",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.19333333333333,
      "lon": 17.749166666666667
    }
  },
  {
    "name": "Rönnäng",
    "synonyms": [
      "RÖNNÄNG",
      "RÖNNÄNG BRYGGA",
      "RØNNÆNG",
      "RØNNÆNG BRYGGA"
    ],
    "lId": "00879",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 57.93555555555555,
      "lon": 11.575555555555555
    }
  },
  {
    "name": "Rönnöfors",
    "synonyms": [
      "RÖNNÖFORS",
      "RØNNØFORS"
    ],
    "lId": "01284",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 63.654444444444444,
      "lon": 13.829166666666666
    }
  },
  {
    "name": "Rörbäcksnäs",
    "synonyms": [
      "RÖRBÄCKSNÄS",
      "RØRBÆCKSNÆS"
    ],
    "lId": "01285",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 61.12861111111111,
      "lon": 12.81388888888889
    }
  },
  {
    "name": "Rörstorp station",
    "synonyms": [
      "RÖRSTORP STATION",
      "RÖRSTORP STN",
      "RØRSTORP STATION",
      "RØRSTORP STN"
    ],
    "lId": "24861",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 57.17194444444444,
      "lon": 14.065000000000001
    }
  },
  {
    "name": "Rörvattnet",
    "synonyms": [
      "RÖRVATTNET",
      "RØRVATTNET"
    ],
    "lId": "13403",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 63.96277777777778,
      "lon": 14.064722222222223
    }
  },
  {
    "name": "Rörvik",
    "synonyms": [
      "RÖRVIK",
      "RÖRVIK V TORG",
      "RØRVIK",
      "RØRVIK V TORG"
    ],
    "lId": "01286",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 57.238055555555555,
      "lon": 14.573611111111111
    }
  },
  {
    "name": "Röstånga",
    "synonyms": [
      "RÖSTÅNGA",
      "RÖSTÅNGA BSTN",
      "RØSTÅNGA",
      "RØSTÅNGA BSTN"
    ],
    "lId": "01287",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 56.003055555555555,
      "lon": 13.289444444444444
    }
  },
  {
    "name": "S.t Eriksplan T-bana",
    "synonyms": [
      "S.T ERIKSPLAN T-BANA",
      "S:T ERIKSPLAN T-BANA",
      "SANKT ERIKSPLAN T-BANA",
      "ST ERIKSPLAN T-BANA"
    ],
    "lId": "21665",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.339444444444446,
      "lon": 18.036944444444448
    }
  },
  {
    "name": "Sala",
    "synonyms": [
      "SALA",
      "SALA STN"
    ],
    "lId": "00214",
    "prio": 1,
    "pId": "074",
    "pos": {
      "lat": 59.925,
      "lon": 16.60638888888889
    }
  },
  {
    "name": "Saladamm",
    "synonyms": [
      "SALADAMM"
    ],
    "lId": "11317",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.98222222222223,
      "lon": 16.64
    }
  },
  {
    "name": "Salbohed",
    "synonyms": [
      "SALBOHED"
    ],
    "lId": "11318",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.91027777777778,
      "lon": 16.34583333333333
    }
  },
  {
    "name": "Salem",
    "synonyms": [
      "SALEM",
      "SALEM CENTRUM"
    ],
    "lId": "01053",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.20111111111111,
      "lon": 17.76722222222222
    }
  },
  {
    "name": "Saltarö strand",
    "synonyms": [
      "SALTARÖ STRAND",
      "SALTARØ STRAND"
    ],
    "lId": "24942",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.34027777777778,
      "lon": 18.610000000000003
    }
  },
  {
    "name": "Saltsjö-Duvnäs station",
    "synonyms": [
      "SALTSJÖ-DUVNÄS STATION",
      "SALTSJØ-DUVNÆS STATION"
    ],
    "lId": "20875",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.30027777777777,
      "lon": 18.198611111111113
    }
  },
  {
    "name": "Saltsjö-Järla station",
    "synonyms": [
      "SALTSJÖ-JÄRLA STATION",
      "SALTSJØ-JÆRLA STATION"
    ],
    "lId": "20874",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.306666666666665,
      "lon": 18.149444444444445
    }
  },
  {
    "name": "Saltsjöbaden",
    "synonyms": [
      "SALTSJÖBADEN",
      "SALTSJÖBADN STN",
      "SALTSJØBADEN",
      "SALTSJØBADN STN"
    ],
    "lId": "00751",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.278888888888886,
      "lon": 18.31277777777778
    }
  },
  {
    "name": "Saltvik Härnösand",
    "synonyms": [
      "SALTVIK HÄRNÖSAND",
      "SALTVIK HÆRNØSAND"
    ],
    "lId": "27657",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 62.66,
      "lon": 17.86277777777778
    }
  },
  {
    "name": "Sandared",
    "synonyms": [
      "SANDARED",
      "SANDARED STN"
    ],
    "lId": "00272",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 57.70944444444445,
      "lon": 12.792222222222222
    }
  },
  {
    "name": "Sandarne",
    "synonyms": [
      "SANDARNE"
    ],
    "lId": "00639",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 61.26,
      "lon": 17.14527777777778
    }
  },
  {
    "name": "Sandbacken",
    "synonyms": [
      "SANDBACKEN"
    ],
    "lId": "21223",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.46472222222223,
      "lon": 15.130555555555556
    }
  },
  {
    "name": "Sandhamn",
    "synonyms": [
      "SANDHAMN"
    ],
    "lId": "20694",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.288333333333334,
      "lon": 18.915555555555553
    }
  },
  {
    "name": "Sandhem",
    "synonyms": [
      "SANDHEM",
      "SANDHEM STN"
    ],
    "lId": "24005",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 57.98833333333334,
      "lon": 13.771944444444445
    }
  },
  {
    "name": "Sandhult kyrka",
    "synonyms": [
      "SANDHULT KYRKA"
    ],
    "lId": "12369",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 57.769999999999996,
      "lon": 12.821388888888889
    }
  },
  {
    "name": "Sandsborg T-bana",
    "synonyms": [
      "SANDSBORG T-BANA"
    ],
    "lId": "21702",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.28472222222222,
      "lon": 18.092222222222222
    }
  },
  {
    "name": "Sandslån",
    "synonyms": [
      "SANDSLÅN"
    ],
    "lId": "15276",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 63.01166666666666,
      "lon": 17.795555555555556
    }
  },
  {
    "name": "Sandviken Norra Porten",
    "synonyms": [
      "SANDVIKEN NORRA PORTEN"
    ],
    "lId": "19984",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 60.61972222222222,
      "lon": 16.789444444444445
    }
  },
  {
    "name": "Sandviken Posten",
    "synonyms": [
      "SANDVIKEN POSTEN"
    ],
    "lId": "19846",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 60.618611111111115,
      "lon": 16.77638888888889
    }
  },
  {
    "name": "Sandviken station",
    "synonyms": [
      "SANDVIKEN STATION",
      "SANDVIKEN STN"
    ],
    "lId": "00195",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 60.61416666666667,
      "lon": 16.778055555555554
    }
  },
  {
    "name": "Sandviken stadszon",
    "synonyms": [
      "SANDVIKEN STADSZON",
      "SANDVIKEN ZON"
    ],
    "lId": "79012",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 60.61416666666667,
      "lon": 16.778055555555554
    }
  },
  {
    "name": "Sandö",
    "synonyms": [
      "SANDÖ",
      "SANDØ"
    ],
    "lId": "29052",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 62.88361111111111,
      "lon": 17.890833333333333
    }
  },
  {
    "name": "Sangis",
    "synonyms": [
      "SANGIS",
      "SANGIS BYN"
    ],
    "lId": "01289",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 65.86583333333333,
      "lon": 23.499166666666667
    }
  },
  {
    "name": "Sangis E4",
    "synonyms": [
      "SANGIS E4"
    ],
    "lId": "20142",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 65.85583333333332,
      "lon": 23.49277777777778
    }
  },
  {
    "name": "Sankt Anna",
    "synonyms": [
      "S.T ANNA V210",
      "SANKT ANNA"
    ],
    "lId": "01288",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 58.34861111111111,
      "lon": 16.706666666666667
    }
  },
  {
    "name": "Sankt Olof Byvägen",
    "synonyms": [
      "S.T OLOF BYVÄG",
      "S.T OLOF BYVÆG",
      "SANKT OLOF BYVÄGEN",
      "SANKT OLOF BYVÆGEN"
    ],
    "lId": "22151",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 55.63722222222222,
      "lon": 14.130555555555556
    }
  },
  {
    "name": "Sannahed",
    "synonyms": [
      "SANNAHED"
    ],
    "lId": "11336",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.095555555555556,
      "lon": 15.160833333333334
    }
  },
  {
    "name": "Sannarp",
    "synonyms": [
      "SANNARP",
      "SANNARP STN"
    ],
    "lId": "01290",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 56.68611111111111,
      "lon": 12.892777777777777
    }
  },
  {
    "name": "Sarpsborg",
    "synonyms": [
      "SARPSBORG",
      "XKQ"
    ],
    "lId": "00527",
    "prio": 0,
    "pId": "076",
    "pos": {
      "lat": 59.28361111111111,
      "lon": 11.157777777777778
    }
  },
  {
    "name": "Saxdalen",
    "synonyms": [
      "SAXDALEN",
      "SAXDALEN OLSJÖV",
      "SAXDALEN OLSJØV"
    ],
    "lId": "12974",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 60.151944444444446,
      "lon": 14.976666666666667
    }
  },
  {
    "name": "Saxemara",
    "synonyms": [
      "SAXEMARA"
    ],
    "lId": "11337",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 56.1675,
      "lon": 15.229166666666666
    }
  },
  {
    "name": "Saxnäs",
    "synonyms": [
      "SAXNÄS",
      "SAXNÆS"
    ],
    "lId": "01291",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 64.97,
      "lon": 15.35388888888889
    }
  },
  {
    "name": "Saxtorp kyrka",
    "synonyms": [
      "SAXTORP KYRKA"
    ],
    "lId": "16846",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 55.839444444444446,
      "lon": 12.959722222222222
    }
  },
  {
    "name": "Saxvallen",
    "synonyms": [
      "SAXVALLEN"
    ],
    "lId": "29983",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 63.55833333333333,
      "lon": 12.339166666666667
    }
  },
  {
    "name": "Segeltorp",
    "synonyms": [
      "SEGELTORP",
      "SEGELTORP CM"
    ],
    "lId": "01292",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.279444444444444,
      "lon": 17.942777777777778
    }
  },
  {
    "name": "Segersäng",
    "synonyms": [
      "SEGERSÄNG",
      "SEGERSÄNG STN",
      "SEGERSÆNG",
      "SEGERSÆNG STN"
    ],
    "lId": "30043",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.028888888888886,
      "lon": 17.92638888888889
    }
  },
  {
    "name": "Segmon Sågtorpsskolan",
    "synonyms": [
      "SEGMON SÅGTORPSSKOLAN"
    ],
    "lId": "11341",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.264722222222225,
      "lon": 13.023611111111112
    }
  },
  {
    "name": "Selknä station",
    "synonyms": [
      "SELKNÄ STATION",
      "SELKNÄ STN"
    ],
    "lId": "26057",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.855000000000004,
      "lon": 17.90833333333333
    }
  },
  {
    "name": "Sennan station",
    "synonyms": [
      "SENNAN STATION",
      "SENNAN STN"
    ],
    "lId": "00234",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 56.77166666666667,
      "lon": 12.98
    }
  },
  {
    "name": "Seskarö byn",
    "synonyms": [
      "SESKARÖ BYN",
      "SESKARØ BYN"
    ],
    "lId": "14971",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 65.735,
      "lon": 23.745
    }
  },
  {
    "name": "Sevalla",
    "synonyms": [
      "SEVALLA"
    ],
    "lId": "11345",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.73888888888889,
      "lon": 16.71527777777778
    }
  },
  {
    "name": "Sexdrega väg 154",
    "synonyms": [
      "SEXDREGA V 154",
      "SEXDREGA VÄG 154",
      "SEXDREGA VÆG 154"
    ],
    "lId": "23538",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 57.580000000000005,
      "lon": 13.124444444444444
    }
  },
  {
    "name": "Siaröfortet brygga",
    "synonyms": [
      "SIARÖFORTET BRYGGA"
    ],
    "lId": "08760",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.555277777777775,
      "lon": 18.622777777777777
    }
  },
  {
    "name": "Sibbhult",
    "synonyms": [
      "SIBBHULT",
      "SIBBHULT BSTN"
    ],
    "lId": "01293",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 56.26833333333333,
      "lon": 14.20111111111111
    }
  },
  {
    "name": "Sickla station",
    "synonyms": [
      "SICKLA STATION",
      "SICKLA STN"
    ],
    "lId": "24807",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.306666666666665,
      "lon": 18.121111111111112
    }
  },
  {
    "name": "Sickla kaj",
    "synonyms": [
      "SICKLA KAJ"
    ],
    "lId": "24926",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.302499999999995,
      "lon": 18.103611111111114
    }
  },
  {
    "name": "Sickla köpkvarter",
    "synonyms": [
      "SICKLA KÖPKVARTER",
      "SICKLA KØPKVARTER"
    ],
    "lId": "45902",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.30416666666667,
      "lon": 18.128611111111113
    }
  },
  {
    "name": "Sickla udde",
    "synonyms": [
      "SICKLA UDDE"
    ],
    "lId": "24927",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.30611111111111,
      "lon": 18.108611111111113
    }
  },
  {
    "name": "Sidensjö kyrka bron",
    "synonyms": [
      "SIDENSJÖ KYRKA BRON",
      "SIDENSJØ KYRKA BRON"
    ],
    "lId": "15279",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 63.2925,
      "lon": 18.29388888888889
    }
  },
  {
    "name": "Siesta-Festivalen",
    "synonyms": [
      "SIESTA-FESTIVALEN"
    ],
    "lId": "32944",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 56.1575,
      "lon": 13.763055555555555
    }
  },
  {
    "name": "Siggesta",
    "synonyms": [
      "SIGGESTA"
    ],
    "lId": "66479",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.3725,
      "lon": 18.52777777777778
    }
  },
  {
    "name": "Sigtuna",
    "synonyms": [
      "SIGTUNA",
      "SIGTUNA BSTN"
    ],
    "lId": "00667",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.617222222222225,
      "lon": 17.723055555555554
    }
  },
  {
    "name": "Sigtuna Hällsboskolan",
    "synonyms": [
      "SIGTUNA HÄLLSBOSKOLAN"
    ],
    "lId": "12860",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.62722222222222,
      "lon": 17.70111111111111
    }
  },
  {
    "name": "Sigtuna Jupitergatan",
    "synonyms": [
      "SIGTUNA JUPITERGATAN"
    ],
    "lId": "67347",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.61555555555556,
      "lon": 17.811666666666667
    }
  },
  {
    "name": "Sigtuna Stora Brännbo",
    "synonyms": [
      "SIGTUNA ST BRÄN",
      "SIGTUNA ST BRÆN",
      "SIGTUNA STORA BRÄNNBO",
      "SIGTUNA STORA BRÆNNBO"
    ],
    "lId": "10552",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.62027777777778,
      "lon": 17.711944444444445
    }
  },
  {
    "name": "Sikeå E4",
    "synonyms": [
      "SIKEÅ E4"
    ],
    "lId": "00471",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 64.16833333333334,
      "lon": 20.924722222222222
    }
  },
  {
    "name": "Sikfors herrgård",
    "synonyms": [
      "SIKFORS HERRGD",
      "SIKFORS HERRGÅRD"
    ],
    "lId": "21228",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.80083333333333,
      "lon": 14.58388888888889
    }
  },
  {
    "name": "Sikås",
    "synonyms": [
      "SIKÅS"
    ],
    "lId": "13233",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 63.63055555555555,
      "lon": 15.213333333333333
    }
  },
  {
    "name": "Siljansnäs kiosken",
    "synonyms": [
      "SILJANSNÄS",
      "SILJANSNÄS KIOSKEN",
      "SILJANSNÆS KIOSKEN"
    ],
    "lId": "00650",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 60.77611111111111,
      "lon": 14.864444444444445
    }
  },
  {
    "name": "Silverdalen centrum",
    "synonyms": [
      "SILVERDALEN CENTRUM",
      "SILVERDALEN CM"
    ],
    "lId": "20279",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 57.5425,
      "lon": 15.752222222222223
    }
  },
  {
    "name": "Simlångsdalen",
    "synonyms": [
      "SIMLÅNGSDALEN"
    ],
    "lId": "00517",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 56.720555555555556,
      "lon": 13.130277777777778
    }
  },
  {
    "name": "Simonstorp",
    "synonyms": [
      "SIMONSTORP",
      "SIMONSTORP STN"
    ],
    "lId": "11353",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 58.780833333333334,
      "lon": 16.15972222222222
    }
  },
  {
    "name": "Simpnäs brygga",
    "synonyms": [
      "SIMPNÄS BRYGGA",
      "SIMPNÆS BRYGGA"
    ],
    "lId": "11354",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.86944444444445,
      "lon": 19.077222222222222
    }
  },
  {
    "name": "Simremarken Mopsvägen",
    "synonyms": [
      "SIMREMARKEN MOPSVÄGEN",
      "SIMREMARKEN MOPSVÆGEN"
    ],
    "lId": "30572",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 55.345555555555556,
      "lon": 13.280277777777778
    }
  },
  {
    "name": "Simris Bjärsjövägen",
    "synonyms": [
      "SIMRIS BJÄRSJÖVÄGEN",
      "SIMRIS BJÆRSJØVÆGEN"
    ],
    "lId": "31242",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 55.53777777777778,
      "lon": 14.318333333333333
    }
  },
  {
    "name": "Simrishamn",
    "synonyms": [
      "SIMRISHAMN",
      "SIMRISHAMN STN"
    ],
    "lId": "00169",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 55.553888888888885,
      "lon": 14.351944444444444
    }
  },
  {
    "name": "Singö",
    "synonyms": [
      "SINGÖ",
      "SINGÖ ELLAN",
      "SINGØ",
      "SINGØ ELLAN"
    ],
    "lId": "01294",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 60.206944444444446,
      "lon": 18.738055555555558
    }
  },
  {
    "name": "Sjisjka",
    "synonyms": [
      "SJISJKA",
      "SJISJKA STN"
    ],
    "lId": "01437",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 67.62416666666665,
      "lon": 20.234444444444446
    }
  },
  {
    "name": "Sjunnen",
    "synonyms": [
      "SJUNNEN"
    ],
    "lId": "11358",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 57.43583333333333,
      "lon": 15.173055555555555
    }
  },
  {
    "name": "Sjuntorp",
    "synonyms": [
      "SJUNTORP",
      "SJUNTORP TORGET"
    ],
    "lId": "00999",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 58.19638888888888,
      "lon": 12.223888888888888
    }
  },
  {
    "name": "Själevad E4",
    "synonyms": [
      "SJÄLEVAD E4",
      "SJÆLEVAD E4"
    ],
    "lId": "29081",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 63.28722222222222,
      "lon": 18.609722222222224
    }
  },
  {
    "name": "Sjötofta fd station",
    "synonyms": [
      "SJÖTOFTA FD STATION",
      "SJÖTOFTA FD STN",
      "SJØTOFTA FD STATION",
      "SJØTOFTA FD STN"
    ],
    "lId": "23066",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 57.35777777777778,
      "lon": 13.289444444444444
    }
  },
  {
    "name": "Sjöberg",
    "synonyms": [
      "SJÖBERG",
      "SJØBERG"
    ],
    "lId": "25718",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.426944444444445,
      "lon": 17.999166666666667
    }
  },
  {
    "name": "Sjöbo",
    "synonyms": [
      "SJOBO",
      "SJÖBO",
      "SJÖBO BSTN",
      "SJØBO",
      "SJØBO BSTN"
    ],
    "lId": "00949",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 55.63055555555555,
      "lon": 13.700833333333332
    }
  },
  {
    "name": "Sjögestad by",
    "synonyms": [
      "SJÖGESTAD BY",
      "SJØGESTAD BY"
    ],
    "lId": "23376",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 58.365833333333335,
      "lon": 15.370833333333334
    }
  },
  {
    "name": "Sjögränd",
    "synonyms": [
      "SJÖGRÄND",
      "SJØGRÆND"
    ],
    "lId": "20230",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 60.03472222222222,
      "lon": 13.58888888888889
    }
  },
  {
    "name": "Sjömarken",
    "synonyms": [
      "SJÖMARKEN",
      "SJÖMARKEN KIOSK",
      "SJØMARKEN",
      "SJØMARKEN KIOSK"
    ],
    "lId": "01379",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 57.71555555555556,
      "lon": 12.837222222222223
    }
  },
  {
    "name": "Sjörröd",
    "synonyms": [
      "SJÖRRÖD",
      "SJØRRØD"
    ],
    "lId": "22955",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 56.138888888888886,
      "lon": 13.73861111111111
    }
  },
  {
    "name": "Sjösa skolan",
    "synonyms": [
      "SJÖSA SKOLA",
      "SJÖSA SKOLAN",
      "SJØSA SKOLA"
    ],
    "lId": "11368",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 58.77611111111111,
      "lon": 17.086388888888887
    }
  },
  {
    "name": "Sjötorp",
    "synonyms": [
      "SJÖTORP",
      "SJØTORP"
    ],
    "lId": "16441",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 58.83833333333334,
      "lon": 13.979722222222222
    }
  },
  {
    "name": "Sjövik",
    "synonyms": [
      "SJÖVIK",
      "SJÖVIK BSTN",
      "SJØVIK",
      "SJØVIK BSTN"
    ],
    "lId": "01496",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 57.914722222222224,
      "lon": 12.369166666666667
    }
  },
  {
    "name": "Skagersvik",
    "synonyms": [
      "SKAGERSVIK"
    ],
    "lId": "11371",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 58.967777777777776,
      "lon": 14.105555555555556
    }
  },
  {
    "name": "Skalspasset",
    "synonyms": [
      "SKALSPASSET"
    ],
    "lId": "64292",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 62.49138888888889,
      "lon": 13.946944444444444
    }
  },
  {
    "name": "Skalstugan",
    "synonyms": [
      "SKALSTUGAN"
    ],
    "lId": "29456",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 63.573888888888895,
      "lon": 12.275833333333335
    }
  },
  {
    "name": "Skanstull T-bana",
    "synonyms": [
      "SKANSTULL T-BANA"
    ],
    "lId": "21655",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.30777777777777,
      "lon": 18.07611111111111
    }
  },
  {
    "name": "Skanör",
    "synonyms": [
      "SKANOR",
      "SKANÖR",
      "SKANÖR CENTRUM",
      "SKANØR",
      "SKANØR CENTRUM"
    ],
    "lId": "00950",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 55.41138888888889,
      "lon": 12.843611111111112
    }
  },
  {
    "name": "Skara",
    "synonyms": [
      "SKARA",
      "SKARA BSTN"
    ],
    "lId": "00611",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 58.38305555555556,
      "lon": 13.43888888888889
    }
  },
  {
    "name": "Skara Sommarland",
    "synonyms": [
      "SKARA SOMMARLAND",
      "SKARA SOMMARLND",
      "SOMMARLAND"
    ],
    "lId": "00819",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 58.40138888888889,
      "lon": 13.550833333333333
    }
  },
  {
    "name": "Skarnes",
    "synonyms": [
      "SKARNES"
    ],
    "lId": "00315",
    "prio": 0,
    "pId": "076",
    "pos": {
      "lat": 60.24583333333334,
      "lon": 11.705555555555556
    }
  },
  {
    "name": "Skarpnäck T-bana",
    "synonyms": [
      "SKARPNÄCK T-BANA",
      "SKARPNÆCK T-BANA"
    ],
    "lId": "21691",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.266666666666666,
      "lon": 18.133333333333333
    }
  },
  {
    "name": "Skarvsjöby",
    "synonyms": [
      "SKARVSJÖBY",
      "SKARVSJØBY"
    ],
    "lId": "13943",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 64.97083333333333,
      "lon": 17.109444444444446
    }
  },
  {
    "name": "Skateholm",
    "synonyms": [
      "SKATEHOLM",
      "SKATEHOLM CEDER"
    ],
    "lId": "16854",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 55.38055555555555,
      "lon": 13.471111111111112
    }
  },
  {
    "name": "Skattkärr",
    "synonyms": [
      "SKATTKÄRR",
      "SKATTKÄRR SKOLA",
      "SKATTKÆRR",
      "SKATTKÆRR SKOLA"
    ],
    "lId": "01297",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.41222222222222,
      "lon": 13.671111111111111
    }
  },
  {
    "name": "Skattunge handel",
    "synonyms": [
      "SKATTUNGE HANDEL"
    ],
    "lId": "01298",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 61.18611111111111,
      "lon": 14.8575
    }
  },
  {
    "name": "Skaulo",
    "synonyms": [
      "SKAULO",
      "SKAULO E10"
    ],
    "lId": "14832",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 67.41361111111112,
      "lon": 21.11277777777778
    }
  },
  {
    "name": "Skavsta flygplats",
    "synonyms": [
      "SKAVSTA FLYGPLATS"
    ],
    "lId": "11384",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 58.784166666666664,
      "lon": 16.923055555555557
    }
  },
  {
    "name": "Skebobruk",
    "synonyms": [
      "SKEBOBRUK",
      "SKEBOBRUK NORRA"
    ],
    "lId": "01299",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.96888888888889,
      "lon": 18.605555555555558
    }
  },
  {
    "name": "Skebokvarn",
    "synonyms": [
      "SKEBOKVARN"
    ],
    "lId": "11386",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.06388888888888,
      "lon": 16.714166666666667
    }
  },
  {
    "name": "Skeda udde",
    "synonyms": [
      "SKEDA UDDE"
    ],
    "lId": "11387",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 58.28944444444444,
      "lon": 15.56027777777778
    }
  },
  {
    "name": "Skedala",
    "synonyms": [
      "SKEDALA"
    ],
    "lId": "17159",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 56.69222222222222,
      "lon": 12.972222222222223
    }
  },
  {
    "name": "Skede kyrka",
    "synonyms": [
      "SKEDE KYRKA"
    ],
    "lId": "11389",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 57.471944444444446,
      "lon": 15.175277777777778
    }
  },
  {
    "name": "Skee",
    "synonyms": [
      "SKEE",
      "SKEE STN"
    ],
    "lId": "00075",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 58.92333333333333,
      "lon": 11.261666666666667
    }
  },
  {
    "name": "Skegrie Stationsvägen",
    "synonyms": [
      "SKEGRIE STATIONSVÄGEN",
      "SKEGRIE STATIONSVÆGEN",
      "SKEGRIE STNVÄG",
      "SKEGRIE STNVÆG"
    ],
    "lId": "16856",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 55.405277777777776,
      "lon": 13.081666666666667
    }
  },
  {
    "name": "Skelleftehamn centrum",
    "synonyms": [
      "SKELLEFTEHAMN CENTRUM"
    ],
    "lId": "71108",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 64.68694444444445,
      "lon": 21.237222222222222
    }
  },
  {
    "name": "Skellefteå",
    "synonyms": [
      "SKELLEFTEA",
      "SKELLEFTEÅ",
      "SKELLEFTEÅ BSTN"
    ],
    "lId": "00053",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 64.75222222222222,
      "lon": 20.954166666666666
    }
  },
  {
    "name": "Skene",
    "synonyms": [
      "SKENE",
      "SKENE STN"
    ],
    "lId": "00314",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 57.488055555555555,
      "lon": 12.64861111111111
    }
  },
  {
    "name": "Skepparslöv kyrka",
    "synonyms": [
      "SKEPPARSLÖV KA",
      "SKEPPARSLÖV KYRKA"
    ],
    "lId": "04117",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 56.01361111111111,
      "lon": 14.069444444444445
    }
  },
  {
    "name": "Skepplanda",
    "synonyms": [
      "SKEPPLANDA",
      "SKEPPLANDA ALBO"
    ],
    "lId": "00642",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 57.98361111111111,
      "lon": 12.21111111111111
    }
  },
  {
    "name": "Skeppsdalsström",
    "synonyms": [
      "SKEPPSDALSSTR3M",
      "SKEPPSDALSSTRÖM"
    ],
    "lId": "25716",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.305,
      "lon": 18.484166666666667
    }
  },
  {
    "name": "Skeppshult gjuteri",
    "synonyms": [
      "SKEPPSHULT GJUT",
      "SKEPPSHULT GJUTERI"
    ],
    "lId": "20229",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 57.125277777777775,
      "lon": 13.379166666666666
    }
  },
  {
    "name": "Ski",
    "synonyms": [
      "SKI"
    ],
    "lId": "00508",
    "prio": 0,
    "pId": "076",
    "pos": {
      "lat": 59.72527777777778,
      "lon": 10.875277777777779
    }
  },
  {
    "name": "Skillingaryd",
    "synonyms": [
      "SKILLINGARYD"
    ],
    "lId": "00164",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 57.42833333333333,
      "lon": 14.090555555555556
    }
  },
  {
    "name": "Skillinge busstation",
    "synonyms": [
      "SKILLINGE BSTN",
      "SKILLINGE BUSSTATION"
    ],
    "lId": "00732",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 55.473333333333336,
      "lon": 14.278333333333334
    }
  },
  {
    "name": "Skinnskatteberg",
    "synonyms": [
      "SKINNSKATTEBERG"
    ],
    "lId": "00186",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.84916666666667,
      "lon": 15.665833333333333
    }
  },
  {
    "name": "Skinnskatteberg Långvikstorp",
    "synonyms": [
      "SKINNSKATTEBERG LÅNGVIKSTORP"
    ],
    "lId": "43991",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.84305555555556,
      "lon": 15.70611111111111
    }
  },
  {
    "name": "Skipås",
    "synonyms": [
      "SKIPÅS"
    ],
    "lId": "01497",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 56.78,
      "lon": 12.622777777777777
    }
  },
  {
    "name": "Skivarp torget",
    "synonyms": [
      "SKIVARP TORGET"
    ],
    "lId": "16859",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 55.42305555555555,
      "lon": 13.569166666666666
    }
  },
  {
    "name": "Skoby väg 288",
    "synonyms": [
      "SKOBY VÄG 288",
      "SKOBY VÆG 288"
    ],
    "lId": "26590",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 60.032777777777774,
      "lon": 18.021666666666665
    }
  },
  {
    "name": "Skodsborg",
    "synonyms": [
      "SKODSBORG"
    ],
    "lId": "00661",
    "prio": 0,
    "pId": "086",
    "pos": {
      "lat": 55.82361111111111,
      "lon": 12.571111111111112
    }
  },
  {
    "name": "Skog Kramfors",
    "synonyms": [
      "SKOG KRAMFORS"
    ],
    "lId": "15282",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 62.91611111111111,
      "lon": 18.028888888888886
    }
  },
  {
    "name": "Skog kyrka",
    "synonyms": [
      "SKOG KYRKA"
    ],
    "lId": "17251",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 61.165,
      "lon": 16.821944444444444
    }
  },
  {
    "name": "Skoghall",
    "synonyms": [
      "SKOGHALL",
      "SKOGHALL CM"
    ],
    "lId": "00820",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.323055555555555,
      "lon": 13.465
    }
  },
  {
    "name": "Skogsby",
    "synonyms": [
      "SKOGSBY",
      "SKOGSBY CENTRUM"
    ],
    "lId": "01300",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 56.62916666666667,
      "lon": 16.5125
    }
  },
  {
    "name": "Skogskyrkogården T-bana",
    "synonyms": [
      "SKOGSKYRKOGÅRDEN T-BANA"
    ],
    "lId": "21701",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.27916666666667,
      "lon": 18.095277777777778
    }
  },
  {
    "name": "Skogslund Växjö",
    "synonyms": [
      "SKOGSLUND VÄXJÖ"
    ],
    "lId": "35476",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 56.80972222222222,
      "lon": 14.881111111111112
    }
  },
  {
    "name": "Skogstibble kyrka",
    "synonyms": [
      "SKOGSTIBBLE KA",
      "SKOGSTIBBLE KYRKA"
    ],
    "lId": "21026",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.831388888888895,
      "lon": 17.31833333333333
    }
  },
  {
    "name": "Skogstorp centrum Sörmland",
    "synonyms": [
      "SKOGSTORP CENTRUM SÖRMLAND",
      "SKOGSTORP CENTRUM SØRMLAND",
      "SKOGSTORP CM"
    ],
    "lId": "11405",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.32777777777778,
      "lon": 16.481944444444444
    }
  },
  {
    "name": "Skogstorp Prästkragev Halland",
    "synonyms": [
      "SKOGSTORP PRÄSTKRAGEV HALLAND",
      "SKOGSTORP PRÆSTKRAGEV HALLAND"
    ],
    "lId": "23973",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 56.914722222222224,
      "lon": 12.433055555555555
    }
  },
  {
    "name": "Skogås",
    "synonyms": [
      "SKOGÅS",
      "SKOGÅS STN"
    ],
    "lId": "00757",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.21805555555556,
      "lon": 18.154166666666665
    }
  },
  {
    "name": "Skokloster Slott",
    "synonyms": [
      "SKOKLOSTER SLOTT"
    ],
    "lId": "01159",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.70527777777778,
      "lon": 17.6225
    }
  },
  {
    "name": "Skolsta",
    "synonyms": [
      "SKOLSTA"
    ],
    "lId": "12855",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.660555555555554,
      "lon": 17.241944444444446
    }
  },
  {
    "name": "Skorped kiosk",
    "synonyms": [
      "SKORPED KIOSK"
    ],
    "lId": "15283",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 63.38472222222222,
      "lon": 17.854444444444447
    }
  },
  {
    "name": "Skottorp",
    "synonyms": [
      "SKOTTORP"
    ],
    "lId": "17166",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 56.45027777777778,
      "lon": 12.95861111111111
    }
  },
  {
    "name": "Skottsund",
    "synonyms": [
      "SKOTTSUND"
    ],
    "lId": "15284",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 62.29111111111111,
      "lon": 17.386388888888888
    }
  },
  {
    "name": "Skra Bro",
    "synonyms": [
      "SKRA BRO"
    ],
    "lId": "59559",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 57.75805555555556,
      "lon": 11.831111111111111
    }
  },
  {
    "name": "Skrea korsväg",
    "synonyms": [
      "SKREA KORSVÄG",
      "SKREA KORSVÆG"
    ],
    "lId": "17168",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 56.88583333333333,
      "lon": 12.568055555555555
    }
  },
  {
    "name": "Skruv",
    "synonyms": [
      "SKRUV",
      "SKRUV MEJERIG"
    ],
    "lId": "01301",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 56.67638888888889,
      "lon": 15.365833333333333
    }
  },
  {
    "name": "Skucku",
    "synonyms": [
      "SKUCKU"
    ],
    "lId": "13441",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 62.78472222222222,
      "lon": 14.5
    }
  },
  {
    "name": "Skultorp trafikplats",
    "synonyms": [
      "SKULTORP TRAFIKPLATS"
    ],
    "lId": "18262",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 58.34055555555556,
      "lon": 13.860555555555555
    }
  },
  {
    "name": "Skultuna",
    "synonyms": [
      "SKULTUNA"
    ],
    "lId": "00680",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.718611111111116,
      "lon": 16.42888888888889
    }
  },
  {
    "name": "Skummeslövsstrand",
    "synonyms": [
      "SKUMMESLÖVSSTRAND",
      "SKUMMESLØVSSTRAND"
    ],
    "lId": "17169",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 56.46138888888889,
      "lon": 12.921666666666667
    }
  },
  {
    "name": "Skurup",
    "synonyms": [
      "SKURUP",
      "SKURUP STN"
    ],
    "lId": "00138",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 55.480000000000004,
      "lon": 13.500277777777777
    }
  },
  {
    "name": "Skutskär station",
    "synonyms": [
      "SKUTSKÄR STATION",
      "SKUTSKÄR STN",
      "SKUTSKÆR STATION",
      "SKUTSKÆR STN"
    ],
    "lId": "21861",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 60.62388888888889,
      "lon": 17.405277777777776
    }
  },
  {
    "name": "Skyllberg",
    "synonyms": [
      "SKYLLBERG"
    ],
    "lId": "20933",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 58.94277777777778,
      "lon": 14.99472222222222
    }
  },
  {
    "name": "Skyttorp",
    "synonyms": [
      "SKYTTORP",
      "SKYTTORP STN"
    ],
    "lId": "00438",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 60.07944444444445,
      "lon": 17.736944444444447
    }
  },
  {
    "name": "Skålan",
    "synonyms": [
      "SKÅLAN"
    ],
    "lId": "13353",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 62.644444444444446,
      "lon": 14.159166666666668
    }
  },
  {
    "name": "Skåne-Tranås",
    "synonyms": [
      "SKÅNE TRANÅS",
      "SKÅNE-TRANÅS"
    ],
    "lId": "01302",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 55.614444444444445,
      "lon": 13.996666666666666
    }
  },
  {
    "name": "Skånes Djurpark",
    "synonyms": [
      "SKÅNES DJURPARK"
    ],
    "lId": "24994",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 55.96277777777778,
      "lon": 13.538333333333334
    }
  },
  {
    "name": "Skånes-Fagerhult",
    "synonyms": [
      "SKÅNE FAGERHULT",
      "SKÅNE-FAGERHULT",
      "SKÅNES FAGERHULT",
      "SKÅNES-FAGERHULT"
    ],
    "lId": "00537",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 56.36833333333333,
      "lon": 13.47
    }
  },
  {
    "name": "Skånes Viby Grylleängsvägen",
    "synonyms": [
      "SKÅNES VIBY GRYLLEÄNGSVÄGEN",
      "SKÅNES VIBY GRYLLEÆNGSVÆGEN"
    ],
    "lId": "31059",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 56.0175,
      "lon": 14.23
    }
  },
  {
    "name": "Skånes Värsjö",
    "synonyms": [
      "SKÅNES VÄRSJÖ",
      "SKÅNES VÆRSJØ"
    ],
    "lId": "12834",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 56.33527777777778,
      "lon": 13.435555555555556
    }
  },
  {
    "name": "Skåpafors Skåpakorset",
    "synonyms": [
      "SKÅPAFORS SKÅPAKORSET"
    ],
    "lId": "21830",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.01638888888889,
      "lon": 12.268333333333334
    }
  },
  {
    "name": "Skåre Sågen",
    "synonyms": [
      "SKÅRE SÅGEN"
    ],
    "lId": "18258",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.43611111111111,
      "lon": 13.4425
    }
  },
  {
    "name": "Skåre bytespunkt Ilanda",
    "synonyms": [
      "SKÅRE BYT ILAND",
      "SKÅRE BYTESPUNKT ILANDA",
      "SKÅRE BYTESPUNKT LLANDA",
      "SKÅRE ILANDA",
      "SKÅRE LLANDA"
    ],
    "lId": "25761",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.428888888888885,
      "lon": 13.413333333333334
    }
  },
  {
    "name": "Skäftruna vägskäl",
    "synonyms": [
      "SKÄFTRUNA VÄGSKÄL"
    ],
    "lId": "45185",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.40833333333333,
      "lon": 15.997222222222222
    }
  },
  {
    "name": "Skälby",
    "synonyms": [
      "SKÄLBY",
      "SKÄLBY KONSUM",
      "SKÆLBY",
      "SKÆLBY KONSUM"
    ],
    "lId": "01187",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.39138888888889,
      "lon": 17.849444444444444
    }
  },
  {
    "name": "Skällinge affär",
    "synonyms": [
      "SKÄLLINGE AFFÄR",
      "SKÆLLINGE AFFÆR"
    ],
    "lId": "23701",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 57.1825,
      "lon": 12.467777777777778
    }
  },
  {
    "name": "Skänninge station",
    "synonyms": [
      "SKÄNNINGE STATION",
      "SKÆNNINGE STATION"
    ],
    "lId": "00545",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 58.39277777777778,
      "lon": 15.092500000000001
    }
  },
  {
    "name": "Skär",
    "synonyms": [
      "SKÄR",
      "SKÆR"
    ],
    "lId": "01194",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 57.97777777777778,
      "lon": 19.300555555555555
    }
  },
  {
    "name": "Skärblacka Strömport",
    "synonyms": [
      "SKÄRBLACKA STRÖMPORT",
      "SKÆRBLACKA STRØMPORT"
    ],
    "lId": "00856",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 58.58111111111111,
      "lon": 15.9075
    }
  },
  {
    "name": "Skärgårdsstad",
    "synonyms": [
      "SKÄRGÅRDSSTAD",
      "SKÆRGÅRDSSTAD"
    ],
    "lId": "24824",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.486666666666665,
      "lon": 18.41222222222222
    }
  },
  {
    "name": "Skärhamn",
    "synonyms": [
      "SKÄRHAMN",
      "SKÄRHAMN TORG",
      "SKÆRHAMN",
      "SKÆRHAMN TORG"
    ],
    "lId": "00330",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 57.99111111111111,
      "lon": 11.546111111111111
    }
  },
  {
    "name": "Skärholmen T-bana",
    "synonyms": [
      "SKÄRHOLMEN T-BANA",
      "SKÆRHOLMEN T-BANA"
    ],
    "lId": "21726",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.276944444444446,
      "lon": 17.90694444444444
    }
  },
  {
    "name": "Skärmarbrink T-bana",
    "synonyms": [
      "SKÄRMARBRINK T-BANA",
      "SKÆRMARBRINK T-BANA"
    ],
    "lId": "21704",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.29527777777778,
      "lon": 18.090277777777775
    }
  },
  {
    "name": "Skärplinge bussterminal",
    "synonyms": [
      "SKÄRPLINGE BSTN",
      "SKÄRPLINGE BUSSTERMINAL",
      "SKÆRPLINGE BSTN",
      "SKÆRPLINGE BUSSTERMINAL"
    ],
    "lId": "07180",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 60.47027777777778,
      "lon": 17.758333333333333
    }
  },
  {
    "name": "Skärstad Svängen",
    "synonyms": [
      "SKÄRSTAD SVÄNGEN",
      "SKÆRSTAD SVÆNGEN"
    ],
    "lId": "39510",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 57.88472222222222,
      "lon": 14.360277777777778
    }
  },
  {
    "name": "Skärså",
    "synonyms": [
      "SKÄRSÅ",
      "SKÆRSÅ"
    ],
    "lId": "11429",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 61.379444444444445,
      "lon": 17.10888888888889
    }
  },
  {
    "name": "Skärsätra",
    "synonyms": [
      "SKÄRSÄTRA",
      "SKÆRSÆTRA"
    ],
    "lId": "23965",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.343333333333334,
      "lon": 18.17027777777778
    }
  },
  {
    "name": "Skärvången",
    "synonyms": [
      "SKÄRVÅNGEN",
      "SKÆRVÅNGEN"
    ],
    "lId": "13397",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 63.76222222222222,
      "lon": 14.318055555555555
    }
  },
  {
    "name": "Sköldinge",
    "synonyms": [
      "SKÖLDINGE",
      "SKØLDINGE"
    ],
    "lId": "11430",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.03194444444444,
      "lon": 16.449722222222224
    }
  },
  {
    "name": "Sköllersta skola",
    "synonyms": [
      "SKÖLLERSTA SKOLA",
      "SKØLLERSTA SKOLA"
    ],
    "lId": "49564",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.13666666666666,
      "lon": 15.337777777777779
    }
  },
  {
    "name": "Sköndal",
    "synonyms": [
      "SKÖNDAL",
      "SKÖNDAL CENTRUM",
      "SKØNDAL",
      "SKØNDAL CENTRUM"
    ],
    "lId": "01188",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.255833333333335,
      "lon": 18.113611111111112
    }
  },
  {
    "name": "Skövde C",
    "synonyms": [
      "SKOVDE C",
      "SKÖVDE C",
      "SKØVDE C"
    ],
    "lId": "00008",
    "prio": 1,
    "pId": "074",
    "pos": {
      "lat": 58.39083333333333,
      "lon": 13.853055555555555
    }
  },
  {
    "name": "Slagnäs bensinstation",
    "synonyms": [
      "SLAGNÄS BENSINSTATION",
      "SLAGNÆS BENSINSTATION"
    ],
    "lId": "23836",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 65.58527777777778,
      "lon": 18.16472222222222
    }
  },
  {
    "name": "Slaka skolan",
    "synonyms": [
      "SLAKA SKOLAN"
    ],
    "lId": "23328",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 58.368611111111115,
      "lon": 15.556944444444445
    }
  },
  {
    "name": "Slite",
    "synonyms": [
      "SLITE",
      "SLITE PRESSBYRÅ"
    ],
    "lId": "00973",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 57.70388888888889,
      "lon": 18.800833333333333
    }
  },
  {
    "name": "Slottsbron E45 Åstorpsvägen",
    "synonyms": [
      "SLOTTSBRON 1STP",
      "SLOTTSBRON E45 ÅSTORPSVÄGEN",
      "SLOTTSBRON E45 ÅSTORPSVÆGEN"
    ],
    "lId": "11442",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.323055555555555,
      "lon": 13.107222222222221
    }
  },
  {
    "name": "Slussen T-bana",
    "synonyms": [
      "SLUSSEN",
      "SLUSSEN T",
      "SLUSSEN T-BANA"
    ],
    "lId": "20101",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.31944444444445,
      "lon": 18.072222222222223
    }
  },
  {
    "name": "Slussfors",
    "synonyms": [
      "SLUSSFORS",
      "SLUSSFORS BYN"
    ],
    "lId": "13784",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 65.42888888888889,
      "lon": 16.241666666666667
    }
  },
  {
    "name": "Slussfors E12",
    "synonyms": [
      "SLUSSFORS E12"
    ],
    "lId": "20371",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 65.43,
      "lon": 16.270833333333332
    }
  },
  {
    "name": "Slättingebygd",
    "synonyms": [
      "SLÄTTINGEBYGD",
      "SLÆTTINGEBYGD"
    ],
    "lId": "14367",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 56.843333333333334,
      "lon": 15.98
    }
  },
  {
    "name": "Slättäng väg 26/47",
    "synonyms": [
      "SLÄTTÄNG VÄG 26/47",
      "SLÅTTÅNG VÄG 26/47",
      "SLÆTTÆNG VÆG 26/47"
    ],
    "lId": "23252",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 58.027499999999996,
      "lon": 13.83388888888889
    }
  },
  {
    "name": "Slätviken",
    "synonyms": [
      "SLÄTVIKEN",
      "SLÆTVIKEN"
    ],
    "lId": "11447",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.44444444444444,
      "lon": 16.533611111111114
    }
  },
  {
    "name": "Slöinge Göteborgsvägen",
    "synonyms": [
      "SLÖINGE GÖTEBGV",
      "SLÖINGE GÖTEBORGSVÄGEN",
      "SLØINGE GØTEBGV",
      "SLØINGE GØTEBORGSVÆGEN"
    ],
    "lId": "24856",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 56.85388888888889,
      "lon": 12.693055555555556
    }
  },
  {
    "name": "Smedby centrum",
    "synonyms": [
      "SMEDBY CENTRUM"
    ],
    "lId": "25962",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 56.675,
      "lon": 16.2425
    }
  },
  {
    "name": "Smedby station",
    "synonyms": [
      "SMEDBY STATION"
    ],
    "lId": "38527",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 56.67583333333333,
      "lon": 16.243055555555557
    }
  },
  {
    "name": "Smedjebacken",
    "synonyms": [
      "SMEDJEBACKEN",
      "SMEDJEBACKN STN"
    ],
    "lId": "00062",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 60.13611111111111,
      "lon": 15.405555555555557
    }
  },
  {
    "name": "Smedslätten",
    "synonyms": [
      "SMEDSLÄTTEN",
      "SMEDSLÆTTEN"
    ],
    "lId": "24816",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.32083333333334,
      "lon": 17.964166666666667
    }
  },
  {
    "name": "Smedstorp",
    "synonyms": [
      "SMEDSTORP"
    ],
    "lId": "01307",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 55.54944444444444,
      "lon": 14.1175
    }
  },
  {
    "name": "Smygehamn",
    "synonyms": [
      "SMYGEHAMN",
      "SMYGEHAMN ÄNGAV",
      "SMYGEHAMN ÆNGAV"
    ],
    "lId": "00505",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 55.34527777777778,
      "lon": 13.377500000000001
    }
  },
  {
    "name": "Smådalarö",
    "synonyms": [
      "SMÅDALARÖ",
      "SMÅDALARØ"
    ],
    "lId": "20173",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.16555555555556,
      "lon": 18.45138888888889
    }
  },
  {
    "name": "Smålandsstenar",
    "synonyms": [
      "SMALANDSSTENAR",
      "SMÅLANDSSTENAR"
    ],
    "lId": "00289",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 57.16138888888889,
      "lon": 13.414444444444445
    }
  },
  {
    "name": "Smögen",
    "synonyms": [
      "SMÖGEN",
      "SMÖGEN BSTN",
      "SMØGEN",
      "SMØGEN BSTN"
    ],
    "lId": "00355",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 58.356944444444444,
      "lon": 11.230277777777777
    }
  },
  {
    "name": "Snekkersten",
    "synonyms": [
      "SNEKKERSTEN"
    ],
    "lId": "00668",
    "prio": 0,
    "pId": "086",
    "pos": {
      "lat": 56.009166666666665,
      "lon": 12.583333333333334
    }
  },
  {
    "name": "Snipen",
    "synonyms": [
      "SNIPEN"
    ],
    "lId": "15594",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 57.56194444444444,
      "lon": 11.9475
    }
  },
  {
    "name": "Snogeröd affären",
    "synonyms": [
      "SNOGERÖD AFFÄREN",
      "SNOGERØD AFFÆREN"
    ],
    "lId": "25961",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 55.83916666666667,
      "lon": 13.492222222222221
    }
  },
  {
    "name": "Snöveltorp",
    "synonyms": [
      "SNÖVELTORP",
      "SNØVELTORP"
    ],
    "lId": "54815",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 58.49888888888889,
      "lon": 16.16861111111111
    }
  },
  {
    "name": "Sockenplan T-bana",
    "synonyms": [
      "SOCKENPLAN T-BANA"
    ],
    "lId": "21708",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.283055555555556,
      "lon": 18.070555555555554
    }
  },
  {
    "name": "Solberg",
    "synonyms": [
      "SOLBERG",
      "SOLBERG ICA"
    ],
    "lId": "01308",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 63.78777777777778,
      "lon": 17.641666666666666
    }
  },
  {
    "name": "Solberga Sundsvägen Småland",
    "synonyms": [
      "SOLBERGA SUNDSVÄGEN SMÅLAND",
      "SOLBERGA SUNDSVÆGEN SMÅLAND"
    ],
    "lId": "24357",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 57.73277777777778,
      "lon": 14.74472222222222
    }
  },
  {
    "name": "Sollebrunn",
    "synonyms": [
      "SOLLEBRUNN",
      "SOLLEBRUNN BSTN"
    ],
    "lId": "00113",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 58.118611111111115,
      "lon": 12.533888888888889
    }
  },
  {
    "name": "Sollefteå",
    "synonyms": [
      "SOLLEFTEA",
      "SOLLEFTEÅ",
      "SOLLEFTEÅ STN"
    ],
    "lId": "00043",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 63.18833333333333,
      "lon": 17.236944444444447
    }
  },
  {
    "name": "Sollenkroka",
    "synonyms": [
      "SOLLENKROKA",
      "SOLLENKROKA BRY"
    ],
    "lId": "01309",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.37277777777778,
      "lon": 18.698611111111113
    }
  },
  {
    "name": "Sollentuna",
    "synonyms": [
      "SOLLENTUNA",
      "SOLLENTUNA STN"
    ],
    "lId": "00758",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.42861111111111,
      "lon": 17.947777777777777
    }
  },
  {
    "name": "Sollerön",
    "synonyms": [
      "SOLLERÖN",
      "SOLLERÖN CM",
      "SOLLERØN",
      "SOLLERØN CM"
    ],
    "lId": "00051",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 60.915277777777774,
      "lon": 14.617222222222223
    }
  },
  {
    "name": "Solna business park Spårv",
    "synonyms": [
      "SOLNA BUSINESS PARK SPÅRV"
    ],
    "lId": "64052",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.359722222222224,
      "lon": 17.97861111111111
    }
  },
  {
    "name": "Solna centrum T-bana",
    "synonyms": [
      "SOLNA CENTRUM T-BANA"
    ],
    "lId": "21642",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.35861111111111,
      "lon": 17.99888888888889
    }
  },
  {
    "name": "Solna station",
    "synonyms": [
      "SOLNA STATION",
      "SOLNA STN"
    ],
    "lId": "00759",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.365,
      "lon": 18.01
    }
  },
  {
    "name": "Solna strand T-bana",
    "synonyms": [
      "SOLNA STRAND T-BANA"
    ],
    "lId": "21671",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.35416666666667,
      "lon": 17.973888888888887
    }
  },
  {
    "name": "Solsidan",
    "synonyms": [
      "SOLSIDAN",
      "SOLSIDAN STN"
    ],
    "lId": "01150",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.270833333333336,
      "lon": 18.295833333333334
    }
  },
  {
    "name": "Solvalla",
    "synonyms": [
      "SOLVALLA"
    ],
    "lId": "49186",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.361111111111114,
      "lon": 17.94
    }
  },
  {
    "name": "Sommen",
    "synonyms": [
      "SOMMEN",
      "SOMMEN STN"
    ],
    "lId": "00862",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 58.138888888888886,
      "lon": 14.966666666666667
    }
  },
  {
    "name": "Sonstorp Bangrindarna",
    "synonyms": [
      "SONSTORP BANGRINDARNA"
    ],
    "lId": "23314",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 58.719722222222224,
      "lon": 15.644444444444444
    }
  },
  {
    "name": "Sorsele busstation",
    "synonyms": [
      "SORSELE BUSSTATION"
    ],
    "lId": "13636",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 65.53611111111111,
      "lon": 17.530833333333334
    }
  },
  {
    "name": "Sorunda",
    "synonyms": [
      "SORUNDA",
      "SORUNDA SPÅNGBR"
    ],
    "lId": "00761",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.00805555555556,
      "lon": 17.80527777777778
    }
  },
  {
    "name": "Sotholmen",
    "synonyms": [
      "SOTHOLMEN"
    ],
    "lId": "69624",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.04555555555555,
      "lon": 18.00777777777778
    }
  },
  {
    "name": "Sparreholm",
    "synonyms": [
      "SPARREHOLM"
    ],
    "lId": "11458",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.07277777777778,
      "lon": 16.83222222222222
    }
  },
  {
    "name": "Sparreholm Fabriken",
    "synonyms": [
      "SPARREHOLM FABRIKEN"
    ],
    "lId": "72320",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.07888888888889,
      "lon": 16.828055555555554
    }
  },
  {
    "name": "Spenshult sjukhus",
    "synonyms": [
      "SPENSHULT SJUKH",
      "SPENSHULT SJUKHUS"
    ],
    "lId": "01310",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 56.85,
      "lon": 13.017222222222223
    }
  },
  {
    "name": "Spiken",
    "synonyms": [
      "SPIKEN"
    ],
    "lId": "00507",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 58.689166666666665,
      "lon": 13.200277777777776
    }
  },
  {
    "name": "Spillersboda bryggan",
    "synonyms": [
      "SPILLERSBODA BRYGGAN"
    ],
    "lId": "11461",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.70027777777778,
      "lon": 18.855555555555558
    }
  },
  {
    "name": "Spjutsbygd",
    "synonyms": [
      "SPJUTSBYGD"
    ],
    "lId": "11462",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 56.311388888888885,
      "lon": 15.59388888888889
    }
  },
  {
    "name": "Spjutstorp Henrik Olsson",
    "synonyms": [
      "SPJUTSTORP HENRIK OLSSON"
    ],
    "lId": "04167",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 55.58111111111111,
      "lon": 14.015277777777778
    }
  },
  {
    "name": "Sproge",
    "synonyms": [
      "SPROGE"
    ],
    "lId": "01311",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 57.25388888888889,
      "lon": 18.209722222222222
    }
  },
  {
    "name": "Sprängsviken",
    "synonyms": [
      "SPRÄNGSVIKEN",
      "SPRÆNGSVIKEN"
    ],
    "lId": "01499",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 62.859722222222224,
      "lon": 17.87027777777778
    }
  },
  {
    "name": "Spånga",
    "synonyms": [
      "SPÅNGA",
      "SPÅNGA STN"
    ],
    "lId": "00764",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.38305555555556,
      "lon": 17.898611111111112
    }
  },
  {
    "name": "Spångenäs station",
    "synonyms": [
      "SPÅNGENÄS STATION"
    ],
    "lId": "14369",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 57.59916666666667,
      "lon": 16.099166666666665
    }
  },
  {
    "name": "Spångsholm bruk",
    "synonyms": [
      "SPÅNGSHOLM BRUK"
    ],
    "lId": "11465",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 58.348888888888894,
      "lon": 15.227222222222222
    }
  },
  {
    "name": "Staa",
    "synonyms": [
      "STAA"
    ],
    "lId": "13293",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 63.40333333333333,
      "lon": 12.81638888888889
    }
  },
  {
    "name": "Staby Bro",
    "synonyms": [
      "STABY BRO"
    ],
    "lId": "53831",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 58.433055555555555,
      "lon": 15.683055555555555
    }
  },
  {
    "name": "Stadion T-bana",
    "synonyms": [
      "STADION T-BANA"
    ],
    "lId": "21647",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.34277777777778,
      "lon": 18.081666666666667
    }
  },
  {
    "name": "Stadra",
    "synonyms": [
      "STADRA"
    ],
    "lId": "11474",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.562777777777775,
      "lon": 14.73611111111111
    }
  },
  {
    "name": "Stadshagen T-bana",
    "synonyms": [
      "STADSHAGEN T-BANA"
    ],
    "lId": "21662",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.33694444444445,
      "lon": 18.01722222222222
    }
  },
  {
    "name": "Staffanstorp Storgatan",
    "synonyms": [
      "STAFFANSTORP STORGATAN",
      "STAFFANSTRP STG"
    ],
    "lId": "00951",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 55.64111111111111,
      "lon": 13.205
    }
  },
  {
    "name": "Stallarholmen busstation",
    "synonyms": [
      "STALLARHOLMEN BUSSTATION"
    ],
    "lId": "11476",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.36694444444444,
      "lon": 17.2075
    }
  },
  {
    "name": "Stalon",
    "synonyms": [
      "STALON"
    ],
    "lId": "13908",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 64.93861111111111,
      "lon": 15.859444444444444
    }
  },
  {
    "name": "Stavre station",
    "synonyms": [
      "STAVRE STATION",
      "STAVRE STN"
    ],
    "lId": "00686",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 62.82944444444445,
      "lon": 15.304722222222223
    }
  },
  {
    "name": "Stavreviken",
    "synonyms": [
      "STAVREVIKEN"
    ],
    "lId": "15290",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 62.551944444444445,
      "lon": 17.40833333333333
    }
  },
  {
    "name": "Stavsjö",
    "synonyms": [
      "STAVSJÖ",
      "STAVSJØ"
    ],
    "lId": "11480",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 58.724444444444444,
      "lon": 16.41611111111111
    }
  },
  {
    "name": "Stavsnäs",
    "synonyms": [
      "STAVSNÄS",
      "STAVSNÄS VIHAMN",
      "STAVSNÆS",
      "STAVSNÆS VIHAMN"
    ],
    "lId": "01312",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.28611111111111,
      "lon": 18.705
    }
  },
  {
    "name": "Stavsudda norra",
    "synonyms": [
      "STAVSUDDA NORRA"
    ],
    "lId": "24913",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.40416666666667,
      "lon": 18.779999999999998
    }
  },
  {
    "name": "Stehag",
    "synonyms": [
      "STEHAG",
      "STEHAG STN"
    ],
    "lId": "00952",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 55.900555555555556,
      "lon": 13.39472222222222
    }
  },
  {
    "name": "Stenared",
    "synonyms": [
      "STENARED"
    ],
    "lId": "01500",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 57.80722222222222,
      "lon": 12.186388888888889
    }
  },
  {
    "name": "Stenbacken",
    "synonyms": [
      "STENBACKEN",
      "STENBACKEN STN"
    ],
    "lId": "00582",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 68.24916666666667,
      "lon": 19.504166666666666
    }
  },
  {
    "name": "Stendörren",
    "synonyms": [
      "STENDÖRREN",
      "STENDØRREN"
    ],
    "lId": "38562",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 58.76583333333333,
      "lon": 17.372777777777777
    }
  },
  {
    "name": "Stenhamra",
    "synonyms": [
      "STENHAMRA",
      "STENHAMRA SOLBA"
    ],
    "lId": "01313",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.340833333333336,
      "lon": 17.695555555555554
    }
  },
  {
    "name": "Steninge",
    "synonyms": [
      "STENINGE"
    ],
    "lId": "01314",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 56.76305555555555,
      "lon": 12.633888888888889
    }
  },
  {
    "name": "Stenkullen",
    "synonyms": [
      "STENKULLEN",
      "STENKULLEN STN"
    ],
    "lId": "01315",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 57.791666666666664,
      "lon": 12.314722222222223
    }
  },
  {
    "name": "Stenkyrka",
    "synonyms": [
      "STENKYRKA",
      "STENKYRKA AFFÄR",
      "STENKYRKA AFFÆR"
    ],
    "lId": "01316",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 57.799166666666665,
      "lon": 18.513055555555557
    }
  },
  {
    "name": "Stensele",
    "synonyms": [
      "STENSELE"
    ],
    "lId": "01140",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 65.07055555555556,
      "lon": 17.139444444444443
    }
  },
  {
    "name": "Stensjön station",
    "synonyms": [
      "STENSJON  STATION",
      "STENSJÖN STATION",
      "STENSJÖN STN",
      "STENSJØN  STATION",
      "STENSJØN STN"
    ],
    "lId": "00974",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 57.5825,
      "lon": 14.822777777777777
    }
  },
  {
    "name": "Stenslätten",
    "synonyms": [
      "STENSLÄTTEN",
      "STENSLÆTTEN"
    ],
    "lId": "18270",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.39666666666667,
      "lon": 18.449722222222224
    }
  },
  {
    "name": "Stenstorp",
    "synonyms": [
      "STENSTORP",
      "STENSTORP STN"
    ],
    "lId": "00924",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 58.27361111111111,
      "lon": 13.714722222222221
    }
  },
  {
    "name": "Stenungsund",
    "synonyms": [
      "STENUNGSUND",
      "STENUNGSUND STN"
    ],
    "lId": "00014",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 58.072500000000005,
      "lon": 11.824722222222222
    }
  },
  {
    "name": "Stenungsön",
    "synonyms": [
      "STENUNGSÖN",
      "STENUNGSØN"
    ],
    "lId": "15750",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 58.06527777777777,
      "lon": 11.805000000000001
    }
  },
  {
    "name": "Stenvred vändplan",
    "synonyms": [
      "STENVRED VÄNDPLAN",
      "STENVRED VÆNDPLAN"
    ],
    "lId": "21294",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.13333333333333,
      "lon": 15.794722222222221
    }
  },
  {
    "name": "Stenåsa kyrka",
    "synonyms": [
      "STENÅSA KYRKA"
    ],
    "lId": "14371",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 56.515,
      "lon": 16.601666666666667
    }
  },
  {
    "name": "Sticklinge",
    "synonyms": [
      "STICKLINGE"
    ],
    "lId": "24783",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.38611111111111,
      "lon": 18.105555555555558
    }
  },
  {
    "name": "Stidsvig Skogsbrynsvägen",
    "synonyms": [
      "STIDSVIG SKOGSBRYNSVÄGEN",
      "STIDSVIG SKOGSBRYNSVÆGEN"
    ],
    "lId": "16892",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 56.20027777777778,
      "lon": 13.123611111111112
    }
  },
  {
    "name": "Stigen",
    "synonyms": [
      "STIGEN",
      "STIGEN CENTRUM"
    ],
    "lId": "01501",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 58.56638888888889,
      "lon": 12.065277777777778
    }
  },
  {
    "name": "Stigtomta",
    "synonyms": [
      "STIGTOMTA",
      "STIGTOMTA TÄNGS",
      "STIGTOMTA TÆNGS"
    ],
    "lId": "00836",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 58.803888888888885,
      "lon": 16.781666666666666
    }
  },
  {
    "name": "Stjerneskolan",
    "synonyms": [
      "STJERNESKOLAN"
    ],
    "lId": "01410",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 60.13916666666667,
      "lon": 13.011111111111111
    }
  },
  {
    "name": "Stjärnhov",
    "synonyms": [
      "STJÄRNHOV",
      "STJÆRNHOV"
    ],
    "lId": "11497",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.07888888888889,
      "lon": 17.013055555555557
    }
  },
  {
    "name": "Stjärnsund Sandvika",
    "synonyms": [
      "STJÄRNSUND SANDVIKA",
      "STJÆRNSUND SANDVIKA"
    ],
    "lId": "25080",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 60.42944444444444,
      "lon": 16.2275
    }
  },
  {
    "name": "Stoby Lövstigen",
    "synonyms": [
      "STOBY LÖVSTIGEN",
      "STOBY LØVSTIGEN"
    ],
    "lId": "23493",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 56.17444444444444,
      "lon": 13.826944444444445
    }
  },
  {
    "name": "Stocka",
    "synonyms": [
      "STOCKA"
    ],
    "lId": "23370",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 61.8975,
      "lon": 17.33722222222222
    }
  },
  {
    "name": "Stockamöllan Stenbocksliden",
    "synonyms": [
      "STOCKAMÖLLAN STENBOCKSLIDEN",
      "STOCKAMØLLAN STENBOCKSLIDEN"
    ],
    "lId": "16893",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 55.945277777777775,
      "lon": 13.375277777777779
    }
  },
  {
    "name": "Stockaryd",
    "synonyms": [
      "STOCKARYD",
      "STOCKARYD STN"
    ],
    "lId": "01318",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 57.31333333333333,
      "lon": 14.591666666666667
    }
  },
  {
    "name": "Stockholm C",
    "synonyms": [
      "STOCKHOLM C",
      "STOCKHOLM CENTRAL",
      "XEV"
    ],
    "lId": "00001",
    "prio": 500,
    "pId": "074",
    "pos": {
      "lat": 59.330000000000005,
      "lon": 18.058055555555555
    }
  },
  {
    "name": "Stockholm Bellmansro",
    "synonyms": [
      "STOCKHOLM BELLMANSRO"
    ],
    "lId": "46067",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.323888888888895,
      "lon": 18.110277777777778
    }
  },
  {
    "name": "Stockholm Blockhusudden",
    "synonyms": [
      "STOCKHOLM BLOCKHUSUDDEN"
    ],
    "lId": "18279",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.321111111111115,
      "lon": 18.154166666666665
    }
  },
  {
    "name": "Stockholm Djurgårdsbron",
    "synonyms": [
      "STOCKHOLM DJURGÅRDSBRON"
    ],
    "lId": "46036",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.33166666666667,
      "lon": 18.093333333333334
    }
  },
  {
    "name": "Stockholm Djurgårdsskolan",
    "synonyms": [
      "STOCKHOLM DJURGÅRDSSKOLAN"
    ],
    "lId": "46066",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.323055555555555,
      "lon": 18.104722222222225
    }
  },
  {
    "name": "Stockholm Ersta sjukhus",
    "synonyms": [
      "STOCKHOLM ERSTA SJUKHUS"
    ],
    "lId": "46051",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.31527777777777,
      "lon": 18.08972222222222
    }
  },
  {
    "name": "Stockholm Frihamnen",
    "synonyms": [
      "STHLM FRIHAMNEN",
      "STOCKHOLM FRIHAMNEN"
    ],
    "lId": "01174",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.34138888888889,
      "lon": 18.11777777777778
    }
  },
  {
    "name": "Stockholm Gröna Lund",
    "synonyms": [
      "GRÖNA LUND",
      "GRØNA LUND",
      "STOCKHOLM GRÖNA LUND",
      "STOCKHOLM GRØNA LUND"
    ],
    "lId": "18282",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.325,
      "lon": 18.096944444444443
    }
  },
  {
    "name": "Stockholm Kaknästornet",
    "synonyms": [
      "KAKNÄSTORNET",
      "KAKNÆSTORNET",
      "STOCKHOLM KAKNÄSTORNET",
      "STOCKHOLM KAKNÆSTORNET"
    ],
    "lId": "18283",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.333333333333336,
      "lon": 18.12472222222222
    }
  },
  {
    "name": "Stockholm Klara Mälarstrand",
    "synonyms": [
      "STOCKHOLM KLARA MÄLARSTRAND"
    ],
    "lId": "12144",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.32777777777778,
      "lon": 18.058055555555555
    }
  },
  {
    "name": "Stockholm Kungsträdgården",
    "synonyms": [
      "STOCKHOLM KUNGSTRÄDGÅRDEN"
    ],
    "lId": "37355",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.33277777777778,
      "lon": 18.07111111111111
    }
  },
  {
    "name": "Stockholm Nordiska museet/Vasa",
    "synonyms": [
      "STOCKHOLM NORDISKA MUSEET/VASA"
    ],
    "lId": "46031",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.32916666666667,
      "lon": 18.095277777777778
    }
  },
  {
    "name": "Stockholm Norrmalmstorg Spårv",
    "synonyms": [
      "STOCKHOLM NORRMALMSTORG SPÅRV"
    ],
    "lId": "45943",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.333333333333336,
      "lon": 18.07361111111111
    }
  },
  {
    "name": "Stockholm Nybroplan",
    "synonyms": [
      "STOCKHOLM NYBROPLAN"
    ],
    "lId": "19408",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.3325,
      "lon": 18.07638888888889
    }
  },
  {
    "name": "Stockholm Sabbatsbergs sjukhus",
    "synonyms": [
      "STOCKHOLM SABBATSBERGS SJUKHUS"
    ],
    "lId": "46061",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.33888888888889,
      "lon": 18.048333333333336
    }
  },
  {
    "name": "Stockholm Sergels Torg Spårv",
    "synonyms": [
      "STOCKHOLM SERGELS TORG SPÅRV"
    ],
    "lId": "35997",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.3325,
      "lon": 18.066111111111113
    }
  },
  {
    "name": "Stockholm Skansen",
    "synonyms": [
      "SKANSEN",
      "STOCKHOLM SKANSEN"
    ],
    "lId": "18281",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.323888888888895,
      "lon": 18.10138888888889
    }
  },
  {
    "name": "Stockholm Strömkajen",
    "synonyms": [
      "STOCKHOLM STRÖMKAJEN",
      "STOCKHOLM STRØMKAJEN"
    ],
    "lId": "20691",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.32916666666667,
      "lon": 18.075277777777778
    }
  },
  {
    "name": "Stockholm Styrmansgatan",
    "synonyms": [
      "STOCKHOLM STYRMANSGATAN"
    ],
    "lId": "46065",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.331388888888895,
      "lon": 18.084444444444443
    }
  },
  {
    "name": "Stockholm Södra",
    "synonyms": [
      "STOCKHOLM SÖDRA",
      "STOCKHOLM SØDRA"
    ],
    "lId": "00765",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.314166666666665,
      "lon": 18.064444444444444
    }
  },
  {
    "name": "Stockholm Tegelvikshamnen",
    "synonyms": [
      "STOCKHOLM TEGELVIKSHAMNEN",
      "TEGELVIKSHAMNEN"
    ],
    "lId": "01265",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.31583333333333,
      "lon": 18.09638888888889
    }
  },
  {
    "name": "Stockholm Vattugatan",
    "synonyms": [
      "STHLMVATTUGATAN",
      "STOCKHOLM VATTUGATAN"
    ],
    "lId": "69350",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.32944444444445,
      "lon": 18.060833333333335
    }
  },
  {
    "name": "Stockholm Värtahamnen",
    "synonyms": [
      "STOCKHOLM VÄRTAHAMNEN",
      "STOCKHOLM VÆRTAHAMNEN",
      "VÄRTAHAMNEN",
      "VÆRTAHAMNEN"
    ],
    "lId": "01386",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.35,
      "lon": 18.106944444444444
    }
  },
  {
    "name": "Stockholm Waldemarsudde",
    "synonyms": [
      "STOCKHOLM WALDEMARSUDDE"
    ],
    "lId": "18280",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.322500000000005,
      "lon": 18.111111111111114
    }
  },
  {
    "name": "Stockholm Zon A",
    "synonyms": [
      "STOCKHOLM INNERSTAD",
      "STOCKHOLM ZON A"
    ],
    "lId": "01317",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.331388888888895,
      "lon": 18.060000000000002
    }
  },
  {
    "name": "Stockholm zon ABC",
    "synonyms": [
      "STOCKHOLM ZON ABC"
    ],
    "lId": "79004",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.331388888888895,
      "lon": 18.060000000000002
    }
  },
  {
    "name": "Stocksund station",
    "synonyms": [
      "STOCKSUND STATION",
      "STOCKSUND STN"
    ],
    "lId": "21643",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.385,
      "lon": 18.04388888888889
    }
  },
  {
    "name": "Stockvik E4",
    "synonyms": [
      "STOCKVIK E4"
    ],
    "lId": "26930",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 62.33361111111111,
      "lon": 17.360277777777778
    }
  },
  {
    "name": "Stora Beddinge",
    "synonyms": [
      "STORA BEDDINGE"
    ],
    "lId": "16875",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 55.394999999999996,
      "lon": 13.446111111111112
    }
  },
  {
    "name": "Stora Blåsjön",
    "synonyms": [
      "STORA BLÅSJÖN",
      "STORA BLÅSJØN"
    ],
    "lId": "00453",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 64.83638888888889,
      "lon": 14.08361111111111
    }
  },
  {
    "name": "Stora Dyrön norra",
    "synonyms": [
      "ST DYRÖN NORRA",
      "ST DYRØN NORRA",
      "STORA DYRÖN NORRA",
      "STORA DYRØN NORRA"
    ],
    "lId": "15793",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 57.92944444444444,
      "lon": 11.601111111111111
    }
  },
  {
    "name": "Stora Essingen",
    "synonyms": [
      "STORA ESSINGEN"
    ],
    "lId": "24924",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.32472222222223,
      "lon": 17.99277777777778
    }
  },
  {
    "name": "Stora Frö",
    "synonyms": [
      "STORA FRÖ"
    ],
    "lId": "14349",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 56.57083333333334,
      "lon": 16.421666666666667
    }
  },
  {
    "name": "Stora Herrestad södra",
    "synonyms": [
      "ST HERRESTAD S",
      "STORA HERRESTAD SÖDRA",
      "STORA HERRESTAD SØDRA"
    ],
    "lId": "24986",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 55.47083333333334,
      "lon": 13.871666666666668
    }
  },
  {
    "name": "Stora Höga",
    "synonyms": [
      "STORA HÖGA",
      "STORA HÖGA STN",
      "STORA HØGA",
      "STORA HØGA STN"
    ],
    "lId": "00859",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 58.018055555555556,
      "lon": 11.835277777777778
    }
  },
  {
    "name": "Stora Köpinge",
    "synonyms": [
      "STORA KÖPINGE",
      "STORA KØPINGE"
    ],
    "lId": "10746",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 55.471111111111114,
      "lon": 13.946388888888889
    }
  },
  {
    "name": "Stora Levene",
    "synonyms": [
      "ST LEVENE STN",
      "STORA LEVENE"
    ],
    "lId": "00813",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 58.325833333333335,
      "lon": 12.925555555555555
    }
  },
  {
    "name": "Stora Mellby",
    "synonyms": [
      "STORA MELLBY"
    ],
    "lId": "12511",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 58.14194444444444,
      "lon": 12.580833333333333
    }
  },
  {
    "name": "Stora Mellösa",
    "synonyms": [
      "STORA MELLÖSA",
      "STORA MELLØSA"
    ],
    "lId": "01319",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.20888888888889,
      "lon": 15.499722222222221
    }
  },
  {
    "name": "Stora mossen T-bana",
    "synonyms": [
      "STORA MOSSEN T",
      "STORA MOSSEN T-BANA"
    ],
    "lId": "21690",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.33444444444444,
      "lon": 17.96611111111111
    }
  },
  {
    "name": "Stora Sjöfallet",
    "synonyms": [
      "STORA SJÖFALLET",
      "STORA SJØFALLET"
    ],
    "lId": "01215",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 67.4825,
      "lon": 18.359722222222224
    }
  },
  {
    "name": "Stora Skedvi skolan",
    "synonyms": [
      "ST SKEDVI SKOLA",
      "STORA SKEDVI SKOLAN"
    ],
    "lId": "22651",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 60.40472222222222,
      "lon": 15.808611111111112
    }
  },
  {
    "name": "Stora Vika",
    "synonyms": [
      "STORA VIKA"
    ],
    "lId": "01320",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 58.9525,
      "lon": 17.790277777777778
    }
  },
  {
    "name": "Stordalen",
    "synonyms": [
      "STORDALEN",
      "STORDALEN STN"
    ],
    "lId": "01436",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 68.3436111111111,
      "lon": 19.066666666666666
    }
  },
  {
    "name": "Storebro centrum",
    "synonyms": [
      "STOREBRO CENTRUM",
      "STOREBRO CM"
    ],
    "lId": "14373",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 57.588055555555556,
      "lon": 15.842222222222222
    }
  },
  {
    "name": "Storfors station",
    "synonyms": [
      "STORFORS STATION",
      "STORFORS STN"
    ],
    "lId": "00347",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.533055555555556,
      "lon": 14.27138888888889
    }
  },
  {
    "name": "Storhallen",
    "synonyms": [
      "STORHALLEN"
    ],
    "lId": "13352",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 62.68611111111111,
      "lon": 14.284722222222221
    }
  },
  {
    "name": "Storhogna Hotell",
    "synonyms": [
      "STORHOGNA HOTELL"
    ],
    "lId": "23989",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 62.50388888888889,
      "lon": 14.098333333333334
    }
  },
  {
    "name": "Storhogna M",
    "synonyms": [
      "STORHOGNA M"
    ],
    "lId": "72520",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 62.50388888888889,
      "lon": 14.098333333333334
    }
  },
  {
    "name": "Storholmsjö",
    "synonyms": [
      "STORHOLMSJÖ",
      "STORHOLMSJØ"
    ],
    "lId": "20863",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 63.67944444444444,
      "lon": 14.335277777777778
    }
  },
  {
    "name": "Storhögen",
    "synonyms": [
      "STORHÖGEN",
      "STORHØGEN"
    ],
    "lId": "13238",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 63.37083333333334,
      "lon": 15.186666666666667
    }
  },
  {
    "name": "Storlien",
    "synonyms": [
      "STORLIEN",
      "STORLIEN STN"
    ],
    "lId": "00025",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 63.31583333333333,
      "lon": 12.09888888888889
    }
  },
  {
    "name": "Storsjö",
    "synonyms": [
      "STORSJÖ",
      "STORSJØ"
    ],
    "lId": "01321",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 62.80083333333333,
      "lon": 13.053333333333335
    }
  },
  {
    "name": "Storuman station",
    "synonyms": [
      "STORUMAN STATION",
      "STORUMAN STN"
    ],
    "lId": "00428",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 65.09694444444445,
      "lon": 17.112222222222222
    }
  },
  {
    "name": "Storvallen",
    "synonyms": [
      "STORVALLEN"
    ],
    "lId": "13532",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 63.28472222222222,
      "lon": 12.125555555555556
    }
  },
  {
    "name": "Storvik",
    "synonyms": [
      "STORVIK",
      "STORVIK STN"
    ],
    "lId": "00244",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 60.581944444444446,
      "lon": 16.534722222222225
    }
  },
  {
    "name": "Storvik Centralvägen",
    "synonyms": [
      "STORVIK CENTRALVÄGEN",
      "STORVIK CENTRALVÆGEN",
      "STORVIK CENTRV"
    ],
    "lId": "20163",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 60.583333333333336,
      "lon": 16.52861111111111
    }
  },
  {
    "name": "Storvreta",
    "synonyms": [
      "STORVRETA"
    ],
    "lId": "00392",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.95583333333334,
      "lon": 17.70583333333333
    }
  },
  {
    "name": "Storå station",
    "synonyms": [
      "STORÅ STATION"
    ],
    "lId": "01567",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.71361111111111,
      "lon": 15.143055555555556
    }
  },
  {
    "name": "Storängen",
    "synonyms": [
      "STORÄNGEN",
      "STORÄNGEN STN",
      "STORÆNGEN",
      "STORÆNGEN STN"
    ],
    "lId": "24809",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.30555555555555,
      "lon": 18.17777777777778
    }
  },
  {
    "name": "Strand",
    "synonyms": [
      "STRAND"
    ],
    "lId": "13196",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 63.89722222222222,
      "lon": 15.531666666666668
    }
  },
  {
    "name": "Straumsnes",
    "synonyms": [
      "STRAUMSNES"
    ],
    "lId": "02403",
    "prio": 0,
    "pId": "076",
    "pos": {
      "lat": 68.42527777777778,
      "lon": 17.6225
    }
  },
  {
    "name": "Stretered",
    "synonyms": [
      "STRETERED"
    ],
    "lId": "59885",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 57.60583333333334,
      "lon": 12.074166666666667
    }
  },
  {
    "name": "Striberg Franssons backe",
    "synonyms": [
      "STRIBERG FRANSB",
      "STRIBERG FRANSSONS BACKE"
    ],
    "lId": "24418",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.54388888888889,
      "lon": 14.924722222222222
    }
  },
  {
    "name": "Strålsnäs station",
    "synonyms": [
      "STRÅLSNÄS STATION",
      "STRÅLSNÄS STN",
      "STRÅLSNÆS STATION",
      "STRÅLSNÆS STN"
    ],
    "lId": "11514",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 58.236111111111114,
      "lon": 15.093055555555557
    }
  },
  {
    "name": "Strångsjö",
    "synonyms": [
      "STRÅNGSJÖ",
      "STRÅNGSJØ"
    ],
    "lId": "11515",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 58.90277777777778,
      "lon": 16.192777777777778
    }
  },
  {
    "name": "Stråssa",
    "synonyms": [
      "STRÅSSA"
    ],
    "lId": "01322",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.73916666666667,
      "lon": 15.194166666666668
    }
  },
  {
    "name": "Strängnäs",
    "synonyms": [
      "STRANGNAS",
      "STRÄNGNÄS",
      "STRÄNGNÄS STN",
      "STRÆNGNÆS",
      "STRÆNGNÆS STN",
      "XFH"
    ],
    "lId": "00108",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.37027777777778,
      "lon": 17.02777777777778
    }
  },
  {
    "name": "Strängnäs Tosterö skola",
    "synonyms": [
      "STRÄNGNÄS TOSTERÖ SKOLA",
      "STRÆNGNÆS TOSTERØ SKOLA"
    ],
    "lId": "10002",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.393055555555556,
      "lon": 17.02861111111111
    }
  },
  {
    "name": "Strängsmåla",
    "synonyms": [
      "STRÄNGSMÅLA",
      "STRÆNGSMÅLA"
    ],
    "lId": "14381",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 56.56666666666667,
      "lon": 15.448055555555555
    }
  },
  {
    "name": "Strömma Värmdö",
    "synonyms": [
      "STRÖMMA VÄRMDÖ",
      "STRØMMA VÆRMDØ"
    ],
    "lId": "25717",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.28638888888889,
      "lon": 18.546666666666667
    }
  },
  {
    "name": "Strömsbruk",
    "synonyms": [
      "STRÖMSBRUK",
      "STRØMSBRUK"
    ],
    "lId": "23371",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 61.86944444444445,
      "lon": 17.316111111111113
    }
  },
  {
    "name": "Strömsfors vägskäl",
    "synonyms": [
      "STRÖMSFORS VSK",
      "STRÖMSFORS VÄGSKÄL",
      "STRØMSFORS VSK",
      "STRØMSFORS VÆGSKÆL"
    ],
    "lId": "01323",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 58.68694444444444,
      "lon": 16.343055555555555
    }
  },
  {
    "name": "Strömsholm",
    "synonyms": [
      "STRÖMSHOLM",
      "STRØMSHOLM"
    ],
    "lId": "11523",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.52194444444444,
      "lon": 16.254722222222224
    }
  },
  {
    "name": "Strömsnäs",
    "synonyms": [
      "STRÖMSNÄS",
      "STRÖMSNÄS Ö VSK",
      "STRØMSNÆS",
      "STRØMSNÆS Ø VSK"
    ],
    "lId": "13250",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 63.172777777777775,
      "lon": 15.874166666666667
    }
  },
  {
    "name": "Strömsnäsbruk",
    "synonyms": [
      "STRÖMSNÄSBRUK",
      "STRØMSNÆSBRUK"
    ],
    "lId": "00136",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 56.550555555555555,
      "lon": 13.731944444444444
    }
  },
  {
    "name": "Strömstad",
    "synonyms": [
      "STROMSTAD",
      "STRÖMSTAD",
      "STRÖMSTAD STN",
      "STRØMSTAD",
      "STRØMSTAD STN"
    ],
    "lId": "00095",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 58.936388888888885,
      "lon": 11.173055555555555
    }
  },
  {
    "name": "Strömsund",
    "synonyms": [
      "STRÖMSUND",
      "STRÖMSUND BSTN",
      "STRØMSUND",
      "STRØMSUND BSTN"
    ],
    "lId": "00421",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 63.849722222222226,
      "lon": 15.554722222222223
    }
  },
  {
    "name": "Strövelstorp Klockarevägen",
    "synonyms": [
      "STRÖVELSTORP KLOCKAREVÄGEN",
      "STRØVELSTORP KLOCKAREVÆGEN"
    ],
    "lId": "11525",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 56.16888888888889,
      "lon": 12.835277777777778
    }
  },
  {
    "name": "Studsvik",
    "synonyms": [
      "STUDSVIK"
    ],
    "lId": "11527",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 58.7675,
      "lon": 17.3825
    }
  },
  {
    "name": "Stugun",
    "synonyms": [
      "STUGUN"
    ],
    "lId": "00454",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 63.1675,
      "lon": 15.596388888888889
    }
  },
  {
    "name": "Stureby T-bana",
    "synonyms": [
      "STUREBY T-BANA"
    ],
    "lId": "21710",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.27444444444444,
      "lon": 18.055555555555557
    }
  },
  {
    "name": "Sturefors Centrum",
    "synonyms": [
      "STUREFORS CENTRUM",
      "STUREFORS CM"
    ],
    "lId": "20330",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 58.336666666666666,
      "lon": 15.720555555555556
    }
  },
  {
    "name": "Sturkö",
    "synonyms": [
      "STURKÖ",
      "STURKÖ KVARN",
      "STURKØ",
      "STURKØ KVARN"
    ],
    "lId": "00469",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 56.11277777777778,
      "lon": 15.681388888888888
    }
  },
  {
    "name": "Stuvsta",
    "synonyms": [
      "STUVSTA",
      "STUVSTA STN"
    ],
    "lId": "00772",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.253055555555555,
      "lon": 17.995555555555555
    }
  },
  {
    "name": "Styrnäs kyrka",
    "synonyms": [
      "STYRNÄS KYRKA",
      "STYRNÆS KYRKA"
    ],
    "lId": "15297",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 63.08722222222222,
      "lon": 17.775555555555556
    }
  },
  {
    "name": "Styrsvik brygga",
    "synonyms": [
      "STYRSVIK BRYGGA"
    ],
    "lId": "25723",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.28,
      "lon": 18.731388888888887
    }
  },
  {
    "name": "Styrsö Bratten",
    "synonyms": [
      "STYRSÖ BRATTEN",
      "STYRSØ BRATTEN"
    ],
    "lId": "01213",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 57.615833333333335,
      "lon": 11.794444444444444
    }
  },
  {
    "name": "Styrsö Skäret",
    "synonyms": [
      "STYRSÖ SKÄRET",
      "STYRSØ SKÆRET"
    ],
    "lId": "24410",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 57.603611111111114,
      "lon": 11.790833333333333
    }
  },
  {
    "name": "Styrsö Tången",
    "synonyms": [
      "STYRSÖ TÅNGEN",
      "STYRSØ TÅNGEN"
    ],
    "lId": "24411",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 57.62138888888889,
      "lon": 11.769722222222223
    }
  },
  {
    "name": "Ståltorp Surahammar",
    "synonyms": [
      "STÅLTORP SURAHAMMAR"
    ],
    "lId": "44896",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.68444444444444,
      "lon": 16.18305555555556
    }
  },
  {
    "name": "Stånga",
    "synonyms": [
      "STÅNGA",
      "STÅNGA BSTN"
    ],
    "lId": "01324",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 57.28111111111111,
      "lon": 18.471944444444443
    }
  },
  {
    "name": "Stångby",
    "synonyms": [
      "STÅNGBY",
      "STÅNGBY STN"
    ],
    "lId": "00834",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 55.75111111111111,
      "lon": 13.2
    }
  },
  {
    "name": "Ställberg Bönhusbacken",
    "synonyms": [
      "STALLBERG BONHB",
      "STALLBERG BONHUSB",
      "STALLBERG BONHUSBACKEN",
      "STÄLLBERG BÖNHB",
      "STÄLLBERG BÖNHUSB",
      "STÄLLBERG BÖNHUSBACKEN",
      "STÆLLBERG BØNHUSB",
      "STÆLLBERG BØNHUSBACKEN"
    ],
    "lId": "04269",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.978611111111114,
      "lon": 14.924722222222222
    }
  },
  {
    "name": "Ställdalen",
    "synonyms": [
      "STALLDALEN",
      "STÄLLDALEN",
      "STÄLLDALEN STN",
      "STÆLLDALEN",
      "STÆLLDALEN STN"
    ],
    "lId": "00638",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.933611111111105,
      "lon": 14.943055555555556
    }
  },
  {
    "name": "Stävie Häradsvägen",
    "synonyms": [
      "STÄVIE HÄRADSVÄGEN"
    ],
    "lId": "16623",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 55.77027777777778,
      "lon": 13.085277777777778
    }
  },
  {
    "name": "Stöde",
    "synonyms": [
      "STODE",
      "STÖDE",
      "STØDE"
    ],
    "lId": "00380",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 62.419444444444444,
      "lon": 16.59861111111111
    }
  },
  {
    "name": "Stöllet RV 62",
    "synonyms": [
      "STÖLLET RV 62",
      "STØLLET RV 62"
    ],
    "lId": "00821",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 60.410555555555554,
      "lon": 13.272222222222224
    }
  },
  {
    "name": "Stömne södra infarten",
    "synonyms": [
      "STÖMNE SÖDRA INFARTEN",
      "STØMNE SØDRA INFARTEN"
    ],
    "lId": "11536",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.42861111111111,
      "lon": 12.757222222222222
    }
  },
  {
    "name": "Stöpen",
    "synonyms": [
      "STÖPEN",
      "STÖPEN SKOLAN",
      "STØPEN",
      "STØPEN SKOLAN"
    ],
    "lId": "00178",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 58.47527777777778,
      "lon": 13.865
    }
  },
  {
    "name": "Stöpen väg 26",
    "synonyms": [
      "STÖPEN VÄG 26",
      "STØPEN VÆG 26"
    ],
    "lId": "20238",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 58.47527777777778,
      "lon": 13.85
    }
  },
  {
    "name": "Stöten hotellet",
    "synonyms": [
      "STÖTEN HOTELLET",
      "STØTEN HOTELLET",
      "SÄLEN STÖTEN HOTELLET",
      "SÆLEN STØTEN HOTELLET"
    ],
    "lId": "01160",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 61.266666666666666,
      "lon": 12.887777777777778
    }
  },
  {
    "name": "Sudersand",
    "synonyms": [
      "SUDERSAND"
    ],
    "lId": "01161",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 57.95583333333334,
      "lon": 19.25138888888889
    }
  },
  {
    "name": "Sulvik macken",
    "synonyms": [
      "SULVIK MACKEN"
    ],
    "lId": "11540",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.67638888888889,
      "lon": 12.417777777777777
    }
  },
  {
    "name": "Sundborn",
    "synonyms": [
      "SUNDBORN",
      "SUNDBORN AFFÄR",
      "SUNDBORN AFFÆR"
    ],
    "lId": "00654",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 60.65277777777778,
      "lon": 15.774166666666668
    }
  },
  {
    "name": "Sundbyberg station",
    "synonyms": [
      "SUNDBYBERG",
      "SUNDBYBERG STATION"
    ],
    "lId": "00773",
    "prio": 1,
    "pId": "074",
    "pos": {
      "lat": 59.36083333333333,
      "lon": 17.97083333333333
    }
  },
  {
    "name": "Sundbyholm",
    "synonyms": [
      "SUNDBYHOLM"
    ],
    "lId": "11543",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.44416666666666,
      "lon": 16.621944444444445
    }
  },
  {
    "name": "Sunderby sjukhus station",
    "synonyms": [
      "SUNDERBY SJHSTN",
      "SUNDERBY SJUKHUS STATION"
    ],
    "lId": "22983",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 65.67500000000001,
      "lon": 21.93138888888889
    }
  },
  {
    "name": "Sunhultsbrunn centrum",
    "synonyms": [
      "SUNHULTSBRUNN CENTRUM"
    ],
    "lId": "11547",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 57.92833333333333,
      "lon": 14.911388888888888
    }
  },
  {
    "name": "Sundsvall C",
    "synonyms": [
      "SUNDSVALL C"
    ],
    "lId": "00130",
    "prio": 1,
    "pId": "074",
    "pos": {
      "lat": 62.38666666666666,
      "lon": 17.315555555555555
    }
  },
  {
    "name": "Sundsvall Västra",
    "synonyms": [
      "SUNDSVALL V",
      "SUNDSVALL VASTRA",
      "SUNDSVALL VÄSTRA",
      "SUNDSVALL VÆSTRA"
    ],
    "lId": "20045",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 62.38972222222222,
      "lon": 17.291666666666668
    }
  },
  {
    "name": "Sunnansjö affären",
    "synonyms": [
      "SUNNANSJÖ AFFÄREN"
    ],
    "lId": "01326",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 60.21666666666667,
      "lon": 14.957777777777777
    }
  },
  {
    "name": "Sunne",
    "synonyms": [
      "SUNNE",
      "SUNNE STN"
    ],
    "lId": "00184",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.83555555555556,
      "lon": 13.149166666666666
    }
  },
  {
    "name": "Sunnemo",
    "synonyms": [
      "SUNNEMO",
      "SUNNEMO KYRKA"
    ],
    "lId": "11549",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.88583333333333,
      "lon": 13.720833333333333
    }
  },
  {
    "name": "Suorva",
    "synonyms": [
      "SUORVA"
    ],
    "lId": "20196",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 67.52444444444444,
      "lon": 18.211388888888887
    }
  },
  {
    "name": "Surahammar",
    "synonyms": [
      "SURAHAMMAR",
      "SURAHAMMAR STN"
    ],
    "lId": "00384",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.70638888888889,
      "lon": 16.21944444444444
    }
  },
  {
    "name": "Surte station",
    "synonyms": [
      "SURTE STATION"
    ],
    "lId": "01601",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 57.825,
      "lon": 12.014444444444445
    }
  },
  {
    "name": "Svalsta skolan",
    "synonyms": [
      "SVALSTA SKOLAN"
    ],
    "lId": "11552",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 58.74138888888889,
      "lon": 16.872777777777777
    }
  },
  {
    "name": "Svalöv centrum",
    "synonyms": [
      "SVALOV CENTRUM",
      "SVALÖV CENTRUM",
      "SVALØV CENTRUM"
    ],
    "lId": "00955",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 55.91277777777778,
      "lon": 13.10611111111111
    }
  },
  {
    "name": "Svanesund centrum",
    "synonyms": [
      "SVANESUND CENTRUM",
      "SVANESUND CM"
    ],
    "lId": "15836",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 58.143055555555556,
      "lon": 11.819444444444445
    }
  },
  {
    "name": "Svanskog",
    "synonyms": [
      "SVANSKOG",
      "SVANSKOG KIOSK"
    ],
    "lId": "00822",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.17916666666667,
      "lon": 12.551666666666668
    }
  },
  {
    "name": "Svanstein",
    "synonyms": [
      "SVANSTEIN",
      "SVANSTEIN SKOLA"
    ],
    "lId": "00888",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 66.65666666666667,
      "lon": 23.855
    }
  },
  {
    "name": "Svanö FH",
    "synonyms": [
      "SVANÖ FH",
      "SVANØ FH"
    ],
    "lId": "15302",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 62.89694444444444,
      "lon": 17.875833333333333
    }
  },
  {
    "name": "Svappavaara Konsum",
    "synonyms": [
      "SVAPPAVAARA KONSUM"
    ],
    "lId": "01327",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 67.64611111111111,
      "lon": 21.049444444444447
    }
  },
  {
    "name": "Svarte",
    "synonyms": [
      "SVARTE",
      "SVARTE STN"
    ],
    "lId": "20759",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 55.42833333333333,
      "lon": 13.716944444444444
    }
  },
  {
    "name": "Svartsjö Färjestadsvägen",
    "synonyms": [
      "FÄRJESTADSVÄGEN",
      "FÆRJESTADSVÆGEN",
      "SVARTSJÖ FÄRJESTADSVÄGEN",
      "SVARTSJØ FÆRJESTADSVÆGEN"
    ],
    "lId": "65850",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.361666666666665,
      "lon": 17.735555555555557
    }
  },
  {
    "name": "Svartsö Alsvik",
    "synonyms": [
      "SVARTSÖ ALSVIK",
      "SVARTSØ ALSVIK"
    ],
    "lId": "24884",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.4375,
      "lon": 18.65694444444444
    }
  },
  {
    "name": "Svartvik E4",
    "synonyms": [
      "SVARTVIK E4"
    ],
    "lId": "26931",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 62.31388888888888,
      "lon": 17.37
    }
  },
  {
    "name": "Svartå Letstigen",
    "synonyms": [
      "SVARTÅ LETSTIGEN"
    ],
    "lId": "20294",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.12722222222222,
      "lon": 14.518333333333334
    }
  },
  {
    "name": "Svartå Herrgård",
    "synonyms": [
      "SVARTÅ HERRGÅRD"
    ],
    "lId": "23004",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.111666666666665,
      "lon": 14.544722222222221
    }
  },
  {
    "name": "Svedala",
    "synonyms": [
      "SVEDALA",
      "SVEDALA STN"
    ],
    "lId": "00397",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 55.50666666666667,
      "lon": 13.232222222222223
    }
  },
  {
    "name": "Svedmyra T-bana",
    "synonyms": [
      "SVEDMYRA T-BANA"
    ],
    "lId": "21709",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.277499999999996,
      "lon": 18.06722222222222
    }
  },
  {
    "name": "Sveg",
    "synonyms": [
      "SVEG",
      "SVEG STN"
    ],
    "lId": "00408",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 62.03527777777778,
      "lon": 14.351388888888888
    }
  },
  {
    "name": "Sveg flygplats",
    "synonyms": [
      "SVEG FLYGPLATS"
    ],
    "lId": "26031",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 62.04666666666667,
      "lon": 14.41861111111111
    }
  },
  {
    "name": "Svenarum kyrka",
    "synonyms": [
      "SVENARUM KYRKA"
    ],
    "lId": "11563",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 57.47,
      "lon": 14.316944444444443
    }
  },
  {
    "name": "Svenljunga",
    "synonyms": [
      "SVENLJUNGA",
      "SVENLJUNGA BSTN"
    ],
    "lId": "00502",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 57.49527777777778,
      "lon": 13.108611111111111
    }
  },
  {
    "name": "Svennevad",
    "synonyms": [
      "SVENNEVAD"
    ],
    "lId": "21148",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.018055555555556,
      "lon": 15.381111111111112
    }
  },
  {
    "name": "Svenshögen",
    "synonyms": [
      "SVENSHOGEN",
      "SVENSHÖGEN",
      "SVENSHÖGEN STN",
      "SVENSHØGEN",
      "SVENSHØGEN STN"
    ],
    "lId": "00320",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 58.14472222222222,
      "lon": 11.935555555555556
    }
  },
  {
    "name": "Svenstavik centrum",
    "synonyms": [
      "SVENSTAVIK CENTRUM",
      "SVENSTAVIK CM"
    ],
    "lId": "01552",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 62.76694444444444,
      "lon": 14.436388888888889
    }
  },
  {
    "name": "Svenstavik station",
    "synonyms": [
      "SVENSTAVIK STATION"
    ],
    "lId": "00444",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 62.76722222222222,
      "lon": 14.436388888888889
    }
  },
  {
    "name": "Svenstorp Ängelholm",
    "synonyms": [
      "SVENSTORP ÄNGELHOLM",
      "SVENSTORP ÆNGELHOLM"
    ],
    "lId": "04075",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 56.34027777777778,
      "lon": 12.928333333333333
    }
  },
  {
    "name": "Svinninge gård",
    "synonyms": [
      "SVINNINGE GÅRD"
    ],
    "lId": "24851",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.4575,
      "lon": 18.27027777777778
    }
  },
  {
    "name": "Svängsta",
    "synonyms": [
      "SVÄNGSTA",
      "SVÄNGSTA CM",
      "SVÆNGSTA",
      "SVÆNGSTA CM"
    ],
    "lId": "00197",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 56.26305555555555,
      "lon": 14.770833333333334
    }
  },
  {
    "name": "Svärdsjö",
    "synonyms": [
      "SVÄRDSJÖ",
      "SVÄRDSJÖ CM",
      "SVÆRDSJØ",
      "SVÆRDSJØ CM"
    ],
    "lId": "00655",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 60.74111111111111,
      "lon": 15.905277777777778
    }
  },
  {
    "name": "Svärta kyrka västra vägskäl",
    "synonyms": [
      "SVÄRTA KYRKA VÄSTRA VÄGSKÄL",
      "SVÆRTA KYRKA VÆSTRA VÆGSKÆL"
    ],
    "lId": "21933",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 58.81666666666667,
      "lon": 17.086944444444445
    }
  },
  {
    "name": "Svärtinge",
    "synonyms": [
      "SVÄRTINGE",
      "SVÄRTINGE BJÖRK",
      "SVÆRTINGE",
      "SVÆRTINGE BJØRK"
    ],
    "lId": "00866",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 58.65611111111111,
      "lon": 15.999444444444444
    }
  },
  {
    "name": "Sweden Rock Norje Festivalplat",
    "synonyms": [
      "SWEDEN ROCK NORJE FESTIVALPLAT"
    ],
    "lId": "11938",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 56.12972222222222,
      "lon": 14.673055555555555
    }
  },
  {
    "name": "Sya station",
    "synonyms": [
      "SYA STATION",
      "SYA STN"
    ],
    "lId": "11569",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 58.33444444444444,
      "lon": 15.223888888888888
    }
  },
  {
    "name": "Sysslebäck",
    "synonyms": [
      "SYSSLEBÄCK",
      "SYSSLEBÄCK NÄSV",
      "SYSSLEBÆCK",
      "SYSSLEBÆCK NÆSV"
    ],
    "lId": "00828",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 60.73027777777778,
      "lon": 12.870833333333334
    }
  },
  {
    "name": "Sågmyra",
    "synonyms": [
      "SÅGMYRA"
    ],
    "lId": "01329",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 60.712500000000006,
      "lon": 15.294166666666667
    }
  },
  {
    "name": "Sånga Säby",
    "synonyms": [
      "SÅNGA SÄBY",
      "SÅNGA SÆBY"
    ],
    "lId": "24532",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.367777777777775,
      "lon": 17.649722222222223
    }
  },
  {
    "name": "Såtenäs Stallmästargården",
    "synonyms": [
      "SÅTENÄS STALLMÄSTARGÅRDEN",
      "SÅTENÆS STALLMÆSTARGÅRDEN"
    ],
    "lId": "24113",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 58.43944444444444,
      "lon": 12.694722222222222
    }
  },
  {
    "name": "Säffle",
    "synonyms": [
      "SAFFLE",
      "SÄFFLE",
      "SÄFFLE STN",
      "SÆFFLE",
      "SÆFFLE STN"
    ],
    "lId": "00023",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.132222222222225,
      "lon": 12.916666666666666
    }
  },
  {
    "name": "Säfsen Fritid receptionen",
    "synonyms": [
      "SÄFSEN FRITID",
      "SÄFSEN FRITID RECEPTIONEN",
      "SÆFSEN FRITID",
      "SÆFSEN FRITID RECEPTIONEN"
    ],
    "lId": "25249",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 60.140277777777776,
      "lon": 14.42
    }
  },
  {
    "name": "Sälen by",
    "synonyms": [
      "SÄLEN BY",
      "SÆLEN BY"
    ],
    "lId": "00573",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 61.156666666666666,
      "lon": 13.265833333333333
    }
  },
  {
    "name": "Sälen Hundfjället hotellet",
    "synonyms": [
      "HUNDFJÄLL HOTEL",
      "HUNDFJÆLL HOTEL",
      "SÄLEN HUNDFJÄLLET HOTELLET",
      "SÆLEN HUNDFJÆLLET HOTELLET"
    ],
    "lId": "00646",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 61.17777777777778,
      "lon": 12.965833333333332
    }
  },
  {
    "name": "Sälen Högfjällshotellet",
    "synonyms": [
      "SALEN HOGFJALLSHOTELLET",
      "SÄLEN HÖGFJÄLLSHOTELLET",
      "SÆLEN HØGFJÆLLSHOTELLET"
    ],
    "lId": "00656",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 61.1575,
      "lon": 13.118055555555555
    }
  },
  {
    "name": "Sälfjällstorget",
    "synonyms": [
      "SÄLFJÄLLSTORGET",
      "SÆLFJÆLLSTORGET"
    ],
    "lId": "24272",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 61.165277777777774,
      "lon": 13.177222222222222
    }
  },
  {
    "name": "Sälja vsk",
    "synonyms": [
      "SÄLJA VSK",
      "SÆLJA VSK"
    ],
    "lId": "11834",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 60.25666666666667,
      "lon": 16.954166666666666
    }
  },
  {
    "name": "Sälleryd",
    "synonyms": [
      "SÄLLERYD"
    ],
    "lId": "32008",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 56.29333333333333,
      "lon": 15.846666666666668
    }
  },
  {
    "name": "Sänna Lunnafallsvägen",
    "synonyms": [
      "SÄNNA LUINNAFAV",
      "SÄNNA LUNNAFALLSVÄGEN",
      "SÄNNA LUNNAFAV",
      "SÆNNA LUINNAFAV",
      "SÆNNA LUNNAFALLSVÆGEN"
    ],
    "lId": "24453",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 58.79472222222222,
      "lon": 14.98
    }
  },
  {
    "name": "Särna Gamla Motellet",
    "synonyms": [
      "SÄRNA GAMLA MOTELLET"
    ],
    "lId": "00657",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 61.69416666666666,
      "lon": 13.125277777777779
    }
  },
  {
    "name": "Särö Särögården",
    "synonyms": [
      "SÄRÖ SÄRÖGÅRDEN",
      "SÆRØ SÆRØGÅRDEN"
    ],
    "lId": "16007",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 57.51972222222222,
      "lon": 11.965277777777777
    }
  },
  {
    "name": "Säter",
    "synonyms": [
      "SATER",
      "SÄTER",
      "SÄTER STN",
      "SÆTER",
      "SÆTER STN"
    ],
    "lId": "00026",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 60.34638888888889,
      "lon": 15.756944444444445
    }
  },
  {
    "name": "Säter Torget",
    "synonyms": [
      "SÄTER TORGET",
      "SÆTER TORGET"
    ],
    "lId": "12938",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 60.346944444444446,
      "lon": 15.7525
    }
  },
  {
    "name": "Sätila centrum",
    "synonyms": [
      "SÄTILA CENTRUM",
      "SÆTILA CENTRUM"
    ],
    "lId": "12168",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 57.54194444444444,
      "lon": 12.433333333333334
    }
  },
  {
    "name": "Sätofta Jägersbo",
    "synonyms": [
      "SÄTOFTA JÄGERSBO",
      "SÆTOFTA JÆGERSBO"
    ],
    "lId": "24988",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 55.908055555555556,
      "lon": 13.564722222222223
    }
  },
  {
    "name": "Sätra T-bana",
    "synonyms": [
      "SÄTRA T-BANA",
      "SÆTRA T-BANA"
    ],
    "lId": "21725",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.28472222222222,
      "lon": 17.921111111111113
    }
  },
  {
    "name": "Sätrabrunn",
    "synonyms": [
      "SÄTRABRUNN",
      "SÆTRABRUNN"
    ],
    "lId": "00681",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.86388888888889,
      "lon": 16.433611111111112
    }
  },
  {
    "name": "Sättersta",
    "synonyms": [
      "SÄTTERSTA",
      "SÆTTERSTA"
    ],
    "lId": "20916",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 58.89055555555556,
      "lon": 17.223333333333333
    }
  },
  {
    "name": "Sävar centrum",
    "synonyms": [
      "SÄVAR CENTRUM"
    ],
    "lId": "49224",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 63.900555555555556,
      "lon": 20.55027777777778
    }
  },
  {
    "name": "Sävar samhälle",
    "synonyms": [
      "SÄVAR SAMHÄLLE",
      "SÆVAR SAMHÆLLE"
    ],
    "lId": "00393",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 63.901111111111106,
      "lon": 20.551944444444445
    }
  },
  {
    "name": "Sävast Svängleden",
    "synonyms": [
      "SÄVAST SVÄNGLEDEN",
      "SÆVAST SVÆNGLEDEN"
    ],
    "lId": "14945",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 65.76555555555555,
      "lon": 21.73888888888889
    }
  },
  {
    "name": "Säve Flygplats",
    "synonyms": [
      "SÄVE FLYGPLATS"
    ],
    "lId": "59378",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 57.78194444444444,
      "lon": 11.861944444444443
    }
  },
  {
    "name": "Sävenäs",
    "synonyms": [
      "SÄVENÄS",
      "SÄVENÄS STN",
      "SÆVENÆS",
      "SÆVENÆS STN"
    ],
    "lId": "01330",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 57.724722222222226,
      "lon": 12.025277777777779
    }
  },
  {
    "name": "Sävsjö",
    "synonyms": [
      "SAVSJO",
      "SÄVSJÖ",
      "SÄVSJÖ STN",
      "SÆVSJØ",
      "SÆVSJØ STN"
    ],
    "lId": "00078",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 57.40277777777778,
      "lon": 14.665277777777778
    }
  },
  {
    "name": "Sävsjöström Alstervägen",
    "synonyms": [
      "SÄVSJÖSTRÖM ALSTERVÄGEN",
      "SÆVSJØSTRØM ALSTERVÆGEN"
    ],
    "lId": "24757",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 57.00111111111111,
      "lon": 15.40611111111111
    }
  },
  {
    "name": "Söderala Rosenvall",
    "synonyms": [
      "SÖDERALA ROSENVALL",
      "SØDERALA ROSENVALL"
    ],
    "lId": "11579",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 61.27916666666667,
      "lon": 16.96361111111111
    }
  },
  {
    "name": "Söderboda Gräsö",
    "synonyms": [
      "GRÄSÖ SÖDERBODA",
      "GRÆSØ SØDERBODA",
      "SÖDERBODA GRÄSÖ",
      "SØDERBODA GRÆSØ"
    ],
    "lId": "12710",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 60.437777777777775,
      "lon": 18.415277777777778
    }
  },
  {
    "name": "Söderby-Karl",
    "synonyms": [
      "SÖDERBY-KARL",
      "SÖDERBY-KARL N",
      "SØDERBY-KARL",
      "SØDERBY-KARL N"
    ],
    "lId": "01331",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.89944444444444,
      "lon": 18.703611111111112
    }
  },
  {
    "name": "Söderbärke",
    "synonyms": [
      "SODERBARKE",
      "SÖDERBÄRKE",
      "SÖDERBÄRKE STN",
      "SØDERBÆRKE",
      "SØDERBÆRKE STN"
    ],
    "lId": "00024",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 60.07222222222222,
      "lon": 15.536944444444444
    }
  },
  {
    "name": "Söderfors Bruksskolan",
    "synonyms": [
      "SODERFORS BRUKSSKOLAN",
      "SÖDERFORS BRUKSSKOLAN",
      "SØDERFORS BRUKSSKOLAN"
    ],
    "lId": "00668",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 60.38638888888889,
      "lon": 17.234722222222224
    }
  },
  {
    "name": "Söderhall tpl",
    "synonyms": [
      "SÖDERHALL TPL",
      "SØDERHALL TPL"
    ],
    "lId": "20605",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.6375,
      "lon": 18.33361111111111
    }
  },
  {
    "name": "Söderhamn station",
    "synonyms": [
      "SODERHAMN STATION",
      "SÖDERHAMN STATION",
      "SÖDERHAMN STN",
      "SØDERHAMN STATION",
      "SØDERHAMN STN"
    ],
    "lId": "00154",
    "prio": 1,
    "pId": "074",
    "pos": {
      "lat": 61.29944444444444,
      "lon": 17.035555555555558
    }
  },
  {
    "name": "Söderhamn Aquarena",
    "synonyms": [
      "AQUARENA",
      "SÖDERHAMN AQUARENA"
    ],
    "lId": "06207",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 61.288888888888884,
      "lon": 17.070833333333333
    }
  },
  {
    "name": "Söderhamn Järnbron",
    "synonyms": [
      "SÖDERHAMN JÄRNBRON",
      "SØDERHAMN JÆRNBRON"
    ],
    "lId": "11216",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 61.301944444444445,
      "lon": 17.058055555555555
    }
  },
  {
    "name": "Söderhamn stadszon",
    "synonyms": [
      "SÖDERHAMN STADSZON",
      "SÖDERHAMN ZON",
      "SØDERHAMN STADSZON"
    ],
    "lId": "79013",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 61.29944444444444,
      "lon": 17.035555555555558
    }
  },
  {
    "name": "Söderköping busstation",
    "synonyms": [
      "SÖDERKÖPING BST",
      "SÖDERKÖPING BUSSTATION",
      "SØDERKØPING BST",
      "SØDERKØPING BUSSTATION"
    ],
    "lId": "00576",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 58.47805555555556,
      "lon": 16.323333333333334
    }
  },
  {
    "name": "Södersvik affär",
    "synonyms": [
      "SÖDERSVIK AFFÄR",
      "SØDERSVIK AFFÆR"
    ],
    "lId": "18091",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.74944444444444,
      "lon": 18.910555555555554
    }
  },
  {
    "name": "Södertälje centrum",
    "synonyms": [
      "SÖDERTÄLJE CENTRUM",
      "SÖDERTÄLJE CM",
      "SØDERTÆLJE CENTRUM",
      "SØDERTÆLJE CM"
    ],
    "lId": "00721",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.19222222222222,
      "lon": 17.62666666666667
    }
  },
  {
    "name": "Södertälje hamn",
    "synonyms": [
      "SÖDERTÄLJE HAMN",
      "SØDERTÆLJE HAMN"
    ],
    "lId": "00049",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.17916666666667,
      "lon": 17.64638888888889
    }
  },
  {
    "name": "Södertälje Syd",
    "synonyms": [
      "SODERTALJE SYD",
      "SÖDERTÄLJE SYD",
      "SØDERTÆLJE SYD",
      "XEZ"
    ],
    "lId": "00055",
    "prio": 1,
    "pId": "074",
    "pos": {
      "lat": 59.16222222222222,
      "lon": 17.64527777777778
    }
  },
  {
    "name": "Södertälje Sydpoolen",
    "synonyms": [
      "SÖDERTÄLJE SYDPOOLEN"
    ],
    "lId": "70120",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.19027777777777,
      "lon": 17.634722222222223
    }
  },
  {
    "name": "Söderåkra kyrka",
    "synonyms": [
      "SODERAKRA KYRKA",
      "SÖDERÅKRA KYRKA",
      "SØDERÅKRA KYRKA"
    ],
    "lId": "14385",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 56.44472222222222,
      "lon": 16.070555555555554
    }
  },
  {
    "name": "Söderöra brygga",
    "synonyms": [
      "SÖDERÖRA BRYGGA",
      "SØDERØRA BRYGGA"
    ],
    "lId": "24881",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.62722222222222,
      "lon": 19.011111111111113
    }
  },
  {
    "name": "Södra Sandby",
    "synonyms": [
      "S SANDBY BSTN",
      "SÖDRA SANDBY",
      "SØDRA SANDBY"
    ],
    "lId": "00956",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 55.717222222222226,
      "lon": 13.346666666666668
    }
  },
  {
    "name": "Södra Vi centrum",
    "synonyms": [
      "SÖDRA VI CENTRUM",
      "SÖDRA VI CM",
      "SØDRA VI CENTRUM",
      "SØDRA VI CM"
    ],
    "lId": "14384",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 57.73972222222222,
      "lon": 15.799722222222222
    }
  },
  {
    "name": "Södvik väg 136",
    "synonyms": [
      "SÖDVIK VÄG 136"
    ],
    "lId": "24362",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 57.058611111111105,
      "lon": 16.878333333333334
    }
  },
  {
    "name": "Sölvesborg",
    "synonyms": [
      "SOLVESBORG",
      "SÖLVESBORG",
      "SÖLVESBORG STN",
      "SØLVESBORG",
      "SØLVESBORG STN"
    ],
    "lId": "00079",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 56.04972222222222,
      "lon": 14.5825
    }
  },
  {
    "name": "Sörberge norra",
    "synonyms": [
      "SÖRBERGE NORRA",
      "SØRBERGE NORRA"
    ],
    "lId": "15435",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 62.51555555555556,
      "lon": 17.390833333333333
    }
  },
  {
    "name": "Sörboda",
    "synonyms": [
      "SÖRBODA",
      "SØRBODA"
    ],
    "lId": "01163",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 61.10416666666667,
      "lon": 15.24861111111111
    }
  },
  {
    "name": "Sörbygden",
    "synonyms": [
      "SÖRBYGDEN",
      "SØRBYGDEN"
    ],
    "lId": "01332",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 62.79361111111111,
      "lon": 16.213055555555556
    }
  },
  {
    "name": "Sörfjärden",
    "synonyms": [
      "SÖRFJÄRDEN",
      "SØRFJÆRDEN"
    ],
    "lId": "18948",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 62.03055555555555,
      "lon": 17.428333333333335
    }
  },
  {
    "name": "Sörforsa",
    "synonyms": [
      "SÖRFORSA",
      "SÖRFORSA BSTN",
      "SØRFORSA",
      "SØRFORSA BSTN"
    ],
    "lId": "00722",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 61.717777777777776,
      "lon": 16.96972222222222
    }
  },
  {
    "name": "Sörstafors",
    "synonyms": [
      "SÖRSTAFORS"
    ],
    "lId": "11598",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.5825,
      "lon": 16.21222222222222
    }
  },
  {
    "name": "Sörtjärn",
    "synonyms": [
      "SÖRTJÄRN",
      "SÖRTJÄRN STN",
      "SØRTJÆRN",
      "SØRTJÆRN STN"
    ],
    "lId": "04447",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 62.3425,
      "lon": 14.629722222222222
    }
  },
  {
    "name": "Sörumsand",
    "synonyms": [
      "SORUMSAND",
      "SÖRUMSAND"
    ],
    "lId": "00305",
    "prio": 0,
    "pId": "076",
    "pos": {
      "lat": 59.987500000000004,
      "lon": 11.298055555555555
    }
  },
  {
    "name": "Sörvik",
    "synonyms": [
      "SÖRVIK",
      "SØRVIK"
    ],
    "lId": "12961",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 60.18527777777778,
      "lon": 15.150833333333333
    }
  },
  {
    "name": "Söråker",
    "synonyms": [
      "SÖRÅKER",
      "SÖRÅKER KÖPCENT",
      "SØRÅKER",
      "SØRÅKER KØPCENT"
    ],
    "lId": "00417",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 62.50611111111111,
      "lon": 17.50722222222222
    }
  },
  {
    "name": "Sösdala station",
    "synonyms": [
      "SÖSDALA",
      "SÖSDALA BSTN",
      "SÖSDALA STATION",
      "SØSDALA",
      "SØSDALA BSTN"
    ],
    "lId": "01334",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 56.03611111111111,
      "lon": 13.680277777777777
    }
  },
  {
    "name": "Sösterbekk",
    "synonyms": [
      "SÖSTERBEKK"
    ],
    "lId": "90014",
    "prio": 0,
    "pId": "076",
    "pos": {
      "lat": 0,
      "lon": 0
    }
  },
  {
    "name": "Sövde by",
    "synonyms": [
      "SÖVDE BY",
      "SØVDE BY"
    ],
    "lId": "16910",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 55.58444444444444,
      "lon": 13.675555555555555
    }
  },
  {
    "name": "Sövestad kyrka",
    "synonyms": [
      "SÖVESTAD KYRKA",
      "SØVESTAD KYRKA"
    ],
    "lId": "16911",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 55.5,
      "lon": 13.79888888888889
    }
  },
  {
    "name": "T-Centralen",
    "synonyms": [
      "T-CENTRALEN"
    ],
    "lId": "20749",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.33083333333334,
      "lon": 18.059166666666666
    }
  },
  {
    "name": "Taberg",
    "synonyms": [
      "TABERG"
    ],
    "lId": "00539",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 57.67861111111111,
      "lon": 14.086666666666668
    }
  },
  {
    "name": "Tahult Hallen",
    "synonyms": [
      "TAHULT HALLEN"
    ],
    "lId": "22936",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 57.68944444444444,
      "lon": 12.175277777777778
    }
  },
  {
    "name": "Tallberga",
    "synonyms": [
      "TALLBERGA"
    ],
    "lId": "11602",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 58.73305555555556,
      "lon": 15.578333333333333
    }
  },
  {
    "name": "Tallboda centrum",
    "synonyms": [
      "TALLBODA CENTRUM",
      "TALLBODA CM"
    ],
    "lId": "11603",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 58.42583333333333,
      "lon": 15.679166666666665
    }
  },
  {
    "name": "Tallhed E45",
    "synonyms": [
      "TALLHED E45"
    ],
    "lId": "10729",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 61.21666666666667,
      "lon": 14.699722222222222
    }
  },
  {
    "name": "Tallkrogen T-bana",
    "synonyms": [
      "TALLKROGEN T-BANA"
    ],
    "lId": "21700",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.27111111111111,
      "lon": 18.085277777777776
    }
  },
  {
    "name": "Talludden",
    "synonyms": [
      "TALLUDDEN"
    ],
    "lId": "24794",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.35527777777778,
      "lon": 18.22222222222222
    }
  },
  {
    "name": "Tallåsen skolan",
    "synonyms": [
      "TALLÅSEN SKOLAN"
    ],
    "lId": "11604",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 61.865833333333335,
      "lon": 16.004722222222224
    }
  },
  {
    "name": "Tandsbyn Bodsjövägen",
    "synonyms": [
      "TANDSBYN BODSJV",
      "TANDSBYN BODSJÖVÄGEN",
      "TANDSBYN BODSJØVÆGEN"
    ],
    "lId": "29491",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 63.000277777777775,
      "lon": 14.745833333333332
    }
  },
  {
    "name": "Tandsjöborg",
    "synonyms": [
      "TANDSJÖBORG",
      "TANDSJØBORG"
    ],
    "lId": "18304",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 61.697222222222216,
      "lon": 14.736944444444443
    }
  },
  {
    "name": "Tandådalen fjällkyrkan",
    "synonyms": [
      "TANDÅDAL KYRKAN",
      "TANDÅDALEN FJÄLLKYRKAN"
    ],
    "lId": "00658",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 61.177499999999995,
      "lon": 12.993611111111111
    }
  },
  {
    "name": "Tannefors",
    "synonyms": [
      "TANNEFORS",
      "TANNEFORS STN"
    ],
    "lId": "01336",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 58.400277777777774,
      "lon": 15.659166666666668
    }
  },
  {
    "name": "Tanum",
    "synonyms": [
      "TANUM",
      "TANUM STN"
    ],
    "lId": "00233",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 58.71361111111111,
      "lon": 11.295
    }
  },
  {
    "name": "Tanum Shoppingcenter",
    "synonyms": [
      "TANUM SHOPPINGCENTER"
    ],
    "lId": "71636",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 58.72166666666667,
      "lon": 11.349166666666667
    }
  },
  {
    "name": "Tanumshede centrum",
    "synonyms": [
      "TANUMSHEDE CENTRUM",
      "TANUMSHEDE CM"
    ],
    "lId": "01337",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 58.72222222222222,
      "lon": 11.320833333333333
    }
  },
  {
    "name": "Tanumshede Rasta",
    "synonyms": [
      "TANUMSHEDE RASTA"
    ],
    "lId": "22989",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 58.72027777777778,
      "lon": 11.351666666666667
    }
  },
  {
    "name": "Tattby station",
    "synonyms": [
      "TATTBY STATION",
      "TATTBY STN"
    ],
    "lId": "20879",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.278888888888886,
      "lon": 18.281944444444445
    }
  },
  {
    "name": "Tavelsjö Bygdegården",
    "synonyms": [
      "TAVELSJÖ BYGDEGÅRDEN",
      "TAVELSJØ BYGDEGÅRDEN"
    ],
    "lId": "01338",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 64.03944444444444,
      "lon": 20.069166666666668
    }
  },
  {
    "name": "Taxinge",
    "synonyms": [
      "TAXINGE"
    ],
    "lId": "01339",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.242222222222225,
      "lon": 17.304444444444446
    }
  },
  {
    "name": "Taxinge Näsby Station",
    "synonyms": [
      "TAXINGE NÄSBY STATION",
      "TAXINGE NÆSBY STATION"
    ],
    "lId": "71194",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.240833333333335,
      "lon": 17.299722222222226
    }
  },
  {
    "name": "Teckomatorp",
    "synonyms": [
      "TECKOMATORP",
      "TECKOMATORP STN"
    ],
    "lId": "00011",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 55.870555555555555,
      "lon": 13.086111111111112
    }
  },
  {
    "name": "Tekniska Högskolan T-bana",
    "synonyms": [
      "KTH",
      "STOCKHOLM KTH",
      "TEKNISKA HÖGSKOLAN T-BANA",
      "TEKNISKA HØGSKOLAN T-BANA"
    ],
    "lId": "11606",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.345555555555556,
      "lon": 18.071666666666665
    }
  },
  {
    "name": "Telefonplan T-bana",
    "synonyms": [
      "TELEFONPLAN T-BANA"
    ],
    "lId": "21716",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.29805555555556,
      "lon": 17.997222222222224
    }
  },
  {
    "name": "Tenhult",
    "synonyms": [
      "TENHULT"
    ],
    "lId": "00171",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 57.705000000000005,
      "lon": 14.32638888888889
    }
  },
  {
    "name": "Tensta T-bana",
    "synonyms": [
      "TENSTA T-BANA"
    ],
    "lId": "12885",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.394444444444446,
      "lon": 17.90111111111111
    }
  },
  {
    "name": "Thorildsplan T-bana",
    "synonyms": [
      "THORILDSPLAN T-BANA"
    ],
    "lId": "21664",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.33166666666667,
      "lon": 18.01527777777778
    }
  },
  {
    "name": "Tibble station Täby",
    "synonyms": [
      "TIBBLE STATION TÄBY",
      "TIBBLE STATION TÆBY",
      "TIBBLE STN TÄBY",
      "TIBBLE STN TÆBY"
    ],
    "lId": "20872",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.44222222222222,
      "lon": 18.0625
    }
  },
  {
    "name": "Tibble Upplands Bro",
    "synonyms": [
      "TIBBLE TORGET",
      "TIBBLE UPPL-BRO",
      "TIBBLE UPPLANDS BRO"
    ],
    "lId": "01340",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.485,
      "lon": 17.733055555555556
    }
  },
  {
    "name": "Tibro",
    "synonyms": [
      "TIBRO",
      "TIBRO BSTN"
    ],
    "lId": "00373",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 58.42527777777777,
      "lon": 14.160833333333334
    }
  },
  {
    "name": "Tidaholm",
    "synonyms": [
      "TIDAHOLM",
      "TIDAHOLM BSTN"
    ],
    "lId": "00600",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 58.17944444444444,
      "lon": 13.955555555555556
    }
  },
  {
    "name": "Tidan",
    "synonyms": [
      "TIDAN"
    ],
    "lId": "00829",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 58.572500000000005,
      "lon": 14.004444444444445
    }
  },
  {
    "name": "Tidö Lindö",
    "synonyms": [
      "TIDÖ LINDÖ",
      "TIDØ LINDØ"
    ],
    "lId": "11615",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.515277777777776,
      "lon": 16.529444444444444
    }
  },
  {
    "name": "Tierp station",
    "synonyms": [
      "TIERP STATION",
      "TIERP STN",
      "XFU"
    ],
    "lId": "00301",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 60.34527777777778,
      "lon": 17.514166666666668
    }
  },
  {
    "name": "Tierp kyrkby",
    "synonyms": [
      "TIERP KYRKBY"
    ],
    "lId": "12733",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 60.29972222222222,
      "lon": 17.467499999999998
    }
  },
  {
    "name": "Tillberga centrum",
    "synonyms": [
      "TILLBERGA CENTRUM"
    ],
    "lId": "25845",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.68388888888889,
      "lon": 16.62
    }
  },
  {
    "name": "Timmele",
    "synonyms": [
      "TIMMELE"
    ],
    "lId": "01504",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 57.86055555555556,
      "lon": 13.430277777777777
    }
  },
  {
    "name": "Timmernabben",
    "synonyms": [
      "TIMMERNABB FVIK",
      "TIMMERNABBEN"
    ],
    "lId": "01341",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 56.97083333333334,
      "lon": 16.438055555555557
    }
  },
  {
    "name": "Timmersdala",
    "synonyms": [
      "TIMMERSDALA"
    ],
    "lId": "01505",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 58.52861111111111,
      "lon": 13.759444444444444
    }
  },
  {
    "name": "Timrå station",
    "synonyms": [
      "TIMRÅ STATION",
      "TIMRÅ STN"
    ],
    "lId": "00242",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 62.48638888888889,
      "lon": 17.330277777777777
    }
  },
  {
    "name": "Timsfors Exhultsvägen",
    "synonyms": [
      "TIMSFORS EXHULTSVÄGEN",
      "TIMSFORS EXHULTSVÆGEN"
    ],
    "lId": "11619",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 56.4825,
      "lon": 13.609444444444444
    }
  },
  {
    "name": "Tings Nöbbelöv",
    "synonyms": [
      "TINGS NÖBBELÖV",
      "TINGS NØBBELØV"
    ],
    "lId": "24309",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 55.956944444444446,
      "lon": 14.06638888888889
    }
  },
  {
    "name": "Tingsryd",
    "synonyms": [
      "TINGSRYD",
      "TINGSRYD BSTN"
    ],
    "lId": "00385",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 56.52388888888889,
      "lon": 14.975833333333334
    }
  },
  {
    "name": "Tingstäde",
    "synonyms": [
      "TINGSTÄDE",
      "TINGSTÆDE"
    ],
    "lId": "01342",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 57.73388888888889,
      "lon": 18.60666666666667
    }
  },
  {
    "name": "Tippen station",
    "synonyms": [
      "TIPPEN STATION",
      "TIPPEN STN"
    ],
    "lId": "20878",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.28388888888889,
      "lon": 18.276944444444442
    }
  },
  {
    "name": "Tjunnaryd",
    "synonyms": [
      "TJUNNARYD",
      "TJUNNARYD STN"
    ],
    "lId": "01343",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 57.504444444444445,
      "lon": 14.974722222222223
    }
  },
  {
    "name": "Tjurkö St Lycke",
    "synonyms": [
      "TJURKÖ ST LYCKE",
      "TJURKØ ST LYCKE"
    ],
    "lId": "23365",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 56.123333333333335,
      "lon": 15.625555555555556
    }
  },
  {
    "name": "Tjustskolan",
    "synonyms": [
      "TJUSTSKOLAN",
      "TJUSTSKOLAN STN"
    ],
    "lId": "00522",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 57.753055555555555,
      "lon": 16.63138888888889
    }
  },
  {
    "name": "Tjällmo Egelstorp",
    "synonyms": [
      "TJÄLLMO EGELSTORP",
      "TJÆLLMO EGELSTORP"
    ],
    "lId": "23421",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 58.71472222222223,
      "lon": 15.35611111111111
    }
  },
  {
    "name": "Tjärnelund",
    "synonyms": [
      "TJÄRNELUND",
      "TJÆRNELUND"
    ],
    "lId": "18962",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 61.80638888888888,
      "lon": 16.243055555555557
    }
  },
  {
    "name": "Tjörnarp station",
    "synonyms": [
      "TJÖRNARP STATION"
    ],
    "lId": "01611",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 56.000277777777775,
      "lon": 13.629722222222222
    }
  },
  {
    "name": "Tobo station",
    "synonyms": [
      "TOBO STATION",
      "TOBO STN"
    ],
    "lId": "01345",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 60.25833333333333,
      "lon": 17.635833333333334
    }
  },
  {
    "name": "Tofta bad Gotland",
    "synonyms": [
      "TOFTA BAD GOTLAND"
    ],
    "lId": "00910",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 57.483333333333334,
      "lon": 18.128055555555555
    }
  },
  {
    "name": "Tofta station",
    "synonyms": [
      "TOFTA STATION",
      "TOFTA STN"
    ],
    "lId": "00225",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 57.17333333333333,
      "lon": 12.300277777777778
    }
  },
  {
    "name": "Toftbyn",
    "synonyms": [
      "TOFTBYN"
    ],
    "lId": "13017",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 60.71361111111111,
      "lon": 15.78277777777778
    }
  },
  {
    "name": "Tolita",
    "synonyms": [
      "TOLITA",
      "TOLITA STN"
    ],
    "lId": "00508",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.57777777777778,
      "lon": 13.239722222222222
    }
  },
  {
    "name": "Tollarp E22",
    "synonyms": [
      "TOLLARP E22"
    ],
    "lId": "22817",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 55.92861111111111,
      "lon": 13.967222222222222
    }
  },
  {
    "name": "Tollered",
    "synonyms": [
      "TOLLERED"
    ],
    "lId": "15899",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 57.81722222222223,
      "lon": 12.42
    }
  },
  {
    "name": "Tomelilla",
    "synonyms": [
      "TOMELILLA",
      "TOMELILLA STN"
    ],
    "lId": "00323",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 55.546388888888885,
      "lon": 13.94888888888889
    }
  },
  {
    "name": "Tomta vsk",
    "synonyms": [
      "TOMTA VSK"
    ],
    "lId": "44121",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.801111111111105,
      "lon": 16.560277777777777
    }
  },
  {
    "name": "Torarp Ingärdahej",
    "synonyms": [
      "TORARP INGÄRDAHEJ",
      "TORARP INGÆRDAHEJ"
    ],
    "lId": "32490",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 56.20388888888889,
      "lon": 14.795277777777777
    }
  },
  {
    "name": "Torekov",
    "synonyms": [
      "TOREKOV",
      "TOREKOV BSTN"
    ],
    "lId": "01346",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 56.42388888888889,
      "lon": 12.629722222222222
    }
  },
  {
    "name": "Torhamn",
    "synonyms": [
      "TORHAMN"
    ],
    "lId": "11636",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 56.094722222222224,
      "lon": 15.834444444444445
    }
  },
  {
    "name": "Tormestorp Fläckebäcksvägen",
    "synonyms": [
      "TORMESTORP FLÄCKEBÄCKSVÄGEN",
      "TORMESTORP FLÆCKEBÆCKSVÆGEN"
    ],
    "lId": "24867",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 56.11027777777778,
      "lon": 13.739722222222222
    }
  },
  {
    "name": "Torna Hällestad torget",
    "synonyms": [
      "TORNA HÄLLESTAD TORGET",
      "TORNA HÆLLESTAD TORGET"
    ],
    "lId": "21850",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 55.67805555555555,
      "lon": 13.419722222222221
    }
  },
  {
    "name": "Torneträsk",
    "synonyms": [
      "TORNETRASK",
      "TORNETRÄSK",
      "TORNETRÄSK STN",
      "TORNETRÆSK",
      "TORNETRÆSK STN"
    ],
    "lId": "00281",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 68.21694444444445,
      "lon": 19.710277777777776
    }
  },
  {
    "name": "Tornio linja-autoasema",
    "synonyms": [
      "TORNEÅ BUSSTATION",
      "TORNIO LAS",
      "TORNIO LINJA-AUTOASEMA"
    ],
    "lId": "00831",
    "prio": 0,
    "pId": "010",
    "pos": {
      "lat": 65.84833333333333,
      "lon": 24.14638888888889
    }
  },
  {
    "name": "Torp Terminalen Uddevalla",
    "synonyms": [
      "TORP TERMINALEN UDDEVALLA"
    ],
    "lId": "23098",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 58.353611111111114,
      "lon": 11.816111111111113
    }
  },
  {
    "name": "Torpsbruk Stationsvägen",
    "synonyms": [
      "TORPSBRUK STATIONSVÄGEN",
      "TORPSBRUK STATIONSVÆGEN"
    ],
    "lId": "01347",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 57.035555555555554,
      "lon": 14.575
    }
  },
  {
    "name": "Torpshammar station",
    "synonyms": [
      "TORPSHAMMAR STATION",
      "TORPSHAMMAR STN"
    ],
    "lId": "00688",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 62.473333333333336,
      "lon": 16.334444444444443
    }
  },
  {
    "name": "Torpåkra",
    "synonyms": [
      "TORPAKRA",
      "TORPÅKRA",
      "TORPÅKRA STN"
    ],
    "lId": "00552",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 57.940555555555555,
      "lon": 13.029444444444445
    }
  },
  {
    "name": "Torreby slott",
    "synonyms": [
      "TORREBY SLOTT"
    ],
    "lId": "41771",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 58.44222222222222,
      "lon": 11.5975
    }
  },
  {
    "name": "Torrlösa kyrka",
    "synonyms": [
      "TORRLÖSA KYRKA",
      "TORRLØSA KYRKA"
    ],
    "lId": "12306",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 55.91083333333333,
      "lon": 13.14111111111111
    }
  },
  {
    "name": "Torrom",
    "synonyms": [
      "TORROM"
    ],
    "lId": "15317",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 62.87027777777778,
      "lon": 18.08611111111111
    }
  },
  {
    "name": "Torsby",
    "synonyms": [
      "TORSBY",
      "TORSBY STN"
    ],
    "lId": "00274",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 60.13638888888889,
      "lon": 13.0025
    }
  },
  {
    "name": "Torsebro Färlövsvägen",
    "synonyms": [
      "TORSEBRO FÄRLÖVSVÄGEN",
      "TORSEBRO FÆRLØVSVÆGEN"
    ],
    "lId": "04130",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 56.1,
      "lon": 14.116111111111111
    }
  },
  {
    "name": "Torshälla",
    "synonyms": [
      "TORSHÄLLA",
      "TORSHÄLLA ÖTORG",
      "TORSHÆLLA",
      "TORSHÆLLA ØTORG"
    ],
    "lId": "11645",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.419999999999995,
      "lon": 16.474999999999998
    }
  },
  {
    "name": "Torslanda Torg",
    "synonyms": [
      "TORSLANDA TORG"
    ],
    "lId": "15586",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 57.72222222222222,
      "lon": 11.767222222222223
    }
  },
  {
    "name": "Torsvik",
    "synonyms": [
      "TORSVIK"
    ],
    "lId": "24788",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.361666666666665,
      "lon": 18.11777777777778
    }
  },
  {
    "name": "Torsåker centrum",
    "synonyms": [
      "TORSÅKER CENTRUM",
      "TORSÅKER CM"
    ],
    "lId": "11647",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 60.51027777777778,
      "lon": 16.47222222222222
    }
  },
  {
    "name": "Torsåker station",
    "synonyms": [
      "TORSÅKER STATION",
      "TORSÅKER STN"
    ],
    "lId": "01563",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 60.513888888888886,
      "lon": 16.489166666666666
    }
  },
  {
    "name": "Torsång skolan",
    "synonyms": [
      "TORSÅNG SKOLAN"
    ],
    "lId": "22650",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 60.463055555555556,
      "lon": 15.56861111111111
    }
  },
  {
    "name": "Torsås",
    "synonyms": [
      "TORSÅS",
      "TORSÅS TORGET"
    ],
    "lId": "00932",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 56.411944444444444,
      "lon": 15.997499999999999
    }
  },
  {
    "name": "Tortuna",
    "synonyms": [
      "TORTUNA"
    ],
    "lId": "11649",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.67388888888889,
      "lon": 16.725277777777777
    }
  },
  {
    "name": "Torup",
    "synonyms": [
      "TORUP",
      "TORUP STN"
    ],
    "lId": "00312",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 56.95777777777778,
      "lon": 13.078888888888889
    }
  },
  {
    "name": "Torved",
    "synonyms": [
      "TORVED",
      "TORVED STN"
    ],
    "lId": "01348",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 58.82555555555556,
      "lon": 14.1
    }
  },
  {
    "name": "Torö",
    "synonyms": [
      "TORÖ",
      "TORÖ ANKARUDDEN",
      "TORØ",
      "TORØ ANKARUDDEN"
    ],
    "lId": "01349",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 58.80166666666666,
      "lon": 17.83611111111111
    }
  },
  {
    "name": "Totebo station",
    "synonyms": [
      "TOTEBO STATION",
      "TOTEBO STN"
    ],
    "lId": "24959",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 57.628055555555555,
      "lon": 16.18111111111111
    }
  },
  {
    "name": "Tranemo",
    "synonyms": [
      "TRANEMO",
      "TRANEMO BSTN"
    ],
    "lId": "00523",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 57.485,
      "lon": 13.351388888888888
    }
  },
  {
    "name": "Transtrand",
    "synonyms": [
      "TRANSTRAND",
      "TRANSTRAND KIOS"
    ],
    "lId": "01350",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 61.0925,
      "lon": 13.31861111111111
    }
  },
  {
    "name": "Tranås",
    "synonyms": [
      "TRANAS",
      "TRANÅS",
      "TRANÅS STN"
    ],
    "lId": "00041",
    "prio": 1,
    "pId": "074",
    "pos": {
      "lat": 58.03777777777778,
      "lon": 14.975
    }
  },
  {
    "name": "Traryd",
    "synonyms": [
      "TRARYD",
      "TRARYD BSTN"
    ],
    "lId": "00536",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 56.57944444444445,
      "lon": 13.746388888888887
    }
  },
  {
    "name": "Trehörningsjö UnoX",
    "synonyms": [
      "TREHÖRNINGSJÖ UNOX",
      "TREHØRNINGSJØ UNOX"
    ],
    "lId": "15320",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 63.69305555555555,
      "lon": 18.865000000000002
    }
  },
  {
    "name": "Trekanten Kalmar",
    "synonyms": [
      "TREKANTEN KALMAR"
    ],
    "lId": "00760",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 56.70055555555556,
      "lon": 16.111111111111114
    }
  },
  {
    "name": "Trekanten Liljeholmen",
    "synonyms": [
      "TREKANTEN",
      "TREKANTEN LILJEHOLMEN"
    ],
    "lId": "24922",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.31388888888888,
      "lon": 18.018055555555556
    }
  },
  {
    "name": "Trekanten station",
    "synonyms": [
      "TREKANTEN STATION"
    ],
    "lId": "38526",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 56.70166666666667,
      "lon": 16.11722222222222
    }
  },
  {
    "name": "Trelleborg Centralstation",
    "synonyms": [
      "TRELLEBORG CENTRALSTATION"
    ],
    "lId": "00088",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 55.37138888888889,
      "lon": 13.160833333333334
    }
  },
  {
    "name": "Trelleborg övre",
    "synonyms": [
      "TRELLEBORG ÖVRE",
      "TRELLEBORG ØVRE"
    ],
    "lId": "16922",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 55.376666666666665,
      "lon": 13.158611111111112
    }
  },
  {
    "name": "Trestad Center väg 44",
    "synonyms": [
      "TRESTAD C V 44",
      "TRESTAD CENTER VÄG 44",
      "TRESTAD CENTER VÆG 44"
    ],
    "lId": "70231",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 58.33833333333334,
      "lon": 12.243888888888888
    }
  },
  {
    "name": "Trillevallen",
    "synonyms": [
      "TRILLEVALLEN"
    ],
    "lId": "29938",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 63.26,
      "lon": 13.185833333333333
    }
  },
  {
    "name": "Trinntorp",
    "synonyms": [
      "TRINNTORP"
    ],
    "lId": "18271",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.2275,
      "lon": 18.35388888888889
    }
  },
  {
    "name": "Trollbäcken",
    "synonyms": [
      "TROLLBÄCKEN",
      "TROLLBÄCKEN CM",
      "TROLLBÆCKEN",
      "TROLLBÆCKEN CM"
    ],
    "lId": "01351",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.22361111111111,
      "lon": 18.201944444444443
    }
  },
  {
    "name": "Trollhättan C",
    "synonyms": [
      "TROLLHATTAN C",
      "TROLLHÄTTAN C",
      "TROLLHÆTTAN C"
    ],
    "lId": "00191",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 58.2875,
      "lon": 12.299166666666666
    }
  },
  {
    "name": "Trolmen",
    "synonyms": [
      "TROLMEN",
      "TROLMEN STN"
    ],
    "lId": "01352",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 58.59444444444445,
      "lon": 13.3475
    }
  },
  {
    "name": "Trondheim S",
    "synonyms": [
      "TRONDHEIM S"
    ],
    "lId": "01126",
    "prio": 1,
    "pId": "076",
    "pos": {
      "lat": 63.396388888888886,
      "lon": 10.423888888888888
    }
  },
  {
    "name": "Trosa centrum",
    "synonyms": [
      "TROSA CENTRUM"
    ],
    "lId": "00837",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 58.89722222222222,
      "lon": 17.549722222222226
    }
  },
  {
    "name": "Trosa hamn",
    "synonyms": [
      "TROSA HAMN"
    ],
    "lId": "25406",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 58.89111111111111,
      "lon": 17.552777777777777
    }
  },
  {
    "name": "Trosaporten",
    "synonyms": [
      "TROSAPORTEN"
    ],
    "lId": "11974",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 58.905277777777776,
      "lon": 17.55027777777778
    }
  },
  {
    "name": "Trysil Busstasjon",
    "synonyms": [
      "TRYSIL BUSSTASJ",
      "TRYSIL BUSSTASJON"
    ],
    "lId": "90011",
    "prio": 0,
    "pId": "076",
    "pos": {
      "lat": 0,
      "lon": 0
    }
  },
  {
    "name": "Trysilfjellet Alpin",
    "synonyms": [
      "TRYSILFJELLET",
      "TRYSILFJELLET ALPIN"
    ],
    "lId": "90016",
    "prio": 0,
    "pId": "076",
    "pos": {
      "lat": 0,
      "lon": 0
    }
  },
  {
    "name": "Trysunda",
    "synonyms": [
      "TRYSUNDA"
    ],
    "lId": "01211",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 63.138888888888886,
      "lon": 18.788611111111113
    }
  },
  {
    "name": "Trångstad",
    "synonyms": [
      "TRÅNGSTAD",
      "TRÅNGSTAD STN"
    ],
    "lId": "01420",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.55472222222222,
      "lon": 13.258055555555556
    }
  },
  {
    "name": "Trångsund",
    "synonyms": [
      "TRÅNGSUND",
      "TRÅNGSUND STN"
    ],
    "lId": "00774",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.22777777777778,
      "lon": 18.129444444444445
    }
  },
  {
    "name": "Trångsviken ICA",
    "synonyms": [
      "TRÅNGSVIKEN ICA"
    ],
    "lId": "20982",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 63.33277777777778,
      "lon": 14.014722222222222
    }
  },
  {
    "name": "Trädet",
    "synonyms": [
      "TRÄDET",
      "TRÆDET"
    ],
    "lId": "01506",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 57.98555555555556,
      "lon": 13.535
    }
  },
  {
    "name": "Träkvista",
    "synonyms": [
      "TRÄKVISTA",
      "TRÆKVISTA"
    ],
    "lId": "01353",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.275555555555556,
      "lon": 17.784444444444446
    }
  },
  {
    "name": "Träne Prästgården",
    "synonyms": [
      "TRÄNE PRÄSTGÅRDEN"
    ],
    "lId": "30736",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 55.98722222222222,
      "lon": 13.99111111111111
    }
  },
  {
    "name": "Träslövsläge Storgatan",
    "synonyms": [
      "TRÄSLÖVSLÄGE STORGATAN"
    ],
    "lId": "34250",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 57.051111111111105,
      "lon": 12.286944444444444
    }
  },
  {
    "name": "Trödje",
    "synonyms": [
      "TRÖDJE",
      "TRØDJE"
    ],
    "lId": "26080",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 60.81666666666667,
      "lon": 17.211388888888887
    }
  },
  {
    "name": "Trönninge Halmstad",
    "synonyms": [
      "TRÖNNINGE HALMS",
      "TRÖNNINGE HALMSTAD",
      "TRØNNINGE HALMS",
      "TRØNNINGE HALMSTAD"
    ],
    "lId": "00057",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 56.617777777777775,
      "lon": 12.946388888888889
    }
  },
  {
    "name": "Trönninge Varberg",
    "synonyms": [
      "TRÖNNINGE VARBERG",
      "TRØNNINGE VARBERG"
    ],
    "lId": "17198",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 57.14194444444444,
      "lon": 12.290277777777778
    }
  },
  {
    "name": "Tulebohöjd",
    "synonyms": [
      "TULEBOHÖJD"
    ],
    "lId": "15655",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 57.61833333333333,
      "lon": 12.105277777777777
    }
  },
  {
    "name": "Tulleråsen",
    "synonyms": [
      "TULLERÅSEN"
    ],
    "lId": "13400",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 63.45638888888889,
      "lon": 14.18888888888889
    }
  },
  {
    "name": "Tullgarn",
    "synonyms": [
      "TULLGARN"
    ],
    "lId": "21596",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 58.96416666666667,
      "lon": 17.56416666666667
    }
  },
  {
    "name": "Tullinge",
    "synonyms": [
      "TULLINGE",
      "TULLINGE STN"
    ],
    "lId": "00775",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.205000000000005,
      "lon": 17.903055555555554
    }
  },
  {
    "name": "Tumba",
    "synonyms": [
      "TUMBA",
      "TUMBA STN"
    ],
    "lId": "00776",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.19972222222222,
      "lon": 17.835555555555555
    }
  },
  {
    "name": "Tumbo kyrka",
    "synonyms": [
      "TUMBO",
      "TUMBO KYRKA"
    ],
    "lId": "11670",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.426944444444445,
      "lon": 16.339444444444442
    }
  },
  {
    "name": "Tuna station",
    "synonyms": [
      "TUNA STATION",
      "TUNA STN"
    ],
    "lId": "14404",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 57.5775,
      "lon": 16.10388888888889
    }
  },
  {
    "name": "Tuna Ytterenhörna",
    "synonyms": [
      "TUNA YTTERENHÖRNA",
      "TUNA YTTERENHØRNA"
    ],
    "lId": "01110",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.25333333333333,
      "lon": 17.490277777777777
    }
  },
  {
    "name": "Tunaberg kyrka",
    "synonyms": [
      "TUNABERG KYRKA"
    ],
    "lId": "21336",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 58.64472222222222,
      "lon": 16.899722222222223
    }
  },
  {
    "name": "Tungelsta",
    "synonyms": [
      "TUNGELSTA",
      "TUNGELSTA STN"
    ],
    "lId": "00777",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.102222222222224,
      "lon": 18.044722222222223
    }
  },
  {
    "name": "Tuskö",
    "synonyms": [
      "TUSKÖ",
      "TUSKØ"
    ],
    "lId": "12745",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 60.236666666666665,
      "lon": 18.488055555555558
    }
  },
  {
    "name": "Tuvesvik",
    "synonyms": [
      "TUVESVIK"
    ],
    "lId": "15813",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 58.17472222222222,
      "lon": 11.415833333333333
    }
  },
  {
    "name": "Tving Bygatan",
    "synonyms": [
      "TVING BYGATAN"
    ],
    "lId": "24914",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 56.311388888888885,
      "lon": 15.458055555555555
    }
  },
  {
    "name": "Tvååker Centrum",
    "synonyms": [
      "TVÅÅKER CENTRUM"
    ],
    "lId": "00188",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 57.04138888888889,
      "lon": 12.398333333333333
    }
  },
  {
    "name": "Tvärskog",
    "synonyms": [
      "TVÄRSKOG",
      "TVÆRSKOG"
    ],
    "lId": "14405",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 56.621944444444445,
      "lon": 16.0425
    }
  },
  {
    "name": "Tväråbäck",
    "synonyms": [
      "TVÄRÅBÄCK",
      "TVÄRÅBÄCK BYN",
      "TVÆRÅBÆCK",
      "TVÆRÅBÆCK BYN"
    ],
    "lId": "01354",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 63.99194444444444,
      "lon": 19.724444444444444
    }
  },
  {
    "name": "Tvärålund E12",
    "synonyms": [
      "TVÄRÅLUND E12",
      "TVÆRÅLUND E12"
    ],
    "lId": "01355",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 64.08416666666666,
      "lon": 19.627222222222223
    }
  },
  {
    "name": "Tvärålund station",
    "synonyms": [
      "TVÄRÅLUND STATION",
      "TVÆRÅLUND STATION"
    ],
    "lId": "01609",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 64.09722222222221,
      "lon": 19.674444444444447
    }
  },
  {
    "name": "Tygelsjö Gullkragegatan",
    "synonyms": [
      "TYGELSJÖ GULLKG",
      "TYGELSJÖ GULLKRAGEGATAN",
      "TYGELSJØ GULLKG",
      "TYGELSJØ GULLKRAGEGATAN"
    ],
    "lId": "21761",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 55.51777777777777,
      "lon": 12.998055555555554
    }
  },
  {
    "name": "Tylösand",
    "synonyms": [
      "TYLÖSAND",
      "TYLØSAND"
    ],
    "lId": "01356",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 56.64722222222222,
      "lon": 12.733333333333333
    }
  },
  {
    "name": "Tynnered Briljantgatan",
    "synonyms": [
      "TYNNERED BRILJANTGATAN"
    ],
    "lId": "25613",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 57.64833333333333,
      "lon": 11.903055555555556
    }
  },
  {
    "name": "Tynnered Opaltorget",
    "synonyms": [
      "TYNNERED OPALTG",
      "TYNNERED OPALTORGET"
    ],
    "lId": "25668",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 57.64138888888889,
      "lon": 11.900833333333333
    }
  },
  {
    "name": "Tynnered Smaragdgatan",
    "synonyms": [
      "TYNNERED SMARAGDGATAN"
    ],
    "lId": "25684",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 57.64527777777778,
      "lon": 11.899166666666666
    }
  },
  {
    "name": "Tyresö Brevik",
    "synonyms": [
      "TYRESÖ BREVIK",
      "TYRESÖ BREVIK M",
      "TYRESØ BREVIK",
      "TYRESØ BREVIK M"
    ],
    "lId": "01357",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.213055555555556,
      "lon": 18.379444444444445
    }
  },
  {
    "name": "Tyresö centrum",
    "synonyms": [
      "TYRESÖ CENTRUM",
      "TYRESØ CENTRUM"
    ],
    "lId": "00778",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.24388888888889,
      "lon": 18.229166666666664
    }
  },
  {
    "name": "Tyresö kyrka",
    "synonyms": [
      "TYRESÖ KYRKA",
      "TYRESØ KYRKA"
    ],
    "lId": "24299",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.236666666666665,
      "lon": 18.297500000000003
    }
  },
  {
    "name": "Tyringe",
    "synonyms": [
      "TYRINGE"
    ],
    "lId": "00290",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 56.15972222222222,
      "lon": 13.598055555555556
    }
  },
  {
    "name": "Tyringe Arboga",
    "synonyms": [
      "TYRINGE ARBOGA"
    ],
    "lId": "45206",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.31888888888889,
      "lon": 15.9
    }
  },
  {
    "name": "Tystberga",
    "synonyms": [
      "TYSTBERGA"
    ],
    "lId": "11683",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 58.846944444444446,
      "lon": 17.23611111111111
    }
  },
  {
    "name": "Tystberga trafikplats",
    "synonyms": [
      "TYSTBERGA TRAFIKPLATS",
      "TYSTBERGA TRPL"
    ],
    "lId": "04047",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 58.85666666666667,
      "lon": 17.206666666666667
    }
  },
  {
    "name": "Tågarp",
    "synonyms": [
      "TAGARP",
      "TÅGARP"
    ],
    "lId": "01556",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 55.92638888888889,
      "lon": 12.952499999999999
    }
  },
  {
    "name": "Tångaberg",
    "synonyms": [
      "TÅNGABERG"
    ],
    "lId": "17202",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 57.174166666666665,
      "lon": 12.229722222222222
    }
  },
  {
    "name": "Tångböle",
    "synonyms": [
      "TÅNGBÖLE",
      "TÅNGBØLE"
    ],
    "lId": "29943",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 63.36222222222222,
      "lon": 12.621944444444445
    }
  },
  {
    "name": "Tånnö",
    "synonyms": [
      "TÅNNÖ",
      "TÅNNÖ KYRKA",
      "TÅNNØ",
      "TÅNNØ KYRKA"
    ],
    "lId": "01358",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 57.090833333333336,
      "lon": 14.044166666666667
    }
  },
  {
    "name": "Tårnby",
    "synonyms": [
      "TARNBY",
      "TÅRNBY"
    ],
    "lId": "00857",
    "prio": 0,
    "pId": "086",
    "pos": {
      "lat": 55.629444444444445,
      "lon": 12.604444444444445
    }
  },
  {
    "name": "Tåstarp Hjärnarpsvägen",
    "synonyms": [
      "TÅSTARP HJÄRNARPSVÄGEN",
      "TÅSTARP HJÆRNARPSVÆGEN"
    ],
    "lId": "04078",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 56.280833333333334,
      "lon": 12.944444444444445
    }
  },
  {
    "name": "Täby centrum",
    "synonyms": [
      "TÄBY CENTRUM",
      "TÆBY CENTRUM"
    ],
    "lId": "00779",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.442499999999995,
      "lon": 18.072777777777777
    }
  },
  {
    "name": "Täby kyrkby",
    "synonyms": [
      "TÄBY KYRKBY",
      "TÄBY KYRKBY STN",
      "TÆBY KYRKBY",
      "TÆBY KYRKBY STN"
    ],
    "lId": "01153",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.4925,
      "lon": 18.065555555555555
    }
  },
  {
    "name": "Täfteå samhälle",
    "synonyms": [
      "TÄFTEÅ SAMHÄLLE",
      "TÆFTEÅ SAMHÆLLE"
    ],
    "lId": "13680",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 63.84305555555556,
      "lon": 20.47694444444444
    }
  },
  {
    "name": "Täljö",
    "synonyms": [
      "TÄLJÖ",
      "TÄLJÖ STN",
      "TÆLJØ",
      "TÆLJØ STN"
    ],
    "lId": "24805",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.47222222222222,
      "lon": 18.233333333333334
    }
  },
  {
    "name": "Tällberg",
    "synonyms": [
      "TALLBERG",
      "TÄLLBERG",
      "TÄLLBERG STN",
      "TÆLLBERG",
      "TÆLLBERG STN"
    ],
    "lId": "00097",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 60.81805555555556,
      "lon": 15.018333333333334
    }
  },
  {
    "name": "Tänndalen",
    "synonyms": [
      "TÄNNDALEN",
      "TÆNNDALEN"
    ],
    "lId": "00529",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 62.549166666666665,
      "lon": 12.309722222222224
    }
  },
  {
    "name": "Tännäs",
    "synonyms": [
      "TÄNNÄS",
      "TÆNNÆS"
    ],
    "lId": "00530",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 62.442499999999995,
      "lon": 12.680555555555555
    }
  },
  {
    "name": "Tärendö",
    "synonyms": [
      "TÄRENDÖ",
      "TÄRENDÖ POSTEN",
      "TÆRENDØ",
      "TÆRENDØ POSTEN"
    ],
    "lId": "00892",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 67.1525,
      "lon": 22.63611111111111
    }
  },
  {
    "name": "Tärnaby",
    "synonyms": [
      "TÄRNABY",
      "TÄRNABY BSTN",
      "TÆRNABY",
      "TÆRNABY BSTN"
    ],
    "lId": "00394",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 65.71055555555556,
      "lon": 15.249722222222221
    }
  },
  {
    "name": "Tärnsjö",
    "synonyms": [
      "TÄRNSJÖ",
      "TÄRNSJÖ KONSUM",
      "TÆRNSJØ",
      "TÆRNSJØ KONSUM"
    ],
    "lId": "00682",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 60.15333333333333,
      "lon": 16.927222222222223
    }
  },
  {
    "name": "Tävelsås skola",
    "synonyms": [
      "TÄVELSÅS SKOLA",
      "TÆVELSÅS SKOLA"
    ],
    "lId": "11693",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 56.77472222222222,
      "lon": 14.826944444444445
    }
  },
  {
    "name": "Töcksfors Centralen",
    "synonyms": [
      "TÖCKSFORS CENTRALEN",
      "TØCKSFORS CENTRALEN"
    ],
    "lId": "01360",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.50833333333333,
      "lon": 11.84138888888889
    }
  },
  {
    "name": "Tönnebro Värdshus",
    "synonyms": [
      "TÖNNEBRO VÄRDSHUS"
    ],
    "lId": "23136",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 61.07166666666667,
      "lon": 16.965555555555554
    }
  },
  {
    "name": "Töre",
    "synonyms": [
      "TÖRE",
      "TÖRE BSTN",
      "TØRE",
      "TØRE BSTN"
    ],
    "lId": "00895",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 65.91250000000001,
      "lon": 22.64527777777778
    }
  },
  {
    "name": "Töreboda",
    "synonyms": [
      "TOREBODA",
      "TÖREBODA",
      "TÖREBODA STN",
      "TØREBODA",
      "TØREBODA STN"
    ],
    "lId": "00183",
    "prio": 1,
    "pId": "074",
    "pos": {
      "lat": 58.70583333333334,
      "lon": 14.128333333333334
    }
  },
  {
    "name": "Tösse",
    "synonyms": [
      "TÖSSE",
      "TÖSSE STN",
      "TØSSE",
      "TØSSE STN"
    ],
    "lId": "01507",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 58.972500000000004,
      "lon": 12.644166666666667
    }
  },
  {
    "name": "Töva E14",
    "synonyms": [
      "TÖVA E14",
      "TØVA E14"
    ],
    "lId": "15536",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 62.376666666666665,
      "lon": 17.133333333333333
    }
  },
  {
    "name": "Ucklum skola",
    "synonyms": [
      "UCKLUM SKOLA"
    ],
    "lId": "15765",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 58.085,
      "lon": 11.956944444444444
    }
  },
  {
    "name": "Uddebo",
    "synonyms": [
      "UDDEBO"
    ],
    "lId": "23105",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 57.471944444444446,
      "lon": 13.254166666666666
    }
  },
  {
    "name": "Uddeholm",
    "synonyms": [
      "UDDEHOLM",
      "UDDEHOLM KONTOR"
    ],
    "lId": "01361",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 60.021388888888886,
      "lon": 13.621111111111112
    }
  },
  {
    "name": "Uddevalla C",
    "synonyms": [
      "UDDEVALLA C"
    ],
    "lId": "00119",
    "prio": 1,
    "pId": "074",
    "pos": {
      "lat": 58.35416666666667,
      "lon": 11.9225
    }
  },
  {
    "name": "Uddevalla Östra",
    "synonyms": [
      "UDDEVALLA ÖSTRA",
      "UDDEVALLA ØSTRA"
    ],
    "lId": "20037",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 58.35055555555556,
      "lon": 11.944722222222222
    }
  },
  {
    "name": "Ugglarp",
    "synonyms": [
      "UGGLARP"
    ],
    "lId": "01362",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 56.81777777777778,
      "lon": 12.628333333333334
    }
  },
  {
    "name": "Ullared",
    "synonyms": [
      "ULLARED"
    ],
    "lId": "00182",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 57.13638888888889,
      "lon": 12.716388888888888
    }
  },
  {
    "name": "Ullatti",
    "synonyms": [
      "ULLATTI",
      "ULLATTI AFFÄREN",
      "ULLATTI AFFÆREN"
    ],
    "lId": "01363",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 67.01861111111111,
      "lon": 21.811666666666667
    }
  },
  {
    "name": "Ullersätter",
    "synonyms": [
      "ULLERSÄTTER",
      "ULLERSÆTTER"
    ],
    "lId": "21247",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.45444444444445,
      "lon": 15.449166666666667
    }
  },
  {
    "name": "Ullervad skola",
    "synonyms": [
      "ULLERVAD SKOLA"
    ],
    "lId": "25045",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 58.66583333333333,
      "lon": 13.857222222222221
    }
  },
  {
    "name": "Ullånger",
    "synonyms": [
      "ULLÅNGER",
      "ULLÅNGER OK"
    ],
    "lId": "00467",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 63.01083333333333,
      "lon": 18.188333333333333
    }
  },
  {
    "name": "Ulricehamn",
    "synonyms": [
      "ULRICEHAMN",
      "ULRICEHAMN BSTN"
    ],
    "lId": "00094",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 57.79361111111111,
      "lon": 13.411666666666667
    }
  },
  {
    "name": "Ulricehamn Brunnsnäs",
    "synonyms": [
      "ULRICEHAMN BRUNNSNÄS"
    ],
    "lId": "23239",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 57.801111111111105,
      "lon": 13.397222222222222
    }
  },
  {
    "name": "Ulricehamnsmotet",
    "synonyms": [
      "ULRICEHAMNMOTET",
      "ULRICEHAMNSMOTET"
    ],
    "lId": "72679",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 57.80916666666666,
      "lon": 13.421388888888888
    }
  },
  {
    "name": "Ulrika busstation",
    "synonyms": [
      "ULRIKA BSTN",
      "ULRIKA BUSSTATION",
      "ULRIKA BUSSTN"
    ],
    "lId": "11700",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 58.123333333333335,
      "lon": 15.429722222222221
    }
  },
  {
    "name": "Ulriksdal",
    "synonyms": [
      "ULRIKSDAL",
      "ULRIKSDAL STN"
    ],
    "lId": "00781",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.38055555555555,
      "lon": 18
    }
  },
  {
    "name": "Ulriksfors",
    "synonyms": [
      "ULRIKSFORS",
      "ULRIKSFORS STN"
    ],
    "lId": "30055",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 63.831944444444446,
      "lon": 15.620833333333334
    }
  },
  {
    "name": "Ulvöhamn",
    "synonyms": [
      "ULVÖHAMN",
      "ULVØHAMN"
    ],
    "lId": "01364",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 63.02166666666667,
      "lon": 18.649166666666666
    }
  },
  {
    "name": "Umeå C",
    "synonyms": [
      "UMEÅ C"
    ],
    "lId": "00190",
    "prio": 1,
    "pId": "074",
    "pos": {
      "lat": 63.830000000000005,
      "lon": 20.266666666666666
    }
  },
  {
    "name": "Umeå Östra",
    "synonyms": [
      "UMEÅ ÖSTRA",
      "UMEÅ ØSTRA"
    ],
    "lId": "01581",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 63.8175,
      "lon": 20.293333333333337
    }
  },
  {
    "name": "Umeå Universitetssjukhuset",
    "synonyms": [
      "UMEÅ UNIVERSITETSSJUKHUSET"
    ],
    "lId": "23840",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 63.818333333333335,
      "lon": 20.29638888888889
    }
  },
  {
    "name": "Umeå Ålidhem",
    "synonyms": [
      "UMEÅ ÅLIDHEM"
    ],
    "lId": "45443",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 63.812777777777775,
      "lon": 20.315833333333334
    }
  },
  {
    "name": "Unbyn Gymnastiken",
    "synonyms": [
      "UNBYN GYMNASTIKEN"
    ],
    "lId": "27008",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 65.71527777777779,
      "lon": 21.749722222222225
    }
  },
  {
    "name": "Undenäs kyrka",
    "synonyms": [
      "UNDENÄS KYRKA",
      "UNDENÆS KYRKA"
    ],
    "lId": "24045",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 58.65888888888889,
      "lon": 14.399166666666666
    }
  },
  {
    "name": "Undersvik skolan",
    "synonyms": [
      "UNDERSVIK SKOLAN"
    ],
    "lId": "18551",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 61.614444444444445,
      "lon": 16.32
    }
  },
  {
    "name": "Undersåker",
    "synonyms": [
      "UNDERSAKER",
      "UNDERSÅKER"
    ],
    "lId": "00142",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 63.31472222222222,
      "lon": 13.237777777777778
    }
  },
  {
    "name": "Undrom affär",
    "synonyms": [
      "UNDROM AFFÄR",
      "UNDROM AFFÆR"
    ],
    "lId": "15329",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 63.118611111111115,
      "lon": 17.740277777777777
    }
  },
  {
    "name": "Universitetet T-bana",
    "synonyms": [
      "UNIVERSITETET T-BANA"
    ],
    "lId": "21645",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.36555555555556,
      "lon": 18.054722222222225
    }
  },
  {
    "name": "Unnaryd",
    "synonyms": [
      "UNNARYD"
    ],
    "lId": "17205",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 56.95444444444445,
      "lon": 13.528055555555556
    }
  },
  {
    "name": "Unungehöjden",
    "synonyms": [
      "UNUNGEHÖJDEN",
      "UNUNGEHØJDEN"
    ],
    "lId": "11704",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.90472222222222,
      "lon": 18.578888888888887
    }
  },
  {
    "name": "Upperud",
    "synonyms": [
      "UPPERUD",
      "UPPERUD SLUSSEN"
    ],
    "lId": "01509",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 58.81388888888888,
      "lon": 12.436388888888889
    }
  },
  {
    "name": "Upphärad station",
    "synonyms": [
      "UPPHÄRAD STATION",
      "UPPHÄRAD STN",
      "UPPHÆRAD STATION",
      "UPPHÆRAD STN"
    ],
    "lId": "12310",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 58.15611111111111,
      "lon": 12.306666666666667
    }
  },
  {
    "name": "Upplands Väsby Fresta kyrka",
    "synonyms": [
      "UPPLANDS VÄSBY FRESTA KYRKA"
    ],
    "lId": "66767",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.518055555555556,
      "lon": 17.956944444444442
    }
  },
  {
    "name": "Upplands Väsby Kanalvägen",
    "synonyms": [
      "UPPL VBY KANALV",
      "UPPLANDS VÄSBY KANALVÄGEN"
    ],
    "lId": "66881",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.4975,
      "lon": 17.930555555555557
    }
  },
  {
    "name": "Upplands Väsby Scandic Hotel",
    "synonyms": [
      "UPPLANDS VÄSBY SCANDIC HOTEL"
    ],
    "lId": "23139",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.515,
      "lon": 17.920555555555556
    }
  },
  {
    "name": "Upplands Väsby station",
    "synonyms": [
      "UPPLANDS VÄSBY STATION"
    ],
    "lId": "00782",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.52166666666667,
      "lon": 17.899444444444445
    }
  },
  {
    "name": "Uppsala C",
    "synonyms": [
      "QYX",
      "UPPSALA C"
    ],
    "lId": "00005",
    "prio": 1,
    "pId": "074",
    "pos": {
      "lat": 59.858333333333334,
      "lon": 17.645833333333332
    }
  },
  {
    "name": "Uppsala stadszon",
    "synonyms": [
      "UPPSALA STADSZON",
      "UPPSALA ZON"
    ],
    "lId": "71918",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.858333333333334,
      "lon": 17.645833333333332
    }
  },
  {
    "name": "Uppsala Akademiska sjukhuset",
    "synonyms": [
      "UPPSALA AKADEMISKA SJUKHUSET"
    ],
    "lId": "07637",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.85,
      "lon": 17.643055555555556
    }
  },
  {
    "name": "Uppsala Business Park",
    "synonyms": [
      "UPPSALA BUSINESS PARK"
    ],
    "lId": "08428",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.845555555555556,
      "lon": 17.704722222222223
    }
  },
  {
    "name": "Uppsala Campus Ultuna",
    "synonyms": [
      "ULTUNA CAMPUS",
      "UPPSALA CAMPUS ULTUNA"
    ],
    "lId": "07571",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.81527777777777,
      "lon": 17.659166666666664
    }
  },
  {
    "name": "Uppsala Djursjukhuset",
    "synonyms": [
      "UPPSALA DJURSJUKHUSET"
    ],
    "lId": "12818",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.81333333333333,
      "lon": 17.65888888888889
    }
  },
  {
    "name": "Uppsala Ekonomikum",
    "synonyms": [
      "UPPSALA EKONOMIKUM"
    ],
    "lId": "07480",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.86,
      "lon": 17.62027777777778
    }
  },
  {
    "name": "Uppsala Flogsta väg 55",
    "synonyms": [
      "UPPSALA FLOGSTA V2G 55",
      "UPPSALA FLOGSTA VÄG 55"
    ],
    "lId": "23259",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.852222222222224,
      "lon": 17.58611111111111
    }
  },
  {
    "name": "Uppsala Fyrishovs entré",
    "synonyms": [
      "UPPSALA FYRISHOVS ENTRÉ"
    ],
    "lId": "07854",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.87083333333334,
      "lon": 17.62388888888889
    }
  },
  {
    "name": "Uppsala Garnisonen",
    "synonyms": [
      "UPPSALA GARNISONEN"
    ],
    "lId": "07837",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.88777777777778,
      "lon": 17.606944444444444
    }
  },
  {
    "name": "Uppsala Hj Brantings Gata 46",
    "synonyms": [
      "UPPSALA HJ BRANTINGS GATA 46"
    ],
    "lId": "18293",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.86555555555556,
      "lon": 17.663888888888888
    }
  },
  {
    "name": "Uppsala Science Park",
    "synonyms": [
      "UPPSALA SCIENCE PARK"
    ],
    "lId": "07825",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.84305555555556,
      "lon": 17.63861111111111
    }
  },
  {
    "name": "Uppsala Studentstaden",
    "synonyms": [
      "UPPSALA STUDENTSTADEN"
    ],
    "lId": "07481",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.8575,
      "lon": 17.61277777777778
    }
  },
  {
    "name": "Urshult Stationsvägen",
    "synonyms": [
      "URSHULT STATIONSVÄGEN",
      "URSHULT STATIONSVÆGEN",
      "URSHULT STNSVÄG",
      "URSHULT STNSVÆG",
      "URSHULT STNVÄG",
      "URSHULT STNVÆG"
    ],
    "lId": "23357",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 56.53138888888889,
      "lon": 14.8125
    }
  },
  {
    "name": "Utanede Ragunda",
    "synonyms": [
      "UTANEDE RAGUNDA"
    ],
    "lId": "23273",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 62.95666666666667,
      "lon": 16.68
    }
  },
  {
    "name": "Utansjö Pärleporten",
    "synonyms": [
      "UTANSJÖ PÄRLEPORTEN",
      "UTANSJØ PÆRLEPORTEN"
    ],
    "lId": "26958",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 62.77333333333333,
      "lon": 17.91611111111111
    }
  },
  {
    "name": "Uttersberg",
    "synonyms": [
      "UTTERSBERG"
    ],
    "lId": "43980",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.749722222222225,
      "lon": 15.665833333333333
    }
  },
  {
    "name": "Utvälinge Skeppsvägen",
    "synonyms": [
      "UTVÄLINGE SKEPPSVÄGEN",
      "UTVÄLINGE SKEPV"
    ],
    "lId": "16931",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 56.21277777777778,
      "lon": 12.786388888888888
    }
  },
  {
    "name": "Utö Gruvbryggan",
    "synonyms": [
      "UTÖ GRUVBRYGGAN",
      "UTØ GRUVBRYGGAN"
    ],
    "lId": "20695",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 58.97027777777778,
      "lon": 18.325
    }
  },
  {
    "name": "Uvanå",
    "synonyms": [
      "UVANÅ"
    ],
    "lId": "11709",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 60.28777777777778,
      "lon": 13.783055555555556
    }
  },
  {
    "name": "Vad station",
    "synonyms": [
      "VAD STATION"
    ],
    "lId": "00683",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 60.032222222222224,
      "lon": 15.642222222222221
    }
  },
  {
    "name": "Vadsbro",
    "synonyms": [
      "VADSBRO"
    ],
    "lId": "11723",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 58.96416666666667,
      "lon": 16.59722222222222
    }
  },
  {
    "name": "Vadstena",
    "synonyms": [
      "VADSTENA",
      "VADSTENA STN"
    ],
    "lId": "00628",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 58.443888888888885,
      "lon": 14.88361111111111
    }
  },
  {
    "name": "Vaggeryd",
    "synonyms": [
      "VAGGERYD",
      "VAGGERYD STN"
    ],
    "lId": "00232",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 57.49805555555556,
      "lon": 14.145
    }
  },
  {
    "name": "Vagnhärad",
    "synonyms": [
      "VAGNHARAD",
      "VAGNHÄRAD",
      "VAGNHÄRAD STN",
      "VAGNHÆRAD",
      "VAGNHÆRAD STN"
    ],
    "lId": "00605",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 58.94555555555555,
      "lon": 17.496666666666666
    }
  },
  {
    "name": "Vaikijaur",
    "synonyms": [
      "VAIKIJAUR",
      "VAIKIJAUR STN"
    ],
    "lId": "04456",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 66.64944444444446,
      "lon": 19.829722222222223
    }
  },
  {
    "name": "Vakkotavare",
    "synonyms": [
      "VAKKOTAVARE"
    ],
    "lId": "20197",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 67.58333333333333,
      "lon": 18.087777777777777
    }
  },
  {
    "name": "Valbo",
    "synonyms": [
      "VALBO",
      "VALBO IKEA"
    ],
    "lId": "00273",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 60.63333333333333,
      "lon": 16.988333333333333
    }
  },
  {
    "name": "Valbo Motorvägen",
    "synonyms": [
      "VALBO MOTORVÄGEN",
      "VALBO MOTORVÆGEN"
    ],
    "lId": "16587",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 60.630833333333335,
      "lon": 16.990277777777777
    }
  },
  {
    "name": "Valdemarsvik",
    "synonyms": [
      "VALDEMARSVIK",
      "VALDEMARSVK BST"
    ],
    "lId": "00593",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 58.200833333333335,
      "lon": 16.603333333333335
    }
  },
  {
    "name": "Valdemarsvik E22",
    "synonyms": [
      "VALDEMARSVIK E22"
    ],
    "lId": "18588",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 58.22138888888889,
      "lon": 16.552777777777777
    }
  },
  {
    "name": "Valje",
    "synonyms": [
      "VALJE",
      "VALJE SKOLAN"
    ],
    "lId": "01510",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 56.06305555555555,
      "lon": 14.547777777777778
    }
  },
  {
    "name": "Valla",
    "synonyms": [
      "VALLA",
      "VALLA KIOSKEN"
    ],
    "lId": "11735",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.02055555555555,
      "lon": 16.380833333333335
    }
  },
  {
    "name": "Vallargärdet väg 63",
    "synonyms": [
      "VALLARGÄRDE V63",
      "VALLARGÄRDET VÄG 63",
      "VALLARGÆRDE V63",
      "VALLARGÆRDET VÆG 63"
    ],
    "lId": "11736",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.477222222222224,
      "lon": 13.585833333333333
    }
  },
  {
    "name": "Vallberga",
    "synonyms": [
      "VALLBERGA"
    ],
    "lId": "01511",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 56.46805555555556,
      "lon": 13.023888888888889
    }
  },
  {
    "name": "Vallbo",
    "synonyms": [
      "VALLBO"
    ],
    "lId": "13553",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 63.15694444444444,
      "lon": 13.071388888888889
    }
  },
  {
    "name": "Vallentuna",
    "synonyms": [
      "VALLENTUNA",
      "VALLENTUNA STN"
    ],
    "lId": "00783",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.53333333333333,
      "lon": 18.079722222222223
    }
  },
  {
    "name": "Valleviken",
    "synonyms": [
      "VALLEVIKEN"
    ],
    "lId": "01365",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 57.791666666666664,
      "lon": 18.93888888888889
    }
  },
  {
    "name": "Vallkärra",
    "synonyms": [
      "VALLKÄRRA",
      "VALLKÄRRA STNBY",
      "VALLKÆRRA",
      "VALLKÆRRA STNBY"
    ],
    "lId": "01539",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 55.74611111111111,
      "lon": 13.145
    }
  },
  {
    "name": "Vallsta station",
    "synonyms": [
      "VALLSTA STATION"
    ],
    "lId": "00753",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 61.5175,
      "lon": 16.3675
    }
  },
  {
    "name": "Vallvik",
    "synonyms": [
      "VALLVIK"
    ],
    "lId": "01366",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 61.18444444444444,
      "lon": 17.179722222222225
    }
  },
  {
    "name": "Vallåkra",
    "synonyms": [
      "VALLÅKRA",
      "VALLÅKRA STN"
    ],
    "lId": "16940",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 55.96361111111111,
      "lon": 12.861666666666666
    }
  },
  {
    "name": "Vallåsen Skidanläggning Våxtor",
    "synonyms": [
      "VALLÅSEN SKIDANLÄGGNING VÅXTOR"
    ],
    "lId": "71350",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 56.376111111111115,
      "lon": 13.1
    }
  },
  {
    "name": "Valsjöbyn",
    "synonyms": [
      "VALSJÖBYN",
      "VALSJØBYN"
    ],
    "lId": "01367",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 64.06722222222221,
      "lon": 14.140833333333333
    }
  },
  {
    "name": "Valskog",
    "synonyms": [
      "VALSKOG",
      "VALSKOG CENTRUM"
    ],
    "lId": "00684",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.442499999999995,
      "lon": 15.94888888888889
    }
  },
  {
    "name": "Valstad",
    "synonyms": [
      "VALSTAD"
    ],
    "lId": "04224",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 58.125277777777775,
      "lon": 13.812222222222223
    }
  },
  {
    "name": "Valstad skola",
    "synonyms": [
      "VALSTAD SKOLA",
      "VALSTAD SKOLAN"
    ],
    "lId": "24225",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 58.125,
      "lon": 13.815833333333334
    }
  },
  {
    "name": "Vamlingbo",
    "synonyms": [
      "VAMLINGBO",
      "VAMLINGBO MEJER"
    ],
    "lId": "01368",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 56.97166666666667,
      "lon": 18.235
    }
  },
  {
    "name": "Vankiva affären",
    "synonyms": [
      "VANKIVA AFFÄREN",
      "VANKIVA AFFÆREN"
    ],
    "lId": "31606",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 56.198611111111106,
      "lon": 13.746388888888887
    }
  },
  {
    "name": "Vansbro centrum",
    "synonyms": [
      "VANSBRO CENTRUM"
    ],
    "lId": "00406",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 60.511944444444445,
      "lon": 14.226666666666667
    }
  },
  {
    "name": "Vanstad",
    "synonyms": [
      "VANSTAD"
    ],
    "lId": "16943",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 55.620555555555555,
      "lon": 13.860277777777778
    }
  },
  {
    "name": "Vanås",
    "synonyms": [
      "VANÅS"
    ],
    "lId": "04108",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 56.1875,
      "lon": 14.04861111111111
    }
  },
  {
    "name": "Vaplan",
    "synonyms": [
      "VAPLAN"
    ],
    "lId": "29161",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 63.33722222222222,
      "lon": 14.221388888888889
    }
  },
  {
    "name": "Vara station",
    "synonyms": [
      "VARA STATION",
      "VARA STN"
    ],
    "lId": "00016",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 58.260555555555555,
      "lon": 12.951666666666666
    }
  },
  {
    "name": "Varberg",
    "synonyms": [
      "VARBERG",
      "VARBERG STN"
    ],
    "lId": "00110",
    "prio": 1,
    "pId": "074",
    "pos": {
      "lat": 57.10916666666667,
      "lon": 12.248055555555554
    }
  },
  {
    "name": "Varekil bussterminal",
    "synonyms": [
      "VAREKIL BSTN",
      "VAREKIL BUSSTERMINAL"
    ],
    "lId": "15835",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 58.125,
      "lon": 11.720555555555556
    }
  },
  {
    "name": "Vargens Wärdshus",
    "synonyms": [
      "VARGENS WÄRDSHUS"
    ],
    "lId": "64289",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 62.476111111111116,
      "lon": 13.991666666666665
    }
  },
  {
    "name": "Vargön",
    "synonyms": [
      "VARGON",
      "VARGÖN",
      "VARGÖN STN",
      "VARGØN",
      "VARGØN STN"
    ],
    "lId": "00012",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 58.35916666666667,
      "lon": 12.3925
    }
  },
  {
    "name": "Varjisträsk",
    "synonyms": [
      "VARJISTRÄSK",
      "VARJISTRÄSK STN",
      "VARJISTRÆSK",
      "VARJISTRÆSK STN"
    ],
    "lId": "04457",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 66.04472222222222,
      "lon": 19.531944444444445
    }
  },
  {
    "name": "Varmsätra skola",
    "synonyms": [
      "VARMSÄTRA SKOLA"
    ],
    "lId": "38114",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.86972222222222,
      "lon": 16.71944444444444
    }
  },
  {
    "name": "Varnhem busstation",
    "synonyms": [
      "VARNHEM BSTN",
      "VARNHEM BUSSTATION"
    ],
    "lId": "20259",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 58.38666666666666,
      "lon": 13.648055555555555
    }
  },
  {
    "name": "Vartofta affären",
    "synonyms": [
      "VARTOFTA AFFÄREN",
      "VARTOFTA AFFÆREN"
    ],
    "lId": "11757",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 58.09638888888889,
      "lon": 13.631111111111112
    }
  },
  {
    "name": "Vassijaure",
    "synonyms": [
      "VASSIJAURE",
      "VASSIJAURE STN"
    ],
    "lId": "00208",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 68.42861111111111,
      "lon": 18.260277777777777
    }
  },
  {
    "name": "Vassjön station",
    "synonyms": [
      "VASSJÖN STATION",
      "VASSJÖN STN",
      "VASSJØN STATION",
      "VASSJØN STN"
    ],
    "lId": "04458",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 61.56666666666667,
      "lon": 14.788055555555555
    }
  },
  {
    "name": "Vassmolösa",
    "synonyms": [
      "VASSMOLÖSA",
      "VASSMOLØSA"
    ],
    "lId": "22605",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 56.59305555555556,
      "lon": 16.152777777777775
    }
  },
  {
    "name": "Vattholma",
    "synonyms": [
      "VATTHOLMA",
      "VATTHOLMA STN"
    ],
    "lId": "00458",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 60.025555555555556,
      "lon": 17.730833333333333
    }
  },
  {
    "name": "Vattjom E14",
    "synonyms": [
      "VATTJOM E14"
    ],
    "lId": "13559",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 62.36222222222222,
      "lon": 17.034444444444446
    }
  },
  {
    "name": "Vattnäs vägskäl",
    "synonyms": [
      "VATTNÄS VSK",
      "VATTNÄS VÄGSKÄL",
      "VATTNÆS VSK",
      "VATTNÆS VÆGSKÆL"
    ],
    "lId": "13090",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 61.04833333333333,
      "lon": 14.608333333333333
    }
  },
  {
    "name": "Vaxholm Söderhamnsplan",
    "synonyms": [
      "VAXHOLM SÖDERHAMNSPLAN",
      "VAXHOLM SØDERHAMNSPLAN"
    ],
    "lId": "00784",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.401666666666664,
      "lon": 18.352777777777778
    }
  },
  {
    "name": "Veberöd",
    "synonyms": [
      "VEBERÖD",
      "VEBERÖD CENTRUM",
      "VEBERØD",
      "VEBERØD CENTRUM"
    ],
    "lId": "00957",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 55.63388888888889,
      "lon": 13.491944444444444
    }
  },
  {
    "name": "Veckholm kyrka",
    "synonyms": [
      "VECKHOLM KYRKA"
    ],
    "lId": "12874",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.521388888888886,
      "lon": 17.322222222222223
    }
  },
  {
    "name": "Veda väg 90",
    "synonyms": [
      "VEDA VÄG 90",
      "VEDA VÆG 90"
    ],
    "lId": "15332",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 62.79083333333333,
      "lon": 17.91361111111111
    }
  },
  {
    "name": "Vedbaek",
    "synonyms": [
      "VEDBAEK"
    ],
    "lId": "00662",
    "prio": 0,
    "pId": "086",
    "pos": {
      "lat": 55.85277777777778,
      "lon": 12.5625
    }
  },
  {
    "name": "Veddarsbo Sala",
    "synonyms": [
      "VEDDARSBO SALA"
    ],
    "lId": "44234",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.88777777777778,
      "lon": 16.36777777777778
    }
  },
  {
    "name": "Veddige",
    "synonyms": [
      "VEDDIGE",
      "VEDDIGE STN"
    ],
    "lId": "00363",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 57.266666666666666,
      "lon": 12.3375
    }
  },
  {
    "name": "Vedevåg torget",
    "synonyms": [
      "VEDEVÅG TORGET"
    ],
    "lId": "50559",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.52722222222222,
      "lon": 15.2825
    }
  },
  {
    "name": "Vedum",
    "synonyms": [
      "VEDUM",
      "VEDUM STN"
    ],
    "lId": "00386",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 58.16916666666666,
      "lon": 12.998333333333333
    }
  },
  {
    "name": "Vegby",
    "synonyms": [
      "VEGBY"
    ],
    "lId": "12454",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 57.67861111111111,
      "lon": 13.374722222222223
    }
  },
  {
    "name": "Veinge",
    "synonyms": [
      "VEINGE",
      "VEINGE STN"
    ],
    "lId": "00157",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 56.55305555555555,
      "lon": 13.075277777777778
    }
  },
  {
    "name": "Vejbystrand",
    "synonyms": [
      "VEJBYSTRAND",
      "VEJBYSTRAND CM"
    ],
    "lId": "00744",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 56.315,
      "lon": 12.769166666666667
    }
  },
  {
    "name": "Velanda vägskäl",
    "synonyms": [
      "VELANDA VÄGSKÄL",
      "VELANDA VÆGSKÆL"
    ],
    "lId": "23109",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 58.231944444444444,
      "lon": 12.302777777777779
    }
  },
  {
    "name": "Vellinge",
    "synonyms": [
      "VELLINGE",
      "VELLINGE CM"
    ],
    "lId": "00958",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 55.471944444444446,
      "lon": 13.020555555555557
    }
  },
  {
    "name": "Vellinge ängar",
    "synonyms": [
      "VELLINGE ÄNGAR",
      "VELLINGE ÆNGAR"
    ],
    "lId": "20262",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 55.47277777777778,
      "lon": 13.009722222222223
    }
  },
  {
    "name": "Vemdalen by",
    "synonyms": [
      "VEMDALEN BY"
    ],
    "lId": "00532",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 62.44944444444444,
      "lon": 13.863333333333333
    }
  },
  {
    "name": "Vemdalen Ekbergs/Systemombud",
    "synonyms": [
      "VEMDALEN EKBERGS/SYSTEMOMBUD"
    ],
    "lId": "64333",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 62.44416666666666,
      "lon": 13.8675
    }
  },
  {
    "name": "Vemdalsskalet Hotell",
    "synonyms": [
      "VEMDALSSKALET HOTELL"
    ],
    "lId": "01370",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 62.48277777777778,
      "lon": 13.973888888888888
    }
  },
  {
    "name": "Vemdalsskalet Stockåvallen",
    "synonyms": [
      "VEMDALSSKALET STOCKÅVALLEN"
    ],
    "lId": "62756",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 62.475,
      "lon": 14.015833333333333
    }
  },
  {
    "name": "Vemhån",
    "synonyms": [
      "VEMHÅN"
    ],
    "lId": "13341",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 62.31305555555555,
      "lon": 14.039722222222222
    }
  },
  {
    "name": "Ven",
    "synonyms": [
      "VEN",
      "VEN BÄCKVIKEN",
      "VEN BÆCKVIKEN"
    ],
    "lId": "01199",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 55.90361111111111,
      "lon": 12.720833333333333
    }
  },
  {
    "name": "Vena station",
    "synonyms": [
      "VENA STATION",
      "VENA STN"
    ],
    "lId": "24960",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 57.52444444444444,
      "lon": 15.96888888888889
    }
  },
  {
    "name": "Vendelsö",
    "synonyms": [
      "VENDELSÖ",
      "VENDELSÖ SÅGEN",
      "VENDELSØ",
      "VENDELSØ SÅGEN"
    ],
    "lId": "01371",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.19888888888889,
      "lon": 18.190277777777776
    }
  },
  {
    "name": "Vendevägen station",
    "synonyms": [
      "VENDEVÄGEN STATION",
      "VENDEVÄGEN STN",
      "VENDEVÆGEN STATION",
      "VENDEVÆGEN STN"
    ],
    "lId": "24796",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.39972222222222,
      "lon": 18.067777777777778
    }
  },
  {
    "name": "Venestad Bygata",
    "synonyms": [
      "VENESTAD BYGATA"
    ],
    "lId": "30887",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 55.986111111111114,
      "lon": 13.934166666666666
    }
  },
  {
    "name": "Venjan",
    "synonyms": [
      "VENJAN"
    ],
    "lId": "20981",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 60.9525,
      "lon": 13.908333333333333
    }
  },
  {
    "name": "Verkebäck station",
    "synonyms": [
      "VERKEBÄCK STATION",
      "VERKEBÄCK STN",
      "VERKEBÆCK STATION",
      "VERKEBÆCK STN"
    ],
    "lId": "24957",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 57.728611111111114,
      "lon": 16.515
    }
  },
  {
    "name": "Verkebäcksbron",
    "synonyms": [
      "VERKEBÄCKSBRON"
    ],
    "lId": "14410",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 57.72638888888889,
      "lon": 16.516944444444444
    }
  },
  {
    "name": "Vessigebro",
    "synonyms": [
      "VESSIGEBRO",
      "VESSIGEBRO STNG"
    ],
    "lId": "01373",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 56.9775,
      "lon": 12.65
    }
  },
  {
    "name": "Vetlanda",
    "synonyms": [
      "VETLANDA",
      "VETLANDA STN"
    ],
    "lId": "00086",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 57.425555555555555,
      "lon": 15.081944444444444
    }
  },
  {
    "name": "Vidarkliniken",
    "synonyms": [
      "VIDARKLINIKEN"
    ],
    "lId": "70055",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.06666666666667,
      "lon": 17.61888888888889
    }
  },
  {
    "name": "Vidsel",
    "synonyms": [
      "VIDSEL",
      "VIDSEL HTL RENK"
    ],
    "lId": "01374",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 65.83138888888888,
      "lon": 20.52027777777778
    }
  },
  {
    "name": "Viebäck",
    "synonyms": [
      "VIEBÄCK",
      "VIEBÆCK"
    ],
    "lId": "25116",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 57.57638888888889,
      "lon": 14.568055555555555
    }
  },
  {
    "name": "Viggbyholm",
    "synonyms": [
      "VIGGBYHOLM",
      "VIGGBYHOLM STN"
    ],
    "lId": "20110",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.44888888888889,
      "lon": 18.103611111111114
    }
  },
  {
    "name": "Vigge",
    "synonyms": [
      "VIGGE",
      "VIGGE BERG"
    ],
    "lId": "13357",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 62.843333333333334,
      "lon": 14.384166666666665
    }
  },
  {
    "name": "Vik slott",
    "synonyms": [
      "VIK SLOTT"
    ],
    "lId": "12670",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.736666666666665,
      "lon": 17.4625
    }
  },
  {
    "name": "Vik Vikarevägen Simrishamn",
    "synonyms": [
      "VIK VIKAREVÄGEN SIMRISHAMN",
      "VIK VIKAREVÆGEN SIMRISHAMN"
    ],
    "lId": "31147",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 55.61388888888889,
      "lon": 14.285833333333333
    }
  },
  {
    "name": "Vika kyrka",
    "synonyms": [
      "VIKA KYRKA",
      "VIKA KYRKA FALU"
    ],
    "lId": "22649",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 60.51305555555555,
      "lon": 15.713888888888889
    }
  },
  {
    "name": "Vikarbyn affären",
    "synonyms": [
      "VIKARBYN AFFÄREN",
      "VIKARBYN AFFÆREN"
    ],
    "lId": "01512",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 60.90972222222222,
      "lon": 15.020555555555557
    }
  },
  {
    "name": "Viken",
    "synonyms": [
      "VIKEN",
      "VIKEN CENTRUM"
    ],
    "lId": "00959",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 56.146388888888886,
      "lon": 12.579166666666666
    }
  },
  {
    "name": "Vikene",
    "synonyms": [
      "VIKENE"
    ],
    "lId": "11781",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.66416666666667,
      "lon": 12.884722222222221
    }
  },
  {
    "name": "Vikhammer",
    "synonyms": [
      "VIKHAMMER"
    ],
    "lId": "01204",
    "prio": 0,
    "pId": "076",
    "pos": {
      "lat": 0,
      "lon": 0
    }
  },
  {
    "name": "Vikingstad",
    "synonyms": [
      "VIKINGSTAD",
      "VIKINGSTAD STN"
    ],
    "lId": "00868",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 58.38305555555556,
      "lon": 15.431944444444444
    }
  },
  {
    "name": "Vikmanshyttan",
    "synonyms": [
      "VIKMANSHYTTAN"
    ],
    "lId": "00659",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 60.29722222222222,
      "lon": 15.825
    }
  },
  {
    "name": "Viksjö centrum/Järfälla",
    "synonyms": [
      "VIKSJÖ CENTRUM/JÄRFÄLLA",
      "VIKSJØ CENTRUM/JÆRFÆLLA"
    ],
    "lId": "20638",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.41277777777778,
      "lon": 17.801666666666666
    }
  },
  {
    "name": "Viksjö affären Ångermanland",
    "synonyms": [
      "VIKSJÖ AFFÄREN ÅNGERMANLAND",
      "VIKSJØ AFFÆREN ÅNGERMANLAND"
    ],
    "lId": "22724",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 62.7725,
      "lon": 17.420833333333334
    }
  },
  {
    "name": "Viksjöfors",
    "synonyms": [
      "VIKSJÖFORS",
      "VIKSJØFORS"
    ],
    "lId": "26082",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 61.338055555555556,
      "lon": 15.95361111111111
    }
  },
  {
    "name": "Vilhelmina station",
    "synonyms": [
      "VILHELMINA STATION",
      "VILHELMINA STN"
    ],
    "lId": "00451",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 64.62277777777777,
      "lon": 16.65138888888889
    }
  },
  {
    "name": "Villingsberg",
    "synonyms": [
      "VILLINGSBERG"
    ],
    "lId": "20963",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.280833333333334,
      "lon": 14.6925
    }
  },
  {
    "name": "Vilshult",
    "synonyms": [
      "VILSHULT"
    ],
    "lId": "01377",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 56.35805555555556,
      "lon": 14.481666666666667
    }
  },
  {
    "name": "Vilshärad camping",
    "synonyms": [
      "VILSHÄRAD CAMPING",
      "VILSHÆRAD CAMPING"
    ],
    "lId": "23536",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 56.693888888888885,
      "lon": 12.698055555555555
    }
  },
  {
    "name": "Vimmerby",
    "synonyms": [
      "VIMMERBY",
      "VIMMERBY STN"
    ],
    "lId": "00351",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 57.66305555555555,
      "lon": 15.858055555555556
    }
  },
  {
    "name": "Vinberg kyrkby",
    "synonyms": [
      "VINBERG KYRKBY"
    ],
    "lId": "17220",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 56.92972222222222,
      "lon": 12.548055555555555
    }
  },
  {
    "name": "Vinberg samhälle",
    "synonyms": [
      "VINBERG SAMHÄLLE",
      "VINBERG SAMHÆLLE"
    ],
    "lId": "17221",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 56.947222222222216,
      "lon": 12.541944444444445
    }
  },
  {
    "name": "Vindelgransele",
    "synonyms": [
      "VINDELGRANSELE"
    ],
    "lId": "01378",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 65.10777777777777,
      "lon": 18.304722222222225
    }
  },
  {
    "name": "Vindeln",
    "synonyms": [
      "VINDELN",
      "VINDELN STN"
    ],
    "lId": "00239",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 64.20277777777778,
      "lon": 19.7125
    }
  },
  {
    "name": "Vingåker",
    "synonyms": [
      "VINGÅKER",
      "VINGÅKER STN"
    ],
    "lId": "00839",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.04194444444444,
      "lon": 15.873888888888889
    }
  },
  {
    "name": "Vinninga väg 184",
    "synonyms": [
      "VINNINGA VÄG 184",
      "VINNINGA VÄG184",
      "VINNINGA VÆG 184",
      "VINNINGA VÆG184"
    ],
    "lId": "11793",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 58.44777777777777,
      "lon": 13.245
    }
  },
  {
    "name": "Vinnö Stationsvägen",
    "synonyms": [
      "VINNÖ STATIONSVÄGEN",
      "VINNØ STATIONSVÆGEN"
    ],
    "lId": "30742",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 56.05222222222222,
      "lon": 14.087222222222223
    }
  },
  {
    "name": "Vinslöv station",
    "synonyms": [
      "VINSLOV",
      "VINSLÖV STATION",
      "VINSLÖV STN",
      "VINSLØV STATION",
      "VINSLØV STN"
    ],
    "lId": "00179",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 56.10472222222222,
      "lon": 13.916666666666666
    }
  },
  {
    "name": "Vintrosa",
    "synonyms": [
      "VINTROSA",
      "VINTROSA TOMTA"
    ],
    "lId": "00798",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.2575,
      "lon": 14.96111111111111
    }
  },
  {
    "name": "Virsbo",
    "synonyms": [
      "VIRSBO",
      "VIRSBO STN"
    ],
    "lId": "00196",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.8725,
      "lon": 16.083888888888886
    }
  },
  {
    "name": "Virsbo Krogen",
    "synonyms": [
      "VIRSBO KROGEN"
    ],
    "lId": "11798",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.86527777777778,
      "lon": 16.04388888888889
    }
  },
  {
    "name": "Virserum",
    "synonyms": [
      "VIRSERUM",
      "VIRSERUM TORGET"
    ],
    "lId": "00933",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 57.31527777777777,
      "lon": 15.584722222222222
    }
  },
  {
    "name": "Visby busstation",
    "synonyms": [
      "VISBY BSTN",
      "VISBY BUSSTATION"
    ],
    "lId": "00913",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 57.63527777777778,
      "lon": 18.29527777777778
    }
  },
  {
    "name": "Visby flygplats",
    "synonyms": [
      "VISBY FLYGPLATS"
    ],
    "lId": "26020",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 57.66,
      "lon": 18.339444444444442
    }
  },
  {
    "name": "Visinge station",
    "synonyms": [
      "VISINGE STATION",
      "VISINGE STN"
    ],
    "lId": "24370",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.46083333333333,
      "lon": 18.0625
    }
  },
  {
    "name": "Visingsö",
    "synonyms": [
      "VISINGSÖ",
      "VISINGSØ"
    ],
    "lId": "01005",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 58.03194444444444,
      "lon": 14.351388888888888
    }
  },
  {
    "name": "Viskafors",
    "synonyms": [
      "VISKAFORS"
    ],
    "lId": "00159",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 57.62833333333333,
      "lon": 12.843611111111112
    }
  },
  {
    "name": "Viskan anstalten",
    "synonyms": [
      "VISKAN ANSTALTEN"
    ],
    "lId": "15345",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 62.44194444444444,
      "lon": 16.42666666666667
    }
  },
  {
    "name": "Viskan kiosken",
    "synonyms": [
      "VISKAN KIOSKEN"
    ],
    "lId": "25867",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 62.44916666666666,
      "lon": 16.433888888888887
    }
  },
  {
    "name": "Vislanda",
    "synonyms": [
      "VISLANDA",
      "VISLANDA STN"
    ],
    "lId": "00145",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 56.786944444444444,
      "lon": 14.453333333333333
    }
  },
  {
    "name": "Vissefjärda",
    "synonyms": [
      "VISSEFJÄRDA",
      "VISSEFJÄRDA STN",
      "VISSEFJÆRDA",
      "VISSEFJÆRDA STN"
    ],
    "lId": "01380",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 56.538333333333334,
      "lon": 15.581388888888888
    }
  },
  {
    "name": "Visseltofta Sjuhultsvägen",
    "synonyms": [
      "VISSELTOFTA SJUHULTSVÄGEN",
      "VISSELTOFTA SJUHULTSVÆGEN"
    ],
    "lId": "04104",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 56.42666666666666,
      "lon": 13.854166666666666
    }
  },
  {
    "name": "Vistinge",
    "synonyms": [
      "VISTINGE"
    ],
    "lId": "01164",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 58.69083333333333,
      "lon": 15.925277777777778
    }
  },
  {
    "name": "Vitaby Hotellplan",
    "synonyms": [
      "VITABY HOTELLPLAN"
    ],
    "lId": "04144",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 55.68472222222222,
      "lon": 14.154166666666667
    }
  },
  {
    "name": "Vitemölla Källebacken",
    "synonyms": [
      "VITEMÖLLA KÄLLEBACKEN",
      "VITEMØLLA KÆLLEBACKEN"
    ],
    "lId": "04159",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 55.69638888888888,
      "lon": 14.202222222222222
    }
  },
  {
    "name": "Vittangi",
    "synonyms": [
      "VITTANGI",
      "VITTANGI BSTN"
    ],
    "lId": "00904",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 67.67555555555556,
      "lon": 21.633055555555558
    }
  },
  {
    "name": "Vittaryd Skolvägen",
    "synonyms": [
      "VITTARYD SKOLVÄGEN",
      "VITTARYD SKOLVÆGEN"
    ],
    "lId": "04055",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 56.970555555555556,
      "lon": 13.944444444444445
    }
  },
  {
    "name": "Vittinge station",
    "synonyms": [
      "VITTINGE STATION",
      "VITTINGE STN"
    ],
    "lId": "11809",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.90333333333333,
      "lon": 17.061666666666667
    }
  },
  {
    "name": "Vittsjö",
    "synonyms": [
      "VITTSJO",
      "VITTSJÖ",
      "VITTSJÖ BSTN",
      "VITTSJØ",
      "VITTSJØ BSTN"
    ],
    "lId": "00432",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 56.341944444444444,
      "lon": 13.663055555555555
    }
  },
  {
    "name": "Vittskövle slott",
    "synonyms": [
      "VITTSKÖVLE SLOTT",
      "VITTSKØVLE SLOTT"
    ],
    "lId": "11812",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 55.85416666666667,
      "lon": 14.135833333333332
    }
  },
  {
    "name": "Vitvattnet",
    "synonyms": [
      "VITVATTNET",
      "VITVATTNET STN"
    ],
    "lId": "00905",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 66.06027777777777,
      "lon": 23.197222222222223
    }
  },
  {
    "name": "Vojmån",
    "synonyms": [
      "VOJMÅN",
      "VOJMÅN STN"
    ],
    "lId": "04461",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 64.79166666666667,
      "lon": 16.815555555555555
    }
  },
  {
    "name": "Volgsele",
    "synonyms": [
      "VOLGSELE",
      "VOLGSELE STN"
    ],
    "lId": "04462",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 64.74416666666667,
      "lon": 16.7125
    }
  },
  {
    "name": "Vollsjö",
    "synonyms": [
      "VOLLSJÖ",
      "VOLLSJÖ PIRATEN",
      "VOLLSJØ",
      "VOLLSJØ PIRATEN"
    ],
    "lId": "01514",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 55.70194444444445,
      "lon": 13.785555555555556
    }
  },
  {
    "name": "Voxnabruk",
    "synonyms": [
      "VOXNABRUK"
    ],
    "lId": "11818",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 61.36416666666667,
      "lon": 15.511666666666667
    }
  },
  {
    "name": "Vrena Skola",
    "synonyms": [
      "VRENA SKOLA"
    ],
    "lId": "50669",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 58.86055555555556,
      "lon": 16.699166666666667
    }
  },
  {
    "name": "Vreta kloster",
    "synonyms": [
      "VRETA KLOSTER"
    ],
    "lId": "00869",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 58.481944444444444,
      "lon": 15.520277777777778
    }
  },
  {
    "name": "Vreta Strandväg södra",
    "synonyms": [
      "VRETA STRANDV S",
      "VRETA STRANDVÄG SÖDRA",
      "VRETA STRANDVÆG SØDRA"
    ],
    "lId": "12825",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.771388888888886,
      "lon": 17.600555555555555
    }
  },
  {
    "name": "Vretstorp",
    "synonyms": [
      "VRETSTORP",
      "VRETSTORP STNG"
    ],
    "lId": "01381",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.022777777777776,
      "lon": 14.868055555555555
    }
  },
  {
    "name": "Vrigstad busstation",
    "synonyms": [
      "VRIGSTAD BUSSTATION"
    ],
    "lId": "00609",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 57.35638888888889,
      "lon": 14.466111111111111
    }
  },
  {
    "name": "Vrångö",
    "synonyms": [
      "VRÅNGÖ",
      "VRÅNGØ"
    ],
    "lId": "01382",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 57.57027777777778,
      "lon": 11.791944444444445
    }
  },
  {
    "name": "Vuollerim",
    "synonyms": [
      "VUOLLERIM",
      "VUOLLERIM UNO-X"
    ],
    "lId": "00416",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 66.43083333333334,
      "lon": 20.60388888888889
    }
  },
  {
    "name": "Vålberg Norsplan",
    "synonyms": [
      "VÅLBERG NORSPLAN"
    ],
    "lId": "00725",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.394999999999996,
      "lon": 13.193888888888889
    }
  },
  {
    "name": "Vålådalen",
    "synonyms": [
      "VÅLÅDALEN",
      "VÅLÅDALEN VÄSTR",
      "VÅLÅDALEN VÆSTR"
    ],
    "lId": "00455",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 63.14861111111111,
      "lon": 12.965
    }
  },
  {
    "name": "Våmhus",
    "synonyms": [
      "VÅMHUS",
      "VÅMHUS CENTRUM"
    ],
    "lId": "13104",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 61.11833333333333,
      "lon": 14.477500000000001
    }
  },
  {
    "name": "Vånga kyrka Skåne",
    "synonyms": [
      "VÅNGA KYRKA SKÅNE"
    ],
    "lId": "01515",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 56.180277777777775,
      "lon": 14.374444444444444
    }
  },
  {
    "name": "Vånga Norrköping",
    "synonyms": [
      "VÅNGA NORRKÖPING",
      "VÅNGA NORRKØPING"
    ],
    "lId": "11830",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 58.57916666666667,
      "lon": 15.811111111111112
    }
  },
  {
    "name": "Vårberg T-bana",
    "synonyms": [
      "VÅRBERG T-BANA"
    ],
    "lId": "21727",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.27583333333333,
      "lon": 17.89
    }
  },
  {
    "name": "Vårby gård T-bana",
    "synonyms": [
      "VÅRBY GÅRD T",
      "VÅRBY GÅRD T-BANA"
    ],
    "lId": "21728",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.26444444444444,
      "lon": 17.884166666666665
    }
  },
  {
    "name": "Vårdinge folkhögskolan",
    "synonyms": [
      "VÅRDINGE FHSK",
      "VÅRDINGE FOLKHÖGSKOLAN",
      "VÅRDINGE FOLKHØGSKOLAN"
    ],
    "lId": "21621",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 58.99,
      "lon": 17.42666666666667
    }
  },
  {
    "name": "Vårdsberg vägkors",
    "synonyms": [
      "VÅRDSBERG VSK",
      "VÅRDSBERG VÄGKORS"
    ],
    "lId": "25967",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 58.39833333333333,
      "lon": 15.7625
    }
  },
  {
    "name": "Vårgårda station",
    "synonyms": [
      "VARGARDA STATION",
      "VÅRGÅRDA STATION",
      "VÅRGÅRDA STN"
    ],
    "lId": "00569",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 58.03111111111111,
      "lon": 12.81027777777778
    }
  },
  {
    "name": "Vårgårda Rasta",
    "synonyms": [
      "VÅRGÅRDA RASTA"
    ],
    "lId": "30075",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 58.05083333333333,
      "lon": 12.815000000000001
    }
  },
  {
    "name": "Vårsta",
    "synonyms": [
      "VÅRSTA",
      "VÅRSTA CENTRUM"
    ],
    "lId": "01383",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.165,
      "lon": 17.797222222222224
    }
  },
  {
    "name": "Våxtorp",
    "synonyms": [
      "VÅXTORP"
    ],
    "lId": "01516",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 56.41638888888889,
      "lon": 13.12138888888889
    }
  },
  {
    "name": "Vä E22",
    "synonyms": [
      "VÄ E22",
      "VÆ E22"
    ],
    "lId": "22946",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 56.00083333333333,
      "lon": 14.100833333333332
    }
  },
  {
    "name": "Vä Talldalsskolan",
    "synonyms": [
      "VÄ TALLDALSSKOLAN",
      "VÆ TALLDALSSKOLAN"
    ],
    "lId": "04118",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 55.99666666666667,
      "lon": 14.085555555555556
    }
  },
  {
    "name": "Väckelsång",
    "synonyms": [
      "VACKELSANG",
      "VÄCKELSÅNG",
      "VÄCKELSÅNG CM",
      "VÆCKELSÅNG",
      "VÆCKELSÅNG CM"
    ],
    "lId": "00152",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 56.63805555555555,
      "lon": 14.920833333333333
    }
  },
  {
    "name": "Väddö kyrka",
    "synonyms": [
      "VÄDDÖ KYRKA",
      "VÆDDØ KYRKA"
    ],
    "lId": "00785",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.98777777777778,
      "lon": 18.810277777777777
    }
  },
  {
    "name": "Väderstad",
    "synonyms": [
      "VÄDERSTAD",
      "VÄDERSTAD KYRKA",
      "VÆDERSTAD",
      "VÆDERSTAD KYRKA"
    ],
    "lId": "01517",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 58.31305555555555,
      "lon": 14.923333333333332
    }
  },
  {
    "name": "Väja kontoret",
    "synonyms": [
      "VÄJA KONTORET",
      "VÆJA KONTORET"
    ],
    "lId": "15337",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 62.976111111111116,
      "lon": 17.708055555555553
    }
  },
  {
    "name": "Väjern",
    "synonyms": [
      "VÄJERN",
      "VÆJERN"
    ],
    "lId": "16220",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 58.379444444444445,
      "lon": 11.263055555555555
    }
  },
  {
    "name": "Välsviken station",
    "synonyms": [
      "VALSVIKEN STATION",
      "VÄLSVIKEN STATION",
      "VÄLSVIKEN STN",
      "VÆLSVIKEN STATION",
      "VÆLSVIKEN STN"
    ],
    "lId": "25002",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.39111111111111,
      "lon": 13.582777777777778
    }
  },
  {
    "name": "Vänersborg C",
    "synonyms": [
      "VANERSBORG C",
      "VÄNERSBORG C",
      "VÆNERSBORG C"
    ],
    "lId": "00241",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 58.3775,
      "lon": 12.317777777777778
    }
  },
  {
    "name": "Vänge kyrka",
    "synonyms": [
      "VÄNGE KYRKA",
      "VÆNGE KYRKA"
    ],
    "lId": "12671",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.856944444444444,
      "lon": 17.433611111111112
    }
  },
  {
    "name": "Vännacka affären",
    "synonyms": [
      "VÄNNACKA AFFÄREN",
      "VÆNNACKA AFFÆREN"
    ],
    "lId": "11839",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.556666666666665,
      "lon": 12.125
    }
  },
  {
    "name": "Vännäs",
    "synonyms": [
      "VANNAS",
      "VÄNNÄS",
      "VÄNNÄS STN",
      "VÆNNÆS",
      "VÆNNÆS STN"
    ],
    "lId": "00181",
    "prio": 1,
    "pId": "074",
    "pos": {
      "lat": 63.90861111111111,
      "lon": 19.749722222222225
    }
  },
  {
    "name": "Vännäsby skola",
    "synonyms": [
      "VÄNNÄSBY SKOLA",
      "VÆNNÆSBY SKOLA"
    ],
    "lId": "01385",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 63.91361111111111,
      "lon": 19.81388888888889
    }
  },
  {
    "name": "Vännäsby station",
    "synonyms": [
      "VÄNNÄSBY STATION",
      "VÄNNÄSBY STN"
    ],
    "lId": "13770",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 63.915,
      "lon": 19.816111111111113
    }
  },
  {
    "name": "Värestorp",
    "synonyms": [
      "VÄRESTORP",
      "VÆRESTORP"
    ],
    "lId": "11840",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 56.19222222222222,
      "lon": 14.213333333333333
    }
  },
  {
    "name": "Väring",
    "synonyms": [
      "VÄRING"
    ],
    "lId": "11841",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 58.510555555555555,
      "lon": 13.970833333333333
    }
  },
  {
    "name": "Värmdö Herrviksnäs",
    "synonyms": [
      "VÄRMDÖ HERRVIKSNÄS"
    ],
    "lId": "66410",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.30027777777777,
      "lon": 18.509166666666665
    }
  },
  {
    "name": "Värmdö kyrka",
    "synonyms": [
      "VÄRMDÖ KYRKA",
      "VÆRMDØ KYRKA"
    ],
    "lId": "00786",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.356944444444444,
      "lon": 18.49638888888889
    }
  },
  {
    "name": "Värmlands Säby",
    "synonyms": [
      "VÄRMLANDS SÄBY"
    ],
    "lId": "58239",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.088055555555556,
      "lon": 14.161944444444444
    }
  },
  {
    "name": "Värmlandsbro centrum",
    "synonyms": [
      "VÄRMLANDSBRO CENTRUM",
      "VÆRMLANDSBRO CENTRUM"
    ],
    "lId": "00830",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.183055555555555,
      "lon": 13.013055555555555
    }
  },
  {
    "name": "Värnamo",
    "synonyms": [
      "VARNAMO",
      "VÄRNAMO",
      "VÄRNAMO STN",
      "VÆRNAMO",
      "VÆRNAMO STN"
    ],
    "lId": "00052",
    "prio": 1,
    "pId": "074",
    "pos": {
      "lat": 57.18611111111111,
      "lon": 14.035555555555556
    }
  },
  {
    "name": "Värnamo ICA Kvantum",
    "synonyms": [
      "VÄRNAMO ICA KVANTUM"
    ],
    "lId": "23247",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 57.169999999999995,
      "lon": 14.061944444444444
    }
  },
  {
    "name": "Värnäs Q8",
    "synonyms": [
      "VÄRNÄS Q8",
      "VÆRNÆS Q8"
    ],
    "lId": "22350",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 60.42194444444444,
      "lon": 13.260555555555555
    }
  },
  {
    "name": "Värsås",
    "synonyms": [
      "VÄRSÅS",
      "VÆRSÅS"
    ],
    "lId": "01183",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 58.35388888888889,
      "lon": 14.049166666666666
    }
  },
  {
    "name": "Värtahamnens färjeterminal",
    "synonyms": [
      "VÄRTAHAMNENS FÄRJETERMINAL"
    ],
    "lId": "71516",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.34916666666667,
      "lon": 18.10638888888889
    }
  },
  {
    "name": "Väröbacka",
    "synonyms": [
      "VÄRÖBACKA",
      "VÆRØBACKA"
    ],
    "lId": "23648",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 57.24944444444444,
      "lon": 12.1825
    }
  },
  {
    "name": "Väsbystrand brygga",
    "synonyms": [
      "VÄSBYSTRAND BRYGGA",
      "VÆSBYSTRAND BRYGGA"
    ],
    "lId": "24870",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.49916666666667,
      "lon": 18.551111111111112
    }
  },
  {
    "name": "Väse",
    "synonyms": [
      "VASE",
      "VÄSE",
      "VÆSE"
    ],
    "lId": "00287",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.38138888888889,
      "lon": 13.853333333333333
    }
  },
  {
    "name": "Väse E18",
    "synonyms": [
      "VÄSE E18",
      "VÆSE E18"
    ],
    "lId": "11849",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.39,
      "lon": 13.853333333333333
    }
  },
  {
    "name": "Väskinde",
    "synonyms": [
      "VÄSKINDE",
      "VÄSKINDE KYRKA",
      "VÆSKINDE",
      "VÆSKINDE KYRKA"
    ],
    "lId": "11850",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 57.69083333333333,
      "lon": 18.42138888888889
    }
  },
  {
    "name": "Västeraspby station",
    "synonyms": [
      "VÄSTERASPBY STATION",
      "VÆSTERASPBY STATION"
    ],
    "lId": "01589",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 63.052499999999995,
      "lon": 17.744722222222222
    }
  },
  {
    "name": "Västerby skolan",
    "synonyms": [
      "VÄSTERBY SKOLAN",
      "VÆSTERBY SKOLAN"
    ],
    "lId": "12928",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 60.30694444444444,
      "lon": 15.935555555555556
    }
  },
  {
    "name": "Västerfärnebo",
    "synonyms": [
      "VÄSTERFÄRNEBO",
      "VÆSTERFÆRNEBO"
    ],
    "lId": "00685",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.94416666666666,
      "lon": 16.279722222222222
    }
  },
  {
    "name": "Västerhaninge",
    "synonyms": [
      "VÄSTERHANINGE",
      "VÆSTERHANINGE"
    ],
    "lId": "00787",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.12277777777778,
      "lon": 18.102500000000003
    }
  },
  {
    "name": "Västerhus",
    "synonyms": [
      "VÄSTERHUS",
      "VÆSTERHUS"
    ],
    "lId": "15341",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 63.32361111111111,
      "lon": 18.551944444444445
    }
  },
  {
    "name": "Västerljung Erikslundsv",
    "synonyms": [
      "VÄSTERLJUNG ERIKSLUNDSV",
      "VÆSTERLJUNG ERIKSLUNDSV"
    ],
    "lId": "21330",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 58.91833333333333,
      "lon": 17.43861111111111
    }
  },
  {
    "name": "Västerlösa Kornettvägen",
    "synonyms": [
      "VÄSTERLÖSA KORNETTVÄGEN",
      "VÆSTERLØSA KORNETTVÆGEN"
    ],
    "lId": "23444",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 58.42055555555555,
      "lon": 15.339722222222223
    }
  },
  {
    "name": "Västermo",
    "synonyms": [
      "VÄSTERMO",
      "VÆSTERMO"
    ],
    "lId": "20894",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.28972222222222,
      "lon": 16.079166666666666
    }
  },
  {
    "name": "Västertorp T-bana",
    "synonyms": [
      "VÄSTERTORP T-BANA",
      "VÆSTERTORP T-BANA"
    ],
    "lId": "21718",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.29111111111111,
      "lon": 17.966666666666665
    }
  },
  {
    "name": "Västervik",
    "synonyms": [
      "VASTERVIK",
      "VÄSTERVIK",
      "VÄSTERVIK STN",
      "VÆSTERVIK",
      "VÆSTERVIK STN"
    ],
    "lId": "00082",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 57.75527777777778,
      "lon": 16.643055555555556
    }
  },
  {
    "name": "Västerås C",
    "synonyms": [
      "VASTERAS C",
      "VST",
      "VÄSTERÅS C",
      "VÆSTERÅS C"
    ],
    "lId": "00099",
    "prio": 250,
    "pId": "074",
    "pos": {
      "lat": 59.6075,
      "lon": 16.551666666666666
    }
  },
  {
    "name": "Västerås Brottberga",
    "synonyms": [
      "VÄSTERÅS BROTTBERGA"
    ],
    "lId": "23968",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.62972222222222,
      "lon": 16.479444444444443
    }
  },
  {
    "name": "Västerås Bäckby centrum",
    "synonyms": [
      "VÄSTERÅS BÄCKBY CENTRUM"
    ],
    "lId": "43391",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.59861111111111,
      "lon": 16.47472222222222
    }
  },
  {
    "name": "Västerås Centrum Stora Gatan",
    "synonyms": [
      "VÄSTERÅS CENTRUM STORA GATAN"
    ],
    "lId": "43357",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.60944444444445,
      "lon": 16.54638888888889
    }
  },
  {
    "name": "Västerås Eriksborg",
    "synonyms": [
      "VÄSTERÅS ERIKSBORG"
    ],
    "lId": "43318",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.619166666666665,
      "lon": 16.464444444444442
    }
  },
  {
    "name": "Västerås Erikslund västra",
    "synonyms": [
      "VÄSTERÅS ERIKSLUND VÄSTRA"
    ],
    "lId": "12568",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.609722222222224,
      "lon": 16.449166666666667
    }
  },
  {
    "name": "Västerås Finnslätten norra",
    "synonyms": [
      "VÄSTERÅS FINNSLÄTTEN NORRA"
    ],
    "lId": "70962",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.64194444444444,
      "lon": 16.58277777777778
    }
  },
  {
    "name": "Västerås flygplats",
    "synonyms": [
      "VASTERAS AIRPORT",
      "VASTERAS FLYGPLATS",
      "VÄSTERÅS FLYGPLATS",
      "VÆSTERÅS FLYGPLATS"
    ],
    "lId": "24556",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.60194444444445,
      "lon": 16.6275
    }
  },
  {
    "name": "Västerås Hacksta",
    "synonyms": [
      "VÄSTERÅS HACKSTA"
    ],
    "lId": "43453",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.586111111111116,
      "lon": 16.47833333333333
    }
  },
  {
    "name": "Västerås Haga Parkgata",
    "synonyms": [
      "VÄSTERÅS HAGA PARKGATA"
    ],
    "lId": "43371",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.620555555555555,
      "lon": 16.572222222222223
    }
  },
  {
    "name": "Västerås Hammarby centrum",
    "synonyms": [
      "HAMMARBY CENTRUM",
      "VÄSTERÅS HAMMARBY CENTRUM"
    ],
    "lId": "43384",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.597500000000004,
      "lon": 16.50722222222222
    }
  },
  {
    "name": "Västerås Hamregatan",
    "synonyms": [
      "VÄSTERÅS HAMREGATAN"
    ],
    "lId": "70967",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.59305555555556,
      "lon": 16.61277777777778
    }
  },
  {
    "name": "Västerås Hälla",
    "synonyms": [
      "VÄSTERÅS HÄLLA"
    ],
    "lId": "43568",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.61027777777778,
      "lon": 16.622222222222224
    }
  },
  {
    "name": "Västerås Klockartorpet",
    "synonyms": [
      "VÄSTERÅS KLOCKARTORPET"
    ],
    "lId": "43576",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.61388888888889,
      "lon": 16.584444444444443
    }
  },
  {
    "name": "Västerås Lögarängen",
    "synonyms": [
      "VÄSTERÅS LÖGARÄNGEN"
    ],
    "lId": "71007",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.59777777777778,
      "lon": 16.528333333333332
    }
  },
  {
    "name": "Västerås Nordanbymotet",
    "synonyms": [
      "VÄSTERÅS NORDANBYMOTET"
    ],
    "lId": "43604",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.63472222222222,
      "lon": 16.560277777777777
    }
  },
  {
    "name": "Västerås Norra Gryta",
    "synonyms": [
      "VÄSTERÅS NORRA GRYTA"
    ],
    "lId": "43454",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.652499999999996,
      "lon": 16.55138888888889
    }
  },
  {
    "name": "Västerås Norra Malmaberg",
    "synonyms": [
      "VÄSTERÅS NORRA MALMABERG"
    ],
    "lId": "43364",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.63111111111111,
      "lon": 16.58222222222222
    }
  },
  {
    "name": "Västerås Pettersberg centrum",
    "synonyms": [
      "VÄSTERÅS PETTERSBERG CENTRUM"
    ],
    "lId": "70964",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.61638888888889,
      "lon": 16.516944444444444
    }
  },
  {
    "name": "Västerås Rocklunda Södra",
    "synonyms": [
      "VÄSTERÅS ROCKLUNDA SÖDRA"
    ],
    "lId": "43464",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.62777777777778,
      "lon": 16.533333333333335
    }
  },
  {
    "name": "Västerås Råby centrum",
    "synonyms": [
      "VÄSTERÅS RÅBY CENTRUM"
    ],
    "lId": "43519",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.60916666666667,
      "lon": 16.49527777777778
    }
  },
  {
    "name": "Västerås Rönnby centrum",
    "synonyms": [
      "VÄSTERÅS RÖNNBY CENTRUM"
    ],
    "lId": "43498",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.64833333333333,
      "lon": 16.50583333333333
    }
  },
  {
    "name": "Västerås Scandic Hotell",
    "synonyms": [
      "VÄSTERÅS SCANDIC HOTELL"
    ],
    "lId": "23846",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.61472222222223,
      "lon": 16.5675
    }
  },
  {
    "name": "Västerås sjukhus",
    "synonyms": [
      "VÄSTERÅS SJUKHUS"
    ],
    "lId": "43412",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.615833333333335,
      "lon": 16.579166666666666
    }
  },
  {
    "name": "Västerås Skallbergstorget",
    "synonyms": [
      "VÄSTERÅS SKALLBERGSTORGET"
    ],
    "lId": "43584",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.625277777777775,
      "lon": 16.548055555555557
    }
  },
  {
    "name": "Västerås Skälby",
    "synonyms": [
      "VÄSTERÅS SKÄLBY"
    ],
    "lId": "70968",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.594722222222224,
      "lon": 16.454166666666666
    }
  },
  {
    "name": "Västerås Tunbytorp",
    "synonyms": [
      "VÄSTERÅS TUNBYTORP"
    ],
    "lId": "43486",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.643055555555556,
      "lon": 16.559166666666666
    }
  },
  {
    "name": "Västerås Vallby Centrum",
    "synonyms": [
      "VÄSTERÅS VALLBY CENTRUM"
    ],
    "lId": "43435",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.62222222222222,
      "lon": 16.502777777777776
    }
  },
  {
    "name": "Västerås Viksäng Centrum",
    "synonyms": [
      "VÄSTERÅS VIKSÄNG CENTRUM"
    ],
    "lId": "43542",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.608333333333334,
      "lon": 16.575833333333332
    }
  },
  {
    "name": "Västland",
    "synonyms": [
      "VÄSTLAND",
      "VÆSTLAND"
    ],
    "lId": "12711",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 60.44944444444444,
      "lon": 17.614444444444445
    }
  },
  {
    "name": "Västra Bodarne",
    "synonyms": [
      "V BODARNE STN",
      "VÄSTRA BODARNE",
      "VÆSTRA BODARNE"
    ],
    "lId": "01387",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 57.88777777777778,
      "lon": 12.474444444444444
    }
  },
  {
    "name": "Västra Husby skolan",
    "synonyms": [
      "V HUSBY SKOLAN",
      "VÄSTRA HUSBY SKOLAN",
      "VÆSTRA HUSBY SKOLAN"
    ],
    "lId": "20308",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 58.4825,
      "lon": 16.171944444444446
    }
  },
  {
    "name": "Västra Ingelstad kyrka",
    "synonyms": [
      "V INGELSTAD KA",
      "VÄSTRA INGELSTAD KYRKA",
      "VÆSTRA INGELSTAD KYRKA"
    ],
    "lId": "16932",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 55.49111111111111,
      "lon": 13.115
    }
  },
  {
    "name": "Västra Ingelstad station",
    "synonyms": [
      "VÄSTRA INGELSTAD STATION"
    ],
    "lId": "01615",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 55.48916666666667,
      "lon": 13.108888888888888
    }
  },
  {
    "name": "Västra Karup Bjärehem",
    "synonyms": [
      "V KARUP BJÄREH",
      "V KARUP BJÆREH",
      "VÄSTRA KARUP BJÄREHEM",
      "VÆSTRA KARUP BJÆREHEM"
    ],
    "lId": "22805",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 56.41361111111111,
      "lon": 12.741666666666665
    }
  },
  {
    "name": "Västra Klagstorps kyrka",
    "synonyms": [
      "V KLAGSTORPS KA",
      "VÄSTRA KLAGSTORPS KYRKA",
      "VÆSTRA KLAGSTORPS KYRKA"
    ],
    "lId": "16139",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 55.52777777777778,
      "lon": 12.995555555555555
    }
  },
  {
    "name": "Västra Skogen T-bana",
    "synonyms": [
      "VÄSTRA SKOGEN T-BANA",
      "VÆSTRA SKOGEN T-BANA"
    ],
    "lId": "21669",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.34722222222222,
      "lon": 18.003888888888888
    }
  },
  {
    "name": "Västra Tommarp",
    "synonyms": [
      "V TOMMARP",
      "VÄSTRA TOMMARP"
    ],
    "lId": "30511",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 55.39805555555556,
      "lon": 13.101944444444444
    }
  },
  {
    "name": "Västra Torup Stationsvägen",
    "synonyms": [
      "V TORUP STNV",
      "VÄSTRA TORUP STATIONSVÄGEN",
      "VÆSTRA TORUP STATIONSVÆGEN"
    ],
    "lId": "11717",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 56.13777777777778,
      "lon": 13.502777777777778
    }
  },
  {
    "name": "Västra Ämtervik",
    "synonyms": [
      "VASTRA AMTERVIK",
      "VÄSTRA ÄMTERVIK",
      "VÆSTRA ÆMTERVIK"
    ],
    "lId": "00504",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.7275,
      "lon": 13.146944444444443
    }
  },
  {
    "name": "Vätö",
    "synonyms": [
      "VÄTÖ",
      "VÄTÖ NORRV BRYG",
      "VÆTØ",
      "VÆTØ NORRV BRYG"
    ],
    "lId": "01389",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.81305555555555,
      "lon": 18.984166666666667
    }
  },
  {
    "name": "Växjö Arenastaden södra",
    "synonyms": [
      "VÄXJÖ ARENASTADEN SÖDRA"
    ],
    "lId": "45052",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 56.87888888888889,
      "lon": 14.776944444444446
    }
  },
  {
    "name": "Växjö Linneuniversitetet",
    "synonyms": [
      "VÄXJÖ LINNEUNIVERSITETET"
    ],
    "lId": "23572",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 56.855000000000004,
      "lon": 14.831666666666667
    }
  },
  {
    "name": "Växjö Samarkand norra",
    "synonyms": [
      "VÄXJÖ SAMARKAND NORRA"
    ],
    "lId": "24656",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 56.885555555555555,
      "lon": 14.763333333333334
    }
  },
  {
    "name": "Växjö Småland Airport",
    "synonyms": [
      "VÄXJÖ SMÅLAND AIRPORT",
      "VÆXJØ SMÅLAND AIRPORT"
    ],
    "lId": "26041",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 56.925,
      "lon": 14.731666666666667
    }
  },
  {
    "name": "Växjö station",
    "synonyms": [
      "VAXJO STATION",
      "VAXJO STN",
      "VAXJØ STATION",
      "VAXJØ STN",
      "VÄXJÖ STATION",
      "VÄXJÖ STN",
      "VÆXJØ STATION",
      "VÆXJØ STN"
    ],
    "lId": "00250",
    "prio": 1,
    "pId": "074",
    "pos": {
      "lat": 56.876666666666665,
      "lon": 14.80638888888889
    }
  },
  {
    "name": "Växjö Vida Arena",
    "synonyms": [
      "VÄXJÖ VIDA ARENA"
    ],
    "lId": "68811",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 56.88055555555555,
      "lon": 14.777222222222223
    }
  },
  {
    "name": "Vällingby T-bana",
    "synonyms": [
      "VÄLLINGBY T-BANA",
      "VÄLLINGBY TBANA",
      "VÆLLINGBY T-BANA",
      "VÆLLINGBY TBANA"
    ],
    "lId": "21683",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.363055555555555,
      "lon": 17.871944444444445
    }
  },
  {
    "name": "Yngsjö Byvägen",
    "synonyms": [
      "YNGSJÖ BYVÄGEN",
      "YNGSJØ BYVÆGEN"
    ],
    "lId": "23943",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 55.88611111111111,
      "lon": 14.234166666666665
    }
  },
  {
    "name": "Ysane kyrka",
    "synonyms": [
      "YSANE KYRKA"
    ],
    "lId": "11865",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 56.08972222222222,
      "lon": 14.65
    }
  },
  {
    "name": "Ysby",
    "synonyms": [
      "YSBY"
    ],
    "lId": "17230",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 56.49277777777778,
      "lon": 13.118055555555555
    }
  },
  {
    "name": "Ystad",
    "synonyms": [
      "YSTAD",
      "YSTAD STN"
    ],
    "lId": "00028",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 55.42722222222222,
      "lon": 13.824444444444444
    }
  },
  {
    "name": "Ystad Djurpark",
    "synonyms": [
      "YSTAD DJURPARK"
    ],
    "lId": "72603",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 55.48527777777778,
      "lon": 13.718055555555555
    }
  },
  {
    "name": "Ytterberg",
    "synonyms": [
      "YTTERBERG"
    ],
    "lId": "17666",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 62.07055555555556,
      "lon": 14.481944444444444
    }
  },
  {
    "name": "Ytterby",
    "synonyms": [
      "YTTERBY",
      "YTTERBY STN"
    ],
    "lId": "00585",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 57.86222222222222,
      "lon": 11.917222222222222
    }
  },
  {
    "name": "Ytterhogdal",
    "synonyms": [
      "YTTERHOGDAL"
    ],
    "lId": "13308",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 62.174166666666665,
      "lon": 14.938055555555556
    }
  },
  {
    "name": "Ytterhogdal station",
    "synonyms": [
      "YTTERHOGDAL STATION",
      "YTTERHOGDAL STN"
    ],
    "lId": "00503",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 62.197222222222216,
      "lon": 14.855
    }
  },
  {
    "name": "Yttermalung E16",
    "synonyms": [
      "YTTERMALUNG E16"
    ],
    "lId": "20476",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 60.5775,
      "lon": 13.826666666666666
    }
  },
  {
    "name": "Ytterån",
    "synonyms": [
      "YTTERÅN"
    ],
    "lId": "00147",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 63.31722222222223,
      "lon": 14.17
    }
  },
  {
    "name": "Yxlan",
    "synonyms": [
      "YXLAN",
      "YXLAN VAGNSUNDA"
    ],
    "lId": "01390",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.58305555555556,
      "lon": 18.795555555555556
    }
  },
  {
    "name": "Yxskaftkälen",
    "synonyms": [
      "YXSKAFTKÄLEN",
      "YXSKAFTKÆLEN"
    ],
    "lId": "20619",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 63.78,
      "lon": 15.224444444444444
    }
  },
  {
    "name": "Zenitvägen",
    "synonyms": [
      "ZENITVÄGEN"
    ],
    "lId": "66935",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.385,
      "lon": 17.826666666666668
    }
  },
  {
    "name": "Zinkensdamm T-bana",
    "synonyms": [
      "ZINKENSDAMM T-BANA"
    ],
    "lId": "21657",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.31777777777778,
      "lon": 18.05
    }
  },
  {
    "name": "Zinkgruvan",
    "synonyms": [
      "ZINKGRUVAN",
      "ZINKGRUVAN KIOS"
    ],
    "lId": "01391",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 58.81527777777777,
      "lon": 15.105833333333333
    }
  },
  {
    "name": "Åby Bandyvägen Småland",
    "synonyms": [
      "ABY BANDYVÆGEN SMÅLAND",
      "ÅBY BANDYVÄGEN SMÅLAND"
    ],
    "lId": "11870",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 57.021388888888886,
      "lon": 14.777777777777779
    }
  },
  {
    "name": "Åby centrum Östergötland",
    "synonyms": [
      "ABY CENTRUM ØSTERGØTLAND",
      "ÅBY CENTRUM ÖSTERGÖTLAND"
    ],
    "lId": "00870",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 58.664722222222224,
      "lon": 16.18111111111111
    }
  },
  {
    "name": "Åbytorp skolan",
    "synonyms": [
      "ÅBYTORP SKOLAN"
    ],
    "lId": "11872",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.12416666666667,
      "lon": 15.0825
    }
  },
  {
    "name": "Åhus Glashyttan",
    "synonyms": [
      "ÅHUS GLASHYTTAN"
    ],
    "lId": "25956",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 55.92916666666667,
      "lon": 14.292222222222222
    }
  },
  {
    "name": "Åkarp",
    "synonyms": [
      "AKARP",
      "ÅKARP",
      "ÅKARP STN"
    ],
    "lId": "00960",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 55.657222222222224,
      "lon": 13.108055555555556
    }
  },
  {
    "name": "Åkermyntan",
    "synonyms": [
      "ÅKERMYNTAN"
    ],
    "lId": "66576",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.37916666666667,
      "lon": 17.816666666666666
    }
  },
  {
    "name": "Åkers Runö station",
    "synonyms": [
      "AKERS RUNØ STATION",
      "AKERS RUNØ STN",
      "ÅKERS RUNÖ STATION",
      "ÅKERS RUNÖ STN"
    ],
    "lId": "23174",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.48083333333334,
      "lon": 18.26833333333333
    }
  },
  {
    "name": "Åkers Styckebruk Folkets Hus",
    "synonyms": [
      "ÅKERS STYCKEBRUK FOLKETS HUS"
    ],
    "lId": "38421",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.25333333333333,
      "lon": 17.096944444444443
    }
  },
  {
    "name": "Åkersberga",
    "synonyms": [
      "AKERSBERGA",
      "ÅKERSBERGA",
      "ÅKERSBERGA STN"
    ],
    "lId": "00788",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.47916666666667,
      "lon": 18.298333333333336
    }
  },
  {
    "name": "Åkersberga Tunagård",
    "synonyms": [
      "ÅKERSBERGA TUNAGÅRD"
    ],
    "lId": "24804",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.469166666666666,
      "lon": 18.307222222222222
    }
  },
  {
    "name": "Åkersjön",
    "synonyms": [
      "AKERSJØN",
      "ÅKERSJÖN"
    ],
    "lId": "00486",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 63.765,
      "lon": 14.080277777777777
    }
  },
  {
    "name": "Åkeshov T-bana",
    "synonyms": [
      "ÅKESHOV T-BANA"
    ],
    "lId": "21688",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.341944444444444,
      "lon": 17.924722222222222
    }
  },
  {
    "name": "Åkesta",
    "synonyms": [
      "ÅKESTA"
    ],
    "lId": "43803",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.66888888888889,
      "lon": 16.476666666666667
    }
  },
  {
    "name": "Ålandsdal",
    "synonyms": [
      "ÅLANDSDAL"
    ],
    "lId": "24541",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.87444444444444,
      "lon": 17.29277777777778
    }
  },
  {
    "name": "Ålberga",
    "synonyms": [
      "ÅLBERGA"
    ],
    "lId": "20233",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 58.724722222222226,
      "lon": 16.574444444444445
    }
  },
  {
    "name": "Åled vägkors",
    "synonyms": [
      "ALED VÆGKORS",
      "ÅLED VÄGKORS"
    ],
    "lId": "00976",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 56.74333333333333,
      "lon": 12.950555555555555
    }
  },
  {
    "name": "Ålem E22",
    "synonyms": [
      "ÅLEM E22"
    ],
    "lId": "31269",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 56.95777777777778,
      "lon": 16.390277777777776
    }
  },
  {
    "name": "Ålem station",
    "synonyms": [
      "ALEM STATION",
      "ÅLEM STATION",
      "ÅLEM STN"
    ],
    "lId": "00762",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 56.94694444444444,
      "lon": 16.384444444444444
    }
  },
  {
    "name": "Ålsten",
    "synonyms": [
      "ÅLSTEN",
      "ÅLSTENS GÅRD"
    ],
    "lId": "01167",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.32055555555556,
      "lon": 17.951944444444443
    }
  },
  {
    "name": "Ålstensgatan",
    "synonyms": [
      "ÅLSTENSGATAN"
    ],
    "lId": "24817",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.32333333333334,
      "lon": 17.95638888888889
    }
  },
  {
    "name": "Ålö brygga",
    "synonyms": [
      "ALØ BRYGGA",
      "ÅLÖ BRYGGA"
    ],
    "lId": "24877",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 58.919999999999995,
      "lon": 18.191666666666666
    }
  },
  {
    "name": "Åmmeberg",
    "synonyms": [
      "ÅMMEBERG",
      "ÅMMEBERG KIOSK"
    ],
    "lId": "01392",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 58.86527777777778,
      "lon": 14.999166666666666
    }
  },
  {
    "name": "Åmot affär",
    "synonyms": [
      "AMOT AFFÆR",
      "ÅMOT AFFÄR",
      "ÅMOT KONSUM"
    ],
    "lId": "11882",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 60.961666666666666,
      "lon": 16.4475
    }
  },
  {
    "name": "Åmotfors",
    "synonyms": [
      "AMOTFORS",
      "ÅMOTFORS"
    ],
    "lId": "00307",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.76888888888889,
      "lon": 12.366111111111111
    }
  },
  {
    "name": "Åmsele",
    "synonyms": [
      "ÅMSELE"
    ],
    "lId": "22970",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 64.52638888888889,
      "lon": 19.34722222222222
    }
  },
  {
    "name": "Åmynnet",
    "synonyms": [
      "ÅMYNNET"
    ],
    "lId": "26925",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 63.184999999999995,
      "lon": 18.530277777777776
    }
  },
  {
    "name": "Åmål",
    "synonyms": [
      "AMAL",
      "ÅMÅL",
      "ÅMÅL STN"
    ],
    "lId": "00076",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.046388888888885,
      "lon": 12.698055555555555
    }
  },
  {
    "name": "Ånga",
    "synonyms": [
      "ÅNGA"
    ],
    "lId": "20912",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 58.740833333333335,
      "lon": 17.19
    }
  },
  {
    "name": "Ånge",
    "synonyms": [
      "ANGE",
      "ÅNGE",
      "ÅNGE STN"
    ],
    "lId": "00105",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 62.52305555555555,
      "lon": 15.658333333333333
    }
  },
  {
    "name": "Ånn",
    "synonyms": [
      "ANN",
      "ÅNN",
      "ÅNN STN"
    ],
    "lId": "00037",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 63.321111111111115,
      "lon": 12.53888888888889
    }
  },
  {
    "name": "Ånäset busstation",
    "synonyms": [
      "ANÆSET BUSSTATION",
      "ÅNÄSET BUSSTATION"
    ],
    "lId": "00541",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 64.27722222222222,
      "lon": 21.043055555555558
    }
  },
  {
    "name": "Åre",
    "synonyms": [
      "ARE",
      "ÅRE",
      "ÅRE STN"
    ],
    "lId": "00115",
    "prio": 1,
    "pId": "074",
    "pos": {
      "lat": 63.39861111111111,
      "lon": 13.075833333333334
    }
  },
  {
    "name": "Århult",
    "synonyms": [
      "ÅRHULT"
    ],
    "lId": "52824",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 57.26138888888889,
      "lon": 16.3175
    }
  },
  {
    "name": "Årjäng busstation",
    "synonyms": [
      "ARJÆNG BSTN",
      "ARJÆNG BUSSTATION",
      "ÅRJÄNG BSTN",
      "ÅRJÄNG BUSSTATION"
    ],
    "lId": "00364",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.394444444444446,
      "lon": 12.131111111111112
    }
  },
  {
    "name": "Årnes",
    "synonyms": [
      "ARNES",
      "ÅRNES"
    ],
    "lId": "00311",
    "prio": 0,
    "pId": "076",
    "pos": {
      "lat": 60.14111111111111,
      "lon": 11.481666666666667
    }
  },
  {
    "name": "Årsta brygga",
    "synonyms": [
      "ÅRSTA BRYGGA"
    ],
    "lId": "01394",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.081944444444446,
      "lon": 18.173333333333336
    }
  },
  {
    "name": "Årsta Linde",
    "synonyms": [
      "ÅRSTA LINDE"
    ],
    "lId": "24918",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.293055555555554,
      "lon": 18.06361111111111
    }
  },
  {
    "name": "Årsta Valla Torg",
    "synonyms": [
      "ÅRSTA VALLA TORG"
    ],
    "lId": "24684",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.294999999999995,
      "lon": 18.048333333333336
    }
  },
  {
    "name": "Årstaberg station",
    "synonyms": [
      "ÅRSTABERG STATION",
      "ÅRSTABERG STN"
    ],
    "lId": "24920",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.299166666666665,
      "lon": 18.029999999999998
    }
  },
  {
    "name": "Årstad",
    "synonyms": [
      "ÅRSTAD"
    ],
    "lId": "17235",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 56.919444444444444,
      "lon": 12.672222222222222
    }
  },
  {
    "name": "Årstadal",
    "synonyms": [
      "ÅRSTADAL"
    ],
    "lId": "24921",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.30638888888888,
      "lon": 18.025555555555556
    }
  },
  {
    "name": "Årstafältet",
    "synonyms": [
      "ARSTAFÆLTET",
      "ÅRSTAFÄLTET"
    ],
    "lId": "24919",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.29611111111111,
      "lon": 18.039444444444445
    }
  },
  {
    "name": "Årsunda",
    "synonyms": [
      "ARSUNDA SØRBY",
      "ÅRSUNDA",
      "ÅRSUNDA SÖRBY"
    ],
    "lId": "00640",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 60.511944444444445,
      "lon": 16.73222222222222
    }
  },
  {
    "name": "Åryd Billavägen Växjö",
    "synonyms": [
      "ÅRYD BILLAVÄGEN VÄXJÖ",
      "ÅRYD BILLAVÆGEN VÆXJØ"
    ],
    "lId": "11893",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 56.82666666666667,
      "lon": 14.980277777777777
    }
  },
  {
    "name": "Åryd kyrka Karlshamn",
    "synonyms": [
      "ÅRYD KYRKA KARLSHAMN"
    ],
    "lId": "11894",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 56.206944444444446,
      "lon": 15.009166666666667
    }
  },
  {
    "name": "Ås Hov",
    "synonyms": [
      "ÅS HOV"
    ],
    "lId": "13387",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 63.24777777777778,
      "lon": 14.567222222222222
    }
  },
  {
    "name": "Ås skolan Nora kommun",
    "synonyms": [
      "ÅS SKOLAN NORA KOMMUN"
    ],
    "lId": "11896",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.528888888888886,
      "lon": 14.981388888888889
    }
  },
  {
    "name": "Ås station",
    "synonyms": [
      "ÅS STATION",
      "ÅS STN"
    ],
    "lId": "01425",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.85722222222223,
      "lon": 12.342500000000001
    }
  },
  {
    "name": "Åsa",
    "synonyms": [
      "ÅSA",
      "ÅSA CENTRUM"
    ],
    "lId": "00769",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 57.35166666666667,
      "lon": 12.121111111111112
    }
  },
  {
    "name": "Åsa station",
    "synonyms": [
      "ASA STATION",
      "ASA STN",
      "ÅSA STATION",
      "ÅSA STN"
    ],
    "lId": "01604",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 57.363055555555555,
      "lon": 12.135555555555555
    }
  },
  {
    "name": "Åsarna busstation",
    "synonyms": [
      "ÅSARNA BUSSTATION"
    ],
    "lId": "18290",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 62.643055555555556,
      "lon": 14.370833333333334
    }
  },
  {
    "name": "Åsarp norra kyrka",
    "synonyms": [
      "ÅSARP N KYRKA",
      "ÅSARP NORRA KYRKA"
    ],
    "lId": "12533",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 58.02166666666667,
      "lon": 13.570555555555556
    }
  },
  {
    "name": "Åsbro",
    "synonyms": [
      "ASBRO",
      "ASBRO BJØRKALLÉ",
      "ÅSBRO",
      "ÅSBRO BJÖRKALLÉ",
      "ÅSBRO BJÖRKALLÉ"
    ],
    "lId": "00799",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 58.981944444444444,
      "lon": 15.049444444444445
    }
  },
  {
    "name": "Åseda",
    "synonyms": [
      "ASEDA",
      "ÅSEDA",
      "ÅSEDA STN"
    ],
    "lId": "00362",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 57.16777777777777,
      "lon": 15.346944444444444
    }
  },
  {
    "name": "Åsele",
    "synonyms": [
      "ÅSELE",
      "ÅSELE BSTN"
    ],
    "lId": "00395",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 64.1613888888889,
      "lon": 17.35027777777778
    }
  },
  {
    "name": "Åsen kapellet",
    "synonyms": [
      "ÅSEN KAPELLET"
    ],
    "lId": "01519",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 61.27388888888889,
      "lon": 13.8225
    }
  },
  {
    "name": "Åsensbruk affären",
    "synonyms": [
      "ÅSENSBRUK AFFÄREN"
    ],
    "lId": "42611",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 58.80638888888888,
      "lon": 12.421666666666667
    }
  },
  {
    "name": "Åshammar centrum",
    "synonyms": [
      "ÅSHAMMAR CENTRUM",
      "ÅSHAMMAR CM"
    ],
    "lId": "11903",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 60.64055555555556,
      "lon": 16.555555555555557
    }
  },
  {
    "name": "Åsljunga Landshövdingevägen",
    "synonyms": [
      "ÅSLJUNGA LANDSH",
      "ÅSLJUNGA LANDSHÖVDINGEVÄGEN"
    ],
    "lId": "11905",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 56.30777777777777,
      "lon": 13.365833333333333
    }
  },
  {
    "name": "Åstol",
    "synonyms": [
      "ÅSTOL"
    ],
    "lId": "01395",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 57.92388888888889,
      "lon": 11.58888888888889
    }
  },
  {
    "name": "Åstorp",
    "synonyms": [
      "ASTORP",
      "ÅSTORP",
      "ÅSTORP STN"
    ],
    "lId": "00155",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 56.13388888888889,
      "lon": 12.949166666666667
    }
  },
  {
    "name": "Åsättra brygga",
    "synonyms": [
      "ASÆTTRA BRYGGA",
      "ÅSÄTTRA BRYGGA"
    ],
    "lId": "20573",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.50527777777778,
      "lon": 18.63722222222222
    }
  },
  {
    "name": "Åtorp centrum",
    "synonyms": [
      "ÅTORP CENTRUM"
    ],
    "lId": "11908",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.115833333333335,
      "lon": 14.365555555555556
    }
  },
  {
    "name": "Åtvidaberg station",
    "synonyms": [
      "ÅTVIDABERG STATION",
      "ÅTVIDABERG STN"
    ],
    "lId": "00338",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 58.203611111111115,
      "lon": 16.002222222222223
    }
  },
  {
    "name": "Åvestbo Fagersta",
    "synonyms": [
      "ÅVESTBO FAGERSTA"
    ],
    "lId": "10319",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.95777777777778,
      "lon": 15.838611111111112
    }
  },
  {
    "name": "Öggestorp kyrka",
    "synonyms": [
      "ÖGGESTORP KYRKA",
      "ØGGESTORP KYRKA"
    ],
    "lId": "25514",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 57.724444444444444,
      "lon": 14.385555555555555
    }
  },
  {
    "name": "Älandsbro E4",
    "synonyms": [
      "ÄLANDSBRO E4",
      "ÆLANDSBRO E4"
    ],
    "lId": "20164",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 62.67611111111111,
      "lon": 17.842499999999998
    }
  },
  {
    "name": "Älgarås",
    "synonyms": [
      "ÄLGARÅS",
      "ÆLGARÅS"
    ],
    "lId": "01522",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 58.81055555555555,
      "lon": 14.254722222222222
    }
  },
  {
    "name": "Älghult Stationsgatan",
    "synonyms": [
      "ÄLGHULT STATIONSGATAN",
      "ÄLGHULT STNGATA",
      "ÆLGHULT STATIONSGATAN",
      "ÆLGHULT STNGATA"
    ],
    "lId": "24758",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 57.0075,
      "lon": 15.570555555555556
    }
  },
  {
    "name": "Älgö",
    "synonyms": [
      "ÄLGÖ",
      "ÆLGØ"
    ],
    "lId": "18039",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.26555555555556,
      "lon": 18.352777777777778
    }
  },
  {
    "name": "Älmeboda",
    "synonyms": [
      "ÄLMEBODA",
      "ÆLMEBODA"
    ],
    "lId": "01523",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 56.59166666666667,
      "lon": 15.247499999999999
    }
  },
  {
    "name": "Älmhult",
    "synonyms": [
      "ALMHULT",
      "ÄLMHULT",
      "ÄLMHULT STN",
      "ÆLMHULT",
      "ÆLMHULT STN"
    ],
    "lId": "00045",
    "prio": 1,
    "pId": "074",
    "pos": {
      "lat": 56.55138888888889,
      "lon": 14.136944444444444
    }
  },
  {
    "name": "Älmsta",
    "synonyms": [
      "ÄLMSTA",
      "ÄLMSTA BSTN",
      "ÆLMSTA",
      "ÆLMSTA BSTN"
    ],
    "lId": "01396",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.97,
      "lon": 18.806944444444444
    }
  },
  {
    "name": "Ölmstad",
    "synonyms": [
      "ÖLMSTAD",
      "ØLMSTAD"
    ],
    "lId": "11956",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 57.92666666666666,
      "lon": 14.396944444444443
    }
  },
  {
    "name": "Älskogsbräcka",
    "synonyms": [
      "ÄLSKOGSBRÄCKA",
      "ÆLSKOGSBRÆCKA"
    ],
    "lId": "01524",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 57.416666666666664,
      "lon": 11.953333333333333
    }
  },
  {
    "name": "Älta centrum",
    "synonyms": [
      "ÄLTA CENTRUM",
      "ÆLTA CENTRUM"
    ],
    "lId": "24821",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.256388888888885,
      "lon": 18.17527777777778
    }
  },
  {
    "name": "Älvdalen",
    "synonyms": [
      "ÄLVDALEN",
      "ÄLVDALEN BSTN",
      "ÆLVDALEN",
      "ÆLVDALEN BSTN"
    ],
    "lId": "00575",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 61.223055555555554,
      "lon": 14.044444444444444
    }
  },
  {
    "name": "Älvho",
    "synonyms": [
      "ÄLVHO",
      "ÄLVHO STN",
      "ÆLVHO",
      "ÆLVHO STN"
    ],
    "lId": "04402",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 61.49805555555556,
      "lon": 14.748055555555554
    }
  },
  {
    "name": "Älvkarleby station",
    "synonyms": [
      "ÄLVKARLEBY STATION",
      "ÄLVKARLEBY STN",
      "ÆLVKARLEBY STATION",
      "ÆLVKARLEBY STN"
    ],
    "lId": "01578",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 60.555,
      "lon": 17.42777777777778
    }
  },
  {
    "name": "Älvros affären",
    "synonyms": [
      "ÄLVROS AFFÄREN",
      "ÆLVROS AFFÆREN"
    ],
    "lId": "13574",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 62.0475,
      "lon": 14.650833333333333
    }
  },
  {
    "name": "Älvsbyn",
    "synonyms": [
      "ALVSBYN",
      "ÄLVSBYN",
      "ÄLVSBYN STN",
      "ÆLVSBYN",
      "ÆLVSBYN STN"
    ],
    "lId": "00156",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 65.67805555555556,
      "lon": 20.994444444444447
    }
  },
  {
    "name": "Älvsered",
    "synonyms": [
      "ÄLVSERED",
      "ÆLVSERED"
    ],
    "lId": "00499",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 57.24111111111111,
      "lon": 12.865555555555556
    }
  },
  {
    "name": "Älvsjö",
    "synonyms": [
      "ALVSJO",
      "STOCKHOLM INTERNATIONAL FAIRS",
      "STOCKHOLMSMÄSSAN",
      "STOCKHOLMSMÆSSAN",
      "ÄLVSJÖ",
      "ÄLVSJÖ STN",
      "ÆLVSJØ",
      "ÆLVSJØ STN"
    ],
    "lId": "00789",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.27861111111111,
      "lon": 18.010833333333334
    }
  },
  {
    "name": "Älvängen station",
    "synonyms": [
      "ÄLVÄNGEN STATION",
      "ÄLVÄNGEN STN",
      "ÆLVÆNGEN STATION",
      "ÆLVÆNGEN STN"
    ],
    "lId": "01564",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 57.95777777777778,
      "lon": 12.116388888888888
    }
  },
  {
    "name": "Ändebol",
    "synonyms": [
      "ÄNDEBOL",
      "ÆNDEBOL"
    ],
    "lId": "20922",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 58.856944444444444,
      "lon": 16.192777777777778
    }
  },
  {
    "name": "Ängbyplan T-bana",
    "synonyms": [
      "ÄNGBYPLAN T-BANA",
      "ÆNGBYPLAN T-BANA"
    ],
    "lId": "21687",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.34166666666667,
      "lon": 17.90694444444444
    }
  },
  {
    "name": "Änge",
    "synonyms": [
      "ÄNGE",
      "ÄNGE KROKOM",
      "ÆNGE",
      "ÆNGE KROKOM"
    ],
    "lId": "13414",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 63.45666666666667,
      "lon": 14.065277777777778
    }
  },
  {
    "name": "Ängelholm",
    "synonyms": [
      "ANGELHOLM",
      "ÄNGELHOLM",
      "ÄNGELHOLM STN",
      "ÆNGELHOLM",
      "ÆNGELHOLM STN"
    ],
    "lId": "00064",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 56.245,
      "lon": 12.854166666666666
    }
  },
  {
    "name": "Ängelholm E6 Shell McDonalds",
    "synonyms": [
      "ÄNGELHOLM E6 SHELL MCDONALDS",
      "ÆNGELHOLM E6 SHELL MCDONALDS"
    ],
    "lId": "59033",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 56.25055555555556,
      "lon": 12.893611111111111
    }
  },
  {
    "name": "Ängelsberg",
    "synonyms": [
      "ANGELSBERG",
      "ÄNGELSBERG",
      "ÄNGELSBERG STN",
      "ÆNGELSBERG",
      "ÆNGELSBERG STN"
    ],
    "lId": "00135",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.956944444444446,
      "lon": 16.00888888888889
    }
  },
  {
    "name": "Ängsbyn vändplats",
    "synonyms": [
      "ÄNGSBYN VÄNDPLATS"
    ],
    "lId": "24996",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 55.8875,
      "lon": 13.527222222222223
    }
  },
  {
    "name": "Ängsvik",
    "synonyms": [
      "ÄNGSVIK",
      "ÆNGSVIK"
    ],
    "lId": "25722",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.36222222222222,
      "lon": 18.516944444444444
    }
  },
  {
    "name": "Ängsö",
    "synonyms": [
      "ÄNGSÖ",
      "ÆNGSØ"
    ],
    "lId": "11920",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.53333333333333,
      "lon": 16.859722222222224
    }
  },
  {
    "name": "Äppelbo E16",
    "synonyms": [
      "ÄPPELBO E16"
    ],
    "lId": "00446",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 60.490833333333335,
      "lon": 14.001111111111111
    }
  },
  {
    "name": "Ärentuna kyrka",
    "synonyms": [
      "ÄRENTUNA KYRKA",
      "ÆRENTUNA KYRKA"
    ],
    "lId": "12799",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.95472222222222,
      "lon": 17.60527777777778
    }
  },
  {
    "name": "Ärla kyrka",
    "synonyms": [
      "ÄRLA KYRKA",
      "ÆRLA KYRKA"
    ],
    "lId": "20378",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.25833333333333,
      "lon": 16.586666666666666
    }
  },
  {
    "name": "Ärligbo",
    "synonyms": [
      "ÄRLIGBO",
      "ÆRLIGBO"
    ],
    "lId": "10158",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 60.17638888888889,
      "lon": 17.03611111111111
    }
  },
  {
    "name": "Äs",
    "synonyms": [
      "ÄS",
      "ÄS VÄGSKÄL",
      "ÆS",
      "ÆS VÆGSKÆL"
    ],
    "lId": "11923",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.151666666666664,
      "lon": 16.10777777777778
    }
  },
  {
    "name": "Äskekärr",
    "synonyms": [
      "ÄSKEKÄRR",
      "ÄSKEKÄRR STN",
      "ÆSKEKÆRR",
      "ÆSKEKÆRR STN"
    ],
    "lId": "01398",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 58.626111111111115,
      "lon": 13.608611111111111
    }
  },
  {
    "name": "Äsköping",
    "synonyms": [
      "ÄSKÖPING",
      "ÆSKØPING"
    ],
    "lId": "11924",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.14805555555556,
      "lon": 16.065555555555555
    }
  },
  {
    "name": "Äsperöd torget",
    "synonyms": [
      "ÄSPERÖD TORGET",
      "ÆSPERØD TORGET"
    ],
    "lId": "14065",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 55.61055555555556,
      "lon": 13.917499999999999
    }
  },
  {
    "name": "Äsphult",
    "synonyms": [
      "ÄSPHULT"
    ],
    "lId": "11926",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 55.978611111111114,
      "lon": 13.799444444444445
    }
  },
  {
    "name": "Äspskär vändplan Gräsö",
    "synonyms": [
      "GRÄSÖ ÄSPSKÄR VÄNDPLAN",
      "GRÆSØ ÆSPSKÆR VÆNDPLAN",
      "ÄSPSKÄR VÄNDPLAN",
      "ÄSPSKÄR VÄNDPLAN GRÄSÖ",
      "ÆSPSKÆR VÆNDPLAN",
      "ÆSPSKÆR VÆNDPLAN GRÆSØ"
    ],
    "lId": "01191",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 60.30166666666666,
      "lon": 18.58972222222222
    }
  },
  {
    "name": "Östanå färjeläge",
    "synonyms": [
      "ÖSTANÅ FÄRJELÄGE",
      "ØSTANÅ FÆRJELÆGE"
    ],
    "lId": "20572",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.54833333333333,
      "lon": 18.574444444444445
    }
  },
  {
    "name": "Ätran",
    "synonyms": [
      "ÄTRAN",
      "ÆTRAN"
    ],
    "lId": "01399",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 57.12166666666667,
      "lon": 12.948611111111111
    }
  },
  {
    "name": "Ättersta",
    "synonyms": [
      "ÄTTERSTA",
      "ÆTTERSTA"
    ],
    "lId": "21296",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.13666666666666,
      "lon": 15.967222222222222
    }
  },
  {
    "name": "Öckerö",
    "synonyms": [
      "ÖCKERÖ",
      "ÖCKERÖ FÄRJELÄG",
      "ØCKERØ",
      "ØCKERØ FÆRJELÆG"
    ],
    "lId": "00861",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 57.71055555555556,
      "lon": 11.658333333333333
    }
  },
  {
    "name": "Ödeborg Bruksskolan",
    "synonyms": [
      "ÖDEBORG BRUKSSKOLAN",
      "ØDEBORG BRUKSSKOLAN"
    ],
    "lId": "12033",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 58.54555555555555,
      "lon": 11.969722222222222
    }
  },
  {
    "name": "Ödeshög",
    "synonyms": [
      "ODESHOG",
      "ÖDESHÖG",
      "ÖDESHÖG TORGET",
      "ØDESHØG",
      "ØDESHØG TORGET"
    ],
    "lId": "00606",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 58.228611111111114,
      "lon": 14.653055555555556
    }
  },
  {
    "name": "Ödåkra",
    "synonyms": [
      "ODAKRA",
      "ÖDÅKRA",
      "ÖDÅKRA STN",
      "ØDÅKRA",
      "ØDÅKRA STN"
    ],
    "lId": "01543",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 56.10472222222222,
      "lon": 12.74472222222222
    }
  },
  {
    "name": "Öje centrumhuset",
    "synonyms": [
      "ÖJE CENTRUMHUSET",
      "ØJE CENTRUMHUSET"
    ],
    "lId": "13113",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 60.808611111111105,
      "lon": 13.860555555555555
    }
  },
  {
    "name": "Öjebyn",
    "synonyms": [
      "ÖJEBYN",
      "ÖJEBYN GAMLA E4",
      "ØJEBYN",
      "ØJEBYN GAMLA E4"
    ],
    "lId": "20149",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 65.34055555555555,
      "lon": 21.40694444444444
    }
  },
  {
    "name": "Öjervik",
    "synonyms": [
      "ÖJERVIK",
      "ÖJERVIK STN",
      "ØJERVIK",
      "ØJERVIK STN"
    ],
    "lId": "01417",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.77361111111111,
      "lon": 13.122777777777777
    }
  },
  {
    "name": "Ölmbrotorp",
    "synonyms": [
      "ÖLMBROTORP",
      "ØLMBROTORP"
    ],
    "lId": "01400",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.390277777777776,
      "lon": 15.24611111111111
    }
  },
  {
    "name": "Ölme E18 stolpen",
    "synonyms": [
      "ÖLME E18 STOLPEN",
      "ØLME E18 STOLPEN"
    ],
    "lId": "22220",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.369166666666665,
      "lon": 14.01388888888889
    }
  },
  {
    "name": "Äng station",
    "synonyms": [
      "ANG STATION",
      "ÄNG STATION",
      "ÄNG STN",
      "ÆNG STATION",
      "ÆNG STN"
    ],
    "lId": "11918",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 57.69166666666666,
      "lon": 14.567777777777778
    }
  },
  {
    "name": "Önneköp",
    "synonyms": [
      "ÖNNEKÖP"
    ],
    "lId": "16992",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 55.78638888888889,
      "lon": 13.871944444444445
    }
  },
  {
    "name": "Önnestad centrum",
    "synonyms": [
      "ÖNNESTAD CENTRUM",
      "ÖNNESTAD CM",
      "ØNNESTAD CENTRUM",
      "ØNNESTAD CM"
    ],
    "lId": "30890",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 56.05361111111111,
      "lon": 14.023055555555556
    }
  },
  {
    "name": "Önnestad station",
    "synonyms": [
      "ÖNNESTAD STATION"
    ],
    "lId": "01606",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 56.06055555555555,
      "lon": 14.02888888888889
    }
  },
  {
    "name": "Ör terminal",
    "synonyms": [
      "ÖR TERMINAL",
      "ØR TERMINAL"
    ],
    "lId": "20686",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 56.992222222222225,
      "lon": 14.681666666666667
    }
  },
  {
    "name": "Örby centrum Kinna",
    "synonyms": [
      "ÖRBY CENTRUM KINNA",
      "ÖRBY CM KINNA",
      "ØRBY CENTRUM KINNA",
      "ØRBY CM KINNA"
    ],
    "lId": "12158",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 57.4825,
      "lon": 12.701666666666666
    }
  },
  {
    "name": "Örby slott",
    "synonyms": [
      "ÖRBY SLOTT",
      "ØRBY SLOTT"
    ],
    "lId": "65511",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.28138888888889,
      "lon": 18.031944444444445
    }
  },
  {
    "name": "Örbyhus station",
    "synonyms": [
      "ÖRBYHUS STATION",
      "ÖRBYHUS STN",
      "ØRBYHUS STATION",
      "ØRBYHUS STN"
    ],
    "lId": "00476",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 60.228611111111114,
      "lon": 17.705555555555556
    }
  },
  {
    "name": "Örebro C",
    "synonyms": [
      "ORB",
      "OREBRO C",
      "ÖREBRO C",
      "ØREBRO C"
    ],
    "lId": "00133",
    "prio": 1,
    "pId": "074",
    "pos": {
      "lat": 59.278888888888886,
      "lon": 15.21111111111111
    }
  },
  {
    "name": "Örebro Södra",
    "synonyms": [
      "OREBRO SODRA",
      "ÖREBRO SÖDRA",
      "ØREBRO SØDRA"
    ],
    "lId": "00361",
    "prio": 1,
    "pId": "074",
    "pos": {
      "lat": 59.26972222222222,
      "lon": 15.202222222222222
    }
  },
  {
    "name": "Örebro universitet",
    "synonyms": [
      "ÖREBRO UNIV",
      "ÖREBRO UNIVERSITET",
      "ØREBRO UNIV",
      "ØREBRO UNIVERSITET"
    ],
    "lId": "22865",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.255,
      "lon": 15.248055555555554
    }
  },
  {
    "name": "Örebro USÖ Slussen",
    "synonyms": [
      "ÖREBRO USÖ SLUSSEN",
      "ØREBRO USØ SLUSSEN"
    ],
    "lId": "22010",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.27444444444444,
      "lon": 15.238333333333333
    }
  },
  {
    "name": "Öregrund färjeläget",
    "synonyms": [
      "ÖREGRUND FÄRJELÄGET",
      "ØREGRUND FÆRJELÆGET"
    ],
    "lId": "00470",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 60.34055555555556,
      "lon": 18.44611111111111
    }
  },
  {
    "name": "Örestad",
    "synonyms": [
      "OERESTAD",
      "ÖRESTAD"
    ],
    "lId": "00856",
    "prio": 0,
    "pId": "086",
    "pos": {
      "lat": 55.62833333333333,
      "lon": 12.57861111111111
    }
  },
  {
    "name": "Örkelljunga",
    "synonyms": [
      "ORKELLJUNGA",
      "ÖRKELLJUNGA",
      "ÖRKELLJUNGA BST",
      "ØRKELLJUNGA",
      "ØRKELLJUNGA BST"
    ],
    "lId": "00549",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 56.283055555555556,
      "lon": 13.281111111111112
    }
  },
  {
    "name": "Ärla station",
    "synonyms": [
      "ÄRLA STATION",
      "ÄRLA STN",
      "ÆRLA STATION",
      "ÆRLA STN"
    ],
    "lId": "00328",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.282777777777774,
      "lon": 16.67638888888889
    }
  },
  {
    "name": "Örnsberg T-bana",
    "synonyms": [
      "ÖRNSBERG T-BANA",
      "ØRNSBERG T-BANA"
    ],
    "lId": "21721",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.305277777777775,
      "lon": 17.989166666666666
    }
  },
  {
    "name": "Örnsköldsvik C",
    "synonyms": [
      "ÖRNSKÖLDSVIK C",
      "ØRNSKØLDSVIK C"
    ],
    "lId": "01570",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 63.28916666666667,
      "lon": 18.704166666666666
    }
  },
  {
    "name": "Örnsköldsvik Fjällräven Center",
    "synonyms": [
      "ÖRNSKÖLDSVIK FJÄLLRÄVEN CENTER"
    ],
    "lId": "68818",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 63.284166666666664,
      "lon": 18.724444444444444
    }
  },
  {
    "name": "Örnsköldsvik Norra station",
    "synonyms": [
      "ÖRNSKÖLDSVIK NORRA STATION",
      "ØRNSKØLDSVIK NORRA STATION"
    ],
    "lId": "01569",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 63.30277777777778,
      "lon": 18.715833333333332
    }
  },
  {
    "name": "Örserum",
    "synonyms": [
      "ÖRSERUM",
      "ÖRSERUM CENTRUM",
      "ØRSERUM",
      "ØRSERUM CENTRUM"
    ],
    "lId": "11968",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 58.00694444444444,
      "lon": 14.577777777777778
    }
  },
  {
    "name": "Örsjö",
    "synonyms": [
      "ÖRSJÖ",
      "ØRSJØ"
    ],
    "lId": "14442",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 56.698611111111106,
      "lon": 15.751388888888888
    }
  },
  {
    "name": "Örsjö station",
    "synonyms": [
      "ÖRSJÖ STATION"
    ],
    "lId": "38520",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 56.69638888888888,
      "lon": 15.749722222222221
    }
  },
  {
    "name": "Örskärssund Gräsö",
    "synonyms": [
      "GRÄSÖ ÖRSKÄRSSUND",
      "GRÆSØ ØRSKÆRSSUND",
      "ÖRSKÄRSSUND",
      "ÖRSKÄRSSUND GRÄSÖ",
      "ØRSKÆRSSUND",
      "ØRSKÆRSSUND GRÆSØ"
    ],
    "lId": "01192",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 60.50361111111111,
      "lon": 18.389444444444443
    }
  },
  {
    "name": "Örsundsbro centrum",
    "synonyms": [
      "ÖRSUNDSBRO CENTRUM",
      "ÖRSUNDSBRO CM",
      "ØRSUNDSBRO CENTRUM",
      "ØRSUNDSBRO CM"
    ],
    "lId": "00737",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.73361111111111,
      "lon": 17.30777777777778
    }
  },
  {
    "name": "Örtagården",
    "synonyms": [
      "ÖRTAGÅRDEN"
    ],
    "lId": "43863",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.5625,
      "lon": 16.47694444444444
    }
  },
  {
    "name": "Örtofta",
    "synonyms": [
      "ORTOFTA",
      "ÖRTOFTA",
      "ÖRTOFTA STN",
      "ØRTOFTA",
      "ØRTOFTA STN"
    ],
    "lId": "00961",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 55.778888888888886,
      "lon": 13.243888888888888
    }
  },
  {
    "name": "Ösby skola",
    "synonyms": [
      "ÖSBY SKOLA",
      "ØSBY SKOLA"
    ],
    "lId": "25732",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.97972222222222,
      "lon": 16.6475
    }
  },
  {
    "name": "Ösmo",
    "synonyms": [
      "ÖSMO",
      "ÖSMO STN",
      "ØSMO",
      "ØSMO STN"
    ],
    "lId": "00790",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 58.98444444444444,
      "lon": 17.9025
    }
  },
  {
    "name": "Össjö",
    "synonyms": [
      "ÖSSJÖ",
      "ÖSSJÖ SKOLA",
      "ØSSJØ",
      "ØSSJØ SKOLA"
    ],
    "lId": "01525",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 56.22666666666667,
      "lon": 13.036111111111111
    }
  },
  {
    "name": "Östad",
    "synonyms": [
      "ÖSTAD",
      "ØSTAD"
    ],
    "lId": "16252",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 58.774166666666666,
      "lon": 11.562222222222223
    }
  },
  {
    "name": "Östanbro",
    "synonyms": [
      "ÖSTANBRO"
    ],
    "lId": "11973",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.62222222222222,
      "lon": 16.861111111111114
    }
  },
  {
    "name": "Östansjö",
    "synonyms": [
      "ÖSTANSJÖ",
      "ÖSTANSJÖ KÖPMG",
      "ØSTANSJØ",
      "ØSTANSJØ KØPMG"
    ],
    "lId": "01402",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.04472222222222,
      "lon": 14.982222222222223
    }
  },
  {
    "name": "Östanå väg 23 Skåne",
    "synonyms": [
      "ÖSTANÅ VÄG 23 SKÅNE",
      "ØSTANÅ VÆG 23 SKÅNE"
    ],
    "lId": "01526",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 56.305277777777775,
      "lon": 14.006666666666666
    }
  },
  {
    "name": "Östavall",
    "synonyms": [
      "ÖSTAVALL",
      "ØSTAVALL"
    ],
    "lId": "15357",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 62.42861111111111,
      "lon": 15.475555555555555
    }
  },
  {
    "name": "Östberga station Djursholm",
    "synonyms": [
      "ÖSTBERGA DJURSH",
      "ÖSTBERGA STATION DJURSHOLM",
      "ÖSTBERGA STN",
      "ØSTBERGA DJURSH",
      "ØSTBERGA STATION DJURSHOLM",
      "ØSTBERGA STN"
    ],
    "lId": "24797",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.40416666666667,
      "lon": 18.073888888888888
    }
  },
  {
    "name": "Österbybruk",
    "synonyms": [
      "ÖSTERBYBRUK",
      "ÖSTERBYBRUK BST",
      "ØSTERBYBRUK",
      "ØSTERBYBRUK BST"
    ],
    "lId": "00670",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 60.196666666666665,
      "lon": 17.898333333333333
    }
  },
  {
    "name": "Österbymo",
    "synonyms": [
      "ÖSTERBYMO",
      "ÖSTERBYMO BSTN",
      "ØSTERBYMO",
      "ØSTERBYMO BSTN"
    ],
    "lId": "00871",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 57.82611111111112,
      "lon": 15.274722222222223
    }
  },
  {
    "name": "Österforse",
    "synonyms": [
      "ÖSTERFORSE",
      "ÖSTERFORSE KIOS",
      "ØSTERFORSE",
      "ØSTERFORSE KIOS"
    ],
    "lId": "15358",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 63.155,
      "lon": 17.023888888888887
    }
  },
  {
    "name": "Österfärnebo kyrka",
    "synonyms": [
      "ÖSTERFÄRNEBO KA",
      "ÖSTERFÄRNEBO KYRKA",
      "ØSTERFÆRNEBO KA",
      "ØSTERFÆRNEBO KYRKA"
    ],
    "lId": "17974",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 60.30305555555555,
      "lon": 16.794722222222223
    }
  },
  {
    "name": "Östergraninge",
    "synonyms": [
      "ÖSTERGRANINGE",
      "ØSTERGRANINGE"
    ],
    "lId": "01404",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 62.98305555555556,
      "lon": 17.18166666666667
    }
  },
  {
    "name": "Östermalmstorg T-bana",
    "synonyms": [
      "ÖSTERMALMSTORG T-BANA",
      "ØSTERMALMSTORG T-BANA"
    ],
    "lId": "21651",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.334722222222226,
      "lon": 18.073888888888888
    }
  },
  {
    "name": "Östersjö brygga",
    "synonyms": [
      "ÖSTERSJÖ BRYGGA",
      "ØSTERSJØ BRYGGA"
    ],
    "lId": "01020",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.83361111111111,
      "lon": 19.077222222222222
    }
  },
  {
    "name": "Österskär",
    "synonyms": [
      "ÖSTERSKÄR",
      "ÖSTERSKÄR STN",
      "ØSTERSKÆR",
      "ØSTERSKÆR STN"
    ],
    "lId": "01303",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.46083333333333,
      "lon": 18.311666666666667
    }
  },
  {
    "name": "Österslöv",
    "synonyms": [
      "ÖSTERSLÖV",
      "ÖSTERSLÖV KYRKA",
      "ØSTERSLØV",
      "ØSTERSLØV KYRKA"
    ],
    "lId": "01527",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 56.09916666666667,
      "lon": 14.249722222222221
    }
  },
  {
    "name": "Österstad Allevägen",
    "synonyms": [
      "ÖSTERSTAD ALLEVÄGEN",
      "ØSTERSTAD ALLEVÆGEN"
    ],
    "lId": "11984",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 58.51833333333333,
      "lon": 15.176944444444445
    }
  },
  {
    "name": "Östersund C",
    "synonyms": [
      "OSTERSUND C",
      "ÖSTERSUND C",
      "ØSTERSUND C"
    ],
    "lId": "00123",
    "prio": 1,
    "pId": "074",
    "pos": {
      "lat": 63.17027777777778,
      "lon": 14.637777777777778
    }
  },
  {
    "name": "Östersund Brunnsgränd",
    "synonyms": [
      "ÖSTERSUND BRUNNSGRÄND"
    ],
    "lId": "29593",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 63.17305555555555,
      "lon": 14.639166666666666
    }
  },
  {
    "name": "Östersund STCC",
    "synonyms": [
      "ÖSTERSUND STCC",
      "ØSTERSUND STCC"
    ],
    "lId": "65097",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 63.19166666666666,
      "lon": 14.491666666666665
    }
  },
  {
    "name": "Östersund Västra",
    "synonyms": [
      "OSTERSUND VASTRA",
      "ÖSTERSUND V STN",
      "ÖSTERSUND VÄSTRA",
      "ØSTERSUND V STN",
      "ØSTERSUND VÆSTRA"
    ],
    "lId": "20168",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 63.17833333333333,
      "lon": 14.631111111111112
    }
  },
  {
    "name": "Östertälje",
    "synonyms": [
      "ÖSTERTÄLJE",
      "ÖSTERTÄLJE STN",
      "ØSTERTÆLJE",
      "ØSTERTÆLJE STN"
    ],
    "lId": "00791",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.18416666666666,
      "lon": 17.66
    }
  },
  {
    "name": "Östervik",
    "synonyms": [
      "ÖSTERVIK",
      "ÖSTERVIK STN",
      "ØSTERVIK",
      "ØSTERVIK STN"
    ],
    "lId": "24810",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.294999999999995,
      "lon": 18.235555555555557
    }
  },
  {
    "name": "Östervåla",
    "synonyms": [
      "ÖSTERVÅLA",
      "ÖSTERVÅLA BSTN",
      "ØSTERVÅLA",
      "ØSTERVÅLA BSTN"
    ],
    "lId": "00671",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 60.180277777777775,
      "lon": 17.18027777777778
    }
  },
  {
    "name": "Österäng",
    "synonyms": [
      "ÖSTERÄNG",
      "ÖSTERÄNG STN",
      "ØSTERÆNG",
      "ØSTERÆNG STN"
    ],
    "lId": "01405",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 58.63388888888889,
      "lon": 13.559722222222224
    }
  },
  {
    "name": "Östhammar",
    "synonyms": [
      "ÖSTHAMMAR",
      "ÖSTHAMMAR BSTN",
      "ØSTHAMMAR",
      "ØSTHAMMAR BSTN"
    ],
    "lId": "00672",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 60.25833333333333,
      "lon": 18.369722222222222
    }
  },
  {
    "name": "Östmark",
    "synonyms": [
      "ÖSTMARK",
      "ØSTMARK"
    ],
    "lId": "00831",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 60.27861111111111,
      "lon": 12.765
    }
  },
  {
    "name": "Östra Grevie kyrka",
    "synonyms": [
      "Ö GREVIE KYRKA",
      "ÖSTRA GREVIE KYRKA",
      "Ø GREVIE KYRKA",
      "ØSTRA GREVIE KYRKA"
    ],
    "lId": "16980",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 55.468611111111116,
      "lon": 13.135833333333332
    }
  },
  {
    "name": "Östra Grevie station",
    "synonyms": [
      "ÖSTRA GREVIE STATION"
    ],
    "lId": "01614",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 55.465833333333336,
      "lon": 13.13361111111111
    }
  },
  {
    "name": "Östra Husby",
    "synonyms": [
      "Ö HUSBY CENTRUM",
      "ÖSTRA HUSBY",
      "Ø HUSBY CENTRUM",
      "ØSTRA HUSBY"
    ],
    "lId": "00872",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 58.57555555555556,
      "lon": 16.565833333333334
    }
  },
  {
    "name": "Östra Karup",
    "synonyms": [
      "Ö KARUP AFFÄREN",
      "ÖSTRA KARUP",
      "Ø KARUP AFFÆREN",
      "ØSTRA KARUP"
    ],
    "lId": "17245",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 56.424166666666665,
      "lon": 12.946111111111112
    }
  },
  {
    "name": "Östra Ljungby",
    "synonyms": [
      "Ö LJUNGBY BSTN",
      "ÖSTRA LJUNGBY",
      "Ø LJUNGBY BSTN",
      "ØSTRA LJUNGBY"
    ],
    "lId": "01528",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 56.189722222222215,
      "lon": 13.065277777777778
    }
  },
  {
    "name": "Östra Ryd Eke",
    "synonyms": [
      "ÖSTRA RYD EKE",
      "ØSTRA RYD EKE"
    ],
    "lId": "20350",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 58.403055555555554,
      "lon": 16.175
    }
  },
  {
    "name": "Östra Sönnarslöv",
    "synonyms": [
      "Ö SÖNNARSLÖV",
      "ÖSTRA SÖNNARSLÖV",
      "Ø SØNNARSLØV",
      "ØSTRA SØNNARSLØV"
    ],
    "lId": "22131",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 55.88444444444444,
      "lon": 14.016944444444444
    }
  },
  {
    "name": "Östra Tommarp Bygatan",
    "synonyms": [
      "ÖSTRA TOMMARP BYGATAN",
      "ØSTRA TOMMARP BYGATAN"
    ],
    "lId": "24593",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 55.53388888888889,
      "lon": 14.240277777777777
    }
  },
  {
    "name": "Östra Vemmerlöv centrum",
    "synonyms": [
      "Ö VEMMERLÖV CM",
      "ÖSTRA VEMMERLÖV CENTRUM",
      "Ø VEMMERLØV CM",
      "ØSTRA VEMMERLØV CENTRUM"
    ],
    "lId": "04154",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 55.58305555555556,
      "lon": 14.231388888888889
    }
  },
  {
    "name": "Östra Vram",
    "synonyms": [
      "Ö VRAM KYRKA",
      "ÖSTRA VRAM",
      "Ø VRAM KYRKA",
      "ØSTRA VRAM"
    ],
    "lId": "01197",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 55.93111111111111,
      "lon": 14.022777777777778
    }
  },
  {
    "name": "Östraby kyrka",
    "synonyms": [
      "ÖSTRABY KYRKA"
    ],
    "lId": "21854",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 55.76,
      "lon": 13.681666666666667
    }
  },
  {
    "name": "Överammer",
    "synonyms": [
      "ÖVERAMMER",
      "ØVERAMMER"
    ],
    "lId": "13243",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 63.21388888888889,
      "lon": 15.952777777777778
    }
  },
  {
    "name": "Överberg övre vägen",
    "synonyms": [
      "ÖVERBERG ÖV VÄG",
      "ÖVERBERG ÖVRE VÄGEN",
      "ØVERBERG ØV VÆG",
      "ØVERBERG ØVRE VÆGEN"
    ],
    "lId": "29902",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 62.065555555555555,
      "lon": 14.287222222222223
    }
  },
  {
    "name": "Överby brygga",
    "synonyms": [
      "ÖVERBY BRYGGA",
      "ØVERBY BRYGGA"
    ],
    "lId": "01039",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 59.36055555555556,
      "lon": 18.647222222222222
    }
  },
  {
    "name": "Överby station",
    "synonyms": [
      "ÖVERBY STATION",
      "ÖVERBY STN",
      "ØVERBY STATION",
      "ØVERBY STN"
    ],
    "lId": "00056",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 58.843333333333334,
      "lon": 11.259166666666667
    }
  },
  {
    "name": "Överbyn Vägsjöfors",
    "synonyms": [
      "ÖVERBYN VÄGSJÖFORS",
      "ØVERBYN VÆGSJØFORS"
    ],
    "lId": "57125",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 60.275,
      "lon": 13.029444444444445
    }
  },
  {
    "name": "Överhogdal OKQ8",
    "synonyms": [
      "ÖVERHOGDAL OKQ8",
      "ØVERHOGDAL OKQ8"
    ],
    "lId": "13310",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 62.280833333333334,
      "lon": 14.803055555555556
    }
  },
  {
    "name": "Överhärde",
    "synonyms": [
      "ÖVERHÄRDE",
      "ØVERHÆRDE"
    ],
    "lId": "21803",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 60.61638888888889,
      "lon": 16.97611111111111
    }
  },
  {
    "name": "Överhörnäs",
    "synonyms": [
      "ÖVERHÖRNÄS",
      "ØVERHØRNÆS"
    ],
    "lId": "15362",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 63.286944444444444,
      "lon": 18.555555555555557
    }
  },
  {
    "name": "Överkalix",
    "synonyms": [
      "OVERKALIX",
      "ÖVERKALIX",
      "ÖVERKALIX BSTN",
      "ØVERKALIX",
      "ØVERKALIX BSTN"
    ],
    "lId": "00906",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 66.3261111111111,
      "lon": 22.836944444444445
    }
  },
  {
    "name": "Överlida centrum",
    "synonyms": [
      "ÖVERLIDA CENTRUM",
      "ÖVERLIDA CM",
      "ØVERLIDA CENTRUM",
      "ØVERLIDA CM"
    ],
    "lId": "12197",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 57.349444444444444,
      "lon": 12.895
    }
  },
  {
    "name": "Övertorneå",
    "synonyms": [
      "ÖVERTORNEÅ",
      "ÖVERTORNEÅ BSTN",
      "ØVERTORNEÅ",
      "ØVERTORNEÅ BSTN"
    ],
    "lId": "00464",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 66.39,
      "lon": 23.6575
    }
  },
  {
    "name": "Överturingen",
    "synonyms": [
      "ÖVERTURINGEN",
      "ØVERTURINGEN"
    ],
    "lId": "15364",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 62.450833333333335,
      "lon": 14.92
    }
  },
  {
    "name": "Överum kiosken",
    "synonyms": [
      "ÖVERUM KIOSKEN",
      "ØVERUM KIOSKEN"
    ],
    "lId": "14446",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 57.98916666666667,
      "lon": 16.311111111111114
    }
  },
  {
    "name": "Överums bruk",
    "synonyms": [
      "OVERUMS BRUK",
      "ÖVERUMS BRUK",
      "ÖVERUMS BRUK STATION",
      "ØVERUMS BRUK STATION"
    ],
    "lId": "30062",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 57.99,
      "lon": 16.319444444444443
    }
  },
  {
    "name": "Överå",
    "synonyms": [
      "ÖVERÅ",
      "ØVERÅ"
    ],
    "lId": "15365",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 63.331388888888895,
      "lon": 18.056944444444444
    }
  },
  {
    "name": "Övre Soppero",
    "synonyms": [
      "ÖV SOPPERO UNOX",
      "ÖVRE SOPPERO",
      "ØV SOPPERO UNOX",
      "ØVRE SOPPERO"
    ],
    "lId": "01408",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 68.09055555555555,
      "lon": 21.700555555555553
    }
  },
  {
    "name": "Öxnered",
    "synonyms": [
      "OXNERED",
      "ÖXNERED",
      "ÖXNERED STN",
      "ØXNERED",
      "ØXNERED STN"
    ],
    "lId": "00173",
    "prio": 0,
    "pId": "074",
    "pos": {
      "lat": 58.35916666666667,
      "lon": 12.273611111111112
    }
  }
]

for stop in stationsraw:
     stations[str(int(stop['pId']))+stop['lId']] = stop

stationsraw = ''