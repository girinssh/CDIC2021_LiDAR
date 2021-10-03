
#include "StepM.h"
#include <SoftwareSerial.h>

SoftwareSerial mySerial(10, 11);
const int endstopPin1 = 6;
const int endstopPin2 = 7;
const int endstopPin3 = 8;


int step_pin[] = {A0, A1, A2, A3, A4, A5};
int step_speed[] = {1000, 400};
bool endstop_status[] = {false, false, false};

StepM stepMoter = StepM(step_pin, step_speed);

String str = "initialize success";

void setup() {
  // put your setup code here, to run once:
  
  mySerial.begin(9600);

  //stepMoter.init_endstop(endstop_status);
  
  //send to Main
  while(!mySerial.available()){
    
  }
  for(int i = 0; i < str.length(); i++)
    mySerial.write(str.charAt(i));
}

void loop() {
  // put your main code here, to run repeatedly:
  stepMoter.stepMove();

}

//void is_on(){
//  String str = "";
//  if(mySerial.available()){
//    str = mySerial.readStringUntil('\n');
//    if(str.equals("on")){
//      for(int i = 0; i < str.length(); i++)
//        mySerial.write(str.charAt(i));
//    }
//  }
//}
