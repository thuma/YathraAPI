# !/usr/bin/env python
# -*- coding: utf-8 -*-

import tornado.httpclient
from bs4 import BeautifulSoup


http_client = tornado.httpclient.HTTPClient()
try:
    response = http_client.fetch('https://raw.githubusercontent.com/thuma/Transit-Stop-Identifier-Conversions-Sweden/master/swebus-gtfs.csv')
    list_data = response.body
except httpclient.HTTPError as e:
    print "Error:", e
http_client.close()
cache = {}
stops = {}
list_data = list_data.split('\n')

for row in list_data:
	try:
		parts = row.split(',')
		stops[parts[0]] = {}
		stops[parts[0]]['id'] = parts[2]
		stops[parts[0]]['name'] = parts[3]
	except:
		parts = ''


print stops



'''
/*
#################### Request data ###################
Key:							Data:		Example:		Comment:			
departureTime 		[Required]	[HH:MM]		[06:30]
arrivalTime			[Optional]	[HH:MM]		[10:00]			Use if two trains have the same deparature time but different arrival times.
date				[Required]	[YYYY-MM-DD]	[2013-01-15]
from				[Required]	[ID]		[7000002]
to					[Required]	[ID]		[7000001]
travelerAge			[Optional]	[NN]		[29]
promotionCode		[Optional]	[String]	[MAX295]
travelerIsStudent	[Optional]	[Any]		[1]				(Any data is counted as true including 0 and false)

#################### Respone data (To be decided:)###################
Key:				Data:		Example:
departureTime 		[HH:MM]		[06:30]
arrivalTime			[HH:MM]		[10:00]
date				[YYY-MM-DD]	[2013-01-15]
from				[Name]		[Lund C]
to					[Name]		[Stockholm C]
travelerAge			[NN]		[23]
promotionCode		[String]	[MAX295]
travelerIsStudent	[Any]		[1]
price				[N SEK]		[345 SEK]
validPrice			[T/F]		[True]
soldOut				[T/F]		[False]
bookable			[T/F]		[True]
departed			[T/F]		[False]
*/


//Check that station is selected.
if(isset($_GET["from"]) == FALSE OR isset($_GET["to"])==FALSE){
	die('{"error":"No station selected."}');
}

if(isset($station[$_GET["from"]]) == FALSE OR isset($station[$_GET["to"]])==FALSE){
	die('{"error":"Station not in list"}');
}

//Check that date and time is given.
if(isset($_GET["date"]) == FALSE OR isset($_GET["departureTime"])==FALSE){
	die('{"error":"Time or date is missing."}');
}

$Adult = 1;
$Child = 0;
$Youth = 0;
$Student = 0;
$Pensioner = 0;
$Pet = 0;

$url = 'http://www.swebus.se/Express/Sokresultat/'
.'?from='.$station[$_GET["from"]]['id']
.'&fromtype=BusStop'
.'&to='.$station[$_GET["to"]]['id']
.'&totype=BusStop'
.'&away='.$_GET["date"]
.'&Adult='.$Adult
.'&Child='.$Child
.'&Youth='.$Youth
.'&Student='.$Student
.'&Pensioner='.$Pensioner
.'&Pet='.$Pet
.'&campaignCode='
.'&id=1101'
.'&epslanguage=sv-SE';

$resordom = new DOMDocument;
@$resordom->loadHTML('<?xml encoding="UTF-8">'.file_get_contents($url));

$table = $resordom->getElementsByTagName('table');

$trippdata = array();
for($i = 1; $i < $table->length; $i++){
	foreach($table->item($i)->getElementsByTagName('th') as $coll){
		$trippdata[$i][trim($coll->getAttribute('class'))] = trim($coll->nodeValue);
		if($coll->getAttribute('class')=='Price1'){
			if($coll->getElementsByTagName('input')->length > 0){
				$trippdata[$i][trim($coll->getAttribute('class'))] = $coll->getElementsByTagName('input')->item(0)->getAttribute('value');
				}
		}
		elseif($coll->getAttribute('class')=='Price2'){
			if($coll->getElementsByTagName('input')->length > 0){
				$trippdata[$i][trim($coll->getAttribute('class'))] = $coll->getElementsByTagName('input')->item(0)->getAttribute('value');
				}
		}
		elseif($coll->getAttribute('class')=='Price3'){
			if($coll->getElementsByTagName('input')->length > 0){
				$trippdata[$i][trim($coll->getAttribute('class'))] = $coll->getElementsByTagName('input')->item(0)->getAttribute('value');
			}
		}
	}
}

$final = false;
foreach($trippdata as $trip){
	if(isset($_GET['arrivalTime']) == FALSE){
		if($trip['Departure'] == $_GET['departureTime']){
			$final = $trip;
			break;
		}
	}
	if(isset($_GET['arrivalTime'])){
		if($trip['Departure'] == $_GET['departureTime'] AND $trip['Arrival'] == $_GET['arrivalTime']){
			$final = $trip;
			break;
		}
	}
}

if($final==false){
	die('{"error":"Triptime not found"}');
}

$result = array(
"departureTime" => $_GET["departureTime"],
"arrivalTime" => $final['Arrival'],
"date" => $_GET["date"],
"from" => $_GET["from"],
"to" => $_GET["to"],
"price" => preg_replace("/ SEK/","", $final["Price1"]),
"currency" => "SEK",
"validPrice" => true,
"url" => $url,
"sellername" => "SWEBUS"
);

print json_encode($result);

 ?>'''