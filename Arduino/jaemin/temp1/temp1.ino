#include <Adafruit_NeoPixel.h>
#include "setup.h"
#include "loop.h"
#include <Servo.h>
#include <SoftwareSerial.h>

SoftwareSerial subArduino(10, 11); 

#define GPSBAUD 9600

//Gps gps(GPSBAUD);
Servo servo1, servo2, servo3;

int led_spd;
int led_pre_time = 0, led_cur_time;
boolean isLedOn = false;
String getstr = "";
String warn_case;

float serv_deg[3];

void setup() {
  //led, speaker init
  ledsp_setup();
  subArduino.begin(9600);

  servo1.attach(A0);
  servo2.attach(A2);
  servo3.attach(A4);
  
  servo_init();
  
  String get_serv_deg = "10.4, 20.5, 25.5";
  
  //initializing sub
  for(int i =0; i < get_serv_deg.length(); i++)
    subArduino.write(get_serv_deg.charAt(i));
  setting_serv_deg(get_serv_deg);

   
  //recive success data
  while(!subArduino.available()){    
  }
  while(subArduino.available())
    getstr = subArduino.readStringUntil("\n");
  
  getstr.trim();

  //after 10seconds, execute
  delay(10000);
}

void loop() {
  
  
  // 3 digit for neopixel, 1 digit for speed, 4 digit for led
  String recv_data = "00111000";
  recv_data.trim();
 
  //parsing
  //String recv_data = "00121010";
  String neo_info = recv_data.substring(0, 3);
  String spd_info = String(recv_data.charAt(3));
  String led_info = recv_data.substring(4);
  
  if(neo_info.equals("001"))
    neo_info = "110000000011";
  else if(neo_info.equals("010"))
    neo_info = "000000111100";
  else if(neo_info.equals("100"))
    neo_info = "001111000000";
  else if(neo_info.equals("000"))
    neo_info = "000000000000";
  else if(neo_info.equals("110"))
    neo_info = "001111111100";
  else if(neo_info.equals("101"))
    neo_info = "111111000011";
  else if(neo_info.equals("011"))
    neo_info = "110000111111";
  else if(neo_info.equals("111"))
    neo_info = "111111111111";
  
  
  int spd = spd_info.toInt();
  
  //servo setting
  servo_move(serv_deg[spd]);
  String warn_case = "led" + neo_info + "spd" + spd_info + "kind" + led_info;
  
 // warn_case = "led101010101010spd1kind1010";
  
  led_spd = spd +1;
 
  ledsp_loop(warn_case);
  led_cur_time = millis();
  led_pre_time = led_cur_time;
  isLedOn = true;
  
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

void servo_move(float angle){
  servo1.write(92-angle);
  servo2.write(75-angle);
  servo3.write(91-angle);
}

void servo_init(){
  servo1.write(92);
  servo2.write(75);
  servo3.write(91);
}
  
