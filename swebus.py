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

class CachePrint(tornado.web.RequestHandler):
	def get(self):
		global cache
		self.write(cache)

class Handler(tornado.web.RequestHandler):
	@tornado.web.asynchronous
	def get(self):
		global cache
		global stops
		
		try:
			price = cache[self.get_argument('date')+self.get_argument('from')+self.get_argument('to')+self.get_argument('departureTime')+self.get_argument('arrivalTime')]
			outdata = {"travelerAge":35,	
				"travelerIsStudent":False,
				"sellername":"Swebuss",
				"price":"",
				"currency":"SEK",
				"validPrice":True
				}
		
			outdata['departureTime'] = self.get_argument('departureTime')
			outdata['arrivalTime'] = self.get_argument('arrivalTime')
			outdata['date'] = self.get_argument('date')
			outdata['from'] = self.get_argument('from')
			outdata['to'] = self.get_argument('to')
			outdata['price'] = price['Price1']
			outdata['validPrice'] = 1
			#outdata['url'] = price['url']
	
			self.write(outdata)
			self.finish()
			return
		except:
			notfoundincache = 1	
		
		
		self.http_client = tornado.httpclient.AsyncHTTPClient()
		try:
			self.url = 'http://www.swebus.se/Express/Sokresultat/\
?from='+stops[self.get_argument('from')]['id']+'\
&fromtype=BusStop\
&to='+stops[self.get_argument('to')]['id']+'\
&totype=BusStop\
&away='+self.get_argument('date')+'\
&Adult=1\
&Child=0\
&Youth=0\
&Student=0\
&Pensioner=0\
&Pet=0\
&campaignCode=\
&id=1101\
&epslanguage=sv-SE'
			self.myhttprequest = tornado.httpclient.HTTPRequest(self.url) 
			self.http_client.fetch(self.myhttprequest, self.searchdone)
		except:
			self.write({'error':'from/to station not in network'})
			self.finish()
			return
		
	def searchdone(self, response):
		global cache
		html_data = response.body
		try:
			html_data = BeautifulSoup(html_data)
		except:
			#self.http_client.fetch(self.myhttprequest, self.searchdone)
			#return
			end = 1
		lista = html_data.find(id='bookingSearchResultsAway').findAll("div", { "class" : "Accordion" })
		lista = lista[0].findAll("table") 

		for i in lista:
                        data = {}
                        data['Departure'] = i.findAll("th", { "class" : "Departure" })[0].string.strip()
                        data['Arrival'] = i.findAll("th", { "class" : "Arrival" })[0].string.strip()
                        data['Price1'] = i.findAll("th", { "class" : "Price1" })[0].findAll("input")[0]['value']
                        data['Price2'] = i.findAll("th", { "class" : "Price2" })[0].findAll("input")[0]['value']
                        data['Price3'] = i.findAll("th", { "class" : "Price3" })[0].findAll("input")[0]['value']

                        cache[self.get_argument('date')+self.get_argument('from')+self.get_argument('to')+data['Departure']+data['Arrival']] = data
                
                try:
			price = cache[self.get_argument('date')+self.get_argument('from')+self.get_argument('to')+self.get_argument('departureTime')+self.get_argument('arrivalTime')]
			outdata = {"travelerAge":35,	
				"travelerIsStudent":False,
				"sellername":"Swebuss",
				"price":"",
				"currency":"SEK",
				"validPrice":True
				}
		
			outdata['departureTime'] = self.get_argument('departureTime')
			outdata['arrivalTime'] = self.get_argument('arrivalTime')
			outdata['date'] = self.get_argument('date')
			outdata['from'] = self.get_argument('from')
			outdata['to'] = self.get_argument('to')
			outdata['price'] = price['Price1']
			outdata['validPrice'] = 1
			#outdata['url'] = price['url']
	
			self.write(outdata)
			self.finish()
			return
		except:
			notfoundincache = 1	
                        
                self.write('{"Error":"No trip found"}')
                self.finish()
		'''
		scripts = html_doc.find_all('script')

		for script in scripts:
			rad = script.string
			try:
				rad = rad.strip()
			except:
				rad = "nodatainstring"
			if rad[:8] == 'dValidFr':
				done = rad

		rawprice = done.split('\n')
		tripdata = {}

		for row in rawprice:
			row = row.strip()
			if row[:9] == 'priceArr[':
				parts = row.split('(')
				rownumb = row.split(']')[0].split('[')[1]
				tripdata[rownumb] = {}
				tripdata[rownumb]['prices'] = parts[1][1:-2].split('\',\'')
				

		for index in tripdata:
			svar = html_doc.find(id="result-"+index)
			data = svar.find_all('td')
			tripdata[index]['times'] = {}
			tripdata[index]['times']['dep'] = data[1].string
			tripdata[index]['times']['arr'] = data[2].string
			tripdata[index]['times']['dur'] = data[3].string
			tripdata[index]['times']['changes'] = data[4].string
			tripdata[index]['url'] = self.url
			htlcache[self.get_argument('date')+self.get_argument('from')+self.get_argument('to')+tripdata[index]['times']['dep']+tripdata[index]['times']['arr']] = tripdata[index]

		try:
			price = htlcache[self.get_argument('date')+self.get_argument('from')+self.get_argument('to')+self.get_argument('departureTime')+self.get_argument('arrivalTime')]
			outdata = {"travelerAge":35,	
				"travelerIsStudent":False,
				"sellername":"HLT",
				"price":"",
				"currency":"SEK",
				"validPrice":True
				}
		
			outdata['departureTime'] = self.get_argument('departureTime')
			outdata['arrivalTime'] = self.get_argument('arrivalTime')
			outdata['date'] = self.get_argument('date')
			outdata['from'] = self.get_argument('from')
			outdata['to'] = self.get_argument('to')
			outdata['price'] = price['prices'][3]
			outdata['validPrice'] = 1
			outdata['url'] = price['url']
	
			self.write(outdata)
			self.finish()
			return	
		except:		
			self.write({'error':'No trip found'})
			self.finish()
		'''
		


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