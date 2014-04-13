<?php

$ch = curl_init("https://www.sbb.ch/ticketshop/b2c/sprache.do?en");                                                                      
curl_setopt($ch, CURLOPT_HEADER, true);		                                                               
curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);				 
curl_setopt($ch, CURLOPT_SSL_VERIFYPEER, false);
$result = curl_exec($ch);

$result = preg_split("/Set-Cookie: /",$result);
$result = preg_split("/;/",$result[1]);
print $result[0].$result[1];

$ch = curl_init("https://www.sbb.ch/ticketshop/b2c/adw.do?4004");                                                                      
curl_setopt($ch, CURLOPT_HEADER, true);		                                                               
curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
curl_setopt($ch, COOKIE, $result[0]);
curl_setopt($ch, CURLOPT_SSL_VERIFYPEER, false);
$resultb = curl_exec($ch);

//print $resultb;

$resulta = preg_split("/Set-Cookie: /",$resultb);
$resulta = preg_split("/;/",$resulta[1]);
print $resulta[0].$resulta[1];

$token = preg_split("/org.apache.struts.taglib.html.TOKEN/",$resultb);
$token = preg_split('/value="/',$token[1]);
$token = preg_split('/"/',$token[1]);

$ch = curl_init("https://www.sbb.ch/ticketshop/b2c/artikelspezSAGeneric.do");                                                                      
curl_setopt($ch, CURLOPT_HEADER, true);
curl_setopt($ch, CURLOPT_POST, true);
curl_setopt($ch, CURLOPT_POSTFIELDS, "org.apache.struts.taglib.html.TOKEN=".$token[0]."&artikelspez.abgang.name=Aarau&artikelspez.bestimmung.name=Basel+SBB&artikelspez.via%5B0%5D.name=&artikelspez.reiseDatum.datumViewDDMMYYYY_E=04.12.2012+%28Tu%29&method%3Acont=Next");		                                                               
curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
curl_setopt($ch, COOKIE, "WT_FPC=id=109.58.54.33-4287147520.30263505:lv=1353918389004:ss=1353918066739; ".$resulta[0]);
curl_setopt($ch, CURLOPT_SSL_VERIFYPEER, false);
$resultc = curl_exec($ch);

print $resultc;

$token = preg_split("/org.apache.struts.taglib.html.TOKEN/", $resultc);
$token = preg_split('/value="/', $token[1]);
$token = preg_split('/"/',$token[1]);
print "Token:".$token[0];

$cookie = preg_split("/Set-Cookie: /",$resultc);
$cookie = preg_split("/;/",$cookie[1]);
print $cookie[0];

$ch = curl_init("https://www.sbb.ch/ticketshop/b2c/artikelspezSAGeneric.do");                                                                      
curl_setopt($ch, CURLOPT_HEADER, true);
curl_setopt($ch, CURLOPT_POST, true);
curl_setopt($ch, CURLOPT_POSTFIELDS, "org.apache.struts.taglib.html.TOKEN=".$token[0]."&artikelspez.abgang.name=Aarau&artikelspez.bestimmung.name=Basel+SBB&artikelspez.via%5B0%5D.name=&artikelspez.reiseDatum.datumViewDDMMYYYY_E=04.12.2012+%28Tu%29&method%3Acont=Next");		                                                               
curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
curl_setopt($ch, COOKIE, $cookie[0].";"."id=109.58.54.33-4287147520.30263505:lv=1353603613636:ss=1353603254703");
curl_setopt($ch, CURLOPT_SSL_VERIFYPEER, false);
$resultc = curl_exec($ch);

//print $resultc;
//action	getSparbillettAngebote
//value	ht-14:00
//curl --cookie cookies.txt --data "org.apache.struts.taglib.html.TOKEN=beaa264b50bcf283272786317ff76220&reiseBildung.klasseString=KLASSE_2&reiseBildung.fahrartString=EINFACH&reiseBildung.reisende%5B0%5D.vorname=Martin&reiseBildung.reisende%5B0%5D.nachname=Thuresson&reiseBildung.reisende%5B0%5D.geburtsdatum=23.03.1983&reiseBildung.reisende%5B0%5D.ermaessigungValue=0&method%3Acont=Next" https://www.sbb.ch/ticketshop/b2c/angebotReisende.do

?>

