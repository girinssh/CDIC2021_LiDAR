#include <Adafruit_NeoPixel.h>

int pin = 6;
const int num_of_led = 12;
int speaker = 9;
String str;
String arr1;
String arr2;
String arr3;
bool indices1[12] = { false };
bool indices2[1] = { false };
bool indices3[4] = { false };
int num1;
int num2;
int num3;
int a;
void blinkLED();
void kind();

Adafruit_NeoPixel neopixel = Adafruit_NeoPixel(num_of_led, pin, NEO_GRB + NEO_KHZ800);

void setup()
{
    Serial.begin(9600);
    neopixel.begin();
    neopixel.show();
    pinMode(speaker, OUTPUT);
    pinMode(2, OUTPUT);
    pinMode(3, OUTPUT);
    pinMode(4, OUTPUT);
    pinMode(5, OUTPUT);
}

void loop()
{
    if (Serial.available())
    {
        str = Serial.readString();

        arr1 = str.substring(3, 15);
        arr2 = str.substring(18, 19);
        arr3 = str.substring(23, 27);

        num1 = arr1.toInt();
        num2 = arr2.toInt();
        num3 = arr3.toInt();

        if (str == "stop")
        {
            a = 0;
        }
        else
        {
            for (int i = 0; i < num_of_led; i++)
            {
                if (arr1[i] == '1')
                {
                    indices1[i] = true;
                }
                else if (arr1[i] == '0')
                {
                    indices1[i] = false;
                }
            }
            for (int j = 0; j < 4; j++)
            {
                if (arr3[j] == '1')
                {
                    indices3[j] = true;
                }
                else if (arr3[j] == '0')
                {
                    indices3[j] = false;
                }
            }
            a = 1;
        }
    }

    if (a > 0)
    {
        blinkLED();
        kind();
        tone(speaker, 440);
        noTone(speaker);
    }
    else if (a == 0)
    {
        Serial.println("Call reset");
        for (int i = 0; i < num_of_led; i++)
        {
            indices1[i] = false;
            neopixel.setPixelColor(i, neopixel.Color(0, 0, 0)); // Black 컬러(LED OFF) 준비
            neopixel.show();
        }
        for (int j = 0; j < 4; j++)
        {
            indices3[j] = false;
            digitalWrite(j + 2, LOW);
        }
        a = -1;
    }
    delay(500);
    for (int i = 0; i < num_of_led; i++)
    {
        Serial.print(String(indices1[i]) + "  ");
    }
    Serial.println();
}

void blinkLED()
{
    for (int i = 0; i < num_of_led; i++)
    {
        if (indices1[i])
            neopixel.setPixelColor(i, 128, 0, 0);
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
        neopixel.setPixelColor(i, neopixel.Color(0, 0, 0)); // Black 컬러(LED OFF) 준비
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

void kind()
{
    for (int j = 0; j < 4; j++)
    {
        if (indices3[j])
        {
            digitalWrite(j + 2, HIGH);
        }
        else
        {
            digitalWrite(j + 2, LOW);
        }
    }
}