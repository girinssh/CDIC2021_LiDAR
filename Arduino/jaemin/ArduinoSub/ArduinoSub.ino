
#include "StepM.h"
#include <SoftwareSerial.h>

SoftwareSerial mainArduino(2, 3);
const int endstopPin1 = 6;
const int endstopPin2 = 7;
const int endstopPin3 = 8;


int step_pin[] = {A0, A1, A2, A3, A4, A5};
int step_speed[] = {1000, 400};
bool endstop_status[] = {false, false, false};

StepM stepMoter = StepM(step_pin, step_speed);

void setup() {
  // put your setup code here, to run once:

  mainArduino.begin(115200);

  //motor initialize
  //stepMoter.init_endstop(endstop_status);

  //send to Main
  mainArduino.write("initialize success");
}

void loop() {
  // put your main code here, to run repeatedly:
  mainArduino.write("initialize success");
  stepMoter.stepMove();
}
