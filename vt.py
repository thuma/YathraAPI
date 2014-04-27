# !/usr/bin/env python
# -*- coding: utf-8 -*-

import tornado.httpclient
import tornado.escape
import time
from bs4 import BeautifulSoup


http_client = tornado.httpclient.HTTPClient()
try:
    response = http_client.fetch('https://raw.githubusercontent.com/thuma/Transit-Stop-Identifier-Conversions-Sweden/master/vasttrafik-gtfs.csv')
    list_data = response.body
except httpclient.HTTPError as e:
    print "Error:", e
http_client.close()
cache = {}
stops = {}
list_data = list_data.split('\n')

for row in list_data:
	try:
		parts = row.split(';')
		stops[parts[4]] = {}
		stops[parts[4]]['id'] = parts[3]
		stops[parts[4]]['name'] = parts[0]
	except:
		parts = ''


url = "http://reseplanerare.vasttrafik.se/bin/query.exe/sn\
?SGID="+stops['7400002']['id']+"\
&ZGID="+stops['7415633']['id']+"\
&date=2014-04-28\
&time="+tornado.escape.url_escape("14:30")+"\
&start=1\
&L=vs_vasttrafik\
&timesel=depart"

print url

http_client = tornado.httpclient.HTTPClient()
response = http_client.fetch(url)
print response.headers['Set-Cookie']

exit()

bsdata = BeautifulSoup(response.body)
lista = bsdata.find_all("td", { "class" : "timeDep"})
for i in lista:
	purl = i.parent.find_all("td", { "class" : "last"})[0].find_all("a")[0]["href"]
	print purl

response = http_client.fetch(purl)

print response.body

http_client.close()

'''
$table = $doc->getElementById('tableBody_filteredCons');
foreach($rows as $row){
	$cols = $row->getElementsByTagName('td');
 	if(isset($cols->item(1)->nodeValue) AND isset($cols->item(3)->nodeValue)){
 		$priser[trim($cols->item(1)->nodeValue)][trim($cols->item(3)->nodeValue)] = $cols->item(9)->getElementsByTagName('a')->item(0)->getAttribute('href');
 	}
}

$prishtml = str_replace ('<table class="resultTablePriceInfo">' , '<table class="resultTablePriceInfo" id="pristabell">', $prishtml );
$olikapriser = Array();
@$doc->loadHTML($prishtml);
$table = $doc->getElementById('pristabell');
$rows =  $table->getElementsByTagName('tr');
foreach($rows as $row){
	$cols = $row->getElementsByTagName('td');
	if(isset($cols->item(0)->nodeValue) AND isset($cols->item(1)->nodeValue) AND isset($cols->item(2)->nodeValue) AND isset($cols->item(3)->nodeValue))
	{
		$olikapriser[trim($cols->item(0)->nodeValue)]["Vuxen"] = $cols->item(1)->nodeValue;
		$olikapriser[trim($cols->item(0)->nodeValue)]["Ungdom"] = $cols->item(2)->nodeValue;
		$olikapriser[trim($cols->item(0)->nodeValue)]["Skolungdom"] = $cols->item(3)->nodeValue; 
	}
}'''


