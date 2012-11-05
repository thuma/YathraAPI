<?php
header('Content-Type: text/html; charset=UTF-8');

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
// Check if student is a student.
if (isset($_GET["travelerIsStudent"])){
		$agestring = "ST";
}

// Compile Searh string:
$searchstring ="travelQuery.departureLocationName=".urlencode($_GET["from"]).
"&travelQuery.arrivalLocationName=".urlencode($_GET["to"]).
"&travelQuery.includeOnlySjProducer=true".
"&_travelQuery.includeOnlySjProducer=on".
"&travelQuery.includeOnlyNonStopTravel=true".
"&_travelQuery.includeOnlyNonStopTravel=on".
"&_travelQuery.includeExpressBuses=on".
"&travelQuery.campaignCode=".urlencode($_GET["promotionCode"]).
"&changeTravellerInfoRequest.selectedTravellerType=".$agestring.
"&travelQuery.outTimeDeparture=true".
"&travelQuery.outDateTime=".urlencode($_GET["date"])."T".urlencode($_GET["deparatureTime"])."+".
"&submitSearchLater=S%C3%B6k+resa";

// Open connection
$ch = curl_init();
curl_setopt($ch,CURLOPT_URL, "http://mobil.sj.se/timetable/searchtravel.do");
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
);

// Send responce as: XML / JSON:
if (isset($_GET["xml"])){
	print '<?xml version="1.0"?>';
	print '<trip>';
	foreach($result as $key => $value){
		print "<".key.">".$value."</".$key.">";
	}
	print '</trip>';
}
else{
	print json_encode($result);
}
?>