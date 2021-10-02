#include "SerMo.h"

SerMo :: SerMo(int ServoMotorInfo[3])
{  
  ser_MO[0].attach(ServoMotorInfo[0]);
  ser_MO[1].attach(ServoMotorInfo[1]);
  ser_MO[2].attach(ServoMotorInfo[2]); // 핀 번호 입력

  ser_MO[0].write(0);
  ser_MO[1].write(0);
  ser_MO[2].write(0);   /// default 0도
}





void SerMo:: SerMotorMove(float angle)
{
  ser_MO[0].write(angle);
  ser_MO[1].write(angle);
  ser_MO[2].write(angle);  
}
