#include "StepM.h"

  StepM::StepM(int StepMinfo[6], int StepMSpeed[2])
{
  stepper1 = AccelStepper(AccelStepper ::DRIVER, StepMinfo[0],StepMinfo[1]);
  stepper2 = AccelStepper(AccelStepper ::DRIVER, StepMinfo[2],StepMinfo[3]);
  stepper3 = AccelStepper(AccelStepper ::DRIVER, StepMinfo[4],StepMinfo[5]);// Defaults to AccelStepper::DRIVER, STEP_PIN, Dir_PIN

 
  stepper1.setMaxSpeed(StepMSpeed[0]);
  stepper1.setSpeed(StepMSpeed[1]); //steps per second = 200[steps/rotation]*RPM /60[seconds/minute]
  stepper2.setMaxSpeed(StepMSpeed[0]);
  stepper2.setSpeed(StepMSpeed[1]);  //steps per second = 200[steps/rotation]*RPM /60[seconds/minute]
  stepper3.setMaxSpeed(StepMSpeed[0]);
  stepper3.setSpeed(StepMSpeed[1]); //steps per second = 200[steps/rotation]*RPM /60[seconds/minute]


}

void StepM:: stepMove(){
  stepper1.runSpeed();
  stepper2.runSpeed();
  stepper3.runSpeed();
}


void StepM:: init_endstop(bool endStop[]){
  while(true){
    if(endStop[0] == 1){
      if(endStop[1] == 1){
        if(endStop[2] == 1){
          break; 
        }
        else{
          stepper3.runSpeed();
        }
      }
      else{
        stepper2.runSpeed();
        stepper3.runSpeed();
      }
    }
    else{
      stepper1.runSpeed();
      stepper2.runSpeed();
      stepper3.runSpeed();
    }
  }
}
