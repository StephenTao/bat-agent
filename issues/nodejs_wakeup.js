var server =require("websocket").server
var http = require('http');
var libvirt = require('libvirt')
var hypervisor_object = new libvirt.Hypervisor("qemu:///system")

var socket=new server({
    httpServer:http.createServer(function(request,response){}).listen(3008,function(){console.log("Server is listening")})
});

hypervisor_object.connect(function(err){
    if(!err) {
        console.log("Virsh connected")
    } else {
        console.log("Virish connection failed");
    }
});

socket.on('request',function(request){
    var connection=request.accept(null,request.origin);
    console.log("connection accepted");

    connection.on('message',function(message){
        console.log("message received")
        var returnjson = {};
        //init ids list
        hypervisor_object.listActiveDomains(function(err, domainIds){
        	returnjson.active_ids = domainIds;
        	returnjson.last_active_ids = [];
        });

        var id = setInterval(function(){
        	hypervisor_object.listActiveDomains(function(err, domainIds){
        		returnjson.last_active_ids = returnjson.active_ids;
        		returnjson.active_ids = domainIds;
        	});
        	
        	// get need wakeup instance
			wakeup_ids = difference_array(returnjson.active_ids, returnjson.last_active_ids);
			console.log("active_ids:",returnjson.active_ids, "last_active_ids:",returnjson.last_active_ids,"wakeup_ids:", wakeup_ids);
			// send message to wakeup instance
        	for (var index in wakeup_ids) {
        		domainId = wakeup_ids[index];
        		hypervisor_object.lookupDomainById(parseInt(domainId), function(err, domain){
        			domain.getUUID(function(err, uuid){
        				returnjson.instance_id = uuid;
        				returnjson.time = new Date().getTime();
        				connection.sendUTF(JSON.stringify(returnjson))
        			});
        		});
        	}
        }, 1000);
    });
});


/*
parameter:
	a: array
	b: array
return:
	a - b
*/
function difference_array(a, b) {
    var clone = a.slice(0);
    for(var i = 0; i < b.length; i ++) {
        var temp = b[i];
        for(var j = 0; j < clone.length; j ++) {
           	if(temp === clone[j]) {
           		clone.splice(j,1);
           	}
       	}
   	}
   	return clone;
}