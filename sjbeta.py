import requests
import json
import demjson

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
            "departureLocation":{"id":"00110:074"},
            "arrivalLocation":{"id":"00001:074"},
            "journeyDate":{"date":"2016-01-28"},
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
    print i

# Print all to screen:
print json.dumps(trips)
