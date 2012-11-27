<?php
header('Content-Type: text/html; charset=UTF-8');

// Get chace controller:
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

// Set default age:
if (isset($_GET["travelerAge"])){}
else {
$_GET["travelerAge"] = "29";
}

// Check if travelever is entield to age disscounts.
$ageInt = intval($_GET["travelerAge"]);
if ($ageInt <= 19 AND $ageInt >= 7){
	$ageno = 4;
}
else {
	$ageno = 3;
	}

// Build array for search in cache:
$test = Array("deparatureTime" => $_GET["deparatureTime"],
"arrivalTime" => $_GET["arrivalTime"],
"date" => $_GET["date"],
"from" => $_GET["from"],
"to" => $_GET["to"],
"travelerAge" => $_GET["travelerAge"]);

// Search cache for recent data:
$fromcache = getCache("sktr", $test);

// Check if data found in cache:
if(isset($fromcache["date"])){

	// Create array from cache.
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
	$stationsearch = "http://www.labs.skanetrafiken.se/v2.2/querypage.asp?".
	"inpPointFr=".urlencode($_GET["from"]).
	"&inpPointTo=".urlencode($_GET["to"]);

	// Get station ids:
	$stationsobject = soaptophpobject($stationsearch,"GetStartEndPointResult");

	$from = urlencode($stationsobject->StartPoints->Point[0]->Name).'|'.
	$stationsobject->StartPoints->Point[0]->Id .'|0';
	
	$to = urlencode($stationsobject->EndPoints->Point[0]->Name).'|'.
	$stationsobject->EndPoints->Point[0]->Id .'|0';

	// Start search 2 minutes before the deparature time:
	$before =(	intval(substr($_GET["deparatureTime"],0,2))*3600 + 
				intval(substr($_GET["deparatureTime"],3,2))*60) -120 ;
			
	// Make search:
	$connectionsearch = "http://www.labs.skanetrafiken.se/v2.2/resultspage.asp?cmdaction=next".
	"&selPointFr=".urlencode($from).
	"&selPointTo=".urlencode($to).	
	"&LastStart=".$_GET["date"]."%20".date("G:i", $before).
	"&NoOf=3";

	// Get connection list:
	$connectionsobject = soaptophpobject($connectionsearch,"GetJourneyResult");

	// Find the required trip.
	$requestedtrip = "";
	foreach ($connectionsobject->Journeys->Journey as $Journey){

		if (substr($Journey->DepDateTime, 11, 5) == $_GET["deparatureTime"]){
			if (isset($_GET["arrivalTime"])){
				if(substr($Journey->ArrDateTime, 11, 5)==$_GET["arrivalTime"]){
					$requestedtrip = $Journey;
				}
			}
			else{
				$requestedtrip = $Journey;
			}
		}
	}

	// Arrange data for processing:
	$result = array(
	"deparatureTime" => $_GET["deparatureTime"],
	"arrivalTime" => substr($requestedtrip->ArrDateTime,11,5),
	"date" => $_GET["date"],
	"from" => $_GET["from"],
	"to" => $_GET["to"],
	"travelerAge" => $_GET["travelerAge"],
	"price" => strval($requestedtrip->Prices->PriceInfo[$ageno]->Price)." SEK",
	"validPrice" => isset($requestedtrip->Prices->PriceInfo[$ageno]->Price),
	"url" => "http://www.skanetrafiken.se"
	);
	
	// Store data in cache:
	putCache("sktr", $result);

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


// Get SOAP data and return as PHP object
function soaptophpobject($url,$string){

	$xmlString = file_get_contents($url);
	$xmlString = preg_split( "/<".$string.">/" , $xmlString, 2);
	$xmlString = preg_split( "/<\/".$string.">/" , $xmlString[1], 2);
	$xmlString = '<?xml version="1.0" encoding="utf-8"?><data>'.$xmlString[0].'</data>';
	
	return simplexml_load_string($xmlString);
	}
?>