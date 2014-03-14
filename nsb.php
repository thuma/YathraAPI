<?php
header('Content-type: application/json; charset=UTF-8');
date_default_timezone_set('UTC');
include('simple_html_dom.php');

/*
#################### Request data ##################
Key:			Data:		Example:	Comment:			
deparatureTime 		[Required]	[HH:MM]		[06:30]
arrivalTime		[Optional]	[HH:MM]		[10:00]		Use if two trains have the same deparature time.
date			[Required]	[YYY-MM-DD]	[2013-01-15]
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

006-Elmedia

*/

$_GET['from'] = '7600100';
$_GET['to']   = '7400002';
$_GET['date'] = '2014-03-15';
$_GET['departureTime'] = '13:02';
$_GET['arrivalTime'] = '16:50';

$stops['7600527'] = "Sarpsborg";
$stops['7600522'] = "Fredrikstad";
$stops['7600546'] = "Halden";
$stops['7400002'] = "Gøteborg";
$stops['7600516'] = "Moss";
$stops['7600518'] = "Rygge";
$stops['7600519'] = "Råde";
$stops['7400173'] = "Øxnered";
$stops['7600100'] = "Oslo S";
$stops['7400191'] = "Trollhättan";
$stops['7400283'] = "Ed";
$stops['7600508'] = "Ski";

$manat['januar'] = '01';
$manat['februar'] = '02';
$manat['mars'] = '03';
$manat['april'] = '04';
$manat['mai'] = '05';
$manat['juni'] = '06';
$manat['juli'] = '07';
$manat['august'] = '08';
$manat['september'] = '09';
$manat['oktober'] = '10';
$manat['november'] = '11';
$manat['desember'] = '12';

if(isset($stops[$_GET["from"]]) AND isset($stops[$_GET["to"]])){}
else {
die('{"error":"station not in list"}');
}

// Set deault age:
if (isset($_GET["travelerAge"])){}
else{$_GET["travelerAge"]="29";}
$agecode = "1";

// Check if retired:
if (intval($_GET["travelerAge"])>67){
$agcode = "3";
}

// Check if student
if (isset($_GET["travelerIsStudent"]) && intval($_GET["travelerAge"])<30){
$agcode = "4";
}

// Generatore correct data syntax for page:
$date = date("d.m.Y", strtotime($_GET["date"]));

// Generater correct deparature time for page:
$hh = substr($_GET["departureTime"], 0,2);

// Generate request url:
$url  = 'https://www.nsb.no/bestill/travel-planner-validator?'.
'redirect_to=https%3A%2F%2Fwww.nsb.no%2Fbestill%2Fvelg-togavgang'.
'&portable=false'.
'&from='.urlencode($stops[$_GET["from"]]).
'&to='.urlencode($stops[$_GET["to"]]).
'&type=single'.
'&date='.$date.
'&hour='.$hh.
'&returnDate='.$date.
'&returnHour='.$hh.
'&passengers=1'.
'&passengerType1='.$agecode.
'&passengerCard1='.
'&bookingPassengerExtrasStroller=0'.
'&bookingPassengerExtrasPetfree=0'.
'&bookingPassengerExtrasClosetodog=0'.
'&bookingPassengerExtrasAnimalsallowed=0'.
'&booking-submit-form=Se+togtider+og+priser';

	// Generate HTML data with info:
	$ch = curl_init($url);
	curl_setopt($ch, CURLOPT_SSL_VERIFYPEER, false);
	curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
	curl_setopt($ch, CURLOPT_FOLLOWLOCATION, true);
	$htmldata = curl_exec($ch);

	curl_close($ch);
	$dom = new simple_html_dom($htmldata);

	if ($dom === null){die('{"Error":"Error no response from NSB"}');}
	// Find all images
	$days = $dom->find('section.journey-list',0);

	$loop = 0;
	foreach($days->find('ol') as $day){
		$daydate = $day->prev_sibling()->find("span.date", 0)->plaintext;
	foreach($day->find('div.main') as $element){
       		$trip[$loop] = array();
		$trip[$loop]['departureTime'] = trim($element->find('div.depart',0)->plaintext);
                $trip[$loop]['arrivalTime'] = trim($element->find('div.arrive',0)->plaintext);
		@$trip[$loop]['lowestPrice'] = preg_replace("/[^0-9]/",'',$element->find('label.cheapest',0)->plaintext);
		@$trip[$loop]['normalPrice'] =  preg_replace("/[^0-9]/",'',$element->find('label',0)->plaintext);
		$dateparts = preg_split('/\s/',preg_replace('/\./','',trim(preg_split('/,/',$daydate)[1])));
		$trip[$loop]['date'] = $dateparts[2].'-'.$manat[$dateparts[1]].'-'.$dateparts[0];
		$loop ++;
		}
	}

$finalprice = "";
foreach($trip as $row){
	if(
	$row['departureTime'] == $_GET['departureTime'] &&
	$row['arrivalTime'] == $_GET['arrivalTime'] &&
	$row['date'] == $_GET['date']){
		if(intval($row['lowestPrice']) > 1){
		$finalprice = $row['lowestPrice'];
		}
		else{
		$finalprice = $row['normalPrice'];
		}
	}
}
	
// Check if price is valid:
$pricevalid = true;
if($finalprice==""){
$pricevalid = false;
die('{"Error":"No trip found."}');
}



$xml = simplexml_load_string(file_get_contents('http://www.ecb.europa.eu/stats/eurofxref/eurofxref-daily.xml'));
$obj = json_decode(preg_replace('/@/','',json_encode($xml)));
foreach($obj->Cube->Cube->Cube as $currency){
	$change[$currency->attributes->currency] = $currency->attributes->rate;
}


// Arrange data for processing:
$result = array(
"deparatureTime" => $_GET["departureTime"],
"arrivalTime" => $_GET['arrivalTime'],
"date" => $_GET["date"],
"from" => $_GET["from"],
"to" => $_GET["to"],
"price" => strval(round(floatval($finalprice)*$change['SEK']/$change['NOK'])),
"currency" => "SEK",
"validPrice" => $pricevalid,
"sellername" => "NSB",
"url" => $url
);

print json_encode($result);

?>
