#include "mpu9250.h"
#include<Wire.h>
const int MPU_ADDR = 0x68;

Mpu9250 mpu(&Wire, 0x68);
double AcX, AcY, AcZ, Tmp, GyX, GyY, GyZ, magX, magY, magZ; 
double roll, pitch, yaw;
double angleAcX, angleAcY, angleAcZ;
double angleGyX, angleGyY, angleGyZ;
double angleFiX, angleFiY, angleFiZ;

const double RADIAN_TO_DEGREE = 180 / 3.14159;  
const double DEG_PER_SEC = 32767 / 500;    // 1초에 회전하는 각도
const double ALPHA = 1 / (1 + 0.05);
// GyX, GyY, GyZ 값의 범위 : -32768 ~ +32767 (16비트 정수범위)

unsigned long now = 0;   // 현재 시간 저장용 변수
unsigned long past = 0;  // 이전 시간 저장용 변수
double dt = 0;           // 한 사이클 동안 걸린 시간 변수 
double during = 0;
double storeTime = 0;

double averAcX, averAcY, averAcZ;
double averGyX, averGyY, averGyZ;

int number = 0;

class MpuController{
  double roll;
  double pitch;
  


  private:
  double AcX, AcY, AcZ, Tmp, GyX, GyY, GyZ, magX, magY, magZ;
  const double RADIAN_TO_DEGREE = 180 / 3.14159;  
  const double DEG_PER_SEC = 32767 / 500;    // 1초에 회전하는 각도
  const double ALPHA = 1 / (1 + 0.05);
  unsigned long now = 0;   // 현재 시간 저장용 변수
  unsigned long past = 0;  // 이전 시간 저장용 변수
  double dt = 0;           // 한 사이클 동안 걸린 시간 변수 
  double during = 0;
  double storeTime = 0;

  
  double getRoll(){
    return roll;  
  }
  double getpitch(){
    return pitch;
  }
  
  void run(){
    caliSensor();
    
  }

  void caliSensor() {
    double sumAcX = 0 , sumAcY = 0, sumAcZ = 0;
    double sumGyX = 0 , sumGyY = 0, sumGyZ = 0;
    getData();
    for (int i=0;i<10;i++) {
      getData();
      sumAcX+=AcX;  sumAcY+=AcY,  sumAcZ+=AcZ;
      sumGyX+=GyX;  sumGyY+=GyY;  sumGyZ+=GyZ;
    }
    averAcX=sumAcX/10;  averAcY=sumAcY/10,  averAcZ=sumAcZ/10;  
    averGyX=sumGyX/10;  averGyY=sumGyY/10;  averGyZ=sumGyZ/10;
  }

  void getData() {
    AcX = mpu.accel_x_mps2();
    AcY = mpu.accel_y_mps2();
    AcZ = mpu.accel_z_mps2();
    
    GyX = mpu.gyro_x_radps();
    GyY = mpu.gyro_y_radps();
    GyZ = mpu.gyro_z_radps();
  
    magX = mpu.mag_x_ut();
    magY = mpu.mag_y_ut();
    magZ = mpu.mag_z_ut();
  }

  void getDT() {
    now = millis();   
    during = now-past;
    
    dt = (double)during / 1000.0;  
    past = now;
  }


  void reset(){
    //Serial.print("reset called\t");
    //Serial.println(number);
    caliSensor();
    storeTime = 0;
    number =0;
  }

  void calc_angle(){
    if (mpu.Read()) {
      getData(); 
      getDT();
      
      angleAcX = atan(AcY / sqrt(pow(AcX, 2) + pow(AcZ, 2))) * RADIAN_TO_DEGREE;
      angleAcY = atan(-AcX / sqrt(pow(AcY, 2) + pow(AcZ, 2))) * RADIAN_TO_DEGREE;
  
      angleGyX += ((GyX - averGyX) / DEG_PER_SEC) * dt;  
      angleGyY += ((GyY - averGyY) / DEG_PER_SEC) * dt;
      angleGyZ += ((GyZ - averGyZ) / DEG_PER_SEC) * dt;
      
      double angleTmpX = angleFiX + angleGyX * dt;
      double angleTmpY = angleFiY + angleGyY * dt;
      double angleTmpZ = angleFiZ + angleGyZ * dt;
      
      angleFiX = ALPHA * angleTmpX + (1.0 - ALPHA) * angleAcX; //roll
      angleFiY = ALPHA * angleTmpY + (1.0 - ALPHA) * angleAcY; //pitch
  
      double tempX = angleFiX / RADIAN_TO_DEGREE;
      double tempY = angleFiY / RADIAN_TO_DEGREE;
  
      double Yh = (magY * cos(tempY)) - (magZ * sin(tempY));
      double Xh = (magX * cos(tempX))+(magY * sin(tempY)*sin(tempX)) + (magZ * cos(tempY) * sin(tempX));
      double magYaw = atan2(Yh, Xh) * RADIAN_TO_DEGREE;
      
      angleFiZ = ALPHA * angleTmpZ + (1.0 - ALPHA) * magYaw;   
    }
  }
  
}

void setup() {
  /* Serial to display data */
  Serial.begin(115200);
  caliSensor();
  if (!mpu.Begin()) {
    Serial.println("IMU initialization unsuccessful");
    while(1) {}
  }
  delay(2000);
  calc_angle();
}

void loop() {
  /* Read the sensor */
  calc_angle();

  storeTime += during;
  
  if(storeTime >= 1000.0)
    reset();
    
  number++;

}
