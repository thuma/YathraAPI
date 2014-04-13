<?php
header('Content-type: application/json; charset=UTF-8');
//error_reporting(E_ALL);
//ini_set('display_errors', 'on');
// Stationlist
$station['7400001'] =array('namn'=>'STOCKHOLM Cityterminalen','id'=>'1','type'=>'0');
$station['7400622'] =array('namn'=>'STOCKHOLM Cityterminalen','id'=>'1','type'=>'0');
$station['7400002'] =array('namn'=>'Göteborg Angered centrum hpl H','id'=>'443','type'=>'0');
$station['7400002'] =array('namn'=>'GÖTEBORG','id'=>'14','type'=>'1');
$station['7400003'] =array('namn'=>'MALMÖ','id'=>'36','type'=>'1');
$station['7400003'] =array('namn'=>'MALMÖ C','id'=>'5','type'=>'0');
$station['7400005'] =array('namn'=>'UPPSALA','id'=>'54','type'=>'1');
$station['7400007'] =array('namn'=>'NORRKÖPING Busstn','id'=>'133','type'=>'0');
$station['7411131'] =array('namn'=>'NORRKÖPING Busstn','id'=>'133','type'=>'0');
$station['7400008'] =array('namn'=>'Skövde Resec','id'=>'154','type'=>'0');
$station['7400009'] =array('namn'=>'LINKÖPING Fjärrbussterm','id'=>'110','type'=>'0');
$station['7400016'] =array('namn'=>'Vara Busstn','id'=>'189','type'=>'0');
$station['7400019'] =array('namn'=>'Leksand Jvstn','id'=>'253','type'=>'0');
$station['7400020'] =array('namn'=>'Kalmar Jvstn','id'=>'84','type'=>'0');
$station['7400023'] =array('namn'=>'Säffle Busstn','id'=>'165','type'=>'0');
$station['7400026'] =array('namn'=>'Säter Bstn Centrumgrill','id'=>'220','type'=>'0');
$station['7400030'] =array('namn'=>'Falun Jvstn','id'=>'50','type'=>'0');
$station['7400039'] =array('namn'=>'Mellerud Landsvägsgatan 36','id'=>'121','type'=>'0');
$station['7400043'] =array('namn'=>'Sollefteå Busstn Hpl A','id'=>'337','type'=>'0');
$station['7400049'] =array('namn'=>'SÖDERTÄLJE','id'=>'52','type'=>'1');
$station['7411151'] =array('namn'=>'Nyköping Busstn','id'=>'137','type'=>'0');
$station['7400055'] =array('namn'=>'Södertälje Syd','id'=>'167','type'=>'0');
$station['7400067'] =array('namn'=>'Läggesta jvstn','id'=>'494','type'=>'0');
$station['7400069'] =array('namn'=>'Ronneby Jvstn','id'=>'245','type'=>'0');
$station['7400072'] =array('namn'=>'Enköping jvstn','id'=>'47','type'=>'0');
$station['7400076'] =array('namn'=>'Åmål Jvstn','id'=>'202','type'=>'0');
$station['7400080'] =array('namn'=>'HALMSTAD','id'=>'15','type'=>'1');
$station['7400082'] =array('namn'=>'Västervik Resec','id'=>'198','type'=>'0');
$station['7400084'] =array('namn'=>'Eksjö Jvstn','id'=>'45','type'=>'0');
$station['7400090'] =array('namn'=>'JÖNKÖPING ReseC','id'=>'9','type'=>'0');
$station['7400099'] =array('namn'=>'VÄSTERÅS ReseCentrum','id'=>'199','type'=>'0');
$station['7400108'] =array('namn'=>'Strängnäs Busstn','id'=>'159','type'=>'0');
$station['7400120'] =array('namn'=>'Lund jvstn hpl O','id'=>'115','type'=>'0');
$station['7400130'] =array('namn'=>'Sundsvall Busstn Hpl O/P','id'=>'341','type'=>'0');
$station['7400133'] =array('namn'=>'ÖREBRO Resecentrum','id'=>'7','type'=>'0');
$station['7400140'] =array('namn'=>'Nässjö Jvstn','id'=>'138','type'=>'0');
$station['7400154'] =array('namn'=>'Söderhamn ReseC','id'=>'346','type'=>'0');
$station['7400158'] =array('namn'=>'Rättvik Resec','id'=>'145','type'=>'0');
$station['7400162'] =array('namn'=>'Grängesberg Jvstn','id'=>'58','type'=>'0');
$station['7400164'] =array('namn'=>'Skillingaryd Götaström,Preem','id'=>'493','type'=>'0');
$station['7400170'] =array('namn'=>'Eskilstuna Jvstn','id'=>'48','type'=>'0');
$station['7400176'] =array('namn'=>'Karlskoga Busstn','id'=>'87','type'=>'0');
$station['7400180'] =array('namn'=>'Mjölby Resec','id'=>'123','type'=>'0');
$station['7400187'] =array('namn'=>'HUDIKSVALL','id'=>'94','type'=>'1');
$station['7400191'] =array('namn'=>'Trollhättan Resec','id'=>'176','type'=>'0');
$station['7418557'] =array('namn'=>'Gävle Bro','id'=>'348','type'=>'0');
$station['7400210'] =array('namn'=>'Gävle bstn Hamntorget','id'=>'63','type'=>'0');
$station['7400214'] =array('namn'=>'Sala Jvstn','id'=>'146','type'=>'0');
$station['7400215'] =array('namn'=>'Mullsjö Busstn','id'=>'129','type'=>'0');
$station['7400216'] =array('namn'=>'Mariestad Busstn','id'=>'119','type'=>'0');
$station['7400220'] =array('namn'=>'Kramfors ReseC','id'=>'338','type'=>'0');
$station['7400222'] =array('namn'=>'Kristinehamn ReseC.','id'=>'97','type'=>'0');
$station['7400223'] =array('namn'=>'Gullspång Busstn','id'=>'62','type'=>'0');
$station['7400230'] =array('namn'=>'KARLSKRONA','id'=>'23','type'=>'1');
$station['7400233'] =array('namn'=>'Tanum Rasta','id'=>'286','type'=>'0');
$station['7400241'] =array('namn'=>'Vänersborg Jvstn','id'=>'194','type'=>'0');
$station['7400250'] =array('namn'=>'Växjö Jvstn','id'=>'273','type'=>'0');
$station['7400253'] =array('namn'=>'Härnösand ReseC','id'=>'339','type'=>'0');
$station['7400280'] =array('namn'=>'Kopparberg Jvstn','id'=>'94','type'=>'0');
$station['7400289'] =array('namn'=>'Smålandsstenar Jvstn','id'=>'156','type'=>'0');
$station['7400300'] =array('namn'=>'Borås ReseCentrum','id'=>'37','type'=>'0');
$station['7400302'] =array('namn'=>'Mora Jvstn','id'=>'126','type'=>'0');
$station['7400303'] =array('namn'=>'Djurås Jvstn','id'=>'44','type'=>'0');
$station['7400315'] =array('namn'=>'Mölndals bro hpl F','id'=>'448','type'=>'0');
$station['7400351'] =array('namn'=>'Vimmerby Resec','id'=>'192','type'=>'0');
$station['7400352'] =array('namn'=>'Finspång Jvstn','id'=>'53','type'=>'0');
$station['7400364'] =array('namn'=>'Årjäng Busstn','id'=>'204','type'=>'0');
$station['7400385'] =array('namn'=>'Tingsryd Busstn','id'=>'315','type'=>'0');
$station['7400419'] =array('namn'=>'Hällefors Busstn','id'=>'78','type'=>'0');
$station['7400554'] =array('namn'=>'Landvetter Flygplats','id'=>'321','type'=>'0');
$station['7400555'] =array('namn'=>'Ljungby Busstn','id'=>'112','type'=>'0');
$station['7400556'] =array('namn'=>'ARLANDA','id'=>'83','type'=>'1');
$station['7400561'] =array('namn'=>'Mönsterås Resec','id'=>'131','type'=>'0');
$station['7400573'] =array('namn'=>'Sälen by OKQ8','id'=>'260','type'=>'0');
$station['7400574'] =array('namn'=>'Grövelsjön STF turiststn','id'=>'419','type'=>'0');
$station['7400576'] =array('namn'=>'Söderköping Busstn','id'=>'166','type'=>'0');
$station['7400578'] =array('namn'=>'N:a Unnaryd','id'=>'132','type'=>'0');
$station['7400600'] =array('namn'=>'Tidaholm Busstn','id'=>'170','type'=>'0');
$station['7400611'] =array('namn'=>'Skara Busstn','id'=>'150','type'=>'0');
$station['7400624'] =array('namn'=>'Gislaved Busstn','id'=>'56','type'=>'0');
$station['7400625'] =array('namn'=>'Hyltebruk Jvstn','id'=>'77','type'=>'0');
$station['7400646'] =array('namn'=>'Sälen Hundfjället Hotellet','id'=>'266','type'=>'0');
$station['7400647'] =array('namn'=>'Idre Konsum','id'=>'416','type'=>'0');
$station['7400648'] =array('namn'=>'Sälen Lindvallen SnöCentret','id'=>'261','type'=>'0');
$station['7400656'] =array('namn'=>'Sälen Högfjällshotellet','id'=>'264','type'=>'0');
$station['7400657'] =array('namn'=>'Särna Konsum','id'=>'415','type'=>'0');
$station['7400660'] =array('namn'=>'Bålsta busstn','id'=>'495','type'=>'0');
$station['7400721'] =array('namn'=>'Södertälje, Torget vid kyrkan','id'=>'497','type'=>'0');
$station['7400792'] =array('namn'=>'Finnerödja E 20','id'=>'52','type'=>'0');
$station['7400796'] =array('namn'=>'Pålsboda','id'=>'216','type'=>'0');
$station['7400863'] =array('namn'=>'Idre Fjäll Centrum','id'=>'417','type'=>'0');
$station['7400907'] =array('namn'=>'Ankarsrum Hpl V40','id'=>'486','type'=>'0');
$station['7410955'] =array('namn'=>'LINKÖPING Fjärrbussterm','id'=>'110','type'=>'0');
$station['7400982'] =array('namn'=>'Brålanda Rv 45','id'=>'42','type'=>'0');
$station['7401013'] =array('namn'=>'Astrid Lindgrens värld','id'=>'134','type'=>'1');
$station['7401230'] =array('namn'=>'Liseberg stn','id'=>'331','type'=>'0');
$station['7401350'] =array('namn'=>'Transtrand Stinas Kiosk','id'=>'259','type'=>'0');
$station['7401579'] =array('namn'=>'FALKENBERG','id'=>'124','type'=>'1');
$station['7401583'] =array('namn'=>'Nordmaling Resecentrum','id'=>'390','type'=>'0');
$station['7401587'] =array('namn'=>'Malmö Triangeln','id'=>'461','type'=>'0');
$station['7404180'] =array('namn'=>'Oskarström Bronsgatan','id'=>'141','type'=>'0');
$station['7407178'] =array('namn'=>'UPPSALA Stationsgatan hpl E3/E4','id'=>'6','type'=>'0');
$station['7407455'] =array('namn'=>'Uppsala Flogsta','id'=>'184','type'=>'0');
$station['7407480'] =array('namn'=>'Uppsala Ekonomikum','id'=>'269','type'=>'0');
$station['7407481'] =array('namn'=>'Uppsala Studentstaden','id'=>'254','type'=>'0');
$station['7408380'] =array('namn'=>'Hudiksvall Statoil E4 Glada Hudik','id'=>'344','type'=>'0');
$station['7408428'] =array('namn'=>'Uppsala Business Park','id'=>'309','type'=>'0');
$station['7410288'] =array('namn'=>'Lammhult Statoil','id'=>'326','type'=>'0');
$station['7410300'] =array('namn'=>'Eskilstuna Busstn hpl A','id'=>'498','type'=>'0');
$station['7410325'] =array('namn'=>'Filipstad Busstn','id'=>'51','type'=>'0');
$station['7410553'] =array('namn'=>'Hasslerör Motellet','id'=>'67','type'=>'0');
$station['7410586'] =array('namn'=>'Hjortkvarn','id'=>'217','type'=>'0');
$station['7410589'] =array('namn'=>'Hjulsjö Rv 63','id'=>'72','type'=>'0');
$station['7410657'] =array('namn'=>'Hällestad K:a','id'=>'79','type'=>'0');
$station['7410760'] =array('namn'=>'KARLSTAD Busstn','id'=>'8','type'=>'0');
$station['7410921'] =array('namn'=>'Södertälje stadshus','id'=>'388','type'=>'0');
$station['7411369'] =array('namn'=>'Sjötorp Rv 26','id'=>'149','type'=>'0');
$station['7412993'] =array('namn'=>'Borlänge Resecentrum','id'=>'36','type'=>'0');
$station['7413212'] =array('namn'=>'Gamleby Flisvägen','id'=>'389','type'=>'0');
$station['7414099'] =array('namn'=>'Blankaholm vsk E 22','id'=>'34','type'=>'0');
$station['7414166'] =array('namn'=>'Fårbo vsk E 22','id'=>'55','type'=>'0');
$station['7414286'] =array('namn'=>'Misterhult vsk E 22','id'=>'122','type'=>'0');
$station['7414410'] =array('namn'=>'Verkebäcksbron','id'=>'190','type'=>'0');
$station['7416443'] =array('namn'=>'Otterbäcken Rv 26','id'=>'142','type'=>'0');
$station['7416450'] =array('namn'=>'Lyrestad E20','id'=>'238','type'=>'0');
$station['7416456'] =array('namn'=>'Lövåsen Rv 26','id'=>'224','type'=>'0');
$station['7417388'] =array('namn'=>'Landskrona Statoil Pumpgatan','id'=>'449','type'=>'0');
$station['7418243'] =array('namn'=>'Ljungby Motell E4','id'=>'398','type'=>'0');
$station['7418262'] =array('namn'=>'Skultorp Trafikplats','id'=>'256','type'=>'0');
$station['7418293'] =array('namn'=>'Uppsala Willy:s Hj. Brantingsg.','id'=>'402','type'=>'0');
$station['7418588'] =array('namn'=>'Valdemarsvik E22','id'=>'255','type'=>'0');
$station['7419793'] =array('namn'=>'Kungsberget inkl. en dags liftkort','id'=>'434','type'=>'0');
$station['7420075'] =array('namn'=>'Molkom Graninge','id'=>'368','type'=>'0');
$station['7420238'] =array('namn'=>'Stöpen Rv 26','id'=>'162','type'=>'0');
$station['7420261'] =array('namn'=>'Mullsjö Bosebyleden','id'=>'275','type'=>'0');
$station['7420392'] =array('namn'=>'Oskarshamn Resec','id'=>'140','type'=>'0');
$station['7420461'] =array('namn'=>'Umeå Busstn','id'=>'334','type'=>'0');
$station['7420483'] =array('namn'=>'GÖTEBORG Nils E. Term','id'=>'4','type'=>'0');
$station['7420510'] =array('namn'=>'Karlskrona Kungsplan','id'=>'244','type'=>'0');
$station['7420671'] =array('namn'=>'Arlanda Term 2 och 3','id'=>'362','type'=>'0');
$station['7420862'] =array('namn'=>'Kläppen receptionen','id'=>'437','type'=>'0');
$station['7420990'] =array('namn'=>'Huskvarna Esplanaden, rondellen','id'=>'489','type'=>'0');
$station['7421101'] =array('namn'=>'Laxå E 20','id'=>'102','type'=>'0');
$station['7421110'] =array('namn'=>'Örebro Våghustorget','id'=>'211','type'=>'0');
$station['7421788'] =array('namn'=>'Mariannelund Torget','id'=>'118','type'=>'0');
$station['7421813'] =array('namn'=>'Ludvika Resec','id'=>'114','type'=>'0');
$station['7423131'] =array('namn'=>'Gnarp Statoil','id'=>'370','type'=>'0');
$station['7423136'] =array('namn'=>'Tönnebro Värdshus','id'=>'347','type'=>'0');
$station['7423176'] =array('namn'=>'Götene Rasta','id'=>'64','type'=>'0');
$station['7423232'] =array('namn'=>'Karlstad Universitet','id'=>'90','type'=>'0');
$station['7423239'] =array('namn'=>'Ulricehamn Brunnsnäs','id'=>'182','type'=>'0');
$station['7423242'] =array('namn'=>'Hestra Rv 26','id'=>'71','type'=>'0');
$station['7423247'] =array('namn'=>'Värnamo ICA Kvantum','id'=>'196','type'=>'0');
$station['7423252'] =array('namn'=>'Slättäng Rv 47/26','id'=>'155','type'=>'0');
$station['7423275'] =array('namn'=>'Halmstad EuroStop','id'=>'227','type'=>'0');
$station['7423350'] =array('namn'=>'NORJE SWEDEN ROCK','id'=>'80','type'=>'1');
$station['7423840'] =array('namn'=>'Umeå sjukhus hpl C','id'=>'394','type'=>'0');
$station['7424273'] =array('namn'=>'Sälen HögfjällsCenter','id'=>'287','type'=>'0');
$station['7424484'] =array('namn'=>'Örebro Sörbyängsvägen','id'=>'210','type'=>'0');
$station['7424999'] =array('namn'=>'Knöstad E18','id'=>'363','type'=>'0');
$station['7425037'] =array('namn'=>'Töcksfors Sandviksvägen','id'=>'221','type'=>'0');
$station['7425491'] =array('namn'=>'Gränna Galgen','id'=>'242','type'=>'0');
$station['7425508'] =array('namn'=>'Jönköping Ekhagen Centrun','id'=>'490','type'=>'0');
$station['7425654'] =array('namn'=>'Göteborg Liseberg stn','id'=>'123','type'=>'1');
$station['7426076'] =array('namn'=>'Hova Turistbyrån','id'=>'75','type'=>'0');
$station['7430047'] =array('namn'=>'Hamburg','id'=>'278','type'=>'0');
$station['7430075'] =array('namn'=>'Vårgårda Rasta','id'=>'440','type'=>'0');
$station['7432125'] =array('namn'=>'Karlskrona Verkö färjeterminal','id'=>'403','type'=>'0');
$station['7433206'] =array('namn'=>'Arlanda Term 4','id'=>'361','type'=>'0');
$station['7433862'] =array('namn'=>'LJUNGBY','id'=>'32','type'=>'1');
$station['7433988'] =array('namn'=>'Örnsköldsvik ReseC','id'=>'335','type'=>'0');
$station['7434802'] =array('namn'=>'Växjö Universitet','id'=>'274','type'=>'0');
$station['7441158'] =array('namn'=>'Rostock Scandlines Terminal','id'=>'298','type'=>'0');
$station['7443310'] =array('namn'=>'Arlanda Term. 5','id'=>'320','type'=>'0');
$station['7443449'] =array('namn'=>'Halmstad regionbussterm.','id'=>'408','type'=>'0');
$station['7445443'] =array('namn'=>'Umeå Ålidhem Tvistevägen','id'=>'333','type'=>'0');
$station['7446073'] =array('namn'=>'Karolinska Institutet','id'=>'316','type'=>'0');
$station['7447579'] =array('namn'=>'Mannheim','id'=>'380','type'=>'0');
$station['7447943'] =array('namn'=>'Haag','id'=>'381','type'=>'0');
$station['7449109'] =array('namn'=>'Storsätra Fjällhotellet','id'=>'418','type'=>'0');
$station['7449131'] =array('namn'=>'Grums Nyängen RASTA','id'=>'412','type'=>'0');
$station['7450840'] =array('namn'=>'Kungsberget Centrumhuset','id'=>'433','type'=>'0');
$station['7452904'] =array('namn'=>'Ödeshög Rasta','id'=>'441','type'=>'0');
$station['7453588'] =array('namn'=>'Ullared Gekås','id'=>'313','type'=>'0');
$station['7459033'] =array('namn'=>'Ängelholm E6 Shell/McDonald\'s','id'=>'455','type'=>'0');
$station['7459149'] =array('namn'=>'Göteborg Brunnsbotorget hpl D','id'=>'445','type'=>'0');
$station['7460979'] =array('namn'=>'Alingsås Götaplan','id'=>'450','type'=>'0');
$station['7468306'] =array('namn'=>'Putte i Parken','id'=>'130','type'=>'1');
$station['7625036'] =array('namn'=>'Sarpsborg Quality Hotel','id'=>'222','type'=>'0');
$station['7690001'] =array('namn'=>'OSLO Gallerian','id'=>'3','type'=>'0');
$station['8010100'] =array('namn'=>'Berlin ZOB','id'=>'279','type'=>'0');
$station['8624917'] =array('namn'=>'KÖPENHAMN Ingerslevsgade DGI','id'=>'290','type'=>'0');


// Get value from cmdline;
if(isset($argv[1])){
	parse_str($argv[1], $_GET);
}

/*
#################### Request data ###################
Key:							Data:		Example:		Comment:			
departureTime 		[Required]	[HH:MM]		[06:30]
arrivalTime			[Optional]	[HH:MM]		[10:00]			Use if two trains have the same deparature time but different arrival times.
date				[Required]	[YYYY-MM-DD]	[2013-01-15]
from				[Required]	[ID]		[7000002]
to					[Required]	[ID]		[7000001]
travelerAge			[Optional]	[NN]		[29]
promotionCode		[Optional]	[String]	[MAX295]
travelerIsStudent	[Optional]	[Any]		[1]				(Any data is counted as true including 0 and false)

#################### Respone data (To be decided:)###################
Key:				Data:		Example:
departureTime 		[HH:MM]		[06:30]
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


//Check that station is selected.
if(isset($_GET["from"]) == FALSE OR isset($_GET["to"])==FALSE){
	die('{"error":"No station selected."}');
}

if(isset($station[$_GET["from"]]) == FALSE OR isset($station[$_GET["to"]])==FALSE){
	die('{"error":"Station not in list"}');
}

//Check that date and time is given.
if(isset($_GET["date"]) == FALSE OR isset($_GET["departureTime"])==FALSE){
	die('{"error":"Time or date is missing."}');
}

$Adult = 1;
$Child = 0;
$Youth = 0;
$Student = 0;
$Pensioner = 0;
$Pet = 0;

$url = 'http://www.swebus.se/Express/Sokresultat/'
.'?from='.$station[$_GET["from"]]['id']
.'&fromtype=BusStop'
.'&to='.$station[$_GET["to"]]['id']
.'&totype=BusStop'
.'&away='.$_GET["date"]
.'&Adult='.$Adult
.'&Child='.$Child
.'&Youth='.$Youth
.'&Student='.$Student
.'&Pensioner='.$Pensioner
.'&Pet='.$Pet
.'&campaignCode='
.'&id=1101'
.'&epslanguage=sv-SE';

$resordom = new DOMDocument;
@$resordom->loadHTML('<?xml encoding="UTF-8">'.file_get_contents($url));

$table = $resordom->getElementsByTagName('table');

$trippdata = array();
for($i = 1; $i < $table->length; $i++){
	foreach($table->item($i)->getElementsByTagName('th') as $coll){
		$trippdata[$i][trim($coll->getAttribute('class'))] = trim($coll->nodeValue);
		if($coll->getAttribute('class')=='Price1'){
			if($coll->getElementsByTagName('input')->length > 0){
				$trippdata[$i][trim($coll->getAttribute('class'))] = $coll->getElementsByTagName('input')->item(0)->getAttribute('value');
				}
		}
		elseif($coll->getAttribute('class')=='Price2'){
			if($coll->getElementsByTagName('input')->length > 0){
				$trippdata[$i][trim($coll->getAttribute('class'))] = $coll->getElementsByTagName('input')->item(0)->getAttribute('value');
				}
		}
		elseif($coll->getAttribute('class')=='Price3'){
			if($coll->getElementsByTagName('input')->length > 0){
				$trippdata[$i][trim($coll->getAttribute('class'))] = $coll->getElementsByTagName('input')->item(0)->getAttribute('value');
			}
		}
	}
}

$final = false;
foreach($trippdata as $trip){
	if(isset($_GET['arrivalTime']) == FALSE){
		if($trip['Departure'] == $_GET['departureTime']){
			$final = $trip;
			break;
		}
	}
	if(isset($_GET['arrivalTime'])){
		if($trip['Departure'] == $_GET['departureTime'] AND $trip['Arrival'] == $_GET['arrivalTime']){
			$final = $trip;
			break;
		}
	}
}

if($final==false){
	die('{"error":"Triptime not found"}');
}

$result = array(
"departureTime" => $_GET["departureTime"],
"arrivalTime" => $final['Arrival'],
"date" => $_GET["date"],
"from" => $_GET["from"],
"to" => $_GET["to"],
"price" => preg_replace("/ SEK/","", $final["Price1"]),
"currency" => "SEK",
"validPrice" => true,
"url" => $url,
"sellername" => "SWEBUS"
);

print json_encode($result);

 ?>