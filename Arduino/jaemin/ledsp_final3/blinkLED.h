void ledsp_blinkLED(bool turn)
{
  //turn on
  if(turn){
    for (int i = 0; i < num_of_led; i++)
    {
          if (indices1[i])
          {
              neopixel.setPixelColor(i, 128, 0, 0);
          }
    }
  }
  else{
    for (int i = 0; i < num_of_led; i++)
    {
        neopixel.setPixelColor(i, neopixel.Color(0, 0, 0)); 
    }
  }
  neopixel.show();
}
