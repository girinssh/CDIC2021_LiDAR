
#include "StepM.h"
#include <SoftwareSerial.h>

SoftwareSerial mySerial(10, 11);
const int endstopPin1 = 4;
const int endstopPin2 = 5;
const int endstopPin3 = 6;


int step_pin[] = {A0, A1, A2, A3, A4, A5};
int step_speed[] = {1000, 400};

StepM stepMoter = StepM(step_pin, step_speed);

String str = "initialize success";

void setup() {
  // put your setup code here, to run once:
  
  mySerial.begin(9600);
  //Serial.begin(9600);

  String serv_data;
  //send to Main
  while(!mySerial.available()){  
  }
  while(mySerial.available())
    serv_data = mySerial.readStringUntil("\n");

  initializing();          
  //Serial.println(serv_data);`
   //stepMoter.init_endstop(endstop_status);
  
  for(int i = 0; i < str.length(); i++)
    mySerial.write(str.charAt(i));
    
  //Serial.println(str);

  
}

void loop() {
  // put your main code here, to run repeatedly:
  stepMoter.StepMmove();
  is_on();
}

void is_on(){
  String temp = "";
  if(mySerial.available()){
    temp = mySerial.readStringUntil("\n");
    temp.trim();
    initializing();
   // Serial.println(str);
    //Serial.println(temp);
    for(int i = 0; i < str.length(); i++)
      mySerial.write(str.charAt(i));
    
  }
  while(mySerial.available())
    mySerial.read();
}

void initializing(){
  while(true){
    if(digitalRead(endstopPin1) == HIGH){
      if(digitalRead(endstopPin2) == HIGH){
        if(digitalRead(endstopPin3) == HIGH){
          break; 
        }
        else{
       //   Serial.println("3 run");
          stepMoter.stepMmove3();
        }
      }
      else{
    //    Serial.println("2, 3 run");
        stepMoter.stepMmove2();
        stepMoter.stepMmove3();
      }
    }
    else{
   //   Serial.println("1, 2, 3 run");
      stepMoter.StepMmove();
    }
  }
}
