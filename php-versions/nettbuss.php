<?php
header('Content-Type: text/html; charset=UTF-8');

// Get cahce handler
// include_once("cache.php");

if(isset($_GET['departureTime']) == FALSE){	
	die('{"error":"departureTime not set"}');
}	
if(isset($_GET['arrivalTime']) == FALSE){		
	die('{"error":"arrivalTime not set"}');
}	
if(isset($_GET['date']) == FALSE){	
	die('{"error":"date not set"}');
}	
if(isset($_GET['from']) == FALSE){	
	die('{"error":"from not set"}');
}	
if(isset($_GET['to']) == FALSE){	
	die('{"error":"to not set"}');
}	

if(isset($_GET["travelerAge"]) == FALSE){
	$_GET["travelerAge"] = '35';
}

$agename = "V";
if(intval($_GET["travelerAge"]) <= 29){
	$agename = "J";
}
else if(intval($_GET["travelerAge"]) >= 60){
	$agename = "S";
}

if(isset($_GET["travelerIsStudent"]) == FALSE){
	$_GET["travelerIsStudent"] = false;
}

if(isset($_GET["promotionCode"]) == FALSE){
	$_GET["promotionCode"] = false;
}


/*
#################### Request data ##################
Key:			Data:		Example:	Comment:			
departureTime 		[Required]	[HH:MM]		[06:30]
arrivalTime		[Optional]	[HH:MM]		[10:00]		Use if two trains have the same deparature time.
date			[Required]	[YYYY-MM-DD]	[2013-01-15]
from			[Required]	[Name]		[Lund C]
to			[Required]	[Name]		[Stockholm C]
travelerAge		[Optional]	[NN]		[23]
promotionCode		[Optional]	[String]	[MAX295]
travelerIsStudent	[Optional]	[Any]		[1]		(Any data is counted as true including 0 and false)
xml			[Optional]	[Any]		[1]		(Any data is counted as true including 0 and false)

#################### Respone data ###################
Key:			Data:		Example:
deparatureTime 		[HH:MM]		[06:30]
arrivalTime		[HH:MM]		[10:00]
date			[YYY-MM-DD]	[2013-01-15]
from			[Name]		[Lund C]
to			[Name]		[Stockholm C]
travelerAge		[NN]		[23]
promotionCode		[String]	[MAX295]
travelerIsStudent	[Any]		[1]
price			[N NOK]		[345 NOK]
validPrice		[T/F]		[True]
soldOut			[T/F]		[False]
bookable		[T/F]		[True]
departed		[T/F]		[False]

*/


//GTFS-ID -> Nettbuss Id
$stations['7400300'] = '1393';
$stations['7415561'] = '2340';
$stations['7415561'] = '2340';
$stations['7400266'] = '1406';
$stations['7420483'] = '1394';
$stations['7400044'] = '1388';
$stations['7400090'] = '1387';
$stations['8699658'] = '1399';
$stations['8624917'] = '1397';
$stations['7410955'] = '1396';
$stations['7400291'] = '1401';
$stations['7400120'] = '1389';
$stations['7400003'] = '1390';
$stations['7436225'] = '1450';
$stations['7690003'] = '1998';
$stations['7411131'] = '1395';
$stations['7690001'] = '242';
$stations['7625036'] = '1313';
$stations['7625036'] = '1313';
$stations['7423566'] = '1402';
$stations['7400622'] = '1391';
$stations['7412949'] = '1403';
$stations['7422989'] = '1991';
$stations['7400120'] = '1389';
$stations['7411131'] = '1395';
$stations['7423098'] = '1409';
$stations['7407178'] = '1392';

// Check if station is in network:
if(isset($stations[$_GET['from']]) == FALSE OR isset($stations[$_GET['to']]) == FALSE)
	{
	die('{"error":"station not in list '.$_GET['from'].' '.$_GET['to'].'"}');
	}

// Make date for nettbuss request:
$nettbussdate = preg_replace('/-/','',$_GET['date']);

// Request trips:
$ckfile = tempnam ("/tmp", "CURLCOOKIE");
$url = 'https://www.nettbuss.se/bokning/valj-avgang?s=0-'.$stations[$_GET['from']].'-'.$stations[$_GET['to']].'-'.$nettbussdate;
$ch = curl_init($url);
curl_setopt($ch, CURLOPT_SSL_VERIFYHOST, 0);
curl_setopt($ch, CURLOPT_COOKIEJAR, $ckfile);
curl_setopt($ch, CURLOPT_SSL_VERIFYPEER, 0);
curl_setopt($ch, CURLOPT_RETURNTRANSFER, 1);
$resorraw = curl_exec($ch);



// Get the DOM:
$resordom = new DOMDocument;
@$resordom->loadHTML('<?xml encoding="UTF-8">'.$resorraw);
//print $resordom->saveHTML($resordom->getElementById('departuresLoaderId'));

// Get list table:
$trips = $resordom->getElementById('departuresLoaderId')->firstChild->getElementsByTagName('tr');
$pris = array();


// Itterate thrue table:
for($i=1; $i < $trips->length; $i++){
	//print $resordom->saveHTML($trips->item($i));
	if(	$trips->item($i)->childNodes->item(1)->nodeValue == $_GET['departureTime'] AND ( 
		$trips->item($i)->childNodes->item(2)->nodeValue == $_GET['arrivalTime'] OR isset($_GET['arrivalTime']) == FALSE)){
		$pricekey = preg_split("/'/",$trips->item($i)->getAttribute('onclick'));
		$pricekey = $pricekey[1];
		curl_setopt($ch, CURLOPT_URL, 'https://www.nettbuss.se/Modules/WebPublisher.Modules.TravelBooking/PageParts/DepartureSelector/DepartureSelectorWebService.asmx/GetDepartureInfo');
		curl_setopt($ch, CURLOPT_SSL_VERIFYHOST, 0);
		curl_setopt($ch, CURLOPT_SSL_VERIFYPEER, 0);
		curl_setopt($ch, CURLOPT_RETURNTRANSFER, 1);
		curl_setopt($ch, CURLOPT_COOKIEFILE, $ckfile);
		curl_setopt($ch, CURLOPT_POST, 1);
		curl_setopt($ch, CURLOPT_POSTFIELDS, 'tripKey='.urlencode($pricekey).'&toTrip=true&editing=&allowOnlyOneBooking=false');
		$traveldata = curl_exec($ch);
		curl_close($ch);
		unlink($ckfile);

		$cleaned = preg_replace('/ |\n|\r/','',$traveldata);
		$parts = preg_split('/SEK/',$cleaned);
		foreach($parts as $part){
			$delar = preg_split('/;/',$part);
			if($delar[count($delar)-1]!='</string>'){
				$pris[$delar[count($delar)-3][0]] = $delar[count($delar)-1];
			}
		}
	}
}


if(isset($pris['V']) == FALSE){
		die('{"error":"no trip found in timetable."}');
}

// Arrange data for processing:
$result = array(
"departureTime" => $_GET["departureTime"],
"arrivalTime" => $_GET["arrivalTime"],
"date" => $_GET["date"],
"from" => $_GET["from"],
"to" => $_GET["to"],
"travelerAge" => $_GET["travelerAge"],
"promotionCode" => $_GET["promotionCode"],
"travelerIsStudent" => $_GET["travelerIsStudent"],
"price" => intval($pris[$agename]),
"currency" => "SEK",
"validPrice" => true,
"sellername" => "nettbuss",
"url" => $url
);

print json_encode($result);

//print_r($parts);
//print_r($trips);

//https://www.nettbuss.se/Modules/WebPublisher.Modules.TravelBooking/PageParts/DepartureSelector/DepartureSelectorWebService.asmx/GetDepartureInfo
//2%7C35239%7C2020%7C988%7C992%7C0%7C0%7C0%7C0%7C0%7C0%7C0%7C0

?>
