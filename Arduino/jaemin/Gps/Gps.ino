#include <SoftwareSerial.h>
#include <TinyGPS.h>
 
// Define which pins you will use on the Arduino to communicate with your 
// GPS. In this case, the GPS module's TX pin will connect to the 
// Arduino's RXPIN which is pin 3.
#define RXPIN 6
#define TXPIN 5
//Set this value equal to the baud rate of your GPS
#define GPSBAUD 9600
 

class Gps{
  private:
    SoftwareSerial uart_gps(RXPIN, TXPIN);
    TinyGPS gps;
    float gps_velocity;
    int GPSBAUD;
    
  public:
    Gps(GPSBAUD){
      this.GPSBAUD = GPSBAUD;
    }
    
    void setup_gps(){
      uart_gps.begin(GPSBAUD); // GPSBAUD = 9600
    }

     float get_velocity(){
        int c = uart_gps.read();
        while(uart_gps.available()){ 
          if(gps.encode(c))     // if there is a new valid sentence...
            gps_velocity = gps.f_speed_mps();         // then grab the data.
        }
        return gps_velocity();
     }
}
