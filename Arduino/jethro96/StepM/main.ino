#include "StepM.h"


int StepMInfoArray[]={A7,A8,A9,A10,A11,A12};
int StepMSpeedArray[]={1000, 400};

StepM motorController=  StepM(StepMInfoArray,StepMSpeedArray);

void setup(){
  
}

void loop(){
  motorController.StepMmove();
}
