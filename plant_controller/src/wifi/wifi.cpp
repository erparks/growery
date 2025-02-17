#include <Arduino.h>
#include <WiFiS3.h>
#include <ArduinoHttpClient.h>
#include <ArduinoJson.h>
#include "wifi/wifi.h"
#include "secrets.h"

const int PORT = 3000;
const char* PATH = "/api/data";

// WiFi and HTTP Client
WiFiClient wifi;
HttpClient client = HttpClient(wifi, SERVER, PORT);

void initWifi()
{
  Serial.print("Connecting to WiFi...");
  WiFi.begin(WIFI_SSID, WIFI_PASSWORD);

  while (WiFi.status() != WL_CONNECTED) {
      delay(1000);
      Serial.print(".");
  }
  Serial.println("\nConnected to WiFi!");
}

void post(String sensorName, int value)
{
  Serial.println("Sending HTTP POST request...");

  // save request values
  StaticJsonDocument<200> doc;
  doc["sensor"] = sensorName;
  doc["value"] = value;

  // build JSON
  String jsonPayload;
  serializeJson(doc, jsonPayload);
  Serial.println(jsonPayload);

  // make the HTTP request
  client.beginRequest();
  client.post(PATH);
  client.sendHeader("Content-Type", "application/json");
  client.sendHeader("Content-Length", jsonPayload.length());
  client.beginBody();
  client.print(jsonPayload);
  client.endRequest();

  // read the server response
  int statusCode = client.responseStatusCode();
  String response = client.responseBody();

  Serial.print("Response Code: ");
  Serial.println(statusCode);
  Serial.print("Response Body: ");
  Serial.println(response);
}