const int num_of_led = 12;
int neopixel_pin = 6;
int speaker_pin = 9;
int led1_pin = 2;
int led2_pin = 3;
int led3_pin = 4;
int led4_pin = 5;
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

Adafruit_NeoPixel neopixel = Adafruit_NeoPixel(num_of_led, neopixel_pin, NEO_GRB + NEO_KHZ800);

void ledsp_setup()
{
  Serial.begin(9600);
  neopixel.begin();
  neopixel.show();
  pinMode(speaker_pin, OUTPUT);
  pinMode(led1_pin, OUTPUT);
  pinMode(led2_pin, OUTPUT);
  pinMode(led3_pin, OUTPUT);
  pinMode(led4_pin, OUTPUT);
}
