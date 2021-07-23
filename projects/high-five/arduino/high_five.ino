/*
    This project implements a high-five machine. Or it can simply be
    used to trigger some other action (like pressing the plunger of a
    soap dispenser) when something like a hand is within range.

    It uses an HC-SR04 or US-015 ultrasonic sensor and a micro servo.

    This project has been tested on the following boards, with changes
    being made to the defined pins, as needed:
    - Adafruit Trinket M0
    - Wemos D1 Mini (ESP8266 board)
    - Arduino Uno
    - Arduino Nano 33 IoT
*/

#include <Servo.h>
#include <Ultrasonic.h>

#define activationThresholdCM 40
#define pingPin D5
#define echoPin D6
#define servoPin D8
#define handDown 0
#define handUp 150
#define led LED_BUILTIN

// These constants may seem a little counter-intuitive, but are
// a readability enhancement for when the code is built for an
// ESP8266 board. The built-in LED on these boards operate in
// reverse - they are on when the value is low (0) and off when high (1).
// Uncomment the line below to build for an ESP8266.
// #define ESP8266
#ifdef ESP8266
    #define LED_ON LOW
    #define LED_OFF HIGH
#else
    #define LED_ON HIGH
    #define LED_OFF LOW
#endif

Servo servo;
Ultrasonic sonar(pingPin, echoPin);
int distance;

// ........................................................................
void notifyError() {
    while (true) {
        digitalWrite(led, HIGH);
        delay(250);
        digitalWrite(led, LOW);
        delay(250);
    }
}

// ........................................................................
void setup() {
    servo.attach(servoPin);
    servo.write(handDown);
    pinMode(led, OUTPUT);
    Serial.begin(9600);
    while (!Serial) ;
    Serial.println("Beginning");
    digitalWrite(led, LED_OFF);
}

// ........................................................................
void loop() {
    distance = sonar.read();
    Serial.println(distance);

    if (distance <= activationThresholdCM) {
        digitalWrite(led, LED_ON);
        delay(500);

        servo.write(handUp);
        delay(400);

        for (int pos = handUp; pos > handDown; pos -= 10) {
            servo.write(pos);
            delay(5);
        }

        servo.write(handDown);
        delay(1000);
        digitalWrite(led, LED_OFF);
    }

    delay(1000);
}
