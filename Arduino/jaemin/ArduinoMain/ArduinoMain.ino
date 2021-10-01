

#define GPSBAUD 9600

Gps gps(GPSBAUD);
int led_spd;
int led_pre_time = 0, led_cur_time;
boolean isLedOn = false

void setup() {
  //led, speaker init
  ledsp_setup();
  
  //step_moter init

  //servo init deg
}

void loop() {
  
  float gps_velocity = gps.getVelocity();
  //send data(gps_velocity (+ imu(roll, pitch)))
  if(Serial.available() == 0){
    Serial.println
  }
  
  //waiting & led initial
  while(!Serial.available())(
  }

  //recive data
  String recv_data = Serial.readString();
  //parsing
  
  
  //servo setting
  servo.set_deg(srvo_deg);
  
  //control led
  if(prev_warn_case != warn_case){
    led.set(led_num, warn_case);
    
    led_cur_time = millis();
    led_pre_time = led_cur_time;
    isledOn = true;
  }
  
  if(led_spd)
    led_control();
  
}

void led_control(){
  led_pre_time = led_cur_time;
  led_cur_time = millis();
  if((led_cur_time-led_pre_time) >= led_spd * 1000){
    //switching
    if(isledOn){   //turn on -> off
      ledsp_blinkLED(false);
      isledOn = false;
    }
    else{
      ledsp_blinkLED(true);
      isledOn = true;
    }
  }
}
  
