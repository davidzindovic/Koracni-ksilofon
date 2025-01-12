
#include "PubSubClient.h"
#include "WiFi.h"



// WiFi
const char* AP_ssid = "RPI2";                
const char* AP_wifi_password = "stopnice";

// MQTT
const char* mqtt_server = "192.168.*.*"; 
const char* humidity_topic = "humidity";
const char* temperature_topic = "temperature";
const char* mqtt_username = "RPI"; // MQTT username
const char* mqtt_password = "stopnice"; // MQTT password
const char* clientID = "Weather_Reporter"; // MQTT client ID

// Initialise the WiFi and MQTT Client objects
WiFiClient wifiClient;

// 1883 is the listener port for the Broker
PubSubClient client(mqtt_server, 1883, wifiClient);

 

void setup() {
  Serial.begin(9600);
        // Connect to Wi-Fi network with SSID and password
    Serial.print("Setting AP (Access Point)…");
    // Remove the password parameter, if you want the AP (Access Point) to be open
    WiFi.softAP(AP_ssid, AP_wifi_password);

    IPAddress IP = WiFi.softAPIP();
    Serial.print("AP IP address: ");
    Serial.println(IP);
}

void loop() {
 // connect_MQTT();
  Serial.setTimeout(2000);


  // MQTT can only transmit strings
  String hs="hs";
  String ts="ts";

  // PUBLISH to the MQTT Broker (topic = Temperature)
  if (client.publish(temperature_topic, String(ts).c_str())) {
    Serial.println("Temperature sent!");
  }
  else {
    Serial.println("Temperature failed to send. Reconnecting to MQTT Broker and trying again");
    client.connect(clientID, mqtt_username, mqtt_password);
    delay(10); // This delay ensures that client.publish doesn’t clash with the client.connect call
    client.publish(temperature_topic, String(ts).c_str());
  }

  // PUBLISH to the MQTT Broker (topic = Humidity)
  if (client.publish(humidity_topic, String(hs).c_str())) {
    Serial.println("Humidity sent!");
  }
  else {
    Serial.println("Humidity failed to send. Reconnecting to MQTT Broker and trying again");
    client.connect(clientID, mqtt_username, mqtt_password);
    delay(10); // This delay ensures that client.publish doesn’t clash with the client.connect call
    client.publish(humidity_topic, String(hs).c_str());
  }
 // client.disconnect();  // disconnect from the MQTT broker
  delay(3000);       // print new values after 1 Minute
}
