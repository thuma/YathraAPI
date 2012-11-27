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
xml				  	[Optional]	[Any]		[1]				(Any data is counted as true including 0 and false)

#################### Respone data ###################
Key:				Data:		Example:
deparatureTime 		[HH:MM]		[06:30]
arrivalTime			[HH:MM]		[10:00]
date				[YYY-MM-DD]	[2013-01-15]
from				[Name]		[Lund C]
to					[Name]		[Stockholm C]
price				[N EUR]		[345 EUR]
validPrice			[T/F]		[True]
*/

$YYYY = substr ($_GET["date"] , 0, 4 );
$MM = substr ($_GET["date"] , 5, 2 );
$DD = substr ($_GET["date"] , 8, 2 );

$search = "http://openbahnapi.appspot.com/rest/connections/list?".
"start=".urlencode($_GET["from"]).
"&destination=".urlencode($_GET["to"]).
"&date=".$DD.".".$MM.".".$YYYY;

// Get and arrange data into nice array.
$tripsarray = json_decode(file_get_contents($search), true);

$righttrip = "";
// Find the required trip.
foreach ($tripsarray as $trip){

	if (unixtohhmm($trip["startTime"])==$_GET["deparatureTime"]){
		if (isset($_GET["arrivalTime"])){
			if(unixtohhmm($trip["destinationTime"])==$_GET["arrivalTime"]){
				$righttrip = $trip;
			}
		}
		else{
			$righttrip = $trip;
			}
	}
}

// Arrange data for processing:
$result = array(
"deparatureTime" => $_GET["deparatureTime"],
"arrivalTime" => unixtohhmm($righttrip["destinationTime"]),
"date" => $_GET["date"],
"from" => $_GET["from"],
"to" => $_GET["to"],
"price" => $righttrip["price"]." EUR",
"validPrice" => isset($righttrip["price"])
);

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

function unixtohhmm($sec){
return strval(date("H:i",(intval($sec)/1000)));
}
?>