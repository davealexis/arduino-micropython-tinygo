"""
    --------------------------------------------------------------------------------------
    blinky.py
    --------------------------------------------------------------------------------------

    This is the basic LED blink script that uses the built-in LED on the ESP8266 board.
    It is internally attached to the GPIO2 pin. This LED is set up in a strange way, where
    the Off state actually turns the LED on and the On state turns it off.  If you connect
    your own LED, the behavior will be different.

    Author:  David Alexis (2019)
    --------------------------------------------------------------------------------------
"""

# The 'machine' module contains classes and methods for accessing device-specific
# functionality, like the GPIO pins. We will use the Pin class from the machine
# module.
import machine

# The 'time' module is needed in order to access the sleep() method that lets us tell
# delay a bit between toggling the state of the LED.
import time

# Let's get a reference to the LED on pin 2, and define it as an output pin (Pin.OUT).
# Both ESP8266 and ESP32 boards have a built-in LED on the board that is internally
# connected to GPIO pin 2. Most ESP8266 boards also have another LED on pin 16.
led = machine.Pin(2, machine.Pin.OUT)

# We need an infinite loop in our program so that the device keeps performing our
# desired functionality until it gets turned off or reset.
while True:
    # led.value() gives us the current state of the pin (On or Off / True or False).
    # With every pass through our loop, we will set the state of the LED to the
    # opposite of its current state.
    led.value(not led.value())

    # Do nothing for half a second before going on.
    # The effect of this is that the LED will go on for 1/2 a second, go off for
    # 1/2 a second, then go on for.....  You get the idea.
    time.sleep(.5)
