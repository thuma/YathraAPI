<?php
header('Content-Type: text/html; charset=UTF-8');

// Include cache functions:
include_once("cache.php");

/*
#################### Request data ###################
Key:							Data:		Example:		Comment:			
deparatureTime 		[Required]	[HH:MM]		[06:30]
arrivalTime			[Optional]	[HH:MM]		[10:00]			Use if two trains have the same deparature time.
date				[Required]	[YYY-MM-DD]	[2013-01-15]
from				[Required]	[Name]		[Lund C]
to					[Required]	[Name]		[Stockholm C]
travelerAge			[Optional]	[NN]		[23]
xml				  	[Optional]	[Any]		[1]				(Any data is counted as true including 0 and false)

#################### Respone data ###################
Key:				Data:		Example:
deparatureTime 		[HH:MM]		[06:30]
arrivalTime			[HH:MM]		[10:00]
date				[YYY-MM-DD]	[2013-01-15]
from				[Name]		[Lund C]
to					[Name]		[Stockholm C]
travelerAge			[NN]		[23]
price				[N SEK]		[345 SEK]
validPrice			[T/F]		[True]
*/

// Translationlist:
$stationlist = Array( "Kobenhavn H" => "Kobenhavn Hbf" ,
"Odense" => "Odense St" ,
"Stockholm C" => "Stockholm Central" ,
"Lund C" => "Lund Central" ,
"Wien Westbahnhof" => "WIEN" ,
"Amsterdam CS" => "Amsterdam Centraal" ,
"Berlin Hbf (Tief)" => "Berlin Hbf" ,
"Wien Meidling" => "WIEN" ,
"Varberg" => "Varberg Station"
);

if(isset($stationlist[$_GET["to"]])){
	$_GET["to"] = $stationlist[$_GET["to"]];
}

if(isset($stationlist[$_GET["from"]])){
	$_GET["from"] = $stationlist[$_GET["from"]];
}

// set default traveler age:
if (isset($_GET["travelerAge"])){}
else{$_GET["travelerAge"]="29";}

// Create array for seding to cache search:
$test = Array("deparatureTime" => $_GET["deparatureTime"],
"arrivalTime" => $_GET["arrivalTime"],
"date" => $_GET["date"],
"from" => $_GET["from"],
"to" => $_GET["to"],
"travelerAge" => $_GET["travelerAge"]);

// Search cache for recent data:
$fromcache = getCache("db", $test);

// Check if recent data was found:
if(isset($fromcache["date"])){
	$result = array(
	"deparatureTime" => $fromcache["deparatureTime"],
	"arrivalTime" => $fromcache["arrivalTime"],
	"date" => $fromcache["date"],
	"from" => $fromcache["_from"],
	"to" => $fromcache["_to"],
	"travelerAge" => $fromcache["travelerAge"],
	"price" => $fromcache["price"],
	"validPrice" =>  $fromcache["validPrice"],
	"url" => $fromcache["url"]
	);

} else {


// Compile Station searh string:
$stationsearch = "http://reiseauskunft.bahn.de/bin/query.exe/en?".
"revia=yes&existOptimizePrice=1&country=USA".
"&dbkanal_007=L01_S01_D001_KIN0001_qf-bahn_LZ003".
"&ignoreTypeCheck=yes".
"&S=".urlencode($_GET["from"]).
"&REQ0JourneyStopsSID=&REQ0JourneyStopsS0A=7".
"&Z=".urlencode($_GET["to"]).
"&REQ0JourneyStopsZID=".
"&REQ0JourneyStopsZ0A=7".
"&trip-type=single".
"&date=".urlencode(date("d.n.y", strtotime($_GET["date"]))).
"&time=".urlencode($_GET["deparatureTime"]).
"&timesel=depart".
"&returnTimesel=depart".
"&optimize=0".
"&travelProfile=-1".
"&adult-number=1".
"&children-number=0".
"&infant-number=0".
"&tariffTravellerType.1=E".
"&tariffTravellerReductionClass.1=0".
"&tariffTravellerAge.1=29".
"&qf-trav-bday-1=".
"&tariffTravellerReductionClass.2=0".
"&tariffTravellerReductionClass.3=0".
"&tariffTravellerReductionClass.4=0".
"&tariffTravellerReductionClass.5=0".
"&tariffClass=2".
"&start=1";

// Initiate and run curl request:
$ch = curl_init($stationsearch);
curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
$result = curl_exec($ch);

// close connection.
curl_close($ch);

// Find the trip info rows:
$htmltrips = preg_split('/<tr class=" firstrow">/', $result);

// Generate global variables to stor data to:
$price = "";
$arrivaltaime = "";
$first = true;
$url = "";

// Check all trips one by one for the correct one:
foreach($htmltrips as $htmltrip){

	// Skipp the first row since it is the HTML header etc:
	if ($first){
		
	}
	else 
	{
		// Look for prices in three different ways:
		$pricestart = preg_split('/title="Information about availability">/', $htmltrip);
		$pricestop = preg_split('/&nbsp;EUR<\/a>/',$pricestart[1]);

		$pricebstart = preg_split('/<span class="bold">from<\/span>&nbsp;/', $htmltrip);
		$pricebstop = preg_split('/EUR/', $pricebstart[1]);

		$pricecstart = preg_split('/title="Information about availability">/', $htmltrip);
		$pricecstop = preg_split('/&nbsp;EUR<\/a>/', $pricecstart[1]);
		
		// Generate the url for acces the list site:
		$pricurlend = preg_split('/" title="Checking the availability of the offer/', $htmltrip);
		$pricurlstart = preg_split('/href="/', $pricurlend[0]);
		
		// Genereate strings widh the time inside:
		$deparaturestart = preg_split('/<td class="timetx">\ndep\n<\/td>\n<td class="time">\n/', $htmltrip);
		$arrivalstart = preg_split('/<td class="timetx">arr<\/td>\n<td class="time">\n/', $htmltrip);
		
		// Correct the time to HH:MM:
		$deptime = substr($deparaturestart[1],0,5);
		$arrtime = substr($arrivalstart[1],0,5);
		
		// Check if time is the correct one for the requested price:
		if($deptime == $_GET["deparatureTime"]){
			if($arrtime == $_GET["arrivalTime"] || isset($_GET["arrivalTime"]) == false){
				// Use the price found:
				if ($pricestop[0] == ""){
					if ($pricebstop[0]==""){
						$price = $pricecstop[0];
					}
					else
					{
						$price = $pricebstop[0];
					}
				}
				else{				
					$price = $pricestop[0];
				}
				
				// Store the arrival time:
				$arrivaltaime = $arrtime;
				
				// Store the URL:
				$url = end($pricurlstart);
				
				// Find the URL for accesing the verifyed price:
				$endcheckurl = preg_split('/" title="Checking the availability/',$htmltrip);
				$endcheckurl2 = preg_split('/"/',$endcheckurl[0]);
				$checlurl = preg_replace("/&amp;/","&",end($endcheckurl2));
				
				// Download the price info page:
				$checkedpricedata = file_get_contents($checlurl); 
				
				// Search the page for the price:
				$checksplited = preg_split('/checked="checked" type="radio">/', $checkedpricedata);
				$checksplited = preg_split('/EUR/', end($checksplited));
				$checksplited = preg_split('/>/', $checksplited[0]);
				$checkedprice = end($checksplited);
				
				// If price found in the verify page put it in the price variable:
				if(strlen($checkedprice)>2){ 
					$price = $checkedprice;
				}
			}
		}	
	}
	// Set that the first element is scanned.
	$first = false;
}

// Check if price is valid:
if($price == ""){
$pricevalid = false;
}
else{
$pricevalid = true;
}


// Arrange data for processing:
$result = array(
"deparatureTime" => $_GET["deparatureTime"],
"arrivalTime" => $arrivaltaime,
"date" => $_GET["date"],
"from" => $_GET["from"],
"to" => $_GET["to"],
"travelerAge" => $_GET["travelerAge"],
"price" => $price." EUR",
"validPrice" => $pricevalid,
"url" => $stationsearch
);
putCache("db", $result);

}

// Send responce as: XML / JSON:
if (isset($_GET["xml"])){
	print '<?xml version="1.0"?>';
	print '<trip>';
	foreach($result as $key => $value){
		print "<".$key.">".$value."</".$key.">";
	}
	print '</trip>';
}
else{
	print json_encode($result);
}
?>