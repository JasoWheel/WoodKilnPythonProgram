#include <DHT.h>
#include <OneWire.h>
#include <DallasTemperature.h>
 
#define DHT2PIN 2     // what pin we're connected to
#define DHT3PIN 3
#define ONE_WIRE_BUS 13
#define DHT2TYPE DHT21   // DHT 21 (AM2301)
#define DHT3TYPE DHT21   // DHT 21 (AM2301)
//int LightPin = A0; //analog pin for light sensor
int photocellPin = 5;     // the LDR and cap are connected to pin5
int L2;     // the digital light reading

DHT dht2(DHT2PIN, DHT2TYPE);
DHT dht3(DHT3PIN, DHT3TYPE);
OneWire oneWire(ONE_WIRE_BUS);
DallasTemperature sensors(&oneWire);

void setup() {
  Serial.begin(115200);
  sensors.begin();
  dht2.begin();
  dht3.begin();
}
 
void loop() {
  dht2.read();
  dht3.read();
  delay(4000);

  double dp1;
  double dp2;
  float h1 = 0;
  float h2 = 0;
  h1 = dht2.readHumidity();
  h2 = dht3.readHumidity();
  //h1=h1-2;
  //h2=h2+2; //math to match sensor difference

  //int L1 = 0;
  //L1 = analogRead(LightPin);
  float T1 = 0;
  float T2 = 0;
  float T3 = 0;
  float T4 = 0;
  
  sensors.requestTemperatures();
  delay(4000);
  T1 = sensors.getTempFByIndex(0);
  T2 = sensors.getTempFByIndex(1);
  T3 = sensors.getTempFByIndex(2);
  T4 = sensors.getTempFByIndex(3);

  T1 = T1 - .4; //adjustments because sensors did not show the samw temp when in same place
  T3 = T3 + .9;
  
  if (T4 < -50) { //this is to show that sensor has failed
    T4 = 50;
  }
  if (T3 < -50) { //this is to show that sensor has failed
    T3 = 50;
  }
  if (T2 < -50) { //this is to show that sensor has failed
    T2 = 50;
  }
  if (T1 < -50) { //this is to show that sensor has failed
    T1 = 50;
  }

  float dp1T = (T3 - 32) * 5 / 9; //calls function to calculate dew point
  dp1 = dewPoint(dp1T,h1);
  dp1 = dp1 * 9 / 5 + 32;
  //if (dp1 < 0.5) { //these were to avoid negative numbers, no longer needed
  //  dp1 = 0.5;
  //}

  float dp2T = (T4 - 32) * 5 / 9;//calls function to calculate dew point
  dp2 = dewPoint(dp2T,h2);
  dp2 = dp2 * 9 / 5 + 32;
  //if (dp2 < 0.5) { //these were to avoid negative numbers, no longer needed
  //  dp2 = 0.5;
  //}
  
  L2 = RCtime(photocellPin); //calls function that reads time for light to charge capacitor
  delay(2000);
  
  Serial.print("Light: ");
  Serial.print(L2);
  Serial.print(" H1: "); 
  Serial.print(h1);
  Serial.print(" H2: "); 
  Serial.print(h2);
  Serial.print(" T1: ");
  Serial.print(T1);
  Serial.print(" T2: ");
  Serial.print(T2);
  Serial.print(" T3: ");
  Serial.print(T3);
  Serial.print(" T4: ");
  Serial.print(T4);
  Serial.print(" DP1: ");
  Serial.print(dp1);
  Serial.print(" DP2: ");
  Serial.println(dp2);
  
  delay(2000);
}

int RCtime(int RCpin) { //def for RCtime
  int reading = 0;  // start with 0
 
  pinMode(RCpin, OUTPUT);
  digitalWrite(RCpin, LOW);
  delay(500);
 
  pinMode(RCpin, INPUT);
  while (digitalRead(RCpin) == LOW) { // count how long it takes to rise up to HIGH
    reading++;      // increment to keep track of time 
    if (reading == 32767) {
      break;           // leave the loop
    }
  }
  return reading;
}

double dewPoint(double celsius, double humidity)
{
  // (1) Saturation Vapor Pressure = ESGG(T)
  double RATIO = 373.15 / (273.15 + celsius);
  double RHS = -7.90298 * (RATIO - 1);
  RHS += 5.02808 * log10(RATIO);
  RHS += -1.3816e-7 * (pow(10, (11.344 * (1 - 1 / RATIO ))) - 1) ;
  RHS += 8.1328e-3 * (pow(10, (-3.49149 * (RATIO - 1))) - 1) ;
  RHS += log10(1013.246);

  // factor -3 is to adjust units - Vapor Pressure SVP * humidity
  double VP = pow(10, RHS - 3) * humidity;

  // (2) DEWPOINT = F(Vapor Pressure)
  double T = log(VP / 0.61078); // temp var
  return (241.88 * T) / (17.558 - T); //returns dewpoint celsius
}

