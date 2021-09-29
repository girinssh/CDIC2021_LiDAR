

#define GPSBAUD 9600

Gps gps(GPSBAUD);

void setup() {
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
  }
  
}
