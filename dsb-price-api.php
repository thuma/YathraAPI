<?php

$ch = curl_init("http://www.dsb.dk/salg/netbutikken/");                                                                      
curl_setopt($ch, CURLOPT_HEADER, true);		                                                               
curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
$pagedata = curl_exec($ch);

$result = preg_split("/Set-Cookie: /",$pagedata);
$result = preg_split("/;/",$result[1]);
$cookie =  $result[0];

$formdata = preg_split('/<form action="/',$pagedata);
$formdata = preg_split("/<\/div>/",$formdata[1]);
$formdata = $formdata[0];

$hidden = preg_split('/<input type="hidden" name="/',$formdata);
$hidden = preg_split('/"/',$hidden[1]);
$hidden = $hidden[0];

$action = $hidden = preg_split('/"/',$formdata);
$action = "http://www.dsb.dk/salg/netbutikken/sogeresultat".$action[0];

print $action;

$action = "http://www.dsb.dk/salg/netbutikken/sogeresultat?wicket:interface=:3:content:rejseRegelModalWindow:modalwindow:content:form:ok-frame:ok::IActivePageBehaviorListener:0:-1&wicket:ignoreIfNotActive=true&random=0.21554759123464729";

$searchstring = $hidden.
"&soegebokslayout%3Asoegetyperlayout%3AsoegeType=radio0".
"&soegebokslayout%3AfraDestination%3Aborder%3AdestinationInput=Malm%C3%B6%20C".
"&soegebokslayout%3AtilDestination%3Aborder%3AdestinationInput=K%C3%B8benhavn%20H".
"&soegebokslayout%3Aenkelt=radio4".
"&soegebokslayout%3AtidErrorBorder%3AhiddenField=".
"&soegebokslayout%3AtidErrorBorder%3AfraTidPanel%3AtidBorder%3AdatoValgPanel%3Adag=25".
"&soegebokslayout%3AtidErrorBorder%3AfraTidPanel%3AtidBorder%3AdatoValgPanel%3Amaaned=1".
"&soegebokslayout%3AtidErrorBorder%3AfraTidPanel%3AtidBorder%3AdatoValgPanel%3AdatePicker=2012-12-26".
"&soegebokslayout%3AtidErrorBorder%3AfraTidPanel%3AtidBorder%3AtidTxt=10%3A39".
"&soegebokslayout%3AtidErrorBorder%3AfraTidPanel%3AtidBorder%3Aafgang=radio6".
"&soegebokslayout%3AtidErrorBorder%3AtilTidPanel%3AtidBorder%3AdatoValgPanel%3Adag=1".
"&soegebokslayout%3AtidErrorBorder%3AtilTidPanel%3AtidBorder%3AdatoValgPanel%3Amaaned=0".
"&soegebokslayout%3AtidErrorBorder%3AtilTidPanel%3AtidBorder%3AdatoValgPanel%3AdatePicker=2012-11-26".
"&soegebokslayout%3AtidErrorBorder%3AtilTidPanel%3AtidBorder%3AtidTxt=10%3A39".
"&soegebokslayout%3AtidErrorBorder%3AtilTidPanel%3AtidBorder%3Aafgang=radio8".
"&soegebokslayout%3AkundekategoriPladserPanel%3AcountErrorBorder%3Avoksen=1".
"&soegebokslayout%3AkundekategoriPladserPanel%3AcountErrorBorder%3Aover65=0".
"&soegebokslayout%3AkundekategoriPladserPanel%3AcountErrorBorder%3Alillebarn=0".
"&soegebokslayout%3AkundekategoriPladserPanel%3AcountErrorBorder%3Aung=0".
"&soegebokslayout%3AkundekategoriPladserPanel%3AcountErrorBorder%3Abarn=0".
"&soegebokslayout%3AkundekategoriPladserPanel%3AcountErrorBorder%3AantalPladser=1".
"&soegebokslayout%3Asoeg=1";

$ch = curl_init($action);                                                                      
curl_setopt($ch, CURLOPT_HEADER, true);		                                                               
curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
curl_setopt($ch, CURLOPT_POST, true);
curl_setopt($ch, CURLOPT_POSTFIELDS, $searchstring);
curl_setopt($ch, COOKIE, $cookie);
$resultb = curl_exec($ch);

print $resultb;

?>
