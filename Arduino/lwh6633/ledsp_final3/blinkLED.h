void ledsp_blinkLED()
{
  for (int i = 0; i < num_of_led; i++)
    {
        if (indices1[i])
        {
            neopixel.setPixelColor(i, 128, 0, 0);
        }
    }
    neopixel.show();

    if (num2 == 1)
    {
        delay(300);
    }
    else if (num2 == 2)
    {
        delay(200);
    }
    else if (num2 == 3)
    {
        delay(100);
    }

    for (int i = 0; i < num_of_led; i++)
    {
        neopixel.setPixelColor(i, neopixel.Color(0, 0, 0)); 
    }
    neopixel.show();

    if (num2 == 1)
    {
        delay(300);
    }
    else if (num2 == 2)
    {
        delay(200);
    }
    else if (num2 == 3)
    {
        delay(100);
    }
}
