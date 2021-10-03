#include <Adafruit_NeoPixel.h>
#include "setup.h"
#include "loop.h"
#include "SerMo.h"
#include <SoftwareSerial.h>

SoftwareSerial subArduino(10, 11); 
SoftwareSerial rasberry(4, 5);


#define GPSBAUD 115200
int servo_pin[] = {A0, A1, A2};
int step_pin[] = {A7, A8, A9, A10, A11, A12};
int step_speed[] = {1000, 400};

//Gps gps(GPSBAUD);
SerMo servo_moter = SerMo(servo_pin);


int led_spd;
int led_pre_time = 0, led_cur_time;
boolean isLedOn = false;
String getstr = "";
String pre_warn_case= "", warn_case;

void setup() {
  //led, speaker init
  ledsp_setup();
  Serial.begin(9600);
  //step_moter init
  //step_moter.stepMmove();
  subArduino.begin(9600);

  Serial.println("start");
  
  while(!Serial.available()){
  }

  if(Serial.available()){
    String c = Serial.readStringUntil('\n');
    for(int i =0; i< c.length(); i++)
      subArduino.write(c.charAt(i));
  }
  
  while(subArduino.available()){
    getstr = subArduino.readStringUntil('\n');
  }
  Serial.println(getstr);
  
}

void loop() {
  
//  float gps_velocity = gps.getVelocity();
  //send data(gps_velocity (+ imu(roll, pitch)))
  if(Serial.available() == 0){
    Serial.println();
  }
  
  //waiting 
  while(!Serial.available()){
  }

  //recive data
  String recv_data = Serial.readString();
  //parsing
  
  
  //servo setting
//  servo_moter.SerMotorMove(srvo_deg);
  

  
  //warn_case = Serial.readString();
 // warn_case = "led101010101010spd1kind1010";

  
  led_spd = warn_case[18] - '0';

  if(pre_warn_case != warn_case){
    //led.set(led_num, warn_case);
    ledsp_loop(warn_case);
    
    led_cur_time = millis();
    led_pre_time = led_cur_time;
    isLedOn = true;
    pre_warn_case = warn_case;

  }
  
  if(led_spd)
    led_control();
    
}

void led_control(){
  led_cur_time = millis();
  
  if((led_cur_time - led_pre_time) >= led_spd * 1000){
    //switching
    if(isLedOn){   //turn on -> off
      led_pre_time = led_cur_time;
      ledsp_blinkLED(false);
      isLedOn = false;
    }
    else{ //turn off -> on
      led_pre_time = led_cur_time;
      ledsp_blinkLED(true);
      isLedOn = true;
    }
  }
}
  
