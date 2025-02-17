#include "moisture_sensor.h"
#include <Arduino.h>

#define SENSOR_PIN A0 // Define the sensor pin

void initMoistureSensor()
{
    Serial.begin(115200);
    while (!Serial)
        ;
    Serial.println("Soil Moisture Sensor Initialized");
}

int readMoisture()
{
    return analogRead(SENSOR_PIN); // Read and return sensor value
}
