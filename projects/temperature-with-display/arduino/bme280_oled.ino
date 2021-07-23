/*
    This project uses a BME280 temperature/humidity sensor and an
    SSD1306 OLED display (128x64 pixels). Both use the I2C bus, so
    the only required pins for using both components are the SDA and SCL pins.
    A button is used to switch the displayed temerature units between
    Celcius and Farenheit.

    The code also demonstrates the use of the TaskScheduler library
    to implement the logic as concurrent tasks, rather than the usual
    loops and delays.

    We'll also be using multiple fonts (including glyph fonts for icons)
    on our display. See https://github.com/olikraus/u8g2/wiki/fntlist8x8.

    This code was tested on the following boards:
    - Wemos D1 Mini (ESP8266 board)
    - ESP32 WROOM development board
    - Arduino Uno
    - Arduino Pro Mico (Leonardo)
    - Adafruit Trinket M0
    - Arduino Nano 33 IoT
*/

#include <TaskScheduler.h>
#include <U8x8lib.h>
#include <BME280I2C.h>
#include <Wire.h>

U8X8_SSD1306_128X64_NONAME_HW_I2C display(U8X8_PIN_NONE);
BME280I2C bme;
float temperatureF, temperatureC, humidity, pressure;
volatile bool showCelcius = false;
unsigned long lastPressed;
bool triggered = false;

const static int LED = LED_BUILTIN;
const static int BUTTON = 2;
const static int DEBOUNCE_DELAY = 350;

// We're going to use Tasks to run our sensor reading and display instead of
// using the loop() function.
// Define the callback for the Task.
void sensorCallback();
void buttonHandler();

// Define the sensor reading task
Task sensorTask(500, TASK_FOREVER, &sensorCallback);
Task buttonTask(50, TASK_FOREVER, &buttonHandler);
Scheduler taskRunner;

// - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
void sensorCallback()
{
    bme.read(pressure, temperatureC, humidity);
    temperatureF = temperatureC * 1.8 + 32.0;

    displayReadings();
}

// - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
void displayReadings()
{
    displayTemperature();
    displayHumidity();
}

// - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
void displayIcons()
{
    display.setFont(u8x8_font_open_iconic_weather_2x2);
    display.setCursor(0, 1);
    display.print("E");  // Glyph 69

    display.setFont(u8x8_font_open_iconic_thing_2x2);
    display.setCursor(0, 5);
    display.print('H');  // Glyph 72
}

// - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
void displayTemperature()
{
    int temperature =
        (int)(round((showCelcius
            ? temperatureC
            : temperatureF) * 10) / 10);

    display.setFont(u8x8_font_courB24_3x4_f);
    display.setCursor(3, 1);
    display.print(temperature);
    display.drawGlyph(9, 1, 176);
    display.setCursor(12, 1);
    display.print(showCelcius ? "C" : "F");
}

// - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
void displayHumidity()
{
    display.setFont(u8x8_font_courR18_2x3_r);
    display.setCursor(3, 5);
    display.print((int)round(humidity));
    display.print("%  ");
}

// - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
void buttonHandler()
{
    if (digitalRead(BUTTON) == HIGH)
    {
        if (lastPressed == 0)
            lastPressed = millis();
        else
        {
            if (!triggered)
            {
                digitalWrite(LED, HIGH);
                triggered = true;
                showCelcius = !showCelcius;
            }

            if (millis() - lastPressed > DEBOUNCE_DELAY)
            {
                lastPressed = 0;
                triggered = false;
                digitalWrite(LED, LOW);
            }
        }
    }
}

// .......................................................................
void setup() {
    Wire.begin();
    bme.begin();
    display.begin();

    pinMode(BUTTON, INPUT);
    pinMode(LED, OUTPUT);

    // Initialize and start our background Task.
    taskRunner.init();
    taskRunner.addTask(sensorTask);
    taskRunner.addTask(buttonTask);
    sensorTask.enable();
    buttonTask.enable();

    displayIcons();
}

// .......................................................................
void loop() {
    // All that is needed here is a call to start up the tash scheduler
    // engine, which takes care of continually running our 2 tasks
    // concurrently.
    taskRunner.execute();
}
