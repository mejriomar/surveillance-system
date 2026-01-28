#ifndef SERVO_CONTROL_H
#define SERVO_CONTROL_H

#include <ESP32Servo.h>

extern Servo servo1;  // Déclaration globale (défini dans .cpp)

void initServo();
void moveServo(int angle, int choose);

#endif
