#include "ServoControl.h"

Servo servo1;  // Définition globale de l'objet
Servo servo2;  // Définition globale de l'objet

const int SERVO_PIN_1 = 13;
const int SERVO_PIN_2 = 14;

void initServo() {
  servo1.setPeriodHertz(50);     // 50 Hz standard pour servo
  servo1.attach(SERVO_PIN_1, 500, 2400);  // Pulse min et max
  servo2.setPeriodHertz(50);     // 50 Hz standard pour servo
  servo2.attach(SERVO_PIN_2, 500, 2400);  // Pulse min et max
}

void moveServo(int angle, int choose) {
  if(choose == 1)
  {
    servo1.write(angle);
  }
  else
  {
    servo2.write(angle);
  }
}
