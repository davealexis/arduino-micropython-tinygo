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

package main

import (
	"machine"
	"time"

	"tinygo.org/x/drivers/hcsr04"
	"tinygo.org/x/drivers/servo"
)

var (
	pwm      = machine.TCC0
	servoPin = machine.D0
	pingPin  = machine.D3
	echoPin  = machine.D4
	led      = machine.LED
)

const (
	HandDown              = 640
	HandUp                = 1600
	ActivationThresholdCM = 40
)

// ............................................................................
func notifyError() {
    for {
        led.High()
        time.Sleep(250 * time.Millisecond)
        led.Low()
        time.Sleep(250 * time.Millisecond)
    }
}

// ............................................................................
func main() {
	// --- Setup ----------
	sensor := hcsr04.New(pingPin, echoPin)
	sensor.Configure()
	led.Configure(machine.PinConfig{Mode: machine.PinOutput})

	hand, err := servo.New(pwm, servoPin)
	if err != nil {
        // Let the user know we have an error condition
        notifyError()
	}

	hand.SetMicroseconds(HandDown)
	led.Low()

	// --- Loop ----------
	for {
		if sensor.ReadDistance() <= ActivationThresholdCM {
			led.High()
			time.Sleep(500 * time.Millisecond)

			hand.SetMicroseconds(HandUp)
			time.Sleep(250 * time.Millisecond)

            // Let's ease the hand back to the down position instead of
            // going there at full speed. This avoids bounce at the bottom
            // and provides a nice effect.
			for pos := HandUp; pos > HandDown; pos -= 10 {
				time.Sleep(5 * time.Millisecond)
				hand.SetMicroseconds(pos)
			}

            hand.SetMicroseconds(HandDown)
			time.Sleep(1 * time.Second)
            led.Low()
		}
	}
}
