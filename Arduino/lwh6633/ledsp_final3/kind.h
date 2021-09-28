void ledsp_kind()
{
  for (int j = 0; j < 4; j++)
    {
        if (indices3[j])
        {
            if (j == 0)
            {
                digitalWrite(led1_pin, HIGH);
            }
            else if (j == 1)
            {
                digitalWrite(led2_pin, HIGH);
            }
            else if (j == 2)
            {
                digitalWrite(led3_pin, HIGH);
            }
            else if (j == 3)
            {
                digitalWrite(led4_pin, HIGH);
            }
        }
        else
        {
            if (j == 0)
            {
                digitalWrite(led1_pin, LOW);
            }
            else if (j == 1)
            {
                digitalWrite(led2_pin, LOW);
            }
            else if (j == 2)
            {
                digitalWrite(led3_pin, LOW);
            }
            else if (j == 3)
            {
                digitalWrite(led4_pin, LOW);
            }
        }
    }
}
