<?php
header("Content-type: application/json; charset=utf-8");

if(file_exists('otstations/'.$_GET['from'])==FALSE){
die('{"error":"from station not in list"}');
}
if(file_exists('otstations/'.$_GET['to'])==FALSE){
die('{"error":"to station not in list"}');
}

// Check if in cache:
asort($_GET);
$cachefile = 'otcache/'.md5(json_encode($_GET));
if(file_exists($cachefile)){
		die(file_get_contents($cachefile));
}

$_GET['from'] = json_decode(file_get_contents('otstations/'.$_GET['from']));
$_GET['to'] = json_decode(file_get_contents('otstations/'.$_GET['to']));

// Generate search object.
$query->start = $_GET['from']->Id;
$query->end = $_GET['to']->Id;
$query->date = $_GET['date'].' '.$_GET['departureTime']; 
$query->direction = '0'; 
$query->span = 'default';
$query->traffictype = '31';
$query->changetime = '0';
$query->priority = '0';
$query->walk = 'false';



// Get det data from OT:
$trips = json_decode(processCurlJsonrequest("http://www.ostgotatrafiken.se/rest/TravelHelperWebService.asmx/FindJourney", json_encode($query)));

// change to array:
$trips = $trips->d;

// Loop thrue trips to find the price:
$outprice = null;
$pricevalid = FALSE;
for($i = 0; $i < count($trips); $i++){
	if(  $_GET['departureTime'] == $trips[$i]->strDeparture AND 
		($_GET['arrivalTime'] == $trips[$i]->strArrival OR (isset($_GET['arrivalTime'])==FALSE))){
		$outprice = $trips[$i]->Prices[3]->Price;
		$pricevalid = TRUE;
	}
}

$responce->from = $_GET['from']->Id;
$responce->to = $_GET['to']->Id;
$responce->date = $_GET['date'];
$responce->departureTime = $_GET['departureTime'];
$responce->arrivalTime = $_GET['arrivalTime'];
$responce->price = $outprice;
$responce->validPrice = $pricevalid;
$responce->url = "http://www.ostgotatrafiken.se";
$responce->sellername = "Östgotatrafiken";

print json_encode($responce);
file_put_contents($cachefile, json_encode($result));

//Initiate cURL request and send back the result
function processCurlJsonrequest($URL, $fieldString) { 
    $ch = curl_init();    
    curl_setopt($ch, CURLOPT_HTTPHEADER, array('Content-Type: application/json' , 'Content-Length: ' . strlen($fieldString)));
    curl_setopt($ch, CURLOPT_URL, $URL);
    curl_setopt($ch, CURLOPT_RETURNTRANSFER, 1);
    curl_setopt($ch, CURLOPT_VERBOSE, TRUE);
    curl_setopt($ch, CURLOPT_POSTFIELDS, $fieldString);
    curl_setopt($ch, CURLOPT_POST, 1); 
    $resulta = curl_exec($ch);
    if (curl_errno($ch)) {
        print curl_error($ch);
    } else {
        curl_close($ch);
    }
    return $resulta;
}

?>