var system = require('system');
if (system.args.length === 1) {
    console.log('No args: from to date deparatureTime arrivalTime');
	phantom.exit();
}

var args = system.args[1];
var args = args + "," + system.args[2];
var args = args + "," + system.args[3];
var args = args + "," + system.args[4];
var args = args + "," + system.args[5];

var page = require('webpage').create();
page.viewportSize = { width: 1024, height: 768 };

page.settings.loadImages = false;
page.open('http://www.dsb.dk/salg/netbutikken/', function (status) {
    if (status !== 'success') {
        console.log('Unable to access the network!');
    } else {

			title = page.evaluate(function(){return document.title;});	
			//console.log("load done OK: ->"+title+"<-");
			if (title == "SoegeBoks"){	
				
				var xy = page.evaluate(function(opts) {
					var args = opts.split(",");
					forma = document.forms[0];
					forma.elements["soegebokslayout:fraDestination:border:destinationInput"].value = args[0];
					forma.elements["soegebokslayout:tilDestination:border:destinationInput"].value = args[1];
					forma.elements["soegebokslayout:tidErrorBorder:fraTidPanel:tidBorder:datoValgPanel:datePicker" ].value = args[2];			
					forma.elements["soegebokslayout:tidErrorBorder:fraTidPanel:tidBorder:tidTxt"].value = args[3];
					var elm = document.getElementsByName("soegebokslayout:soeg")[0];
					var evnt = elm["onclick"];
					if (typeof(evnt) == "function") {
						evnt.call(elm);
					}
					return;
				},args);
			}
			else{
			
				checkloop(); 

			}
    }
	
});

function checkloop () {         
				setTimeout(function () {
					var pagedata = page.evaluate(function() {return document.body.innerHTML;});
					if (pagedata.search("Afg.")<1){
						checkloop();
					}
					else{
					
						data = page.evaluate(function(opts) { 
						var args = opts.split(",");
						var svar = "";
						travels = document.getElementById('rejseResultatWrapper');
						lista = travels.getElementsByTagName("div");
						for (var i = 0; i < lista.length; i++){
							if(lista[i].getAttribute('style')=="padding-left:5px;"){
								var price = "";
								var dela = lista[i].innerHTML.split("Afg.</div>");
								var delb = dela[1].split("</div>");
								var delc = delb[0].split("<div>")
								var deparatureTime = delc[1];
								
								var dela = lista[i].innerHTML.split("Ank.</div>");
								var delb = dela[1].split("</div>");
								var delc = delb[0].split("<div>")
								var arrivalTime = delc[1];
								
								var dela = lista[i].innerHTML.split("<span>");
								for (var j = 0; j < dela.length; j++)
									{
									var delb = dela[j].split("<");
									var pris = parseInt(delb[0].split(",")[0]);
									if (pris>1){
											price = pris;
											j = dela.length;
										}
									}
									
								if ((deparatureTime==args[3]) && (arrivalTime=args[4])){
								svar = '{"deparatureTime":"' + deparatureTime + 
										'","arrivalTime":"' + arrivalTime + 
										'","price":"' + price + ' DKK"}';
								}			
							}
						}
						return svar;
						}, args);
						
						console.log(data);
						phantom.exit();
					}
					
				   }, 1000)
				}