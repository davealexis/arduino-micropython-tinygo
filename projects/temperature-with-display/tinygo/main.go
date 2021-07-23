package main

/*
    This project uses a BME280 temperature/humidity sensor and an
    SSD1306 OLED display (128x64 pixels). Both use the I2C bus, so
    the only required pins for using both components are the SDA and SCL pins.
    A button is used to switch the displayed temerature units between
    Celcius and Farenheit.

    The code also demonstrates the use of the TaskScheduler library
    to implement the logic as concurrent tasks, rather than the usual
    loops and delays.

    The TinyFont module allows flexible usage of multple fonts and font
    sizes.

    This code was tested on the following boards:
    - Wemos D1 Mini (ESP8266 board)
    - Arduino Uno
    - Adafruit Trinket M0
    - Arduino Nano 33 IoT

    See https://github.com/toyo/tinyfont-ssd1306 for a sample of using
    the TinyFont library with the I2C-based SSD1306 OLED display, since
    the TinyFont samples seem to be geared towards a specific display.

    Since Go routines support is needed, flash with the `--scheduler tasks`
    parameter.  E.g.:
	   tinygo flash --target arduino-nano33 --scheduler tasks

*/

import (
	"fmt"
	"image/color"
	"machine"
	"time"

	"tinygo.org/x/drivers/bme280"
	"tinygo.org/x/drivers/ssd1306"
	"tinygo.org/x/tinyfont"
	"tinygo.org/x/tinyfont/freesans"
)

var (
	button      = machine.PB10
	led         = machine.LED
	showCelcius bool
	displayText string
	symbolPos   uint32
	textWidth   uint32
	temp        int32
	humidity    int32
	display     ssd1306.Device
	sensor      bme280.Device
	black       = color.RGBA{1, 1, 1, 255}
)

// ............................................................................
func main() {
	setup()
	loop()
}

// ............................................................................
func setup() {
	machine.I2C0.Configure(machine.I2CConfig{})

	sensor = bme280.New(machine.I2C0)
	sensor.Configure()

	display = ssd1306.NewI2C(machine.I2C0)
	display.Configure(ssd1306.Config{
		Width: 128, Height: 64,
		Address: ssd1306.Address_128_32,
	})

	display.ClearDisplay()

	led.Configure(machine.PinConfig{Mode: machine.PinOutput})

	for !sensor.Connected() {
		led.High()
		time.Sleep(250 * time.Millisecond)
		led.Low()
		time.Sleep(1_000 * time.Millisecond)
	}

	button.Configure(machine.PinConfig{Mode: machine.PinInput})

    // The button press handler is run concurrently in a go routine!
	go handleButton()
}

// ............................................................................
func loop() {
	for {
		temp, _ = sensor.ReadTemperature()
		humidity, _ = sensor.ReadHumidity()

		displayReadings()

		time.Sleep(500 * time.Millisecond)
	}
}

// ............................................................................
func handleButton() {
	for {
		if button.Get() {
			showCelcius = !showCelcius
			led.High()
			time.Sleep(500 * time.Millisecond)
		}

		if showCelcius {
			led.High()
		} else {
			led.Low()
		}

		time.Sleep(50 * time.Millisecond)
	}
}

// ............................................................................
func displayReadings() {
	if showCelcius {
		temp /= 1_000
	} else {
		temp = int32(float32(temp)*1.8)/1_000 + 32
	}

	display.ClearBuffer()
	displayText = fmt.Sprintf("%d", temp)
	tinyfont.WriteLine(&display, &freesans.Bold18pt7b, 30, 26, displayText, black)
	_, textWidth := tinyfont.LineWidth(&freesans.Bold18pt7b, displayText)

	if showCelcius {
		tinyfont.WriteLine(&display, &freesans.Bold12pt7b, int16(textWidth)+35, 26, "C", black)
	} else {
		tinyfont.WriteLine(&display, &freesans.Bold12pt7b, int16(textWidth)+35, 26, "F", black)
	}

	displayText = fmt.Sprintf("%d%% H", humidity/100)
	_, textWidth = tinyfont.LineWidth(&freesans.Regular9pt7b, displayText)
	tinyfont.WriteLine(&display, &freesans.Regular9pt7b, 64-(int16(textWidth)/2), 50, displayText, black)

	display.Display()
}
