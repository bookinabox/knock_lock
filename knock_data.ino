
// these constants won't change:
#define LED_BUILTIN 13
const int piezo0 = A0; // top
const int piezo1 = A1; // front
const int piezo2 = A2; 

const int threshold = 80;   // threshold value to decide when the detected sound is a knock or not


// these variables will change:
int sensor0 = 0;  // variable to store the value read from the sensor pin
int sensor1 = 0;  // variable to store the value read from the sensor pin
int sensor2 = 0;  // variable to store the value read from the sensor pin

int ledState = LOW;     // variable used to store the last LED status, to toggle the light

void setup() {
  pinMode(LED_BUILTIN, OUTPUT);  // declare the ledPin as as OUTPUT
  Serial.begin(9600);       // use the serial port
  Serial.println("Ready!");
}

void loop() {
  // read the sensor and store it in the variable sensorReading:
  sensor0 = analogRead(piezo0);
  sensor1 = analogRead(piezo1);
  sensor2 = analogRead(piezo2);
  if (sensor0 + sensor1 + sensor2 > threshold) {
    Serial.print(sensor0);
    Serial.print(", ");
    Serial.print(sensor1);
    Serial.print(", ");
    Serial.println(sensor2);
    
    int numSamp = 30;
    for(int i=0; i<numSamp; i++) {
      sensor0 = analogRead(piezo0);
      sensor1 = analogRead(piezo1);
      sensor2 = analogRead(piezo2);
      Serial.print(sensor0);
      Serial.print(", ");
      Serial.print(sensor1);
      Serial.print(", ");
      Serial.println(sensor2);
    }



  }
  delay(50);  // delay to avoid overloading the serial port buffer
}
