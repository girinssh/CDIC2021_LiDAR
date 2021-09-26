



void setup() {
  //스탭모터 구동
  

  //서보모터 초기 각도
  
}

void loop() {


  
  gps_velocity = gps.getvelocity();
  
  //send data
  if(Serial.available() == 0){
    
  }

  //waiting & led initial
  while(!Serial.available()){
    
  }

  //recive data
  String rec_data = Serial.read();
  
  //control led
}
