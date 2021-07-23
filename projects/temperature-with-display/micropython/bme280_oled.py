"""
    This project uses a BME280 temperature/humidity sensor and an
    SSD1306 OLED display (128x64 pixels). Both use the I2C bus, so
    the only required pins for using both components are the SDA and SCL pins.

    This code was tested on the following boards:
    - Wemos D1 Mini (ESP8266 board)
    - ESP32 WROOM development board
"""

from machine import I2C, Pin
import ssd1306
import utime
import gc
import framebuf
from lib.bme280 import BME280
import lib.freesans20
import lib.writer as screen_writer


gc.collect()    # Starts the garbage collector

i2c = I2C(scl=Pin(5), sda=Pin(4), freq=100000)
bme = BME280(i2c=i2c)
display = ssd1306.SSD1306_I2C(128, 64, i2c)

icons = dict()
writer = screen_writer.Writer(display, freesans20)


# ...........................................................
def displayIcon(iconname, top, left):
    """ displayIcon() reads an image file in BPM format
        (see https://en.wikipedia.org/wiki/BMP_file_format)
        and writes it on the OLED display at the specified
        position.

    Args:
        iconname (str): Name of the icon image file
        top (int): Top position at which to display the image
        left (int): Left position at which to display the image
    """

    # ... Python optimization ...
    # Create references to functions in the local scope.
    # Calling a local-scope function is immediate, whereas
    # Python needs to go look up a globally-scoped function, which is
    # a relatively slow operation, every time the function is called.
    # This technique makes a huge difference for
    # functions that are called in a loop.
    blit = display.blit
    fb = framebuf.FrameBuffer

    # Next we'll cache the icon image in a dictionary so that we
    # only need to read it from "disk" once. This takes up some memory,
    # but the files are tiny and ESP8266 boards have enough RAM to spare
    # for this little application.
    icon = icons.get(iconname)

    if not icon:
        with open("icons/" + iconname, 'rb') as f:
            _ = f.readline()    # Magic number
            dim = f.readline().decode().strip()

            if dim.startswith('#'):
                dim = f.readline().decode().strip()

            w, h = [int(s) for s in dim.split(' ')]    # Dimensions
            data = bytearray(f.read())
            icon = fb(data, w, h, framebuf.MONO_HLSB)
            icons[iconname] = icon

    blit(icon, top, left)


# ...........................................................
def show(tempC, tempF, hum):
    """[summary]

    Args:
        tempC ([type]): [description]
        tempF ([type]): [description]
        hum ([type]): [description]
    """
    slen = writer.stringlen
    setp = writer.set_textpos
    prints = writer.printstring

    start = 30
    setp(start, 10)
    t = str(tempF)
    prints(t)

    start = start + slen(t) + 2
    displayIcon('fahrenheit.pbm', start, 10)
    start = start + 20
    setp(start, 10)
    t = str(tempC)
    prints(t)
    start = start + slen(t) + 2
    displayIcon('celcius.pbm', start, 10)

    start = 30
    setp(start, 40)
    t = str(hum)
    prints(t)
    start = start + slen(t) + 2
    displayIcon('percent.pbm', start, 40)
    display.show()


# ...........................................................
def run():
    """
    This is the main logic of the project.
    Having the logic in a function instead of the at the global
    scope is a Python optimization, whereby code within a function
    executes faster than code in the global scope.
    """

    sleep = utime.sleep
    s = show

    # Show icons
    displayIcon('temperature.pbm', 10, 12)
    displayIcon('humidity.pbm', 10, 42)
    display.show()

    while True:
        try:
            tC, h, _ = bme.values
            tF = round((tC * 1.8) + 32)
            tC = round(tC)
            h = round(h)
            s(tC, tF, h)
        except Exception as e:
            print('bad reading')
            print(e)

        sleep(1)


# ...........................................................
run()
