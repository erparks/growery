#include <Arduino.h>
#include "sensors/moisture/moisture_sensor.h"

void setup()
{
  initMoistureSensor();
}

// Dry soil → Higher values (~800-1023)
// Moist soil → Medium values (~300-700)
// Wet soil → Lower values (~100-300)
void loop()
{
  int moisture = readMoisture();
  Serial.print("Soil moisture level:");
  Serial.println(moisture);

  delay(1000); // Wait 1 second before reading again
}