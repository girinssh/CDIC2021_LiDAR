#ifndef SerMo_h
#define SerMo_h

#include <Arduino.h>
#include <Servo.h>

class SerMo
{
  private:
  Servo ser_MO[3];
        
  public: 
  SerMo(int ServoMotorInfo[3]);  //핀 번호, 연결
  void  SerMotorMove(float angle);     //실행함수. 각도에 맞게 끔 이동
};

#endif
