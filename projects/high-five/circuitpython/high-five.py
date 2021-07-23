"""
    CircuitPython

    This project implements a high-five machine. Or it can simply be
    used to trigger some other action (like pressing the plunger of a
    soap dispenser) when something like a hand is within range.

    It uses an HC-SR04 or US-015 ultrasonic sensor and a micro servo.

    This project has been tested on the following boards, with changes
    being made to the defined pins, as needed:
    - Adafruit Trinket M0
"""

from time import sleep
import board
import digitalio
import pwmio
from adafruit_motor import servo
import adafruit_hcsr04

ACTIVATION_THRESHOLD = 30
HAND_UP = 180
HAND_DOWN = 50

# .....................................................
def run():
    # ... Setup ...
    sonar = adafruit_hcsr04.HCSR04(trigger_pin=board.D3, echo_pin=board.D4)
    led = digitalio.DigitalInOut(board.D13)
    led.direction = digitalio.Direction.OUTPUT
    led.value = False

    pwm = pwmio.PWMOut(board.A2, duty_cycle=2 ** 15, frequency=50)
    srvo = servo.Servo(pwm)

    # ... Loop ...
    while True:
        d = sonar.distance

        if d <= ACTIVATION_THRESHOLD:
            led.value = True
            srvo.angle = HAND_UP
            sleep(.5)
            srvo.angle = HAND_DOWN
            led.value = False
            sleep(1)

        sleep(.5)

# .....................................................
run()
