#include <Arduino.h>
#include "sensors/moisture/moisture_sensor.h"

void initMoistureSensor(){

}

// Dry soil → Higher values (~800-1023)
// Moist soil → Medium values (~300-700)
// Wet soil → Lower values (~100-300)
int readMoisture(int pin)
{
    return analogRead(pin);
}
