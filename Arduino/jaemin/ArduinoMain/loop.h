#include "blinkLED.h"
#include "kind.h"

void ledsp_loop(String led_info){
  str = led_info;    //led(12numbers)spd(1~3)kind(4number)
  
  arr1 = str.substring(3, 15);
  arr2 = str.substring(18, 19);
  arr3 = str.substring(23, 27);

  num1 = arr1.toInt();
  num2 = arr2.toInt();
  num3 = arr3.toInt();

  if (str == "stop"){
    a = 0;
  }
  else{
    for (int i = 0; i < num_of_led; i++){
        if (arr1[i] == '1'){
          indices1[i] = true;
        }
        else if (arr1[i] == '0'){
          indices1[i] = false;
        }
     }
     for (int j = 0; j < 4; j++){
        if (arr3[j] == '1'){
          indices3[j] = true;
        }
        else if (arr3[j] == '0'){
          indices3[j] = false;
        }
     }
     a = 1;
  }
    
  if (a > 0){
     ledsp_blinkLED(true);
     ledsp_kind();
     tone(speaker_pin, 440);
     noTone(speaker_pin);
  }
  else if (a == 0){
     for (int i = 0; i < num_of_led; i++){
         indices1[i] = false;
         neopixel.setPixelColor(i, neopixel.Color(0, 0, 0)); 
         neopixel.show();
     }
     for (int j = 0; j < 4; j++){
         indices3[j] = false;
     }
     digitalWrite(led1_pin, LOW);
     digitalWrite(led2_pin, LOW);
     digitalWrite(led3_pin, LOW);
     digitalWrite(led4_pin, LOW);
     a = -1;
 }
}
