#include "SerMo.h"

int ServoMotorInfoArray[]= { A0, A1, A2};
int ServoAngle = 90 ;

SerMo motorController = SerMo(ServoMotorInfoArray);

 void setup() {
   
 }

 void loop(){
 
  motorController.SerMotorMove(ServoAngle);
 }
