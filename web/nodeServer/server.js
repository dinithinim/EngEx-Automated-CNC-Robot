const { SerialPort } = require('serialport');
const { ReadlineParser } = require('@serialport/parser-readline');
var WebSocketServer = require('ws').Server;

var mqtt = require('mqtt')
var client  = mqtt.connect('mqtt://test.mosquitto.org')

const TOPIC_COM2WEB = 'engex/com2web';
const TOPIC_WEB2COM = 'engex/web2com';



// USB Port selection
console.log("Available Ports: ");
SerialPort.list().then((ports) => {
   ports.forEach(function(port) {
      console.log("\t" + (port.path || port.comName));
   });
}).catch((err) => {
   console.log('Error listing ports:', err);
});
console.log("\n");

if(process.argv[2]==""){
   console.log("Invalid arguments. Type it as, \nnode server.js COMx");
}

// Need to write a validator to check this is available
var portName = process.argv[2];
var myPort;
var parser;

function startPort(pathName) {
   portName = pathName;
   myPort = new SerialPort({ path: portName, baudRate: 115200 });
   parser = myPort.pipe(new ReadlineParser({ delimiter: '\n' }));

   // these are the definitions for the serial events:
   myPort.on('open', showPortOpen);
   myPort.on('close', showPortClose);
   myPort.on('error', showError);
   parser.on('data', readSerialData);
}

if (!portName) {
   console.log('No serial port provided as argument, selecting first available port...');
   SerialPort.list().then((ports) => {
      if (!ports || ports.length === 0) {
         console.error('No serial ports found. Provide a port path as argument: node server.js /dev/tty.usbserial-XXXX');
         process.exit(1);
      }
      const first = ports[0];
      const candidate = first.path || first.comName;
      console.log('Using port: ' + candidate);
      startPort(candidate);
   }).catch((err) => {
      console.error('Error listing ports:', err);
      process.exit(1);
   });
} else {
   startPort(portName);
}


// --------------------------------------------------------

client.on('connect', function () {
   client.subscribe(TOPIC_WEB2COM, function (err) {
      if (!err) {
         client.publish(TOPIC_WEB2COM, 'MQTT connection: success');
      }
   })
})

client.on('message', function (topic, message) {
   if(topic==TOPIC_WEB2COM){
      console.log("-> "+message.toString())
      sendToSerial(message.toString() + '\n');

   }
});






// ------------------------ Serial event functions:
function showPortOpen() {
   console.log('>> port open. Data rate: ' + myPort.baudRate);
}

function readSerialData(data) {
   console.log("<< " + data);
   client.publish(TOPIC_COM2WEB, data);
}


function showPortClose() {
   console.log('>> port closed.');
}
// this is called when the serial port has an error:
function showError(error) {
   console.log('>> port error: ' + error);
}

function sendToSerial(data) {
   console.log(">> sending to serial: " + data);
   myPort.write(data);
}