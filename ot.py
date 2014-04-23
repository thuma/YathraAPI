# !/usr/bin/env python
# -*- coding: utf-8 -*-

import tornado.httpclient
from bs4 import BeautifulSoup


http_client = tornado.httpclient.HTTPClient()
try:
    response = http_client.fetch('https://raw.githubusercontent.com/thuma/Transit-Stop-Identifier-Conversions-Sweden/master/ostgotatrafiken-gtfs.csv')
    list_data = response.body
except tornado.httpclient.HTTPError as e:
    print "Error:", e
http_client.close()
htlcache = {}
hltstops = {}
list_data = list_data.split('\n')

for row in list_data:
	try:
		parts = row.split(';')
		hltstops[parts[4]] = {}
		hltstops[parts[4]]['id'] = parts[3]
		hltstops[parts[4]]['name'] = parts[0]
	except:
		parts = ''



# Generate search object.
query['start'] = $_GET['from']->Id;
query['end'] = $_GET['to']->Id;
query['date'] = $_GET['date'].' '.$_GET['departureTime']; 
query['direction'] = '0'; 
query['span'] = 'default';
query['traffictype'] = '31';
query['changetime'] = '0';
query['priority'] = '0';
query['walk'] = 'false';



// Get det data from OT:
$trips = json_decode(processCurlJsonrequest("http://www.ostgotatrafiken.se/rest/TravelHelperWebService.asmx/FindJourney", json_encode($query)));

// change to array:
$trips = $trips->d;

// Loop thrue trips to find the price:
$outprice = null;
$pricevalid = FALSE;
for($i = 0; $i < count($trips); $i++){
	if(  $_GET['departureTime'] == $trips[$i]->strDeparture AND 
		($_GET['arrivalTime'] == $trips[$i]->strArrival OR (isset($_GET['arrivalTime'])==FALSE))){
		$outprice = $trips[$i]->Prices[3]->Price;
		$pricevalid = TRUE;
	}
}

$responce->from = $_GET['from']->Id;
$responce->to = $_GET['to']->Id;
$responce->date = $_GET['date'];
$responce->departureTime = $_GET['departureTime'];
$responce->arrivalTime = $_GET['arrivalTime'];
$responce->price = $outprice;
$responce->validPrice = $pricevalid;
$responce->url = "http://www.ostgotatrafiken.se";
$responce->sellername = "Östgotatrafiken";

print json_encode($responce);
file_put_contents($cachefile, json_encode($result));

//Initiate cURL request and send back the result
function processCurlJsonrequest($URL, $fieldString) { 
    $ch = curl_init();    
    curl_setopt($ch, CURLOPT_HTTPHEADER, array('Content-Type: application/json' , 'Content-Length: ' . strlen($fieldString)));
    curl_setopt($ch, CURLOPT_URL, $URL);
    curl_setopt($ch, CURLOPT_RETURNTRANSFER, 1);
    curl_setopt($ch, CURLOPT_VERBOSE, TRUE);
    curl_setopt($ch, CURLOPT_POSTFIELDS, $fieldString);
    curl_setopt($ch, CURLOPT_POST, 1); 
    $resulta = curl_exec($ch);
    if (curl_errno($ch)) {
        print curl_error($ch);
    } else {
        curl_close($ch);
    }
    return $resulta;
}

?>
