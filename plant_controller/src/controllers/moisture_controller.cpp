#include "controllers/moisture_controller.h"
#include "sensors/moisture/moisture_sensor.h"
#include "wifi/wifi.h"

MoistureController::MoistureController(String sensorName, int sensorPin) {
    name = sensorName;
    pin = sensorPin;
}

void MoistureController::run() {
    int moistLevel = readMoisture(pin);

    Serial.print(name);
    Serial.print(" | ");
    Serial.println(moistLevel);

    post(name, moistLevel);
}