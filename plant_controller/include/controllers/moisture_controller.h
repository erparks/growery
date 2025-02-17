#ifndef MOISTURE_CONTROLLER_H
#define MOISTURE_CONTROLLER_H

#include <Arduino.h>

class MoistureController {
private:
    String name;
    int pin;
    
public:
    MoistureController(String sensorName, int sensorPin);

    void run();
};

#endif
