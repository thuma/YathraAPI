<?php
header('Content-Type: text/html; charset=UTF-8');

// Get chace handler
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
promotionCode		[Optional]	[String]	[MAX295]
travelerIsStudent	[Optional]	[Any]		[1]				(Any data is counted as true including 0 and false)
xml				  	[Optional]	[Any]		[1]				(Any data is counted as true including 0 and false)

#################### Respone data ###################
Key:				Data:		Example:
deparatureTime 		[HH:MM]		[06:30]
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

// Translationlist:
$stationlist = Array( "Kobenhavns Lufthavn Kastrup" => "Kastrup",
"Umea C" => "Umeå C",
"Kobenhavn H" => "K%C3%B6benhavn+H"
);

if(isset($stationlist[$_GET["to"]])){
	$_GET["to"] = $stationlist[$_GET["to"]];
}

if(isset($stationlist[$_GET["from"]])){
	$_GET["from"] = $stationlist[$_GET["from"]];
}

// Set deault age
if (isset($_GET["travelerAge"])){}
else{$_GET["travelerAge"]="29";}

// Prepare data for cache search
$test = Array("deparatureTime" => $_GET["deparatureTime"],
"arrivalTime" => $_GET["arrivalTime"],
"date" => $_GET["date"],
"from" => $_GET["from"],
"to" => $_GET["to"],
"travelerAge" => $_GET["travelerAge"]);

// Check cache for late entry
$fromcache = getCache("sj", $test);

// Check if found i found resturn the data from cache.
if(isset($fromcache["date"])){

// Create result array from cache data.
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

// Check if travelever is entield to age disscounts.
$agestring = "VU";
if (isset($_GET["travelerAge"])){
	$ageInt = intval($_GET["travelerAge"]);
	if ($ageInt > 26){
		$agestring = "VU";
	}
	elseif ($ageInt < 26 AND $ageInt > 20){
		$agestring = "UN";
	}
	elseif ($ageInt < 20 AND $ageInt > 16){
		$agestring = "U1";
	}
}

// Check if traveler is a student.
if (isset($_GET["travelerIsStudent"])){
		$agestring = "ST";
}

// Compile Searh string:
$searchstring ="travelQuery.departureLocationName=".$_GET["from"].
"&travelQuery.arrivalLocationName=".$_GET["to"].
"&_travelQuery.includeExpressBuses=on".
"&travelQuery.campaignCode=".urlencode($_GET["promotionCode"]).
"&changeTravellerInfoRequest.selectedTravellerType=".$agestring.
"&travelQuery.outTimeDeparture=true".
"&travelQuery.outDateTime=".urlencode($_GET["date"])."T".urlencode($_GET["deparatureTime"])."+".
"&submitSearchLater=S%C3%B6k+resa";

// Open connection
$ch = curl_init();
curl_setopt($ch, CURLOPT_URL, "http://mobil.sj.se/timetable/searchtravel.do");
curl_setopt($ch, CURLOPT_HEADER, true);
curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);

// Get session cookie.
$result = curl_exec($ch);
$datarows = preg_split("/Set-Cookie:/", $result); 
$datarows = preg_split("/;/", $datarows[1]);
$sesionscookie =  trim($datarows[0]);

// POST the search request
curl_setopt($ch, CURLOPT_URL, "http://mobil.sj.se/timetable/searchtravel.do");
curl_setopt($ch, CURLOPT_POST, true);
curl_setopt($ch, CURLOPT_POSTFIELDS, $searchstring);
curl_setopt($ch, CURLOPT_COOKIE, $sesionscookie);
$result = curl_exec($ch);

// Get list with the trips found in the serarch.
curl_setopt($ch, CURLOPT_HTTPGET, true);
curl_setopt($ch, CURLOPT_HEADER, false);
curl_setopt($ch, CURLOPT_URL, "http://mobil.sj.se/api/timetable/departures");
curl_setopt($ch, CURLOPT_COOKIE, $sesionscookie);
$result = curl_exec($ch);

// Arrange data into nice array.
$trips = json_decode($result, true);
$tripsarray = $trips["data"]["rows"];

// Find the required trip.
$tripid="";
foreach ($tripsarray as $trip){
	if ($trip["departureTime"]==$_GET["deparatureTime"]){
		if (isset($_GET["arrivalTime"])){
			if($trip["arrivalTime"]==$_GET["arrivalTime"]){
				$tripid = $trip["id"];
			}
		}
		else{
			$tripid = $trip["id"];
			}
	}
}

// Get price data
curl_setopt($ch, CURLOPT_URL, "http://mobil.sj.se/api/timetable/prices/bestforids");
curl_setopt($ch, CURLOPT_POST, true);
curl_setopt($ch, CURLOPT_POSTFIELDS, "journeyIds=".$tripid);
curl_setopt($ch, CURLOPT_COOKIE, $sesionscookie);
$result = curl_exec($ch);
curl_close($ch);

// Arrange data into nice array.
$prices = json_decode($result, true);
$pricearray = $prices["data"];

// Connect trip data with price data.
foreach ($pricearray as &$price){
	foreach ($tripsarray as &$trip){
		if ($trip["id"] == $price["journeyId"]){
			$price["trip"] =  $trip;
		} 
	}
}

// Arrange data for processing:
$result = array(
"deparatureTime" => $_GET["deparatureTime"],
"arrivalTime" => $pricearray[0]["trip"]["arrivalTime"],
"date" => $_GET["date"],
"from" => $_GET["from"],
"to" => $_GET["to"],
"travelerAge" => $_GET["travelerAge"],
"promotionCode" => $_GET["promotionCode"],
"travelerIsStudent" => $_GET["travelerIsStudent"],
"price" => str_replace(":-"," SEK", $pricearray[0]["price"]),
"validPrice" => $pricearray[0]["validPrice"],
"soldOut" => $pricearray[0]["soldOut"],
"bookable" => $pricearray[0]["trip"]["bookable"],
"departed" => $pricearray[0]["trip"]["departed"],
"url" => "http://www.sj.se"
);

// Stor the data in the cache:
putCache("sj", $result);
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