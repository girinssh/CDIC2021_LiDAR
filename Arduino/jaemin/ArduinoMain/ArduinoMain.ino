



void setup() {
  //step_moter init

  //servo init deg
}

void loop() {

  
  gps_velocity = gps.getVelocity();
  
  //send data(gps_velocity (+ imu(roll, pitch)))
  if(Serial.available() == 0){
    
  }

  //waiting & led initial
  while(!Serial.available())(
    
  }

  //recive data
  String recv_data = Serial.read();
  //parsing


  //servo setting
  servo.set_deg(srvo_deg);
  
  //control led
  if(warn_case){
    led.set(led_num);
  }
  
}
