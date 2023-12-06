#include <ArduinoJson.h>
// these constants won't change:
const int piezo0 = A0; // top
const int piezo1 = A1; // front
const int piezo2 = A2; 
const int numSamp = 1024;
const int threshold = 400000;   // threshold value to decide when the detected sound is a knock or not

int knockData0[numSamp];
int knockData1[numSamp];
int knockData2[numSamp];

// these variables will change:
int sensor0 = 0;  // variable to store the value read from the sensor pin
int sensor1 = 0;  // variable to store the value read from the sensor pin
int sensor2 = 0;  // variable to store the value read from the sensor pin

void setup() {
  Serial.begin(38400);       // use the serial port
  Serial.println("Ready!");
}

void loop() {
      sensor0 = analogRead(piezo0);
      sensor1 = analogRead(piezo1);
      sensor2 = analogRead(piezo2);
      //unsigned long t = millis();
      if (sensor0*sensor0 + sensor1*sensor1 + sensor2*sensor2 > threshold) {
        knockData0[0] = sensor0;
        knockData1[0] = sensor1;
        knockData2[0] = sensor2;
        for(int i=1; i<numSamp; i++) {
          knockData0[i] = analogRead(piezo0);
          knockData1[i] = analogRead(piezo1);
          knockData2[i] = analogRead(piezo2);
        }
        //unsigned long e = millis();
        
        for(int i =0; i<numSamp;i++) {
          const size_t CAPACITY = JSON_ARRAY_SIZE(3);
          StaticJsonDocument<CAPACITY> doc;
          JsonArray array = doc.to<JsonArray>();
          array.add(knockData0[i]);
          array.add(knockData1[i]);
          array.add(knockData2[i]);
          serializeJson(doc, Serial);
          Serial.println();
          delay(1);
        }
        
        
      }
}
