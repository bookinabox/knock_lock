#include <WiFi.h>
#include <PubSubClient.h>
#include <Arduino_LSM6DS3.h>

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
	Serial.begin(115200);
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
  output = "";
  readValues();

  client.publish(topic, output.c_str());
}

void readValues() {
  output += sensor1;
  output += ";"
  output += sensor2;
  output += ";"
  output += sensor3;
}
