"""
    MicroPython
    
    This project implements a high-five machine. Or it can simply be
    used to trigger some other action (like pressing the plunger of a
    soap dispenser) when something like a hand is within range.

    It uses an HC-SR04 or US-015 ultrasonic sensor and a micro servo.

    This project has been tested on the following boards, with changes
    being made to the defined pins, as needed:
    - Wemos D1 Mini (ESP8266 board)
"""

import os
from utime import sleep, sleep_us, ticks_us
from machine import Pin, PWM
from hcsr04 import HCSR04

LED_ON = False if os.uname()[0] == 'esp8266' else True
ACTIVATION_THRESHOLD = 30
HAND_UP = 80
HAND_DOWN = 30

def run():
    # ... Setup ...
    led = Pin(2, Pin.OUT)
    led.value(not LED_ON)
    sensor = HCSR04(trigger_pin=4, echo_pin=5)
    servo = PWM(Pin(14), freq=50)
    servo.duty(HAND_DOWN)

    # ... Loop ...
    while True:
        d = sensor.distance_cm()
        print(d)

        if d > 0 and d <= ACTIVATION_THRESHOLD:
            led.value(LED_ON)
            servo.duty(HAND_UP)
            sleep(.5)
            servo.duty(HAND_DOWN)
            led.value(not LED_ON)
            sleep(1)

        sleep(.5)

# ..........
run()
