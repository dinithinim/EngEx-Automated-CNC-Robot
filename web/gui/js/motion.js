function jog(x, y, z){
   jog(x, y, z, 0, 0);
}
function jog(x, y, z, a){
   jog(x, y, z, a  , 0);
}
function jog(x, y, z, a, b){
   var amount = $("#stepSize").children("option:selected").val();
   var feed = $("#feedSize").children("option:selected").val();

   console.log(" " + amount);

   if(x==0 && y==0 && z==0 && a==0 && b==0){
      sendCommand("\u0085");
   }else{
      sendCommand("$J=G91 X" + (1*x*amount) +"Y"+ (1*y*amount) + "Z" + (1*z*amount) + "F" + feed);
      //+ "A" + (1*a*amount) + "B" + (1*b*amount)
   }
}

var delayInMilliseconds = 2000;

//Move to a certain coordinate on X,Y,Z 3D plane
function gotToCoordinate(x,y,z) {

   console.log("x:" + x + " y:"+y + " z:" + z );

   //Move to home
   sendCommand("G0 Z0\n");

   //Move on X,Y plane after a delay
   setTimeout(function() {
      sendCommand("G1 x"+x+" y"+y + " F1000");
      //Move on Z axis after a delay
      setTimeout(function() {
         sendCommand("G1 z"+z);
      }, 5000);

   }, 3000);



}
