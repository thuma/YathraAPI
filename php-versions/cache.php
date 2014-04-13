<?php

// Stor data to cache.
function putCache($seller, $query){

// Query to create table:
/*
$maketable = "CREATE TABLE cache (Id integer, ".
"seller text, ".
"deparatureTime text, ".
"arrivalTime text, ".
"date text, ".
"_from text, ".
"_to text, ".
"travelerAge text, ".
"price text, ".
"validPrice text, ".
"url text, ".
"PRIMARY KEY(Id));";
*/

// Create query for storing data:
$storedata = "INSERT INTO cache (Id, seller, deparatureTime, ".
"arrivalTime, date, _from, _to, travelerAge, ".
"price, validPrice, url) VALUES(".
time().", '".
$seller."', '".
$query["deparatureTime"]."', '".
$query["arrivalTime"]."', '".
$query["date"]."', '".
$query["from"]."', '".
$query["to"]."', '".
$query["travelerAge"]."', '".
$query["price"]."', '".
$query["validPrice"]."', '".
$query["url"]."');";

// Stor data to the DB:
$db = sqlite_open('tmp/cache');
    sqlite_exec($db, $storedata);
sqlite_close($db);

}

// Find data in cache.
function getCache($seller, $query){

// Create search query:
$finddata = "SELECT * FROM cache WHERE Id < ".(time()+3600)." AND seller = '" . $seller . 
"' AND deparatureTime = '". $query["deparatureTime"] .
"' AND arrivalTime = '". $query["arrivalTime"]. 
"' AND date = '".$query["date"].
"' AND _from = '".$query["from"].
"' AND _to = '".$query["to"].
"' AND travelerAge = '".$query["travelerAge"]."';";

// Open DB and make query:
$db = sqlite_open('tmp/cache');
	$result = sqlite_query($db, $finddata);
	$resultat  = sqlite_fetch_array($result, SQLITE_ASSOC);
sqlite_close($db);

// Return the resuling row:
return $resultat;
}

?>
