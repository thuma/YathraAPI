<?php
header('Content-Type: text/html; charset=UTF-8');

// Get cahce handler
include_once("cache.php");

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

*/

// Generate arry with correct station names: 
$stationarray = array();

// Check if station list is stored:
if(is_file("tmp/nsbstations.txt")){
	$chacheage = filemtime("tmp/nsbstations.txt") + 5000000;
	}

// Check if station chace is too old:
if($chacheage < time())
	{
	$stations = file_get_contents("http://www.nsb.no/javascript/getallstations.php");
	file_put_contents ("tmp/nsbstations.txt", $stations);
	}
	else
	{
	$stations = file_get_contents("tmp/nsbstations.txt");
	}
	
$stations = preg_split("/= \[/",$stations);
$stations = preg_split("/\];/",$stations[1]);
$stations = preg_split("/{label:/", $stations[0]);

// create assosiative array with stations:
foreach ($stations as $station){
	$names = preg_split('/"/',$station);
	$stationarray[$names[1]]=$names[3];
}

// Adda extra station translations:
$stationarray[utf8_encode("Göteborg C")] = utf8_encode("Gøteborg");

// Update station information:
if (isset($stationarray[$_GET["from"]])){
$_GET["from"] = $stationarray[$_GET["from"]];
}
else {
die("No from station.");
}

if (isset($stationarray[$_GET["to"]])){
$_GET["to"] = $stationarray[$_GET["to"]];
}
else {
die("No to station.");
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
$hh = substr($_GET["deparatureTime"], 0,2);

// Generate request url:
$url = "https://www.nsb.no/category2734.html?".
"booking-from=".urlencode($_GET["from"]).
"&booking-to=".urlencode($_GET["to"]).
"&booking-type="."single".
"&booking-date=".$date.
"&booking-date_outward_hour=".$hh.
"&booking-date-return=".$date.
"&booking-date_return_hour=".$hh.
"&booking-passengers="."1".
"&booking-passenger_type1=".$agecode.
"&booking-passenger_type2="."1".
"&booking-passenger_type3="."1".
"&booking-passenger_type4="."1".
"&booking-passenger_type5="."1".
"&booking-passenger_type6="."1".
"&booking-passenger_type7="."1".
"&booking-passenger_type8="."1".
"&booking-passenger_type9="."1";


	// Generate HTML data with info:
	$ch = curl_init($url);
	curl_setopt($ch, CURLOPT_SSL_VERIFYPEER, false);
	curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
	$htmldata= curl_exec($ch);
	curl_close($ch);
	
	// Define strings with final data:
	$finalarrivalTime = "";
	$finaldeparatureTime = "";
	$finalprice = "";
		
		// Split rows with data:
		$triprows = preg_split('/<\!-- ROW/', $htmldata);
		
		//Look for time and price in every row:
		for($i = 1; $i < count($triprows); $i++){
			$bestprice = 10000000;
			$tripfilter = preg_split("/<\/tbody>/", $triprows[$i]);
			$priceinfo = preg_split("/,-</", $tripfilter[0]);
			
			// Look for price:
			foreach($priceinfo as $pris){
				$cleaned = preg_split("/<strong>/", substr($pris, -20));
				
				// Set the price if found:
				if(isset($cleaned[1])){
					$prisint = intval($cleaned[1]);
					if($prisint < $bestprice){
						$bestprice = $prisint;
					}
				}
				
				// Look for price when Local Train:
				if ($bestprice == 10000000){
					$priceinfo = preg_split("/NSB Lokaltog /", $tripfilter[0]);
					$priceinfo = preg_split("/,-/", $priceinfo[1]);
					$bestprice = $priceinfo[0];
				}
				
			}
			
			// Look for departure time:
			$deparature = preg_split('/<td class="depart"/',$tripfilter[0]);
			$deparature = preg_split('/<\/strong>/',$deparature[1]);
			$deparature = preg_split('/>/',$deparature[0]);
			$deparatureTime = $deparature[2];
			
			// Look for arrival time:
			$deparature = preg_split('/<td class="arrive"/',$tripfilter[0]);
			$deparature = preg_split('/<\/strong>/',$deparature[1]);
			$deparature = preg_split('/>/',$deparature[0]);
			$arrivalTime =  $deparature[2];
		
			// Check if the time is correct:
			if (isset($_GET["arrivalTime"])){
				if ($deparatureTime == $_GET["deparatureTime"] && $arrivalTime == $_GET["arrivalTime"]){
					$finalprice = strval($bestprice);
					$finalarrivalTime = $arrivalTime;
					$finaldeparatureTime = $deparatureTime; 
				}
			}
			else{
				if ($deparatureTime == $_GET["deparatureTime"]){
					$finalprice = strval($bestprice);
					$finalarrivalTime = $_GET["arrivalTime"];
					$finaldeparatureTime = $deparatureTime; 
				}		
			}
		}

// Check if price is valid:
$pricevalid = true;
if($finalprice==""){
$pricevalid = false;
}

// Arrange data for processing:
$result = array(
"deparatureTime" => $_GET["deparatureTime"],
"arrivalTime" => $finalarrivalTime,
"date" => $_GET["date"],
"from" => $_GET["from"],
"to" => $_GET["to"],
"travelerAge" => $_GET["travelerAge"],
"promotionCode" => $_GET["promotionCode"],
"travelerIsStudent" => $_GET["travelerIsStudent"],
"price" => $finalprice." NOK",
"validPrice" => $pricevalid,
"url" => $url
);

// Store the data in the cache:
putCache("nsb", $result);

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