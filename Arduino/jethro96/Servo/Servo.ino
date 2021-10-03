#include <Servo.h>
Servo ser_MO[3];

void setup(){
  ser_MO[0].attach(A0);
  ser_MO[1].attach(A1);
  ser_MO[2].attach(A2);

  ser_MO[0].write(0);
  ser_MO[1].write(0);
  ser_MO[2].write(0); 

 
  ser_MO[0].write(92);
  ser_MO[1].write(98);
  ser_MO[2].write(89);  
 }

void loop(){

}
