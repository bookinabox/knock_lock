#include <WiFi.h>
#include <PubSubClient.h>
#include <Arduino_LSM6DS3.h>
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

// WiFi
const char *ssid = "abc123"; // Enter your WiFi name
const char *password = "abcd1234";  // Enter WiFi password

// MQTT Broker
const char *mqtt_broker = "mqtt.eclipseprojects.io";
const char *topic = "ECEM119_knockbox_project";
const int mqtt_port = 1883;

String output = "";
int counter = 0;

WiFiClient espClient;
PubSubClient client(espClient);

void setup() {
 // Set software serial baud to 115200;
	Serial.begin(38400);
	while (!Serial) delay(10); // delay until serial is connected
	// connecting to a WiFi network

  if (!IMU.begin()) {
    Serial.println("Failed to initialize IMU!");

    while (1);
  }
	
	WiFi.begin(ssid, password);
	while (WiFi.status() != WL_CONNECTED) {
			delay(500);
			Serial.println("Connecting to WiFi..");
	}
	Serial.println("Connected to the WiFi network");
	//connecting to a mqtt broker
	client.setServer(mqtt_broker, mqtt_port);
	while (!client.connected()) {
			String client_id = "esp32-client-";
			if (client.connect(client_id.c_str())) { //, mqtt_username, mqtt_password)) {
					Serial.println("mqtt broker connected");
			} else {
					Serial.print("failed with state ");
					Serial.print(client.state());
					delay(2000);
			}
	}
}

void loop()
{
  readValues();
  if (counter >= 4) {
    Serial.println("DATA SENT!");
    client.publish(topic, output.c_str());
    output = "";
    counter = 0;
  }
}

void readValues() {
  sensor0 = analogRead(piezo0);
  sensor1 = analogRead(piezo1);
  sensor2 = analogRead(piezo2);

  if (sensor0*sensor0 + sensor1*sensor1 + sensor2*sensor2 > threshold) {
    output += sensor0;
    output += ";";
    output += sensor1;
    output += ";";
    output += sensor2;
    output += ";";
    Serial.println(output);
    counter++;
  }
  
}
