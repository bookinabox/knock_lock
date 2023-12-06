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
  displayIMU();
  // witholding the delay below will crash client such that it cannot receive anymore values
  // increase values if client is crashing
  delay(40); // 40 is a good minimum value
}

void clientPublish(String output, float num) {
  output += num;
  client.publish(topic, output.c_str());
}

void displayIMU() {
  float x, y, z;

  String output = "";
  bool first = false, second = false;
  if (IMU.accelerationAvailable()) {
    IMU.readAcceleration(x, y, z);

    output += "Acceleration,x,";
    output += x;
    output += ";Acceleration,y,";
    output += y;
    output += ";Acceleration,z,";
    output += z;

    first = true;
  }

  if (IMU.gyroscopeAvailable()) {
    IMU.readGyroscope(x, y, z);

    output += ";Gyroscope,x,";
    output += x;
    output += ";Gyroscope,y,";
    output += y;
    output += ";Gyroscope,z,";
    output += z;

    second = true;
  }

  if (first && second) {
    Serial.println(output);
    client.publish(topic, output.c_str());
  }
}
