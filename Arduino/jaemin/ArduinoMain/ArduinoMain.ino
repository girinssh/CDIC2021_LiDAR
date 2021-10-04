#include <Adafruit_NeoPixel.h>
#include "setup.h"
#include "loop.h"
#include "SerMo.h"
#include <SoftwareSerial.h>

SoftwareSerial subArduino(10, 11); 
SoftwareSerial rasberry(4, 5);


#define GPSBAUD 9600
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

float serv_deg[3];

void setup() {
  //led, speaker init
  ledsp_setup();
  Serial.begin(9600);

  subArduino.begin(9600);


  //rasbarrypi init
  while(!Serial.available()){  
    Serial.println("start");
    delay(100);
  }
  String get_serv_deg;
  while(Serial.available())
    get_serv_deg = Serial.readStringUntil('\n');
  setting_serv_deg(get_serv_deg);
  

  
  while(!Serial.available()){
  }

  if(Serial.available()){
    String c = Serial.readStringUntil('\n');
    for(int i =0; i< c.length(); i++)
      subArduino.write(c.charAt(i));
  }
  String c= "on";

  for(int i =0; i< c.length(); i++)
    subArduino.write(c.charAt(i));
  
  
  while(!subArduino.available()){
    
  }
  
  while(subArduino.available()){
    getstr = subArduino.readStringUntil('\n');
  }
  getstr.trim();
  Serial.println(getstr);

  //send raspi (init)
  String info = "success";
  for(int i =0; i< info.length(); i++)
    Serial.write(info.charAt(i));
}

void loop() {
  
//  float gps_velocity = gps.getVelocity();
  float gps_velocity = 5.01;
  
  //send data to rasberry(gps_velocity)
  if(Serial.available()){
    String temp = String(gps_velocity);
    for(int i =0; i < temp.length(); i++)
      Serial.write(temp.charAt(i));
  }
  
  //waiting 
  while(!Serial.available()){
  }

  // rasberry (recive data)
  String recv_data = "";
  while(Serial.available())
    recv_data = Serial.readStringUntil('\n');
  
  //parsing
  //String recv_data = "00141010";
  recv_data.trim();
  String neo_info = recv_data.substring(0, 4);
  String spd_info = String(recv_data.charAt(3));
  String led_info = recv_data.substring(5);

  if(neo_info.equals("001"))
    neo_info = "110000000011";
  else if(neo_info.equals("010"))
    neo_info = "001111000000";
  else if(neo_info.equals("100"))
    neo_info = "000000111100";
  else if(neo_info.equals("000"))
    neo_info = "000000000000";
  
  
  int spd = spd_info.toInt();
  
  //servo setting
  servo_moter.SerMotorMove(serv_deg[spd]);
  String warn_case = "led" + neo_info + "spd" + spd_info + "kind" + led_info;
  
  //warn_case = Serial.readString();
 // warn_case = "led101010101010spd1kind1010";

  
  led_spd = spd +1;

  if(pre_warn_case != warn_case){
    ledsp_loop(warn_case);
    
    led_cur_time = millis();
    led_pre_time = led_cur_time;
    isLedOn = true;
    pre_warn_case = warn_case;

  }
  
  if(led_spd)
    led_control();
    
}

void setting_serv_deg(String info){
  int index;
  index = info.indexOf(",");
  serv_deg[0] = info.substring(0, index).toFloat();
  info = info.substring(index +2);

  index = info.indexOf(",");
  serv_deg[1] = info.substring(0, index).toFloat();
  info = info.substring(index +2);

  serv_deg[2] = info.toFloat();
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
  
