# NeoPixel library strandtest example
# Author: Tony DiCola (tony@tonydicola.com)
#
# Direct port of the Arduino NeoPixel library strandtest example.  Showcases
# various animations on a strip of NeoPixels.
import time

from neopixel import *

import argparse
import signal
import sys

def signal_handler(signal, frame):
        colorWipe(strip, Color(0,0,0))
        sys.exit(0)

def opt_parse():
        parser = argparse.ArgumentParser()
        parser.add_argument('-c', action='store_true', help='clear the display on exit')
        args = parser.parse_args()
        if args.c:
                signal.signal(signal.SIGINT, signal_handler)

# LED strip configuration:
LED_COUNT      = 16      # Number of LED pixels.
LED_PIN        = 18      # GPIO pin connected to the pixels (18 uses PWM!).
#LED_PIN        = 10      # GPIO pin connected to the pixels (10 uses SPI /dev/spidev0.0).
LED_FREQ_HZ    = 800000  # LED signal frequency in hertz (usually 800khz)
LED_DMA        = 10      # DMA channel to use for generating signal (try 10)
LED_BRIGHTNESS = 255     # Set to 0 for darkest and 255 for brightest
LED_INVERT     = False   # True to invert the signal (when using NPN transistor level shift)
LED_CHANNEL    = 0       # set to '1' for GPIOs 13, 19, 41, 45 or 53
LED_STRIP      = ws.WS2811_STRIP_GRB   # Strip type and colour ordering



# Define functions for dripbot visuals

def ringFlash(strip, color, flashes, wait_ms=50):
    """Flash color to indicate the pot has been grubered."""
    for i in range(flashes):
        for i in range(strip.numPixels()):
            strip.setPixelColor(i, color)
        strip.show()
        time.sleep(wait_ms/1000.0)
        for i in range(strip.numPixels()):
            strip.setPixelColor(i, Color(0, 0, 0))
        strip.show()
        time.sleep(wait_ms/1000.0)
        
def ringTimer(strip, color_list, wait_ms=50, timer_min=60):
    """
    Wipe colors across display a pixel at a time,
    then count down timer in equal amounts of time per pixel.
    """
    # Animate on display
    for i in range(strip.numPixels() -1, -1, -1):
        strip.setPixelColor(i, Color(color_list[i][0], color_list[i][1], color_list[i][2]))
        strip.show()
        time.sleep(wait_ms/1000.0)
    # Timer
    for i in range(strip.numPixels()):
        time.sleep(timer_min * 60.0 / strip.numPixels())
        strip.setPixelColor(i, Color(0,0,0))
        strip.show()
        
def ringTimerSetup(strip, color_list, wait_ms=50):
    """
    Wipe colors across display a pixel at a time,
    then count down timer in equal amounts of time per pixel.
    """
    # Animate on display
    for i in range(strip.numPixels() -1, -1, -1):
        strip.setPixelColor(i, Color(color_list[i][0], color_list[i][1], color_list[i][2]))
        strip.show()
        time.sleep(wait_ms/1000.0)
        
def colorWipe(strip, color, wait_ms=50):
    """Wipe color across display a pixel at a time."""
    for i in range(strip.numPixels()):
        strip.setPixelColor(i, color)
        strip.show()
        time.sleep(wait_ms/1000.0)
        
        

# Main program logic follows:
if __name__ == '__main__':
    # Process arguments
    opt_parse()

    # Create NeoPixel object with appropriate configuration.
    strip = Adafruit_NeoPixel(LED_COUNT, LED_PIN, LED_FREQ_HZ, LED_DMA, LED_INVERT, LED_BRIGHTNESS, LED_CHANNEL, LED_STRIP)
    # Intialize the library (must be called once before other functions).
    strip.begin()
    
    fresh_colors = [[0, 200, 200], [12, 188, 200], [25, 175, 200], [38, 162, 200],
                    [50, 150, 200], [62, 138, 200], [75, 125, 200], [88, 112, 200], 
                    [100, 100, 200], [112, 88, 200], [125, 75, 200], [138, 62, 200],
                    [150, 50, 200], [162, 38, 200], [175, 25, 200], [200, 0, 200]]

    print ('Press Ctrl-C to quit.')
    while True:
        print("gruber animation")
        ringFlash(strip, Color(255, 0, 255), flashes=10, wait_ms=100)
        time.sleep(2)
        print("fresh animation")
        ringTimer(strip, fresh_colors, wait_ms=50, timer_min=0.25)
        time.sleep(2)