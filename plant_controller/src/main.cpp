#include <Arduino.h>
#include "wifi/wifi.h"
#include "sensors/moisture/moisture_sensor.h"
#include "controllers/moisture_controller.h"

MoistureController moistureSensor("moisture", A0);

void setup()
{
  Serial.begin(115200);
  while (!Serial);

  initMoistureSensor();
  initWifi();
}

void loop()
{
  delay(5000);
  moistureSensor.run();
}