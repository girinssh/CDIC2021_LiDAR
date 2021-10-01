#ifndef Stepper_h
#define Stepper_h

#include <Arduino.h>
#include <AccelStepper.h>

class StepM
{
private:
  AccelStepper stepper1;
  AccelStepper stepper2;
  AccelStepper stepper3;

public:
  StepM(int StepMinfo[6], int StepMSpeed[2]);  
  
  // StepMinf[6]={step1_StepPIN, step1_DirPIN, ...} 
  // StepMSpeed[2]={MaxSpeed, speed(steps per second = 200[steps/rotation]*RPM /60[seconds/minute])}
  
  void StepMmove();
  
  
};

#endif
